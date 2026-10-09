import pytest
from app.core.constants import ErrorCode
from app.core.exceptions import (
    AlreadyExistsException,
    AppException,
    AuthenticationException,
    AuthorizationException,
    DocumentProcessingException,
    FileSizeExceededException,
    InvalidTokenException,
    LLMProviderException,
    NotFoundException,
    RateLimitExceededException,
    StorageException,
    TokenExpiredException,
    UnsupportedFileTypeException,
    ValidationException,
    VectorStoreException,
)


def test_base_app_exception():
    exc = AppException("Custom internal error", status_code=500)
    data = exc.to_dict()
    assert data["error"]["code"] == ErrorCode.INTERNAL_SERVER_ERROR.value
    assert data["error"]["message"] == "Custom internal error"


def test_not_found_exception():
    exc = NotFoundException("Document", identifier="doc_42")
    assert exc.status_code == 404
    assert exc.error_code == ErrorCode.NOT_FOUND
    assert "doc_42" in exc.message


def test_already_exists_exception():
    exc = AlreadyExistsException("User", "email", "alice@example.com")
    assert exc.status_code == 409
    assert exc.error_code == ErrorCode.ALREADY_EXISTS
    assert "alice@example.com" in exc.message


def test_validation_exception():
    exc = ValidationException("Field invalid", details={"field": "title"})
    assert exc.status_code == 422
    assert exc.error_code == ErrorCode.VALIDATION_ERROR
    assert exc.details["field"] == "title"


def test_auth_exceptions():
    auth_exc = AuthenticationException()
    assert auth_exc.status_code == 401
    assert auth_exc.error_code == ErrorCode.UNAUTHORIZED

    forbid_exc = AuthorizationException()
    assert forbid_exc.status_code == 403
    assert forbid_exc.error_code == ErrorCode.FORBIDDEN

    exp_exc = TokenExpiredException()
    assert exp_exc.status_code == 401
    assert exp_exc.error_code == ErrorCode.TOKEN_EXPIRED

    inv_exc = InvalidTokenException()
    assert inv_exc.status_code == 401
    assert inv_exc.error_code == ErrorCode.INVALID_TOKEN


def test_rate_limit_exception():
    exc = RateLimitExceededException(retry_after_seconds=30)
    assert exc.status_code == 429
    assert exc.error_code == ErrorCode.RATE_LIMIT_EXCEEDED
    assert exc.details["retry_after_seconds"] == 30


def test_document_exceptions():
    proc_exc = DocumentProcessingException("Failed to parse page 4", document_id="doc_1", stage="extraction")
    assert proc_exc.status_code == 422
    assert proc_exc.error_code == ErrorCode.DOCUMENT_PARSE_ERROR
    assert proc_exc.details["document_id"] == "doc_1"

    type_exc = UnsupportedFileTypeException("archive.zip", mime_type="application/zip")
    assert type_exc.status_code == 415
    assert type_exc.error_code == ErrorCode.UNSUPPORTED_MEDIA_TYPE

    size_exc = FileSizeExceededException(file_size_bytes=60000000, max_allowed_bytes=50000000)
    assert size_exc.status_code == 413
    assert size_exc.error_code == ErrorCode.DOCUMENT_TOO_LARGE


def test_infrastructure_exceptions():
    store_exc = StorageException("Failed to persist file")
    assert store_exc.status_code == 500
    assert store_exc.error_code == ErrorCode.STORAGE_ERROR

    vec_exc = VectorStoreException("Index rebuild timeout")
    assert vec_exc.status_code == 500
    assert vec_exc.error_code == ErrorCode.VECTOR_STORE_ERROR

    llm_exc = LLMProviderException("Quota exhausted", provider="openai")
    assert llm_exc.status_code == 502
    assert llm_exc.error_code == ErrorCode.LLM_PROVIDER_ERROR
    assert llm_exc.details["provider"] == "openai"
