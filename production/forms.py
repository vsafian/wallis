from django import forms
from django.contrib.auth.forms import (
    UserCreationForm
)
from django.db import transaction

from .mixins import FormFieldMixin
from .models import (
    Worker,
    Workplace,
    Printer,
    Material,
    PrintQueue,
    Order
)

from .services import (
    set_remove_foreign_by_cleaned_data_and_instance,
    foreign_case_help_text,
)


class WorkerCreateForm(UserCreationForm):
    class Meta:
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "phone_number",
            "workplace"
        )


class WorkerPhoneNumberForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ("phone_number",)


class WorkplaceForm(
    FormFieldMixin,
    forms.ModelForm
):
    printers = forms.ModelMultipleChoiceField(
        queryset=Printer.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )
    workers = forms.ModelMultipleChoiceField(
        queryset=Worker.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    class Meta:
        model = Workplace
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure_widget_attrs(
            field_name="name",
            attrs={
                "class": "form-control textinput"
            }
        )
        self.initialize()

    def initialize(self):
        for field_name in ["printers", "workers"]:
            field = self.get_field(field_name)
            field.help_text = foreign_case_help_text(
                field_name=field_name,
                instance_name="workplace"
            )
            self.filter_field_queryset_by_instance(field_name)
            self.set_initial_default_queryset(field_name)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            with transaction.atomic():
                instance.save()
                for model in [Printer, Worker]:
                    set_remove_foreign_by_cleaned_data_and_instance(
                        model_to_update=model,
                        cleaned_data=self.cleaned_data,
                        instance=instance,

                    )
        return instance

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = "__all__"


class PrinterForm(
    FormFieldMixin,
    forms.ModelForm
):
    materials = forms.ModelMultipleChoiceField(
        queryset=Material.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = Printer
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        attrs = {"class": "form-control textinput"}
        for field in ["name", "model"]:
            self.configure_widget_attrs(
                field_name=field,
                attrs=attrs
            )
        self.configure_widget_attrs(
            field_name="workplace",
            attrs={
                "class": "select form-control"
            }
        )


class PrintQueueCreateForm(
    FormFieldMixin,
    forms.ModelForm
):
    orders = forms.ModelMultipleChoiceField(
        queryset=(
            Order.objects
            .select_related("material")
            .filter(print_queue=None)
        ),
        widget=forms.CheckboxSelectMultiple(),
        error_messages={
            "required": (
                "Please select at least one order!"
            ),
            "invalid_choice": (
                "There are no available orders yet, "
                "please select other material!"
            )
        }
    )

    class Meta:
        model = PrintQueue
        fields = ("material",)

    def __init__(self, *args, **kwargs):
        self.workplace = kwargs.pop("workplace", None)
        self.printers = (
            Printer.objects
            .select_related('workplace')
            .all()
        )
        super().__init__(*args, **kwargs)

        self.configure_widget_attrs(
            field_name="material",
            attrs={
                "onchange": "this.form.submit();",
                "class": "select form-control",
            }
        )
        self.configure_widget_attrs(
            field_name="orders",
            attrs={
                "onchange": "this.form.submit();",
            }
        )
        self.setup_material_queryset()

    def setup_material_queryset(self):
        materials_field = self.fields['material']
        orders_field = self.fields['orders']
        printers = self.printers.filter(
            workplace=self.workplace
        )
        materials_field.queryset = materials_field.queryset.filter(
            printers__in=printers
        ).distinct()

        orders_field.queryset = orders_field.queryset.filter(
            material__in=materials_field.queryset
        )

    def clean_material(self):
        material = self.cleaned_data["material"]
        orders_field = self.fields['orders']
        orders_field.queryset = orders_field.queryset.filter(
            material=material
        )
        return material

    def clean_orders(self):
        orders = self.cleaned_data.get("orders", Order.objects.none())
        material = self.cleaned_data.get("material", None)
        if not material:
            raise forms.ValidationError(
                "You must select a material first!"
            )
        return orders

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.workplace = self.workplace
        if commit:
            with transaction.atomic():
                instance.save()
                set_remove_foreign_by_cleaned_data_and_instance(
                    model_to_update=Order,
                    cleaned_data=self.cleaned_data,
                    instance=instance,
                )
        return instance


class PrintQueueUpdateForm(
    FormFieldMixin,
    forms.ModelForm
):
    orders = forms.ModelMultipleChoiceField(
        queryset=(
            Order.objects
            .prefetch_related("material")
            .all()
        ),
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = PrintQueue
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.item = kwargs.pop("item", None)
        super().__init__(*args, **kwargs)
        self.configure_widget_attrs(
            field_name="orders",
            attrs={
                "onchange": "this.form.submit();",
            }
        )
        self.initialize()

    def set_instance(self, instance):
        if not self.instance.pk:
            self.instance = instance

    def setup_orders_queryset(self):
        orders = self.get_field("orders")
        orders.queryset = orders.queryset.filter(
            material=self.item.material
        )
        self.filter_field_queryset_by_instance("orders")
        self.set_initial_default_queryset("orders")

    def setup_workplace_queryset(self):
        workplace = self.get_field("workplace")
        workplace.queryset = workplace.queryset.filter(
         printers__materials__in=[self.item.material]
        ).distinct()

    def initialize(self):
        self.setup_orders_queryset()
        self.setup_workplace_queryset()

        material = self.get_field("material")
        material.disabled = True

        for field_name in ["workplace", "material"]:
            self.configure_widget_attrs(
                field_name=field_name,
                attrs={"class": "select form-control"}
            )

        if not self.instance.pk:
            self.initial.setdefault("workplace", self.item.workplace)
            self.initial.setdefault("material", self.item.material)
            self.set_instance(self.item)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            with transaction.atomic():
                instance.save()
                set_remove_foreign_by_cleaned_data_and_instance(
                        model_to_update=Order,
                        cleaned_data=self.cleaned_data,
                        instance=instance
                )
        return instance


class NameFieldSearchForm(
    forms.Form,
    ):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by name"}
        ),
    )


class OrderSearchForm(
    forms.Form,
):
    code = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by code"}
        )
    )
