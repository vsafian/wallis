from copy import copy
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet, Q, Count
from django.db.models.functions import TruncDay
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views import generic
from django_filters.views import FilterView

from production.filters import OrderFilter, PrintQueueFilter
from production.forms import (
    WorkerCreateForm,
    WorkerPhoneNumberForm,
    WorkplaceForm,
    PrinterForm,
    MaterialForm,
    PrintQueueCreateForm,
    PrintQueueUpdateForm,
    NameFieldSearchForm,
    OrderSearchForm,
    WorkerSearchForm,
    IDSearchForm,
)

from production.mixins import (
    DeleteViewMixin,
    ViewSuccessUrlMixin,
    InstanceCacheMixin,
    PostApproveMixin,
    ListViewSearchMixin,
)

from production.models import Worker, Workplace, Material, Printer, PrintQueue, Order

from production.calculations import create_summary_context
from production.services import get_week_time_scheme


@login_required
def index(request):
    """View function for the home page of the site."""
    today = now().date()
    workplaces_leaderboard = (
        Workplace.objects.filter(
            print_queues__status=PrintQueue.DONE,
            print_queues__orders__performing_time__date=today,
        )
        .annotate(
            completed_orders_count=Count(
                "print_queues__orders",
                filter=Q(
                    print_queues__orders__status=PrintQueue.DONE,
                    print_queues__orders__performing_time__date=today,
                ),
                distinct=True,
            )
        )
        .distinct()
        .order_by("-completed_orders_count")
    )
    orders = Order.objects.all()
    seven_days_ago = now().date() - timedelta(days=6)
    weekly_orders_data = (
        orders.filter(status=Order.DONE, performing_time__date__gte=seven_days_ago)
        .annotate(day=TruncDay("performing_time"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    weekly_orders = [0] * 7
    day_to_index = {(seven_days_ago + timedelta(days=i)): i for i in range(7)}

    index_to_day = [(seven_days_ago + timedelta(days=i)).weekday() for i in range(7)]
    week_scheme = get_week_time_scheme(index_to_day)

    for entry in weekly_orders_data:
        day = entry["day"].date()
        if day in day_to_index:
            weekly_orders[day_to_index[day]] = entry["count"]

    num_daily_done_orders = orders.filter(
        status=Order.DONE, performing_time__date=today
    ).count()

    num_problem_orders = orders.filter(
        status=Order.PROBLEM,
    ).count()

    num_orders_to_close = orders.filter(status=Order.READY_TO_PRINT).count()

    context = {
        "workplaces": workplaces_leaderboard,
        "week_scheme": week_scheme,
        "weekly_orders": [weekly_orders],
        "problem_orders": num_problem_orders,
        "num_orders_to_close": num_orders_to_close,
        "num_daily_done_orders": num_daily_done_orders,
    }

    return render(request, "production/index.html", context)


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker


class WorkerCreateView(
    LoginRequiredMixin,
    generic.CreateView,
    ViewSuccessUrlMixin,
):
    model = Worker
    template_name = "production/worker_form.html"
    form_class = WorkerCreateForm


class WorkerDeleteView(LoginRequiredMixin, DeleteViewMixin):
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
    ListViewSearchMixin,
):
    model = Worker
    paginate_by = 14
    search_form = WorkerSearchForm
    search_field = "username"
    queryset = Worker.objects.select_related("workplace").all()


class WorkplaceListView(LoginRequiredMixin, ListViewSearchMixin):
    model = Workplace
    paginate_by = 12
    search_form = NameFieldSearchForm
    search_field = "name"
    queryset = Workplace.objects.prefetch_related(
        "workers", "printers", "print_queues"
    ).all()


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
    queryset = Workplace.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workplace = self.get_object()

        print_queues = PrintQueue.objects.prefetch_related("material").filter(
            status__in=[
                PrintQueue.READY_TO_PRINT,
                PrintQueue.PROBLEM,
                PrintQueue.IN_PROGRESS,
            ],
            workplace=workplace,
        )

        printers = Printer.objects.prefetch_related("materials").filter(
            workplace=workplace,
        )

        workers = Worker.objects.filter(
            workplace=workplace,
        )
        context["print_queues"] = print_queues
        context["printers"] = printers
        context["workers"] = workers
        return context


class WorkplaceDeleteView(LoginRequiredMixin, DeleteViewMixin):
    model = Workplace
    success_url = reverse_lazy("production:workplace-list")
    template_name = "production/workplace_confirm_delete.html"


class MaterialListView(LoginRequiredMixin, ListViewSearchMixin):
    model = Material
    paginate_by = 14
    search_form = NameFieldSearchForm
    search_field = "name"
    queryset = Material.objects.all()


class MaterialDetailView(
    LoginRequiredMixin,
    generic.DetailView,
):
    model = Material
    queryset = Material.objects.prefetch_related(
        "printers", "printers__workplace"
    ).all()


class MaterialCreateView(LoginRequiredMixin, generic.CreateView, ViewSuccessUrlMixin):
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


class MaterialDeleteView(LoginRequiredMixin, DeleteViewMixin):
    model = Material
    success_url = reverse_lazy("production:material-list")
    template_name = "production/material_confirm_delete.html"


class PrinterListView(LoginRequiredMixin, ListViewSearchMixin):
    model = Printer
    paginate_by = 14
    search_form = NameFieldSearchForm
    search_field = "name"
    queryset = Printer.objects.prefetch_related("materials", "workplace").all()

    def get_queryset(self) -> QuerySet:
        form = self.search_form(self.request.GET)
        if form.is_valid():
            return self.queryset.filter(
                Q(name__icontains=form.cleaned_data["name"])
                | Q(model__icontains=form.cleaned_data["name"])
            )
        return self.queryset


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


class PrinterDetailView(LoginRequiredMixin, generic.DetailView):
    model = Printer


class PrinterDeleteView(LoginRequiredMixin, DeleteViewMixin):
    model = Printer
    success_url = reverse_lazy("production:printer-list")
    template_name = "production/printer_confirm_delete.html"


class OrderDetailView(LoginRequiredMixin, generic.DetailView):
    model = Order


class OrderListView(
    LoginRequiredMixin,
    FilterView,
    ListViewSearchMixin,
):
    model = Order
    paginate_by = 10
    search_form = OrderSearchForm
    search_field = "code"
    queryset = Order.objects.prefetch_related("material").all()
    template_name = "production/order_list.html"
    context_object_name = "order_list"
    filterset_class = OrderFilter


class OrderDeleteView(LoginRequiredMixin, DeleteViewMixin):
    model = Order
    success_url = reverse_lazy("production:order-list")
    template_name = "production/order_confirm_delete.html"


class PrintQueueListView(
    LoginRequiredMixin,
    FilterView,
    ListViewSearchMixin,
):
    model = PrintQueue
    paginate_by = 10
    search_form = IDSearchForm
    search_field = "id"
    template_name = "production/print_queue_list.html"
    queryset = PrintQueue.objects.prefetch_related(
        "workplace", "material", "orders"
    ).all()
    context_object_name = "printqueue_list"
    filterset_class = PrintQueueFilter


class PrintQueueDeleteView(LoginRequiredMixin, DeleteViewMixin):
    model = PrintQueue
    success_url = reverse_lazy("production:print-queue-list")
    template_name = "production/print_queue_confirm_delete.html"


class PrintQueueDetailView(LoginRequiredMixin, generic.DetailView):
    model = PrintQueue
    template_name = "production/print_queue_detail.html"
    queryset = PrintQueue.objects.prefetch_related(
        "orders__material"
    ).all()


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

        context.update(create_summary_context(context.get("form")))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["cached_workplace"] = self.workplace
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

        context.update(create_summary_context(context.get("form")))
        context.update({"object": self.print_queue})
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["cached_instance"] = self.print_queue
        return kwargs


@login_required
def change_order_status(request: HttpRequest, pk: int) -> HttpResponse:
    order = get_object_or_404(Order.objects.prefetch_related("print_queue"), pk=pk)
    print_queue = order.print_queue
    order_change_to = {
        order.READY_TO_PRINT: order.PROBLEM,
        order.PROBLEM: order.READY_TO_PRINT,
    }
    if order.is_editable:
        new_status = order_change_to[order.status]
        if print_queue and print_queue.is_editable:
            problem_orders = print_queue.orders.filter(status=order.PROBLEM)
            if new_status == order.READY_TO_PRINT:
                if order in problem_orders and problem_orders.count() == 1:
                    print_queue.status = print_queue.READY_TO_PRINT
                    print_queue.save()
            if new_status == order.PROBLEM:
                if print_queue.status != order.PROBLEM:
                    print_queue.status = print_queue.PROBLEM
                    print_queue.save()
        order.status = new_status
        order.save()

    return HttpResponseRedirect(order.get_absolute_url())
