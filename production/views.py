from audioop import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from production.forms import (
    WorkerCreateForm,
    WorkerPhoneNumberForm,
    WorkplaceCreateForm,
    WorkplaceUpdateForm,
    PrinterCreateForm
)
from production.mixins import (
    DeleteViewMixin,
    ViewSuccessUrlMixin
)
from production.models import (
    Worker, Workplace, Material, Printer
)


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
    ViewSuccessUrlMixin,
    generic.CreateView
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
    ViewSuccessUrlMixin,
    generic.UpdateView
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
    generic.CreateView
):
    model = Workplace
    form_class = WorkplaceCreateForm
    template_name = "production/workplace_form.html"
    success_url = reverse_lazy("production:workplace-list")

class WorkplaceUpdateView(
    LoginRequiredMixin,
    ViewSuccessUrlMixin,
    generic.UpdateView
):
    model = Workplace
    form_class = WorkplaceUpdateForm
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


class MaterialListView(
    LoginRequiredMixin,
    generic.ListView
):
    model = Material
    paginate_by = 10


class MaterialDetailView(
    LoginRequiredMixin,
    generic.DetailView,
   ):
    model = Material
    queryset = (
        Material.objects
        .prefetch_related("printers", "printers__workplace")
        .all()
    )


class PrinterListView(
    LoginRequiredMixin,
    generic.ListView
):
    model = Printer
    paginate_by = 10
    queryset = (
        Printer.objects.prefetch_related("materials").all()
    )

class PrinterCreateView(
    LoginRequiredMixin,
    ViewSuccessUrlMixin,
    generic.CreateView
    ):
    model = Printer
    form_class = PrinterCreateForm
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
