from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from production.forms import WorkerCreateForm
from production.models import Worker


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


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    template_name = "production/worker_form.html"
    form_class = WorkerCreateForm


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Worker
    template_name = "production/worker_confirm_delete.html"
    success_url = reverse_lazy("production:index")