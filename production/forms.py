from django import forms
from django.contrib.auth.forms import (
    UserCreationForm
)
from django.db import transaction

from .models import (
    Worker,
    Workplace,
    Printer,
    Material,
    PrintQueue, Order
)

from .services import (
    filter_queryset_by_instance,
    set_remove_foreign_by_cleaned_data_and_instance,
    foreign_case_help_text, associate_items_with_instance
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


class WorkplaceCreateForm(forms.ModelForm):
    class Meta:
        model = Workplace
        fields = "__all__"


class WorkplaceUpdateForm(forms.ModelForm):
    printers = forms.ModelMultipleChoiceField(
        queryset=Printer.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text=foreign_case_help_text(
            Printer, Workplace
        )
    )
    workers = forms.ModelMultipleChoiceField(
        queryset=Worker.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text=foreign_case_help_text(
            Worker, Workplace
        )
    )

    class Meta:
        model = Workplace
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure_printers_queryset()
        self.configure_workers_queryset()

    def configure_printers_queryset(self):
        printers_field = self.fields.get('printers')
        printers_field.queryset = filter_queryset_by_instance(
            printers_field.queryset, self.instance
        )

    def configure_workers_queryset(self):
        workers_field = self.fields.get('workers')
        workers_field.queryset = filter_queryset_by_instance(
            workers_field.queryset, self.instance
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            with transaction.atomic():
                set_remove_foreign_by_cleaned_data_and_instance(
                    model_to_update=Printer,
                    cleaned_data=self.cleaned_data,
                    instance=instance
                )
                set_remove_foreign_by_cleaned_data_and_instance(
                    model_to_update=Worker,
                    cleaned_data=self.cleaned_data,
                    instance=instance
                )
            instance.save()
        return instance


class PrinterCreateForm(forms.ModelForm):
    materials = forms.ModelMultipleChoiceField(
        queryset=Material.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = Printer
        fields = "__all__"


class PrintQueueCreateForm(
    forms.ModelForm
    ):
    material = forms.ModelChoiceField(
        queryset=(
            Material.objects.all()
        ),
        widget=forms.Select(
            attrs={
                "onchange": "this.form.submit();",
                "class": "select form-control",
            }
        ),
    )

    orders = forms.ModelMultipleChoiceField(
        queryset=Order.objects.select_related("material").
        filter(
            print_queue=None,
        ),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "onchange": "this.form.submit();",
            }
        ),
        error_messages={
            "required": (
                "Please select at least one order!"
            ),
            "invalid_choice": (
                "Please select at least one order!"
            )
        }

    )

    class Meta:
        model = PrintQueue
        fields = ("material", )


    def __init__(self, *args, **kwargs):
        self.workplace = kwargs.pop("workplace", None)
        self.printers = (
            Printer.objects
            .select_related('workplace')
            .all()
        )
        super().__init__(*args, **kwargs)
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
            self.cleaned_data.pop("orders")
            raise forms.ValidationError(
                "You must select a material first!"
            )
        return orders

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.workplace = self.workplace
        orders = self.cleaned_data.get(
            "orders", Order.objects.none()
        )
        if commit:
            with transaction.atomic():
                instance.save()
                associate_items_with_instance(
                    instance=instance,
                    items=orders,
                    field_name="print_queue"
                )
        return instance