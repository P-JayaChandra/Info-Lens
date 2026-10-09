from functools import lru_cache
from pathlib import Path
from typing import Any, List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import (
    EmbeddingProvider,
    Environment,
    LLMProvider,
    StorageBackend,
    VectorStoreType,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General App Config
    APP_NAME: str = "AI Document Intelligence Platform"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # Security & Tokens
    SECRET_KEY: str = Field(
        default="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
        description="Cryptographic secret key for signing JWTs and session tokens",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_HASH_ROUNDS: int = 12

    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./doc_intelligence.db",
        description="Async database connection string",
    )
    DATABASE_SYNC_URL: str = Field(
        default="sqlite:///./doc_intelligence.db",
        description="Sync database connection string for migrations and synchronous tools",
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800
    DATABASE_ECHO: bool = False

    # Redis & Caching
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    CACHE_DEFAULT_TTL_SECONDS: int = 300
    RATE_LIMIT_PER_MINUTE: int = 120

    # Storage Settings
    STORAGE_BACKEND: StorageBackend = StorageBackend.LOCAL
    LOCAL_STORAGE_PATH: str = "./data/storage"
    MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".md", ".html"]
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
        "text/html",
    ]

    # AI & LLM Settings
    DEFAULT_LLM_PROVIDER: LLMProvider = LLMProvider.MOCK
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 2048
    LLM_TIMEOUT_SECONDS: int = 60

    # Embeddings Settings
    DEFAULT_EMBEDDING_PROVIDER: EmbeddingProvider = EmbeddingProvider.MOCK
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536
    EMBEDDING_BATCH_SIZE: int = 64

    # Vector Store Settings
    VECTOR_STORE_BACKEND: VectorStoreType = VectorStoreType.IN_MEMORY
    VECTOR_TABLE_NAME: str = "document_embeddings"
    VECTOR_SIMILARITY_METRIC: str = "cosine"
    VECTOR_TOP_K: int = 5

    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    # Logging & Observability
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_SQL_QUERIES: bool = False
    SLOW_REQUEST_THRESHOLD_SECONDS: float = 1.0

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(f"Invalid CORS_ORIGINS format: {v}")

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == Environment.TESTING

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def resolved_storage_path(self) -> Path:
        path = Path(self.LOCAL_STORAGE_PATH)
        path.mkdir(parents=True, exist_ok=True)
        return path.resolve()


@lru_cache()
def get_settings() -> Settings:
    return Settings()
