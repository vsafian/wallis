from django.urls import path

from production.views import index, WorkerDetailView, WorkerCreateView, WorkerDeleteView

urlpatterns = [
    path("", index, name="index"),

    path(
        "workers/<int:pk>/",
        WorkerDetailView.as_view(),
        name="worker-detail",
    ),

    path("workers/create/",
         WorkerCreateView.as_view(),
         name="worker-create"
         ),

    path("workers/<int:pk>/delete/",
         WorkerDeleteView.as_view(),
         name="worker-delete"
         ),


]

app_name = "production"