import pytest
from app.core.constants import (
    ChunkingStrategy,
    DifficultyLevel,
    DocumentFormat,
    DocumentStatus,
    EmbeddingProvider,
    Environment,
    ErrorCode,
    LLMProvider,
    QuestionType,
    StorageBackend,
    TaskPriority,
    UserRole,
    VectorStoreType,
)


def test_environment_enum_values():
    assert Environment.DEVELOPMENT == "development"
    assert Environment.PRODUCTION == "production"
    assert Environment.TESTING == "testing"
    assert Environment.STAGING == "staging"


def test_user_roles():
    expected_roles = {"superadmin", "admin", "manager", "member", "guest"}
    actual_roles = {role.value for role in UserRole}
    assert expected_roles == actual_roles


def test_document_statuses_lifecycle():
    assert DocumentStatus.PENDING == "pending"
    assert DocumentStatus.UPLOADING == "uploading"
    assert DocumentStatus.EXTRACTING == "extracting"
    assert DocumentStatus.READY == "ready"
    assert DocumentStatus.FAILED == "failed"


def test_document_formats():
    assert DocumentFormat.PDF == "pdf"
    assert DocumentFormat.DOCX == "docx"
    assert DocumentFormat.TXT == "txt"


def test_chunking_strategies():
    strategies = {s.value for s in ChunkingStrategy}
    assert "fixed_size" in strategies
    assert "sliding_window" in strategies
    assert "paragraph" in strategies
    assert "semantic" in strategies
    assert "recursive" in strategies


def test_ai_providers():
    assert LLMProvider.MOCK == "mock"
    assert LLMProvider.OPENAI == "openai"
    assert LLMProvider.ANTHROPIC == "anthropic"

    assert EmbeddingProvider.MOCK == "mock"
    assert EmbeddingProvider.OPENAI == "openai"


def test_vector_store_types():
    types = {v.value for v in VectorStoreType}
    assert "pgvector" in types
    assert "sqlite_vec" in types
    assert "in_memory" in types


def test_error_codes():
    assert ErrorCode.NOT_FOUND == "NOT_FOUND"
    assert ErrorCode.VALIDATION_ERROR == "VALIDATION_ERROR"
    assert ErrorCode.UNAUTHORIZED == "UNAUTHORIZED"
    assert ErrorCode.FORBIDDEN == "FORBIDDEN"
    assert ErrorCode.TOKEN_EXPIRED == "TOKEN_EXPIRED"
    assert ErrorCode.RATE_LIMIT_EXCEEDED == "RATE_LIMIT_EXCEEDED"
