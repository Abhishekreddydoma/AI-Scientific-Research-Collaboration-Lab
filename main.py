"""FastAPI application entry point.

Initializes the application, configures middleware, registers routers,
and sets up exception handlers and database tables on startup.
"""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging, get_logger
from app.database.database import init_db

# ── Bootstrap logging before anything else ────────────────────────────────────
configure_logging()
logger = get_logger(__name__)

# ── Create FastAPI application ─────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI Scientific Research Collaboration Lab — "
        "a multi-agent platform for automated scientific research."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── CORS middleware ────────────────────────────────────────────────────────────
# In production, replace "*" with the actual frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request logging middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every incoming request and its response status + duration."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ── Exception handlers ─────────────────────────────────────────────────────────
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Convert domain exceptions to consistent JSON error responses.

    No Python stack traces are exposed to API consumers.
    """
    logger.warning("AppError: %s — %s", exc.error_code, exc.message)
    return JSONResponse(
        status_code=exc.http_status,
        content={"error": exc.error_code, "message": exc.message},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected exceptions.

    Logs the full traceback internally but returns a generic error to the client.
    """
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
    )


# ── Startup / shutdown events ──────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    """Initialize database tables on application startup."""
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    logger.info("Debug mode: %s", settings.debug)
    init_db()
    logger.info("Application startup complete.")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Log application shutdown."""
    logger.info("Application shutting down.")


from app.api.routes import agents, health, reports, research, results, stream, users  # noqa: E402

API_PREFIX = "/api"

app.include_router(health.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(research.router, prefix=API_PREFIX)
app.include_router(agents.router, prefix=API_PREFIX)
app.include_router(results.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(stream.router, prefix=API_PREFIX)

logger.info("All routers registered.")
