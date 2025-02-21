from django.contrib.auth import get_user_model
from django.test import TestCase

from production.models import Workplace, Printer, Material, Order, PrintQueue


class TestItems(TestCase):

    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin", email="<EMAIL>", password="<PASS*0WORD>"
        )
        self.regular_user = get_user_model().objects.create_user(
            username="regular", email="<EMAIL>", password="<PASS*0WORD>"
        )
        self.not_saved_user = get_user_model()(
            username="not_saved_user", email="<EMAIL>", password="<PASS*0WORD>"
        )
        self.workplace1 = Workplace.objects.create(
            name="workplace1",
        )
        self.workplace2 = Workplace.objects.create(
            name="workplace2",
        )
        self.material1 = Material.objects.create(
            name="Material1", type="test", roll_width=1, winding=1, density=1
        )
        self.material2 = Material.objects.create(
            name="Material2", type="test", roll_width=1, winding=1, density=1
        )
        self.material3 = Material.objects.create(
            name="Material3", type="test", roll_width=1, winding=1, density=1
        )
        self.printer1 = Printer.objects.create(
            name="Printer1",
            model="test1",
        )
        self.printer2 = Printer.objects.create(
            name="Printer2",
            model="test2",
        )
        self.printer3 = Printer.objects.create(
            name="Printer3",
            model="test3",
        )
        self.printer4 = Printer.objects.create(
            name="Printer4",
            model="test4",
        )
        self.order1_m1 = Order.objects.create(
            code="1134",
            owner_full_name="owner",
            country_post="pl-dpd",
            image_name="some_name.tiff",
            width=227,
            height=240,
            material=self.material1,
        )
        self.order2_m1 = Order.objects.create(
            code="1135",
            owner_full_name="owner",
            country_post="pl-dpd",
            image_name="some_name.tiff",
            width=227,
            height=240,
            material=self.material1,
        )
        self.order3_m1 = Order.objects.create(
            code="1136",
            owner_full_name="owner",
            country_post="pl-dpd",
            image_name="some_name.tiff",
            width=227,
            height=240,
            material=self.material1,
        )
        self.order1_m2 = Order.objects.create(
            code="1030",
            owner_full_name="owner",
            country_post="pl-dpd",
            image_name="some_name.tiff",
            width=220,
            height=240,
            material=self.material2,
        )
        self.order2_m2 = Order.objects.create(
            code="1031",
            owner_full_name="owner",
            country_post="pl-dpd",
            image_name="some_name.tiff",
            width=220,
            height=240,
            material=self.material2,
        )

        self.queue_m1 = PrintQueue.objects.create(
            material=self.material1,
        )
