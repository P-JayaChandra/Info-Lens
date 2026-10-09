from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.core.logging import correlation_id_ctx, get_logger

logger = get_logger(__name__)
settings = get_settings()


def _build_error_response(
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
) -> JSONResponse:
    cid = correlation_id_ctx.get()
    content: Dict[str, Any] = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
    if cid:
        content["error"]["correlation_id"] = cid
    if details:
        content["error"]["details"] = details

    return JSONResponse(status_code=status_code, content=content)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning(
        "Application exception [%s] on %s %s: %s",
        exc.error_code.value,
        request.method,
        request.url.path,
        exc.message,
    )
    return _build_error_response(
        status_code=exc.status_code,
        code=exc.error_code.value,
        message=exc.message,
        details=exc.details,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        exc.errors(),
    )
    formatted_errors = []
    for err in exc.errors():
        loc = " -> ".join(str(item) for item in err.get("loc", []))
        formatted_errors.append({
            "field": loc,
            "message": err.get("msg", ""),
            "type": err.get("type", ""),
        })

    return _build_error_response(
        status_code=422,
        code=ErrorCode.VALIDATION_ERROR.value,
        message="Request validation failed",
        details=formatted_errors,
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    logger.info(
        "HTTP exception (%d) on %s %s: %s",
        exc.status_code,
        request.method,
        request.url.path,
        exc.detail,
    )
    code = ErrorCode.INTERNAL_SERVER_ERROR.value
    if exc.status_code == 404:
        code = ErrorCode.NOT_FOUND.value
    elif exc.status_code == 401:
        code = ErrorCode.UNAUTHORIZED.value
    elif exc.status_code == 403:
        code = ErrorCode.FORBIDDEN.value

    return _build_error_response(
        status_code=exc.status_code,
        code=code,
        message=str(exc.detail),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled server error on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
        exc_info=True,
    )
    message = "An unexpected internal server error occurred"
    details = None
    if settings.DEBUG:
        details = {"exception": str(exc), "type": exc.__class__.__name__}

    return _build_error_response(
        status_code=500,
        code=ErrorCode.INTERNAL_SERVER_ERROR.value,
        message=message,
        details=details,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
