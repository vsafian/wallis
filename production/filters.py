import django_filters
from django import forms

from production.mixins import FilterFieldMixin
from production.models import Order, Material, PrintQueue, Workplace


class OrderFilter(
    django_filters.FilterSet,
    FilterFieldMixin
    ):
    material = django_filters.ModelChoiceFilter(
        queryset=Material.objects.all(),
        label='Material:',
    )
    status = django_filters.ChoiceFilter(
        choices=Order.STATUS_CHOICES,
    )
    creation_time = django_filters.DateRangeFilter(
        field_name='creation_time',
        label="Creation Time:",
        lookup_expr='gte',
    )
    country_post = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Post code:',
    )

    class Meta:
        model = Order
        fields = ["material", "status", "creation_time", "country_post"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ["material", "status", "creation_time"]:
            self.set_form_widget_css(
                field_name=field,
                css_class="select form-control"
            )

        self.get_field("country_post").widget = forms.TextInput(
            attrs={"placeholder": "Filter by post code"}
        )
        self.set_form_widget_css(
            field_name="country_post",
            css_class="input form-control"
        )


class PrintQueueFilter(
    django_filters.FilterSet,
    FilterFieldMixin
):
    status = django_filters.ChoiceFilter(
        choices=PrintQueue.STATUS_CHOICES,
    )
    workplace = django_filters.ModelChoiceFilter(
        queryset=Workplace.objects.all(),
        label='Workplace:',
    )

    material = django_filters.ModelChoiceFilter(
        queryset=Material.objects.all(),
        label='Material:',
    )

    class Meta:
        model = PrintQueue
        fields = ["status", "workplace", "material"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ["status", "workplace", "material"]:
            self.set_form_widget_css(
                field_name=field,
                css_class="select form-control"
            )