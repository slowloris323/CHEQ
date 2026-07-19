import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Resource
from .views import IndexView
from django.urls import reverse


class ResourceModelTests(TestCase):
    def test_resource_stores_selected_flight(self):
        """
        A resource can store selected flight details in JSON format
        """
        flight_data = {
            "airline": "Air Canada",
            "flight_number": "AC3",
            "price": 1788.00
        }
        resource = Resource.objects.create(
            process_id=123,
            pub_date=timezone.now(),
            selected_flight=flight_data
        )
        saved_resource = Resource.objects.get(id=resource.id)
        self.assertEqual(saved_resource.selected_flight["airline"], "Air Canada")
        self.assertEqual(saved_resource.selected_flight["flight_number"], "AC3")
        self.assertEqual(float(saved_resource.selected_flight["price"]), 1788.00)

