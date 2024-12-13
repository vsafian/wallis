from django.urls import path

from production.views import (
    index,
    WorkerDetailView,
    WorkerCreateView,
    WorkerDeleteView,
    WorkerPhoneView,
    WorkerListView,
    WorkplaceListView,
    WorkplaceCreateView,
    WorkplaceDetailView
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



]

app_name = "production"