import logging
import unittest

from fastapi.testclient import TestClient

from app.main import app, logger
from app.config import get_settings


class LinkFlowLoggingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = get_settings()
        self.api_key = self.settings.api_key_a or "testkey"
        self.log_records = []

        class CaptureHandler(logging.Handler):
            def __init__(self, records):
                super().__init__()
                self.records = records

            def emit(self, record):
                self.records.append(self.format(record))

        self.handler = CaptureHandler(self.log_records)
        self.handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(self.handler)
        logger.setLevel(logging.INFO)
        self.client = TestClient(app)

    def tearDown(self) -> None:
        logger.removeHandler(self.handler)

    def assert_logging_contains(self, substring: str) -> None:
        self.assertTrue(any(substring in message for message in self.log_records), f"Expected log to contain '{substring}'")

    def assert_logging_not_contains(self, substring: str) -> None:
        self.assertFalse(any(substring in message for message in self.log_records), f"Expected log not to contain '{substring}'")

    def test_invalid_request_returns_422_and_logs_request_id(self):
        resp = self.client.post(
            "/links",
            json={"long_url": "ftp://malicious"},
            headers={"X-API-Key": self.api_key},
        )

        self.assertEqual(resp.status_code, 422)
        body = resp.json()
        self.assertEqual(body["error"]["code"], "validation_error")
        self.assertIn("request_id", body["error"])

        self.assert_logging_contains("status_code=422")
        self.assert_logging_contains("principal_id=principal_a")
        self.assert_logging_not_contains("X-API-Key")

    def test_unauthorized_request_returns_401_and_logs_request_id(self):
        resp = self.client.post(
            "/links",
            json={"long_url": "https://example.com"},
            headers={"X-API-Key": "bad-key"},
        )

        self.assertEqual(resp.status_code, 401)
        body = resp.json()
        self.assertEqual(body["error"]["code"], "unauthorized")
        self.assertIn("request_id", body["error"])

        self.assert_logging_contains("status_code=401")
        self.assert_logging_not_contains("X-API-Key")

    def test_valid_request_returns_201_and_logs_request_id(self):
        create_resp = self.client.post(
            "/links",
            json={"long_url": "https://example.com"},
            headers={"X-API-Key": self.api_key},
        )

        self.assertEqual(create_resp.status_code, 201)
        create_json = create_resp.json()
        self.assertIn("id", create_json)
        self.assertEqual(create_json["created_by"], "principal_a")

        self.assert_logging_contains("status_code=201")
        self.assert_logging_contains("principal_id=principal_a")
        self.assert_logging_not_contains("X-API-Key")


if __name__ == "__main__":
    unittest.main()
