from django.urls import path

from . import views

app_name = "resource_server"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
]