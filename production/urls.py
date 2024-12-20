from django.urls import path

from production.models import Material
from production.views import (
    index,

    WorkerDetailView,
    WorkerCreateView,
    WorkerDeleteView,
    WorkerPhoneView,
    WorkerListView,

    WorkplaceListView,
    WorkplaceCreateView,
    WorkplaceUpdateView,
    WorkplaceDetailView,

    MaterialListView,

    PrinterListView,
    PrinterCreateView,
    PrinterDetailView, PrinterDeleteView,
)

urlpatterns = [
    path("", index, name="index"),

    path(
        "workers/<int:pk>/",
        WorkerDetailView.as_view(),
        name="worker-detail",
    ),

    path(
        "workers/<int:pk>/phone/",
        WorkerPhoneView.as_view(),
        name="worker-phone",
    ),

    path("workers/create/",
         WorkerCreateView.as_view(),
         name="worker-create"
         ),

    path("workers/<int:pk>/delete/",
         WorkerDeleteView.as_view(),
         name="worker-delete"
         ),

    path(
        "workers/",
        WorkerListView.as_view(),
        name="worker-list",
    ),

    path(
        "workplaces/",
        WorkplaceListView.as_view(),
        name="workplace-list",
    ),

    path(
        "workplaces/create/",
        WorkplaceCreateView.as_view(),
        name="workplace-create"
    ),

    path(
        "workplaces/<int:pk>",
        WorkplaceDetailView.as_view(),
        name="workplace-detail",
    ),

    path(
        "workplaces/<int:pk>/update/",
        WorkplaceUpdateView.as_view(),
        name="workplace-update",
    ),

    path(
        "materials/",
        MaterialListView.as_view(),
        name="material-list",
    ),

    path(
        "printers/",
         PrinterListView.as_view(),
         name="printer-list",
    ),

    path(
        "printers/<int:pk>/",
        PrinterDetailView.as_view(),
        name="printer-detail",
    ),

    path(
        "printers/create/",
        PrinterCreateView.as_view(),
        name="printer-create",
    ),
    path(
        "printers/<int:pk>/delete/",
        PrinterDeleteView.as_view(),
        name="printer-delete",
    )
]

app_name = "production"