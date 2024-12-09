from django.urls import path

from production.views import index

urlpatterns = [
    path("", index, name="index"),
]

app_name = "production"