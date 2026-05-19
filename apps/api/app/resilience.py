import pybreaker

from app.config import get_settings


settings = get_settings()

db_circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=settings.db_circuit_fail_max,
    reset_timeout=settings.db_circuit_reset_timeout_seconds,
    name="database",
)


class DependencyUnavailableError(Exception):
    def __init__(self, dependency: str, reason: str) -> None:
        self.dependency = dependency
        self.reason = reason
        super().__init__(f"{dependency} unavailable: {reason}")
