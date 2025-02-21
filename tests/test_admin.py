from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from production.models import Workplace


class AdminSiteTests(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.workplace = Workplace.objects.create(name="test_workplace")
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin", password="testadmin"
        )
        self.client.force_login(self.admin_user)
        self.worker = get_user_model().objects.create_user(
            username="author",
            password="testworker1",
            phone_number="+380999999999",
            workplace=self.workplace,
        )

    def test_worker_phone_number_listed(self) -> None:
        """Test that worker's phone_number is in list_display
        on worker admin page"""
        url = reverse("admin:production_worker_changelist")
        result = self.client.get(url)
        self.assertContains(result, self.worker.phone_number)

    def test_worker_detail_phone_number_listed(self) -> None:
        """Test that worker's phone_number is on detail admin page"""
        url = reverse("admin:production_worker_change", args=[self.worker.id])
        result = self.client.get(url)
        self.assertContains(result, self.worker.phone_number)

    def test_worker_workplace_listed(self) -> None:
        """Test that worker's workplace is in list_display
        on worker admin page"""
        url = reverse("admin:production_worker_changelist")
        result = self.client.get(url)
        self.assertContains(result, self.workplace)

    def test_worker_detail_workplace_listed(self) -> None:
        """Test that worker's workplace is on detail admin page"""
        url = reverse("admin:production_worker_change", args=[self.worker.id])
        result = self.client.get(url)
        self.assertContains(result, self.worker.workplace)
