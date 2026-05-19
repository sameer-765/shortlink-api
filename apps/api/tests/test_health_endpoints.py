import json
import unittest
from unittest.mock import patch

from app.main import health, live, ready


class HealthEndpointTest(unittest.TestCase):
    def test_live_endpoint_reports_process_liveness(self):
        response = live()

        self.assertEqual(response, {"ok": True})

    def test_health_alias_matches_live_contract(self):
        response = health()

        self.assertEqual(response, {"ok": True})

    def test_ready_returns_dependency_checks_when_database_is_available(self):
        with patch("app.main.readiness_check", return_value=(True, "connected")):
            response = ready()

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.body)
        self.assertTrue(body["ok"])
        self.assertEqual(body["checks"]["database"], "connected")
        self.assertIn("uptime_seconds", body["checks"])

    def test_ready_returns_503_with_dependency_reason_when_database_is_unavailable(self):
        with patch("app.main.readiness_check", return_value=(False, "circuit_open")):
            response = ready()

        self.assertEqual(response.status_code, 503)
        body = json.loads(response.body)
        self.assertFalse(body["ok"])
        self.assertEqual(body["checks"]["database"], "circuit_open")
        self.assertIn("uptime_seconds", body["checks"])


if __name__ == "__main__":
    unittest.main()
