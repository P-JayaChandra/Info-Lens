import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that records endpoint execution latency.
    Injects X-Process-Time response header and warns on slow requests.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_seconds = time.perf_counter() - start_time

        duration_ms = duration_seconds * 1000.0
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

        if duration_seconds > settings.SLOW_REQUEST_THRESHOLD_SECONDS:
            logger.warning(
                "Slow request detected: %s %s took %.3fs (threshold: %.3fs)",
                request.method,
                request.url.path,
                duration_seconds,
                settings.SLOW_REQUEST_THRESHOLD_SECONDS,
            )

        return response
