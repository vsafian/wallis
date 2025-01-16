from copy import copy
from lib2to3.fixes.fix_input import context

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from production.forms import (
    WorkerCreateForm,
    WorkerPhoneNumberForm,

    WorkplaceForm,

    PrinterForm,

    MaterialForm,

    PrintQueueCreateForm,
    PrintQueueUpdateForm, NameFieldSearchForm, OrderSearchForm,

)

from production.mixins import (
    DeleteViewMixin,
    ViewSuccessUrlMixin,
    InstanceCacheMixin, PostApproveMixin
)

from production.models import (
    Worker,
    Workplace,
    Material,
    Printer,
    PrintQueue,
    Order
)

from production.calculations import create_summary_context


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """View function for the home page of the site."""
    context = {
    }
    return render(
        request,
        "production/index.html",
        context=context
    )


class WorkerDetailView(
    LoginRequiredMixin,
    generic.DetailView
):
    model = Worker


class WorkerCreateView(
    LoginRequiredMixin,
    generic.CreateView,
    ViewSuccessUrlMixin,
):
    model = Worker
    template_name = "production/worker_form.html"
    form_class = WorkerCreateForm


class WorkerDeleteView(
    LoginRequiredMixin,
    DeleteViewMixin
):
    model = Worker
    template_name = "production/worker_confirm_delete.html"
    success_url = reverse_lazy("production:worker-list")

class WorkerPhoneView(
    LoginRequiredMixin,
    generic.UpdateView,
    ViewSuccessUrlMixin,
):
    model = Worker
    form_class = WorkerPhoneNumberForm
    template_name = "production/worker_phone_number_form.html"


class WorkerListView(
    LoginRequiredMixin,
    generic.ListView
):
    model = Worker
    paginate_by = 10
    queryset = (
        Worker.objects.select_related("workplace").all()
    )


class WorkplaceListView(
    LoginRequiredMixin,
    generic.ListView
):
    model = Workplace
    paginate_by = 10
    queryset = (
        Workplace.objects.prefetch_related("workers").all()
    )


class WorkplaceCreateView(
    LoginRequiredMixin,
    generic.CreateView,
    ViewSuccessUrlMixin,
):
    model = Workplace
    form_class = WorkplaceForm
    template_name = "production/workplace_form.html"


class WorkplaceUpdateView(
    LoginRequiredMixin,
    generic.UpdateView,
    ViewSuccessUrlMixin,
):
    model = Workplace
    form_class = WorkplaceForm
    template_name = "production/workplace_form.html"


class WorkplaceDetailView(
    LoginRequiredMixin,
    generic.DetailView,
):
    model = Workplace
    queryset = (
        Workplace.objects
        .prefetch_related("workers")
        .prefetch_related("printers", "printers__materials")
        .all()
    )


class WorkplaceDeleteView(
    LoginRequiredMixin,
    DeleteViewMixin
):
    model = Workplace
    success_url = reverse_lazy("production:workplace-list")
    template_name = "production/workplace_confirm_delete.html"


class MaterialListView(
    LoginRequiredMixin,
    generic.ListView
):
    model = Material
    paginate_by = 14

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = NameFieldSearchForm(
            initial={"name": name}
        )
        return context


    def get_queryset(self) -> QuerySet:
        queryset = Material.objects.all()
        form = NameFieldSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                name__icontains=form.cleaned_data["name"]
            )
        return queryset


class MaterialDetailView(
    LoginRequiredMixin,
    generic.DetailView,
   ):
    model = Material
    queryset = (
        Material.objects
        .prefetch_related(
            "printers",
            "printers__workplace"
        ).all()
    )


class MaterialCreateView(
    LoginRequiredMixin,
    generic.CreateView,
    ViewSuccessUrlMixin
):
    model = Material
    form_class = MaterialForm
    template_name = "production/material_form.html"


