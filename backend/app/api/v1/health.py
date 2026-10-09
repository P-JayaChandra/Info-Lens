import os
import shutil
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.database.session import check_db_health

router = APIRouter(prefix="/health", tags=["Health & Observability"])
settings = get_settings()


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str
    timestamp: datetime
    components: Dict[str, Any]


class ProbeResponse(BaseModel):
    status: str
    timestamp: datetime


@router.get("", response_model=HealthResponse)
async def get_system_health(response: Response) -> HealthResponse:
    """Comprehensive health check verifying all primary dependencies."""
    db_healthy = await check_db_health()

    # Check local storage writeability
    storage_healthy = False
    storage_info: Dict[str, Any] = {}
    try:
        storage_path = settings.resolved_storage_path
        test_probe = storage_path / ".health_probe"
        test_probe.write_text("ok")
        if test_probe.exists():
            test_probe.unlink()
            storage_healthy = True

        total, used, free = shutil.disk_usage(storage_path)
        storage_info = {
            "writeable": storage_healthy,
            "total_gb": round(total / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
        }
    except Exception as exc:
        storage_info = {"writeable": False, "error": str(exc)}

    all_healthy = db_healthy and storage_healthy
    overall_status = "healthy" if all_healthy else "degraded"

    if not all_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        status=overall_status,
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT.value,
        timestamp=datetime.now(timezone.utc),
        components={
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "engine": settings.DATABASE_URL.split("://")[0],
            },
            "storage": {
                "status": "healthy" if storage_healthy else "unhealthy",
                "backend": settings.STORAGE_BACKEND.value,
                "details": storage_info,
            },
        },
    )


@router.get("/liveness", response_model=ProbeResponse)
async def get_liveness_probe() -> ProbeResponse:
    """Lightweight Kubernetes/container liveness probe."""
    return ProbeResponse(
        status="alive",
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/readiness", response_model=ProbeResponse)
async def get_readiness_probe(response: Response) -> ProbeResponse:
    """Kubernetes/container readiness probe checking core dependency availability."""
    db_ready = await check_db_health()

    if not db_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ProbeResponse(
            status="unready",
            timestamp=datetime.now(timezone.utc),
        )

    return ProbeResponse(
        status="ready",
        timestamp=datetime.now(timezone.utc),
    )
