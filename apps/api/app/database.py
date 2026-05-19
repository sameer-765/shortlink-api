import pybreaker
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, TimeoutError as SQLAlchemyTimeoutError
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models import Base
from app.resilience import DependencyUnavailableError, db_circuit_breaker

_engine = None
_SessionLocal = None


def _ensure_db_circuit_closed() -> None:
    if db_circuit_breaker.current_state == "open":
        raise DependencyUnavailableError("database", "circuit_open")


def _connect_args(db_url: str, timeout_seconds: int) -> dict:
    if "sqlite" in db_url:
        return {"check_same_thread": False, "timeout": timeout_seconds}
    return {"connect_timeout": timeout_seconds}


def _normalize_database_unavailable_reason(exc: Exception) -> str:
    if isinstance(exc, pybreaker.CircuitBreakerError):
        return "circuit_open"
    return "connection_timeout_or_unavailable"


def init_db() -> None:
    global _engine, _SessionLocal
    if _engine is not None:
        return

    _ensure_db_circuit_closed()

    settings = get_settings()
    db_url = settings.database_url
    _engine = create_engine(
        db_url.replace("sqlite:///", "sqlite:///"),
        connect_args=_connect_args(db_url, settings.db_connect_timeout_seconds),
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout_seconds,
        pool_pre_ping=True,
    )
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    try:
        db_circuit_breaker.call(lambda: Base.metadata.create_all(bind=_engine))
        db_circuit_breaker.call(_ensure_schema_updates)
    except pybreaker.CircuitBreakerError as exc:
        raise DependencyUnavailableError("database", "circuit_open") from exc
    except (OperationalError, SQLAlchemyTimeoutError) as exc:
        raise DependencyUnavailableError("database", "connection_timeout_or_unavailable") from exc


def readiness_check() -> tuple[bool, str]:
    try:
        _ensure_db_circuit_closed()
        init_db()
        if _engine is None:
            raise DependencyUnavailableError("database", "engine_uninitialized")

        with _engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "connected"
    except DependencyUnavailableError as exc:
        return False, exc.reason
    except (OperationalError, SQLAlchemyTimeoutError) as exc:
        return False, "connection_timeout_or_unavailable"
    except pybreaker.CircuitBreakerError as exc:
        return False, _normalize_database_unavailable_reason(exc)


def _ensure_schema_updates() -> None:
    if _engine is None:
        return

    with _engine.begin() as connection:
        dialect = connection.dialect.name
        if dialect == "sqlite":
            link_columns = {
                row[1]
                for row in connection.execute(text("PRAGMA table_info(links)"))
            }
            if "title" not in link_columns:
                connection.execute(text("ALTER TABLE links ADD COLUMN title VARCHAR(255)"))
            if "search_text" not in link_columns:
                connection.execute(text("ALTER TABLE links ADD COLUMN search_text TEXT"))

            columns = {
                row[1]
                for row in connection.execute(text("PRAGMA table_info(click_events)"))
            }
            if "event_id" not in columns:
                connection.execute(text("ALTER TABLE click_events ADD COLUMN event_id VARCHAR(100)"))

        connection.execute(
            text(
                "UPDATE links "
                "SET search_text = trim("
                "coalesce(code, '') || ' ' || "
                "coalesce(title, '') || ' ' || "
                "coalesce(long_url, '') || ' ' || "
                "coalesce(tags, '')"
                ") "
                "WHERE search_text IS NULL OR trim(search_text) = ''"
            )
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_links_created_by_created_at "
                "ON links (created_by, created_at)"
            )
        )
        connection.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ix_click_events_event_id ON click_events (event_id)")
        )
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_click_events_link_id_clicked_at "
                "ON click_events (link_id, clicked_at)"
            )
        )


def get_db():
    try:
        _ensure_db_circuit_closed()
        init_db()
        db = _SessionLocal()
    except DependencyUnavailableError:
        raise
    except (OperationalError, SQLAlchemyTimeoutError) as exc:
        raise DependencyUnavailableError("database", "connection_timeout_or_unavailable") from exc

    try:
        yield db
    except (OperationalError, SQLAlchemyTimeoutError) as exc:
        try:
            db_circuit_breaker.call(lambda: (_ for _ in ()).throw(exc))
        except Exception:
            pass
        raise DependencyUnavailableError("database", "query_timeout_or_pool_saturation") from exc
    finally:
        db.close()
