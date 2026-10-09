"""
Custom exceptions hierarchy for the InfoLens AI Engine.
"""

class AIEngineError(Exception):
    """Base exception for all AI Engine errors."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


# --- Document Processing Exceptions ---
class DocumentProcessingError(AIEngineError):
    """Base error for document extraction, cleaning, and metadata parsing."""
    pass

class FileNotFoundOrInaccessibleError(DocumentProcessingError):
    """Raised when the specified document file does not exist or cannot be read."""
    pass

class UnsupportedFormatError(DocumentProcessingError):
    """Raised when an unsupported file type or extension is provided."""
    pass

class EmptyDocumentError(DocumentProcessingError):
    """Raised when a document contains no extractable text or content."""
    pass

class CorruptedDocumentError(DocumentProcessingError):
    """Raised when a document file is corrupted or cannot be parsed."""
    pass

class OCRError(DocumentProcessingError):
    """Raised when OCR processing fails or OCR engine/languages are unavailable."""
    pass


# --- Chunking Exceptions ---
class ChunkingError(AIEngineError):
    """Raised when text chunking fails or receives invalid parameters."""
    pass


# --- Embedding Exceptions ---
class EmbeddingError(AIEngineError):
    """Raised when vector embedding generation fails or encounters provider errors."""
    pass

class EmbeddingDimensionMismatchError(EmbeddingError):
    """Raised when generated vector dimensions do not match the expected index dimension."""
    pass


# --- Vector Store & Retrieval Exceptions ---
class VectorStoreError(AIEngineError):
    """Base error for vector database and index operations."""
    pass

class IndexNotFoundError(VectorStoreError):
    """Raised when a query or deletion is attempted on a non-existent index."""
    pass

class AuthorizationScopeError(VectorStoreError):
    """Raised when an operation attempts to access documents outside authorized scope."""
    pass

class RetrievalError(AIEngineError):
    """Raised when semantic retrieval fails."""
    pass

class EmptyRetrievalResultError(RetrievalError):
    """Raised when no matching chunks meet the relevance criteria."""
    pass


# --- LLM & RAG Exceptions ---
class LLMProviderError(AIEngineError):
    """Base error for LLM provider communication, timeouts, or API errors."""
    pass

class LLMRateLimitError(LLMProviderError):
    """Raised when an LLM provider rate limit is exceeded."""
    pass

class LLMTimeoutError(LLMProviderError):
    """Raised when an LLM call exceeds the configured timeout."""
    pass

class InsufficientEvidenceError(AIEngineError):
    """Raised when retrieved context is inadequate to answer a question reliably."""
    pass

class GenerationValidationError(AIEngineError):
    """Raised when LLM-generated output fails schema validation."""
    pass

class CitationValidationError(AIEngineError):
    """Raised when citations in the generated answer cannot be verified against source chunks."""
    pass
