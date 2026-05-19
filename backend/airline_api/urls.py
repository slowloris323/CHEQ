from django.urls import path
from . import views

app_name = 'airline_api'
urlpatterns = [
    path('search_flights/', views.SearchFights.as_view(), name='search_flights'),
]