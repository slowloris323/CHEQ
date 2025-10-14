from django.urls import path
from . import views

app_name = "resource_server"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("resource/<int:process_id>/", views.ResourceView.as_view(), name="resource"),
    path("result/<int:process_id>/", views.ResultView.as_view(), name="result"),
    path("execute_process/", views.ProcessExecution.as_view(), name="execute_process")
]