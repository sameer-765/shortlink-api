from fastapi.testclient import TestClient
import logging

from app.main import app, logger
from app.config import get_settings


def run_test():
    settings = get_settings()
    api_key = settings.api_key_a or "testkey"

    log_records = []

    class CaptureHandler(logging.Handler):
        def emit(self, record):
            log_records.append(self.format(record))

    handler = CaptureHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    client = TestClient(app)
    create_resp = client.post(
        "/links",
        json={"long_url": "https://example.com"},
        headers={"X-API-Key": api_key},
    )
    print("create_status", create_resp.status_code)
    print(create_resp.json())

    if create_resp.status_code != 201:
        raise SystemExit("create link request failed")

    link_id = create_resp.json()["id"]
    fetch_resp = client.get(f"/links/{link_id}", headers={"X-API-Key": api_key})
    print("get_status", fetch_resp.status_code)
    print(fetch_resp.json())

    print("LOGS")
    for message in log_records:
        print(message)


if __name__ == "__main__":
    run_test()
