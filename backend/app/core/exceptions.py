from typing import Any, Dict, Optional
from app.core.constants import ErrorCode


class AppException(Exception):
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "error": {
                "code": self.error_code.value,
                "message": self.message,
            }
        }
        if self.details:
            payload["error"]["details"] = self.details
        return payload


class NotFoundException(AppException):
    def __init__(
        self,
        resource: str,
        identifier: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        msg = f"{resource} not found"
        if identifier is not None:
            msg = f"{resource} with id '{identifier}' not found"
        super().__init__(
            message=msg,
            error_code=ErrorCode.NOT_FOUND,
            status_code=404,
            details=details,
        )


class AlreadyExistsException(AppException):
    def __init__(
        self,
        resource: str,
        field: str,
        value: Any,
        details: Optional[Dict[str, Any]] = None,
    ):
        msg = f"{resource} with {field} '{value}' already exists"
        super().__init__(
            message=msg,
            error_code=ErrorCode.ALREADY_EXISTS,
            status_code=409,
            details=details,
        )


class ValidationException(AppException):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=422,
            details=details,
        )


class AuthenticationException(AppException):
    def __init__(
        self,
        message: str = "Authentication required or invalid credentials",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.UNAUTHORIZED,
            status_code=401,
            details=details,
        )


class AuthorizationException(AppException):
    def __init__(
        self,
        message: str = "Insufficient permissions to perform this action",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.FORBIDDEN,
            status_code=403,
            details=details,
        )


class TokenExpiredException(AuthenticationException):
    def __init__(
        self,
        message: str = "Security token has expired",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, details=details)
        self.error_code = ErrorCode.TOKEN_EXPIRED


class InvalidTokenException(AuthenticationException):
    def __init__(
        self,
        message: str = "Invalid or corrupted security token",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, details=details)
        self.error_code = ErrorCode.INVALID_TOKEN


class RateLimitExceededException(AppException):
    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        retry_after_seconds: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        info = details or {}
        if retry_after_seconds is not None:
            info["retry_after_seconds"] = retry_after_seconds
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429,
            details=info,
        )


class DocumentProcessingException(AppException):
    def __init__(
        self,
        message: str,
        document_id: Optional[str] = None,
        stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        info = details or {}
        if document_id:
            info["document_id"] = document_id
        if stage:
            info["stage"] = stage
        super().__init__(
            message=message,
            error_code=ErrorCode.DOCUMENT_PARSE_ERROR,
            status_code=422,
            details=info,
        )


class UnsupportedFileTypeException(AppException):
    def __init__(
        self,
        filename: str,
        mime_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        info = details or {}
        info["filename"] = filename
        if mime_type:
            info["mime_type"] = mime_type
        super().__init__(
            message=f"File '{filename}' format is not supported",
            error_code=ErrorCode.UNSUPPORTED_MEDIA_TYPE,
            status_code=415,
            details=info,
        )


class FileSizeExceededException(AppException):
    def __init__(
        self,
        file_size_bytes: int,
        max_allowed_bytes: int,
        details: Optional[Dict[str, Any]] = None,
    ):
        info = details or {}
        info["file_size_bytes"] = file_size_bytes
        info["max_allowed_bytes"] = max_allowed_bytes
        super().__init__(
            message=f"File size ({file_size_bytes} bytes) exceeds limit ({max_allowed_bytes} bytes)",
            error_code=ErrorCode.DOCUMENT_TOO_LARGE,
            status_code=413,
            details=info,
        )


class StorageException(AppException):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.STORAGE_ERROR,
            status_code=500,
            details=details,
        )


class VectorStoreException(AppException):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.VECTOR_STORE_ERROR,
            status_code=500,
            details=details,
        )


class LLMProviderException(AppException):
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        info = details or {}
        if provider:
            info["provider"] = provider
        super().__init__(
            message=message,
            error_code=ErrorCode.LLM_PROVIDER_ERROR,
            status_code=502,
            details=info,
        )
