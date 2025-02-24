from django.test import TestCase
from django.urls import reverse

from production.models import (
    Workplace, Worker,
    Order,  Printer,
    PrintQueue, Material
)

from tests.test_items import TestItems

INDEX_URL = reverse("production:index")
ORDER_URL = reverse("production:order-list")
MATERIAL_URL = reverse("production:material-list")
WORKPLACE_URL = reverse("production:workplace-list")
WORKER_URL = reverse("production:worker-list")
PRINT_QUEUE_URL = reverse("production:print-queue-list")
PRINTER_URL = reverse("production:printer-list")


class TestViewsSetUp(TestItems):
    def setUp(self):
        super().setUp()
        self.name_search = "find_me_by_name"
        self.order_search = "find_me_by_code"

        self.client.force_login(self.admin_user)
        self.username_search = self.admin_user.username
        self.workplace_search = self.workplace1.name


class PublicIndexTest(TestCase):
    def test_login_required(self) -> None:
        response = self.client.get(INDEX_URL)
        self.assertNotEqual(response.status_code, 200)


class PublicWorkerTest(TestCase):
    def test_login_required(self) -> None:
        response = self.client.get(WORKER_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateWorkerTest(TestViewsSetUp):
    def test_retrieve_worker(self) -> None:
        response = self.client.get(WORKER_URL)
        self.assertEqual(response.status_code, 200)
        workers = Worker.objects.all()
        self.assertQuerySetEqual(response.context["worker_list"], workers)
        self.assertTemplateUsed(
            response,
            "production/worker_list.html",
        )

    def test_search_worker_by_username(self) -> None:
        response = self.client.get(WORKER_URL, {"username": self.username_search})
        expected_workers = Worker.objects.filter(
            username__icontains=self.username_search
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["worker_list"], expected_workers)


class PublicWorkplaceTest(TestCase):
    def test_login_required(self) -> None:
        response = self.client.get(WORKPLACE_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateWorkplaceTest(TestViewsSetUp):
    def test_retrieve_workspace(self) -> None:
        response = self.client.get(WORKPLACE_URL)
        workplaces = Workplace.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["workplace_list"], workplaces)

        self.assertTemplateUsed(
            response,
            "production/workplace_list.html",
        )

    def test_search_workspace_by_name(self) -> None:
        response = self.client.get(WORKPLACE_URL, {"name": self.workplace_search})
        workplaces = Workplace.objects.filter(name__icontains=self.workplace_search)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["workplace_list"], workplaces)


class PublicMaterialTest(TestCase):
    def test_login_required(self) -> None:
        response = self.client.get(MATERIAL_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateMaterialTest(TestViewsSetUp):
    def test_retrieve_material(self) -> None:
        response = self.client.get(MATERIAL_URL)
        self.assertEqual(response.status_code, 200)
        expected_materials = Material.objects.all()
        self.assertQuerySetEqual(response.context["materials_list"], expected_materials)
        self.assertTemplateUsed(
            response,
            "production/material_list.html",
        )


class PublicPrinterTest(TestCase):
    def test_login_required(self) -> None:
        response = self.client.get(PRINTER_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivatePrinterTest(TestViewsSetUp):
    def test_retrieve_printer(self) -> None:
        response = self.client.get(PRINTER_URL)
        expected_printers = Printer.objects.all()
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["printers_list"], expected_printers)


class PublicOrderTest(TestCase):
    def test_login_required(self) -> None:
        response = self.client.get(ORDER_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateOrderTest(TestViewsSetUp):
    def test_retrieve_order(self) -> None:
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, 200)
        expected_orders = Order.objects.all()
        self.assertQuerySetEqual(response.context["orders_list"], expected_orders)


class PublicPrintQueueTest(TestCase):
    def test_login_required(self) -> None:
        response = self.client.get(PRINT_QUEUE_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivatePrintQueueTest(TestViewsSetUp):
    def test_retrieve_queue(self) -> None:
        response = self.client.get(PRINT_QUEUE_URL)
        expected_queues = PrintQueue.objects.all()
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["printqueue_list"], expected_queues)


class ChangeOrderStatusTest(TestViewsSetUp):

    @staticmethod
    def target_url(pk: int) -> str:
        return reverse("production:change-order-status", args=[pk])

    def setUp(self):
        super().setUp()
        self.printer1.materials.add(self.material1)
        self.printer1.workplace = self.workplace1
        self.printer1.save()

        self.print_queue = PrintQueue.objects.create(
            material=self.material1, workplace=self.workplace1
        )

    def test_change_status_to_problem_with_queue(self):
        self.order1_m1.status = Order.READY_TO_PRINT
        self.order1_m1.save()

        self.print_queue.orders.add(self.order1_m1)
        self.print_queue.save()

        url = self.target_url(self.order1_m1.pk)
        response = self.client.get(url)

        self.order1_m1.refresh_from_db()
        self.print_queue.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.order1_m1.status, Order.PROBLEM)
        self.assertEqual(self.print_queue.status, PrintQueue.PROBLEM)

    def test_change_status_to_problem_without_queue(self):
        self.order1_m1.status = Order.READY_TO_PRINT
        self.order1_m1.save()
        url = self.target_url(self.order1_m1.pk)
        response = self.client.get(url)

        self.order1_m1.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.order1_m1.status, Order.PROBLEM)

    def test_change_status_to_ready_with_queue(self):
        self.order1_m1.status = Order.PROBLEM
        self.order1_m1.save()
        self.print_queue.orders.add(self.order1_m1)
        self.print_queue.status = PrintQueue.PROBLEM
        self.print_queue.save()

        url = self.target_url(self.order1_m1.pk)
        response = self.client.get(url)

        self.order1_m1.refresh_from_db()
        self.print_queue.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.order1_m1.status, Order.READY_TO_PRINT)
        self.assertEqual(self.print_queue.status, PrintQueue.READY_TO_PRINT)

    def test_change_status_to_ready_without_queue_change(self):
        orders = [self.order1_m2, self.order1_m1]
        for order in orders:
            order.status = Order.PROBLEM
            order.save()

        self.print_queue.orders.add(*orders)
        self.print_queue.status = PrintQueue.PROBLEM
        self.print_queue.save()

        url = self.target_url(self.order1_m1.pk)
        response = self.client.get(url)

        self.order1_m1.refresh_from_db()
        self.print_queue.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.order1_m1.status, Order.READY_TO_PRINT)
        self.assertEqual(self.print_queue.status, PrintQueue.PROBLEM)

    def test_does_not_change_non_editable_order(self):
        self.order1_m1.status = Order.DONE
        self.order1_m1.save()

        url = self.target_url(self.order1_m1.pk)
        response = self.client.get(url)
        self.order1_m1.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.order1_m1.status, Order.DONE)
