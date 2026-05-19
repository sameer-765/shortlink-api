import unittest

from fastapi.testclient import TestClient

from app import database
from app.config import get_settings
from app.main import app
from app.models import ClickEvent, Link


class SearchFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = get_settings()
        self.api_key = self.settings.api_key_a or "testkey"
        self.client = TestClient(app)
        database.init_db()
        self._reset_tables()

    def _reset_tables(self) -> None:
        db = database._SessionLocal()
        try:
            db.query(ClickEvent).delete()
            db.query(Link).delete()
            db.commit()
        finally:
            db.close()

    def _create_link(
        self,
        *,
        title: str,
        long_url: str,
        tags: str | None = None,
    ) -> dict:
        response = self.client.post(
            "/links",
            json={
                "title": title,
                "long_url": long_url,
                "tags": tags,
            },
            headers={"X-API-Key": self.api_key},
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_created_link_is_immediately_searchable(self) -> None:
        created = self._create_link(
            title="unique-search-token-123",
            long_url="https://example.com/unique-search-token-123",
            tags="search,module-08",
        )

        response = self.client.get(
            "/links/search",
            params={"q": "unique-search-token-123", "page": 1, "page_size": 10},
            headers={"X-API-Key": self.api_key},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total"], 1)
        self.assertEqual(len(body["links"]), 1)
        self.assertEqual(body["links"][0]["id"], created["id"])
        self.assertEqual(body["links"][0]["title"], "unique-search-token-123")

    def test_search_pagination_returns_last_page_and_empty_out_of_range_page(self) -> None:
        for index in range(15):
            self._create_link(
                title=f"pagination-token-{index}",
                long_url=f"https://example.com/pagination/{index}",
                tags="pagination-shared-token",
            )

        last_page = self.client.get(
            "/links/search",
            params={"q": "pagination-shared-token", "page": 2, "page_size": 10},
            headers={"X-API-Key": self.api_key},
        )
        self.assertEqual(last_page.status_code, 200)
        last_page_body = last_page.json()
        self.assertEqual(last_page_body["total"], 15)
        self.assertEqual(last_page_body["page"], 2)
        self.assertEqual(len(last_page_body["links"]), 5)

        out_of_range_page = self.client.get(
            "/links/search",
            params={"q": "pagination-shared-token", "page": 3, "page_size": 10},
            headers={"X-API-Key": self.api_key},
        )
        self.assertEqual(out_of_range_page.status_code, 200)
        out_of_range_body = out_of_range_page.json()
        self.assertEqual(out_of_range_body["total"], 15)
        self.assertEqual(out_of_range_body["page"], 3)
        self.assertEqual(out_of_range_body["links"], [])

    def test_search_query_uses_safe_parameter_handling(self) -> None:
        self._create_link(
            title="safe-search-token",
            long_url="https://example.com/safe-search-token",
            tags="security",
        )

        response = self.client.get(
            "/links/search",
            params={"q": "' OR 1=1 --", "page": 1, "page_size": 10},
            headers={"X-API-Key": self.api_key},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total"], 0)
        self.assertEqual(body["links"], [])


if __name__ == "__main__":
    unittest.main()
