from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from confirmation_server.services import get_access_token, _token_cache
import time

@override_settings(
    AUTH0_DOMAIN="mock-tenant.auth0.com",
    AUTH0_CLIENT_ID="mock_client_id",
    AUTH0_CLIENT_SECRET="mock_client_secret",
    AUTH0_AUDIENCE="mock_audience"
)
class ConfirmationServerTokenTests(TestCase):
    def setUp(self):
        # Reset token cache before each test
        _token_cache["access_token"] = None
        _token_cache["expires_at"] = 0

    @patch('confirmation_server.services.requests.post')
    def test_token_caching_and_refresh(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "new_mock_token",
            "expires_in": 3600
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # 1. Fetch token first time (should hit network/mock_post)
        token1 = get_access_token()
        self.assertEqual(token1, "new_mock_token")
        self.assertEqual(mock_post.call_count, 1)

        # 2. Fetch token second time immediately (should return cached token, call count stays 1)
        token2 = get_access_token()
        self.assertEqual(token2, "new_mock_token")
        self.assertEqual(mock_post.call_count, 1)

        # 3. Simulate expired token cache
        _token_cache["expires_at"] = time.time() - 100 # expired
        mock_response.json.return_value = {
            "access_token": "refreshed_mock_token",
            "expires_in": 3600
        }

        # 4. Fetch token third time (should trigger refresh/mock_post)
        token3 = get_access_token()
        self.assertEqual(token3, "refreshed_mock_token")
        self.assertEqual(mock_post.call_count, 2)
