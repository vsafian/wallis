import django_filters

from production.mixins import FilterFieldMixin
from production.models import Order, Material


class OrderFilter(
    django_filters.FilterSet,
    FilterFieldMixin
    ):
    material = django_filters.ModelChoiceFilter(
        queryset=Material.objects.all(),
        label='Material:',
    )
    country_post = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Post code:',
    )

    class Meta:
        model = Order
        fields = ["material", "country_post"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_form_widget_css(
            field_name="material",
            css_class="select form-control"
        )
        self.set_form_widget_css(
            field_name="country_post",
            css_class="input form-control"
        )