class MaterialUpdateView(
    LoginRequiredMixin,
    generic.UpdateView,
    ViewSuccessUrlMixin,
):
    model = Material
    form_class = MaterialForm
    template_name = "production/material_form.html"


class MaterialDeleteView(
    LoginRequiredMixin,
    DeleteViewMixin
):
    model = Material
    success_url = reverse_lazy("production:material-list")
    template_name = "production/material_confirm_delete.html"


class PrinterListView(
    LoginRequiredMixin,
    generic.ListView
):
    model = Printer
    paginate_by = 14
    queryset = (
        Printer.objects
        .prefetch_related("materials", "workplace")
        .all()
    )


class PrinterCreateView(
    LoginRequiredMixin,
    generic.CreateView,
    ViewSuccessUrlMixin,
):
    model = Printer
    form_class = PrinterForm
    template_name = "production/printer_form.html"


class PrinterUpdateView(
    LoginRequiredMixin,
    generic.UpdateView,
    ViewSuccessUrlMixin,
):
    model = Printer
    form_class = PrinterForm
    template_name = "production/printer_form.html"


class PrinterDetailView(
    LoginRequiredMixin,
    generic.DetailView
):
    model = Printer


class PrinterDeleteView(
    LoginRequiredMixin,
    DeleteViewMixin
):
    model = Printer
    success_url = reverse_lazy("production:printer-list")
    template_name = "production/printer_confirm_delete.html"


class PrintQueueDetailView(
    LoginRequiredMixin,
    generic.DetailView
):
    model = PrintQueue
    template_name = "production/print_queue_detail.html"


class PrintQueueListView(
    LoginRequiredMixin,
    generic.ListView
):
    model = PrintQueue
    paginate_by = 10
    template_name = "production/print_queue_list.html"


class PrintQueueDeleteView(
    LoginRequiredMixin,
    DeleteViewMixin
):
    model = PrintQueue
    success_url = reverse_lazy("production:print-queue-list")
    template_name = "production/print_queue_confirm_delete.html"


class OrderDetailView(
    LoginRequiredMixin,
    generic.DetailView
):
    model = Order


class OrderListView(
    LoginRequiredMixin,
    generic.ListView
):
    model = Order
    paginate_by = 16

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        code = self.request.GET.get("code", "")
        context["search_form"] = OrderSearchForm(
            initial={"code": code}
        )
        return context

    def get_queryset(self) -> QuerySet:
        queryset = Order.objects.prefetch_related("material")
        form = OrderSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                code__icontains=form.cleaned_data["code"]
            )
        return queryset

class PrintQueueCreateView(
    PostApproveMixin,
    InstanceCacheMixin,
    LoginRequiredMixin,
    generic.CreateView,
    ViewSuccessUrlMixin,
):

    model = PrintQueue
    form_class = PrintQueueCreateForm
    template_name = "production/print_queue_form.html"

    @property
    def workplace(self) -> Workplace:
        return self.cache_instance(Workplace)

    def get_context_data(self, **kwargs):
        context = copy(kwargs)
        form = self.get_form()

        if "form" not in context:
            context["form"] = form

        context["workplace"] = self.workplace
        context.update(
            create_summary_context(context.get("form"))
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["workplace"] = self.workplace
        return kwargs


class PrintQueueUpdateView(
    PostApproveMixin,
    InstanceCacheMixin,
    LoginRequiredMixin,
    generic.UpdateView,
    ViewSuccessUrlMixin,
):
    model = PrintQueue
    form_class = PrintQueueUpdateForm
    template_name = "production/print_queue_form.html"

    @property
    def print_queue(self) -> PrintQueue:
        return self.cache_instance(PrintQueue)

    def get_context_data(self, **kwargs):
        context = copy(kwargs)
        form = self.get_form()
        if "form" not in context:
            context["form"] = form

        context.update(
            create_summary_context(context.get("form"))
        )
        context.update({"object": self.print_queue})
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["item"] = self.print_queue
        return kwargs
