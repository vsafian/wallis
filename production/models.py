from django.contrib.auth.models import AbstractUser
from django.db import models


class Workplace(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    workplace = models.ForeignKey(
        Workplace,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='workers',
    )

    def __str__(self):
        return f"{self.username}"