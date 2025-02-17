from django import forms
from django.contrib.auth.forms import (
    UserCreationForm
)

from .mixins import (
    FormFieldMixin,
    FormSaveForeignMixin
)
from .services import (
    foreign_case_help_text,
    filter_orders_by_materials,
    fiter_workplaces_by_printers_materials,
    filter_materials_by_printers, filter_orders_by_ready_or_problem_relative,
)

from .models import (
    Worker,
    Workplace,
    Printer,
    Material,
    PrintQueue,
    Order
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
    FormSaveForeignMixin
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
    related_models = [Printer, Worker]

    class Meta:
        model = Workplace
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_form_widget_css(
            field_name="name",
            css_class="form-control textinput"
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
            self.set_initial_default_for_related_field(field_name)


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
        for field_name in ["name", "model"]:
            self.set_form_widget_css(
                field_name=field_name,
                css_class="form-control textinput"
            )
        self.set_form_widget_css(
            field_name="workplace",
            css_class="select form-control"
        )


class PrintQueueCreateForm(
    FormFieldMixin,
    FormSaveForeignMixin
):
    """
    PrintQueueCreateForm:
    - Allows creating a PrintQueue for a given workplace.
    - Filters available materials by printers assigned to the workplace.
    - Filters available orders based on selected material.
    - Uses `FormSaveForeignMixin` to manage Many-to-One relationships.

    Restrictions:
    - The workplace is pre-filled and cannot be changed.
    - At least one order must be selected.
    - The selected orders must match the selected material.
    """
    orders = forms.ModelMultipleChoiceField(
        queryset=(
            Order.objects
            .select_related("material")
            .filter(
                print_queue=None,
                status=Order.READY_TO_PRINT
            )
        ),
        widget=forms.CheckboxSelectMultiple(),
        required=True,
        error_messages={
            "required": (
                "Please select at least one order!"
            ),
            "invalid_choice": ""
        }
    )
    related_models = [Order]

    class Meta:
        model = PrintQueue
        fields = ["workplace", "material"]

    def __init__(self, *args, **kwargs):
        self.cached_workplace = kwargs.pop("cached_workplace", None)
        super().__init__(*args, **kwargs)
        for field_name in ["material", "workplace"]:
            self.set_form_widget_css(
                field_name=field_name,
                css_class="select form-control"
            )
        for field_name in ["orders", "material"]:
            self.set_field_pseudo_dynamic(
                field_name=field_name
            )
        self.initialize()

    def setup_material_queryset(self):
        materials_field = self.fields['material']
        orders_field = self.fields['orders']

        printers = self.cached_workplace.printers.filter(
            status=Printer.ACTIVE
        )

        materials_field.queryset = filter_materials_by_printers(
            materials=materials_field.queryset,
            printers=printers
        )

        orders_field.queryset = filter_orders_by_materials(
            orders=orders_field.queryset,
            materials=materials_field.queryset
        )

    def initialize(self):
        self.disable_field("workplace")
        self.setup_material_queryset()
        self.initial.setdefault("workplace", self.cached_workplace)

    def clean_material(self):
        material = self.cleaned_data["material"]
        orders_field = self.fields['orders']
        orders_field.queryset = filter_orders_by_materials(
            orders=orders_field.queryset,
            materials=[material]
        )
        if not orders_field.queryset:
            raise forms.ValidationError(
                "Please select any other material!"
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


class PrintQueueUpdateForm(
    FormFieldMixin,
    FormSaveForeignMixin
):
    orders = forms.ModelMultipleChoiceField(
        queryset=(
            Order.objects
            .prefetch_related("material")
            .all()
        ),
        widget=forms.CheckboxSelectMultiple(),
    )
    related_models = [Order]

    class Meta:
        model = PrintQueue
        fields = ["material", "workplace"]

    def __init__(self, *args, **kwargs):
        self.cached_instance = kwargs.pop("cached_instance", None)
        super().__init__(*args, **kwargs)
        self.initialize()

    def set_defaults_from_cache(self):
        if not self.instance.pk:
            self.initial.setdefault(
                "workplace", self.cached_instance.workplace
            )
            self.initial.setdefault(
                "material", self.cached_instance.material
            )
            self.instance = self.cached_instance

    def initialize(self):
        self.set_field_pseudo_dynamic("orders")
        self.disable_field("material")
        for field_name in ["workplace", "material"]:
            self.set_form_widget_css(
                field_name=field_name,
                css_class="select form-control"
            )
        self.set_defaults_from_cache()
        self.setup_orders_queryset()
        self.setup_workplace_queryset()

    def setup_orders_queryset(self):
        orders = self.get_field("orders")
        self.filter_field_queryset_by_instance("orders")
        orders.queryset = filter_orders_by_materials(
            orders=orders.queryset,
            materials=[self.instance.material]
        )
        orders.queryset = filter_orders_by_ready_or_problem_relative(
            orders=orders.queryset,
            print_queue=self.instance
        )
        self.set_initial_default_for_related_field("orders")

    def setup_workplace_queryset(self):
        workplace = self.get_field("workplace")
        workplace.queryset = fiter_workplaces_by_printers_materials(
            workplaces=workplace.queryset,
            materials=[self.instance.material]
        )

    def track_problem_orders(self, orders):
        problem_orders = orders.filter(status=Order.PROBLEM)
        if not problem_orders:
            self.instance.status = Order.READY_TO_PRINT

    def clean_orders(self):
        orders = self.cleaned_data.get("orders", Order.objects.none())
        self.track_problem_orders(orders)
        return orders


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
            attrs={"placeholder": "Search by order code"}
        )
    )


class WorkerSearchForm(
    forms.Form,
):
    username = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by username"}
        )
    )


class IDSearchForm(
    forms.Form,
):
    id = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by id"}
        )
    )