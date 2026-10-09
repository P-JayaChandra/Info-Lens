"""
Configuration management for the InfoLens AI Engine.
Provides strongly-typed settings loaded from environment variables or .env files.
"""

from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderType(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    MOCK = "mock"


class EmbeddingProviderType(str, Enum):
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OPENAI = "openai"
    MOCK = "mock"


class VectorStoreType(str, Enum):
    IN_MEMORY_PERSISTENT = "in_memory_persistent"
    FAISS = "faiss"
    CHROMA = "chroma"


class AIEngineConfig(BaseSettings):
    """Global configuration settings for InfoLens AI Document Intelligence Engine."""

    # General / Runtime
    app_name: str = "InfoLens AI Engine"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # LLM Settings
    llm_provider: LLMProviderType = LLMProviderType.MOCK
    llm_model: str = "gpt-4o-mini"
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 2
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2048

    # Embedding Settings
    embedding_provider: EmbeddingProviderType = EmbeddingProviderType.SENTENCE_TRANSFORMERS
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_api_key: Optional[str] = None
    embedding_dimension: int = 384
    embedding_batch_size: int = 32

    # Chunking Settings
    chunk_size: int = 500  # approximate characters/words per chunk
    chunk_overlap: int = 100
    chunk_min_size: int = 40

    # Vector Store & Retrieval Settings
    vector_store_type: VectorStoreType = VectorStoreType.IN_MEMORY_PERSISTENT
    vector_store_dir: Path = Field(default=Path("./data/vector_store"))
    retrieval_top_k: int = 5
    retrieval_similarity_threshold: float = 0.15
    enable_bm25_reranking: bool = True

    # OCR Settings
    ocr_enabled: bool = False
    ocr_language: str = "eng"
    ocr_min_extracted_chars: int = 30  # threshold under which OCR will trigger if enabled
    tesseract_cmd: Optional[str] = None

    # Processing limits & bounds
    max_file_size_bytes: int = 50 * 1024 * 1024  # 50MB
    max_extracted_characters: int = 5_000_000
    max_context_budget_characters: int = 12_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="INFOLENS_AI_",
        case_sensitive=False,
        extra="ignore",
    )


# Singleton or factory for configuration
_global_config: Optional[AIEngineConfig] = None


def get_config() -> AIEngineConfig:
    """Retrieve or initialize the global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = AIEngineConfig()
        # Ensure vector store directory exists if local path
        if _global_config.vector_store_dir:
            _global_config.vector_store_dir.mkdir(parents=True, exist_ok=True)
    return _global_config


def set_config(config: AIEngineConfig) -> None:
    """Explicitly set the active configuration (useful for testing)."""
    global _global_config
    _global_config = config
