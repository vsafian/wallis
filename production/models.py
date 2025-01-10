from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from production.mixins import ModelAbsoluteUrlMixin
from django.conf import settings

from production.sub_classes import PrintQueueSummary


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
        return f"{self.username} | Workplace: {self.workplace}"


class Material(
    models.Model,
    ModelAbsoluteUrlMixin,
):
    name = models.CharField(
        max_length=100,
        unique=True
    )
    type = models.CharField(max_length=100)
    roll_width = models.FloatField()
    winding = models.IntegerField()
    density = models.IntegerField()
    view_name = "production:material-detail"

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['type']


class Printer(
    models.Model,
    ModelAbsoluteUrlMixin,
):
    name = models.CharField(
        max_length=100, unique=False
    )
    model = models.CharField(
        max_length=100, unique=True
    )
    materials = models.ManyToManyField(
        Material,
        related_name='printers'
    )
    workplace = models.ForeignKey(
        Workplace, related_name='printers',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    view_name = "production:printer-detail"

    class Meta:
        ordering = ['name']

    def __str__(self):
        return (
            f"({self.full_name} | "
            f"Workplace: {self.workplace})"
        )

    @property
    def full_name(self):
        return f"{self.name} {self.model}"


class PrintQueue(
    models.Model,
    ModelAbsoluteUrlMixin
):
    workplace = models.ForeignKey(
        Workplace,
        related_name="print_queues",
        on_delete=models.CASCADE,
    )

    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name='print_queues',
    )

    creation_time = models.DateTimeField(
        auto_now_add=True,
    )
    view_name = "production:print-queue-detail"

    class Meta:
        ordering = ['creation_time']
        default_related_name = 'print_queues'

    def __str__(self):
        return f"id: {self.id}|{self.workplace} | Material: {self.material}"

    @property
    def summary(self) -> PrintQueueSummary:
        orders = self.orders.all()
        return PrintQueueSummary(orders, self.material)


class Order(
    models.Model,
    ModelAbsoluteUrlMixin,
):
    code = models.CharField(
        max_length=100, unique=True,
        validators=[RegexValidator(
            regex=r"^\d+$",
            message="The code must contain only digits!",
            code="invalid_code",
        )]
    )
    owner_full_name = models.CharField(max_length=255)
    manager = models.CharField(
        max_length=255,
        default="AutoCreate"
    )
    performer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='orders',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    country_post = models.CharField(
        max_length=255,
        default="ukr-Nova Post"
    )
    creation_time = models.DateTimeField(auto_now_add=True)
    performing_time = models.DateTimeField(
        null=True,
        blank=True
    )
    image_name = models.CharField(max_length=255)
    material = models.ForeignKey(
        Material,
        related_name='orders',
        on_delete=models.CASCADE
    )
    width = models.IntegerField()
    height = models.IntegerField()
    comment = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    print_queue = models.ForeignKey(
        PrintQueue,
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True, blank=True,

    )
    view_name = "production:order-detail"


    def __str__(self):
        return (
            f"#{self.id} | "
            f"Material: {self.material} | "
            f"Tiles: {self.tiles_count} | "
            f"m²: {self.square_meters}"
        )

    @property
    def square_meters(self) -> float:
        return round(
            self.width * self.height / 10000, 2
        )

    @property
    def tiles_count(self, max_tile_width: int = 50) -> int:
        segments = self.width // max_tile_width
        single_tile_width = self.width / segments

        while single_tile_width > max_tile_width:
            segments += 1
            single_tile_width = round(self.width / segments, 2)

        return segments

    @property
    def narrow_tile_width(self) -> float:
        return round(
            (self.width / self.tiles_count) * 10, 2
        )

    @property
    def wide_tile_width(self) -> float:
        return self.narrow_tile_width * 2