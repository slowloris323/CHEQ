from django.urls import path

from . import views
from .views import TriggerView, PerformView

app_name = "confirmation_server"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("trigger_confirmation", TriggerView.as_view(), name='triggers'),
    path("perform_confirmation", PerformView.as_view(), name='perform')
]