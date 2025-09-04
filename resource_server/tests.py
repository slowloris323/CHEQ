import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Resource
from .views import IndexView
from django.urls import reverse


class ResourceModelTests(TestCase):
    def test_process_1_has_5_items(self):
        """
        process 1 has 5 steps in it
        """
        resource = Resource()
        process_1 = resource.get_all_steps_in_process(process_id=1)
        self.assertIs(len(process_1), 5)

    def test_process_1_has_5_items_from_view(self):
        """
        process 1 has 5 steps in it
        """
        index_view = IndexView()
        process_1 = index_view.get_queryset()
        self.assertIs(len(process_1), 5)