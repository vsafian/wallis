from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse


class Workplace(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    phone_number = models.CharField(
        max_length=13, null=True, blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+380\d{9}$',
                message=(
                    "Phone number "
                    "must be entered in the format: "
                    "<+380999999999>!"
                ),
                code="invalid_number",
            ),
        ],
        unique=True
    )
    workplace = models.ForeignKey(
        Workplace,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='workers',
    )

    def __str__(self):
        return f"{self.username}"

    def get_absolute_url(self) -> str:
        return reverse(
            "production:worker-detail",
            kwargs={"pk": self.pk}
        )