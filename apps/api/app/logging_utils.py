import json
import logging
from datetime import datetime, timezone

from app.config import AppEnv, get_settings


LOGGER_NAME = "app"


class HybridFormatter(logging.Formatter):
    def __init__(self, app_env: AppEnv, service_name: str) -> None:
        super().__init__()
        self.app_env = app_env
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        message = record.getMessage()

        payload = {
            "timestamp": timestamp,
            "level": record.levelname,
            "message": message,
            "service_name": self.service_name,
        }

        for key in ("request_id", "route", "method", "status_code", "latency_ms", "principal_id"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        if self.app_env == AppEnv.development:
            extras = " ".join(
                f"{key}={value}"
                for key, value in payload.items()
                if key not in {"timestamp", "level", "message", "service_name"}
            )
            base = f"{payload['timestamp']} {payload['level']} {payload['service_name']} {payload['message']}"
            return f"{base} {extras}".strip()

        return json.dumps(payload)


def get_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    settings = get_settings()

    handler = logging.StreamHandler()
    handler.setFormatter(HybridFormatter(settings.app_env, settings.service_name))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger