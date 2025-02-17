from django.db.models import Q
from django.test import TestCase

from production.forms import (
    WorkerCreateForm,
    WorkerPhoneNumberForm, WorkplaceForm, PrintQueueCreateForm, PrintQueueUpdateForm
)
from production.models import Printer, Material, Order, PrintQueue, Workplace
from tests.test_items import TestItems


class FormsTest(TestCase):
    def setUp(self):
        self.worker_form_data = {
            "username": "new_user",
            "password1": "user12test",
            "password2": "user12test",
            "first_name": "Test first",
            "last_name": "Test last",
            "phone_number": "+380999999999"
        }
        self.form = WorkerCreateForm(data=self.worker_form_data)
        
    @staticmethod
    def phone_number_form_is_valid(number: str) -> bool:
        return WorkerPhoneNumberForm(
            data={"phone_number": number}
        ).is_valid()
    
    def test_worker_creation_form_is_valid(self) -> None:
        self.assertTrue(self.form.is_valid())


    def test_phone_number_is_valid(self) -> None:
        self.assertTrue(
            self.phone_number_form_is_valid("+380999999999")
        )

    def test_phone_number_not_less_than_13(self) -> None:
        self.assertFalse(self.phone_number_form_is_valid("+3809"))

    def test_phone_number_not_more_than_13(self) -> None:
        self.assertFalse(
            self.phone_number_form_is_valid("+3809999999999999999")
        )

    def test_phone_number_with_invalid_characters(self) -> None:
        self.assertFalse(
            self.phone_number_form_is_valid("+380ABCDEF123")
        )


class TestWorkplaceForm(TestItems):
    """
    I'm only testing the initial context, queryset
    and adding/removing printers here,
    it works the same way with workers.
    """
    def setUp(self):
        super().setUp()
        self.printers = [self.printer1, self.printer2]
        self.instance = self.workplace1

        self.new_object_form_data = {
            "name": "test",
        }
        self.instance_form_data = {
            "name": self.instance.name
        }

    def test_workplace_creation_form_is_valid(self) -> None:
        form = WorkplaceForm(data=self.new_object_form_data)
        self.assertTrue(form.is_valid())

    def test_form_initial_context(self):
        workers = [self.regular_user, self.admin_user]
        for printer, worker in zip(self.printers, workers):
            printer.workplace = self.instance
            printer.save()
            worker.workplace = self.instance
            worker.save()

        form = WorkplaceForm(instance=self.instance, data=self.instance_form_data)
        initial_context = form.initial_context
        self.assertListEqual(
            self.printers,
            list(initial_context['printers'])
        )
        self.assertListEqual(
            workers,
            list(initial_context['workers'])
        )

    def test_form_printers_queryset_while_object_was_created(self) -> None:
        for printer in self.printers:
            printer.workplace = self.instance
            printer.save()
        form = WorkplaceForm(
            instance=self.instance,
            data=self.instance_form_data
        )
        expected_queryset = Printer.objects.filter(
            Q(workplace=self.instance) | Q(workplace=None)
        )
        self.assertQuerySetEqual(
            expected_queryset,
            form.fields.get('printers').queryset.all()
        )

    def test_form_printers_queryset_when_create_new_object(self) -> None:
        expected_queryset = Printer.objects.filter(
            workplace=None
        )
        form = WorkplaceForm(data=self.new_object_form_data)
        self.assertQuerySetEqual(
            expected_queryset,
            form.fields.get('printers').queryset.all()
        )

    def test_printers_assigned_to_workplace(self) -> None:
        self.new_object_form_data.update({
                "printers":
                Printer.objects.filter(workplace=None)
        })
        form = WorkplaceForm(
            data=self.new_object_form_data
        )
        instance = form.save()
        instance_printers = instance.printers.all()
        expected_printers = Printer.objects.filter(workplace=instance)
        free_printers = Printer.objects.filter(
            workplace=None
        )
        self.assertQuerySetEqual(
            expected_printers,
            instance_printers
        )
        self.assertNotIn(instance_printers, free_printers)

    def test_printers_remove_from_workplace(self):
        self.printer1.workplace = self.instance
        self.printer1.save()

        self.assertIn(self.printer1, self.instance.printers.all())

        self.instance_form_data.update({
            "printers": []
        })

        form = WorkplaceForm(instance=self.instance, data=self.instance_form_data)
        form.save()
        self.printer1.refresh_from_db()
        self.assertTrue(form.is_valid())
        self.assertNotIn(self.printer1, self.instance.printers.all())
        self.assertIsNone(self.printer1.workplace)


