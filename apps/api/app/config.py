from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: AppEnv
    port: int
    database_url: str
    jwt_secret: str
    service_name: str

    mongodb_uri: Optional[str] = None
    redis_url: Optional[str] = None
    api_key_a: Optional[str] = None
    api_key_b: Optional[str] = None
    db_connect_timeout_seconds: int = 3
    db_pool_timeout_seconds: int = 3
    db_pool_size: int = 5
    db_max_overflow: int = 5
    db_circuit_fail_max: int = 3
    db_circuit_reset_timeout_seconds: int = 30
    redis_socket_timeout_seconds: int = 3
    create_link_per_min: int = 30
    links_read_per_min: int = 60
    redirect_per_min: int = 120
    analytics_retention_days: int = 30


_PRODUCTION_PLACEHOLDER_SECRETS = {
    "dev-secret",
    "testkey-a",
    "testkey-b",
    "ci-secret",
    "local-key-a",
    "local-key-b",
}


def validate_production_runtime_settings(settings: Settings) -> None:
    if settings.app_env != AppEnv.production:
        return

    missing = []
    insecure = []

    if not settings.jwt_secret:
        missing.append("JWT_SECRET")
    elif settings.jwt_secret in _PRODUCTION_PLACEHOLDER_SECRETS:
        insecure.append("JWT_SECRET")

    if not settings.api_key_a:
        missing.append("API_KEY_A")
    elif settings.api_key_a in _PRODUCTION_PLACEHOLDER_SECRETS:
        insecure.append("API_KEY_A")

    if not settings.api_key_b:
        missing.append("API_KEY_B")
    elif settings.api_key_b in _PRODUCTION_PLACEHOLDER_SECRETS:
        insecure.append("API_KEY_B")

    problems = []
    if missing:
        problems.append(f"missing required production secrets: {', '.join(missing)}")
    if insecure:
        problems.append(f"insecure placeholder production secrets: {', '.join(insecure)}")

    if problems:
        raise ValueError("; ".join(problems))


@lru_cache
def get_settings() -> Settings:
    return Settings()
