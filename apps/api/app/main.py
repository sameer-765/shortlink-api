from time import perf_counter, time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from app.config import get_settings, validate_production_runtime_settings
from app.database import readiness_check
from app.logging_utils import get_logger
from app.resilience import DependencyUnavailableError
from app.routers import comments, invitations, links, redirect, teams


app = FastAPI()
logger = get_logger()
PROCESS_START_TIME = time()


HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "route", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "route", "status_code"],
)

URLS_TOTAL = Gauge(
    "urls_total",
    "Total number of shortened URLs",
)


def build_error_envelope(code: str, message: str, request_id: str) -> dict[str, dict[str, str]]:
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }


def build_error_response(status_code: int, code: str, message: str, request_id: str) -> JSONResponse:
    response = JSONResponse(
        status_code=status_code,
        content=build_error_envelope(code=code, message=message, request_id=request_id),
    )
    response.headers["X-Request-ID"] = request_id
    return response


def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def map_http_error_code(status_code: int) -> str:
    mapping = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        410: "gone",
        422: "validation_error",
        429: "rate_limited",
        500: "internal_error",
        503: "service_unavailable",
    }
    return mapping.get(status_code, "http_error")


@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id

    start = perf_counter()
    raw_route = request.url.path

    try:
        response = await call_next(request)

    except Exception as exc:
        latency_seconds = perf_counter() - start
        latency_ms = round(latency_seconds * 1000, 2)

        route_template = (
            request.scope.get("route").path
            if request.scope.get("route")
            else raw_route
        )

        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            route=route_template,
            status_code="500",
        ).inc()

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            route=route_template,
            status_code="500",
        ).observe(latency_seconds)

        logger.exception(
            "request failed",
            extra={
                "request_id": request_id,
                "route": route_template,
                "method": request.method,
                "status_code": 500,
                "latency_ms": latency_ms,
                "principal_id": getattr(request.state, "principal_id", "anonymous"),
            },
        )

        raise exc

    latency_seconds = perf_counter() - start
    latency_ms = round(latency_seconds * 1000, 2)

    route_template = (
        request.scope.get("route").path
        if request.scope.get("route")
        else raw_route
    )

    status_code = str(response.status_code)

    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        route=route_template,
        status_code=status_code,
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=request.method,
        route=route_template,
        status_code=status_code,
    ).observe(latency_seconds)

    response.headers["X-Request-ID"] = request_id

    logger.info(
        "request completed",
        extra={
            "request_id": request_id,
            "route": route_template,
            "method": request.method,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "principal_id": getattr(request.state, "principal_id", "anonymous"),
        },
    )

    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = get_request_id(request)
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed"

    return build_error_response(
        status_code=exc.status_code,
        code=map_http_error_code(exc.status_code),
        message=detail,
        request_id=request_id,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    request_id = get_request_id(request)
    first_error = exc.errors()[0] if exc.errors() else None
    message = first_error.get("msg", "Invalid request") if first_error else "Invalid request"

    return build_error_response(
        status_code=422,
        code="validation_error",
        message=message,
        request_id=request_id,
    )


@app.exception_handler(DependencyUnavailableError)
async def dependency_unavailable_handler(
    request: Request,
    exc: DependencyUnavailableError,
) -> JSONResponse:
    request_id = get_request_id(request)

    logger.error(
        "dependency_timeout",
        extra={
            "request_id": request_id,
            "route": request.scope.get("route").path if request.scope.get("route") else request.url.path,
            "method": request.method,
            "dependency": exc.dependency,
            "reason": exc.reason,
            "status_code": 503,
        },
    )

    return build_error_response(
        status_code=503,
        code="dependency_unavailable",
        message="A required dependency is temporarily unavailable",
        request_id=request_id,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = get_request_id(request)

    route_template = (
        request.scope.get("route").path
        if request.scope.get("route")
        else request.url.path
    )

    logger.error(
        "unhandled exception",
        extra={
            "request_id": request_id,
            "route": route_template,
            "method": request.method,
            "principal_id": getattr(request.state, "principal_id", "anonymous"),
        },
        exc_info=exc,
    )

    return build_error_response(
        status_code=500,
        code="internal_error",
        message="Something went wrong",
        request_id=request_id,
    )


# Include routers
app.include_router(links.router)
app.include_router(redirect.router)
app.include_router(teams.router)
app.include_router(invitations.router)
app.include_router(comments.router)


@app.on_event("startup")
def validate_settings() -> None:
    settings = get_settings()
    validate_production_runtime_settings(settings)

    logger.info(
        "service starting",
        extra={
            "environment": settings.app_env.value,
            "port": settings.port,
        },
    )


@app.get("/live")
def live() -> dict[str, bool]:
    return {"ok": True}


@app.get("/health")
def health() -> dict[str, bool]:
    return live()


@app.get("/ready")
def ready() -> JSONResponse:
    database_ok, database_status = readiness_check()
    checks = {
        "database": database_status,
        "uptime_seconds": int(time() - PROCESS_START_TIME),
    }
    ready_state = database_ok
    status_code = 200 if ready_state else 503

    return JSONResponse(
        status_code=status_code,
        content={"ok": ready_state, "checks": checks},
    )


@app.get("/metrics")
def metrics():
    URLS_TOTAL.set(0)

    return PlainTextResponse(
        generate_latest().decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST,
    )
