from enum import Enum, unique


@unique
class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@unique
class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    GUEST = "guest"


@unique
class DocumentStatus(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    VALIDATED = "validated"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    CHUNKING = "chunking"
    CHUNKED = "chunked"
    EMBEDDING = "embedding"
    EMBEDDED = "embedded"
    INDEXING = "indexing"
    INDEXED = "indexed"
    READY = "ready"
    FAILED = "failed"
    ARCHIVED = "archived"


@unique
class DocumentFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MARKDOWN = "md"
    HTML = "html"
    CSV = "csv"
    JSON = "json"


@unique
class ChunkingStrategy(str, Enum):
    FIXED_SIZE = "fixed_size"
    SLIDING_WINDOW = "sliding_window"
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    MARKDOWN_HEADER = "markdown_header"
    SEMANTIC = "semantic"
    RECURSIVE = "recursive"


@unique
class EmbeddingProvider(str, Enum):
    MOCK = "mock"
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    COHERE = "cohere"


@unique
class LLMProvider(str, Enum):
    MOCK = "mock"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    GROQ = "groq"


@unique
class VectorStoreType(str, Enum):
    PGVECTOR = "pgvector"
    SQLITE_VEC = "sqlite_vec"
    CHROMA = "chroma"
    FAISS = "faiss"
    IN_MEMORY = "in_memory"


@unique
class StorageBackend(str, Enum):
    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    AZURE_BLOB = "azure_blob"
    IN_MEMORY = "in_memory"


@unique
class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    FILL_IN_BLANK = "fill_in_blank"


@unique
class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


@unique
class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@unique
class ErrorCode(str, Enum):
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    DOCUMENT_PARSE_ERROR = "DOCUMENT_PARSE_ERROR"
    DOCUMENT_TOO_LARGE = "DOCUMENT_TOO_LARGE"
    UNSUPPORTED_MEDIA_TYPE = "UNSUPPORTED_MEDIA_TYPE"
    STORAGE_ERROR = "STORAGE_ERROR"
    EMBEDDING_ERROR = "EMBEDDING_ERROR"
    VECTOR_STORE_ERROR = "VECTOR_STORE_ERROR"
    LLM_PROVIDER_ERROR = "LLM_PROVIDER_ERROR"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