class TestPrintQueueCreateForm(TestItems):
    def setUp(self):
        super().setUp()
        self.workplace = self.workplace1
        self.printers = [self.printer1, self.printer2]
        self.printer1.materials.add(self.material1)
        self.printer2.materials.add(self.material2)
        for printer in self.printers:
            printer.workplace = self.workplace
            printer.save()


    def test_form_valid_with_correct_data(self) -> None:
        form_data = {
            "material": self.material1,
            "orders": [self.order1_m1, self.order2_m1,]
        }
        form = PrintQueueCreateForm(
            data=form_data, cached_workplace=self.workplace
        )
        self.assertTrue(form.is_valid())

    def test_material_queryset_is_filtered_by_workplace_printers(self) -> None:
        form = PrintQueueCreateForm(
            cached_workplace=self.workplace
        )
        material_queryset = form.get_field_queryset("material")
        expected_materials = Material.objects.filter(
            printers__in=self.workplace.printers.all()
        ).distinct()
        self.assertQuerySetEqual(material_queryset, expected_materials)

    def test_orders_queryset_is_filtered_by_workplace_materials(self) -> None:
        form = PrintQueueCreateForm(
            cached_workplace=self.workplace
        )
        orders_queryset = form.get_field_queryset("orders")
        materials = Material.objects.filter(
            printers__in=self.workplace.printers.all()
        ).distinct()
        expected_orders = Order.objects.filter(
            material__in=materials
        )
        self.assertQuerySetEqual(orders_queryset, expected_orders)

    def test_when_orders_have_wrong_material(self):
        form_data = {
            "material": self.material1,
            "orders": [self.order1_m2, self.order2_m2,]
        }
        form = PrintQueueCreateForm(
            data=form_data, cached_workplace=self.workplace
        )
        self.assertFalse(form.is_valid())
        self.assertIn("orders", form.errors)


    def test_orders_queryset_is_filtered_by_selected_material(self) -> None:
        form = PrintQueueCreateForm(
            data={"material": self.material1},
            cached_workplace=self.workplace
        )
        form.is_valid()
        orders_queryset = form.get_field_queryset("orders")
        expected_orders = Order.objects.filter(
            print_queue=None, material=self.material1
        )
        self.assertQuerySetEqual(orders_queryset, expected_orders)

    def test_error_when_orders_selected_without_material(self):
        form = PrintQueueCreateForm(
            data={"orders": [self.order1_m1]},
            cached_workplace=self.workplace,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("material", form.errors)

    def test_error_when_no_orders_selected(self):
        form_data = {
            "material": self.material1.id,
            "orders": [],
        }
        form = PrintQueueCreateForm(
            data=form_data, cached_workplace=self.workplace
        )
        self.assertFalse(form.is_valid())
        self.assertIn("orders", form.errors)

    def test_workplace_field_is_disabled(self):
        form = PrintQueueCreateForm(
            cached_workplace=self.workplace
        )
        self.assertTrue(form.fields["workplace"].disabled)

    def test_form_saves_correctly(self):
        orders = [self.order1_m1, self.order2_m1]
        form_data = {
            "material": self.material1,
            "orders": orders
        }
        form = PrintQueueCreateForm(
            data=form_data, cached_workplace=self.workplace
        )
        self.assertTrue(form.is_valid())
        instance = form.save()

        self.assertIsInstance(instance, PrintQueue)
        self.assertEqual(instance.material, self.material1)
        self.assertEqual(instance.workplace, self.workplace)
        self.assertEqual(set(instance.orders.all()), set(orders))


class TestPrintQueueUpdateForm(TestItems):
    def setUp(self):
        super().setUp()
        self.printer1.materials.add(self.material1)
        self.workplace1.printers.add(self.printer1)
        self.print_queue = PrintQueue.objects.create(
            workplace=self.workplace1,
            material=self.material1,
        )
        self.orders = [self.order1_m1, self.order2_m1]

    def test_form_initial_data_is_correct(self):
        for order in self.orders:
            order.print_queue = self.print_queue
            order.save()

        form = PrintQueueUpdateForm(
            cached_instance=self.print_queue
        )
        self.assertEqual(
            form.initial["workplace"], self.workplace1
        )
        self.assertEqual(
            form.initial["material"], self.material1
        )
        self.assertEqual(
            set(form.initial["orders"]), set(self.orders)
        )

    def test_material_field_is_disabled(self):
        form = PrintQueueUpdateForm(
            cached_instance=self.print_queue
        )
        self.assertTrue(form.fields["material"].disabled)

    def test_orders_queryset_is_filtered_by_instance_material(self):
        form = PrintQueueUpdateForm(cached_instance=self.print_queue)
        orders_queryset = form.get_field_queryset("orders")
        expected_orders = Order.objects.filter(
            Q(print_queue=self.print_queue) | Q(print_queue=None),
            material=self.material1
        )
        self.assertQuerySetEqual(orders_queryset, expected_orders)

    def test_workplace_queryset_is_filtered_by_instance_material(self):
        form = PrintQueueUpdateForm(cached_instance=self.print_queue)
        workplace_queryset = form.get_field_queryset("workplace")
        expected_workplaces = Workplace.objects.filter(
            printers__materials__in=[self.material1]
        ).distinct()
        self.assertQuerySetEqual(workplace_queryset, expected_workplaces)

    def test_form_is_valid_with_correct_data(self):
        for order in self.orders:
            order.print_queue = self.print_queue
            order.save()
        form_data = {"workplace": self.workplace1,
                     "material": self.material1,
                     "orders": [self.order3_m1]}
        form = PrintQueueUpdateForm(
            data=form_data, cached_instance=self.print_queue
        )
        self.assertTrue(form.is_valid())

    def test_orders_are_updated_correctly_on_save(self):
        form_data = {
            "workplace": self.workplace1,
            "material": self.material1,
            "orders": self.orders,
        }
        form = PrintQueueUpdateForm(
            data=form_data,
            cached_instance=self.print_queue
        )
        self.assertTrue(form.is_valid())
        instance = form.save()

        self.assertEqual(
            set(instance.orders.all()),
            set(self.orders)
        )

    def test_form_raises_error_when_orders_have_wrong_material(self):
        form_data = {
            "workplace": self.workplace1,
            "material": self.material1,
            "orders": [self.order1_m2],
        }
        form = PrintQueueUpdateForm(
            data=form_data,
            cached_instance=self.print_queue
        )
        self.assertFalse(form.is_valid())
        self.assertIn("orders", form.errors)