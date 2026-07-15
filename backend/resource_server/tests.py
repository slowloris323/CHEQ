import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Resource
from .views import IndexView
from django.urls import reverse


class ResourceModelTests(TestCase):
    fixtures = ['initial_resources.json']

    def test_process_1_has_3_items(self):
        """
        process 1 has 3 steps in it
        """
        process_1 = Resource.get_all_steps_in_process(process_id=1)
        self.assertEqual(len(process_1), 3)


from unittest.mock import patch
from rest_framework.test import APITestCase

class ResourceServerAuthTests(APITestCase):
    fixtures = ['initial_resources.json']

    def test_get_cheq_without_auth_header_fails(self):
        url = reverse('resource_server:resource_cheq', kwargs={"process_id": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Authorization header is missing", response.data["detail"])

    def test_get_cheq_with_invalid_auth_header_fails(self):
        url = reverse('resource_server:resource_cheq', kwargs={"process_id": 1})
        response = self.client.get(url, HTTP_AUTHORIZATION="invalid_format")
        self.assertEqual(response.status_code, 401)
        self.assertIn("must start with Bearer", response.data["detail"])

    @patch('resource_server.views.SignatureService.verify_auth0_token')
    def test_get_cheq_with_valid_token_succeeds(self, mock_verify):
        mock_verify.return_value = {"sub": "mock-m2m-client"}
        url = reverse('resource_server:resource_cheq', kwargs={"process_id": 1})
        response = self.client.get(url, HTTP_AUTHORIZATION="Bearer valid_token")
        self.assertEqual(response.status_code, 200)

    def test_post_decision_without_auth_header_fails(self):
        url = reverse('resource_server:resource', kwargs={"process_id": 1})
        response = self.client.post(url, data={"signed_CHEQ": "token"}, QUERY_STRING="decision=ACCEPT")
        self.assertEqual(response.status_code, 401)

