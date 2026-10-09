from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.database.session import check_db_health, close_database_connections
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.error_handler import register_exception_handlers
from app.middleware.timing import RequestTimingMiddleware

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle management for startup and graceful shutdown."""
    # Startup initialization
    setup_logging(log_level=settings.LOG_LEVEL, log_format=settings.LOG_FORMAT)
    logger.info("Initializing %s (v%s) in %s mode...", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT.value)

    # Ensure storage paths exist
    storage_dir = settings.resolved_storage_path
    logger.info("Local storage configured at: %s", storage_dir)

    # Verify initial database availability
    db_ok = await check_db_health()
    if db_ok:
        logger.info("Database connection verified successfully.")
    else:
        logger.warning("Database connection could not be established at startup. Background retry active.")

    yield

    # Shutdown teardown
    logger.info("Initiating application shutdown...")
    await close_database_connections()
    logger.info("Application shutdown complete.")


def create_application() -> FastAPI:
    """FastAPI application factory configuring middleware, exception handlers, and routing."""
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url="/openapi.json" if settings.DEBUG or not settings.is_production else None,
        docs_url="/docs" if settings.DEBUG or not settings.is_production else None,
        redoc_url="/redoc" if settings.DEBUG or not settings.is_production else None,
        lifespan=lifespan,
    )

    # Add Middleware Stack
    application.add_middleware(RequestTimingMiddleware)
    application.add_middleware(CorrelationIdMiddleware)

    if settings.CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=settings.CORS_CREDENTIALS,
            allow_methods=settings.CORS_METHODS,
            allow_headers=settings.CORS_HEADERS,
        )

    # Register Exception Handlers
    register_exception_handlers(application)

    # Register API Routers
    application.include_router(api_v1_router, prefix=settings.API_V1_STR)

    # Also mount health router directly at root for standard container orchestrators
    from app.api.v1.health import router as health_root_router
    application.include_router(health_root_router)

    return application


app = create_application()
