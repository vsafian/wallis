from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from production.mixins import ModelAbsoluteUrlMixin


class Workplace(models.Model, ModelAbsoluteUrlMixin):
    name = models.CharField(max_length=100)
    view_name = "production:workplace-detail"

    def __str__(self):
        return self.name


class Worker(AbstractUser, ModelAbsoluteUrlMixin):
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
    view_name = "production:worker-detail"

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username}"