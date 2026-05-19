import unittest
from datetime import date

from fastapi.testclient import TestClient

from app import database
from app.config import get_settings
from app.main import app
from app.models import ClickEvent
from app.worker import run_click_event_once


class AnalyticsFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = get_settings()
        self.api_key = self.settings.api_key_a or "testkey"
        self.client = TestClient(app)
        database.init_db()

    def test_replayed_job_does_not_double_count_and_only_stores_ip_hash(self):
        create_resp = self.client.post(
            "/links",
            json={"long_url": "https://example.com/analytics"},
            headers={"X-API-Key": self.api_key},
        )
        self.assertEqual(create_resp.status_code, 201)
        link_id = create_resp.json()["id"]
        event_id = f"evt-analytics-{link_id}"

        inserted_first = run_click_event_once(
            event_id=event_id,
            link_id=link_id,
            clicked_at="2026-05-01T00:00:00",
            user_agent="test-agent",
            referrer="https://ref.example",
            ip_hash="hashed-ip-value",
        )
        inserted_second = run_click_event_once(
            event_id=event_id,
            link_id=link_id,
            clicked_at="2026-05-01T00:00:00",
            user_agent="test-agent",
            referrer="https://ref.example",
            ip_hash="hashed-ip-value",
        )

        self.assertTrue(inserted_first)
        self.assertFalse(inserted_second)

        analytics_resp = self.client.get(
            f"/links/{link_id}/analytics",
            params={"from": date(2000, 1, 1).isoformat(), "to": date(2100, 1, 1).isoformat()},
            headers={"X-API-Key": self.api_key},
        )
        self.assertEqual(analytics_resp.status_code, 200)
        body = analytics_resp.json()
        self.assertEqual(body["link_id"], link_id)
        self.assertEqual(body["click_count"], 1)

        db = database._SessionLocal()
        try:
            event = db.query(ClickEvent).filter(ClickEvent.link_id == link_id).one()
            self.assertEqual(event.ip_hash, "hashed-ip-value")
            self.assertFalse(hasattr(event, "ip_address"))
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
