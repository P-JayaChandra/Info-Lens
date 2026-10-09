import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import correlation_id_ctx, request_id_ctx


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that tracks request correlation across distributed microservices.
    Extracts or generates X-Correlation-ID and X-Request-ID and injects them
    into contextvars and outgoing response headers.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Extract incoming correlation ID or generate fresh UUID
        incoming_correlation_id = (
            request.headers.get("X-Correlation-ID")
            or request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )
        request_id = str(uuid.uuid4())

        # Set context variables for structured logging
        corr_token = correlation_id_ctx.set(incoming_correlation_id)
        req_token = request_id_ctx.set(request_id)

        # Store in request state for downstream handlers
        request.state.correlation_id = incoming_correlation_id
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = incoming_correlation_id
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            correlation_id_ctx.reset(corr_token)
            request_id_ctx.reset(req_token)
