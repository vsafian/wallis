from django import forms
from django.contrib.auth.forms import (
    UserCreationForm
)
from django.db import transaction
from .models import Worker, Workplace, Printer

from .services import (
    filter_queryset_by_instance,
    set_remove_foreign_by_cleaned_data_and_instance,
    foreign_case_help_text
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
