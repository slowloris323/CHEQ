from django.urls import path

from . import views

app_name = "confirmation_server"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
]