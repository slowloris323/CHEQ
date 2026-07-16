from django.test import TestCase
from airline_api.services import AirlineService

class AirlineServiceTests(TestCase):
    def test_get_dynamic_mock_flights(self):
        service = AirlineService()
        params = {
            "origin": "JFK",
            "destination": "LHR",
            "outbound_date": "2026-07-20"
        }
        res = service.get_flights(params)
        # Should generate between 2 and 4 flights
        self.assertTrue(2 <= len(res["best_flights"]) <= 4)
        # Verify the parameters match the query
        for flight in res["best_flights"]:
            self.assertEqual(flight["origin"], "JFK")
            self.assertEqual(flight["destination"], "LHR")
            self.assertEqual(flight["outbound_date"], "2026-07-20")
