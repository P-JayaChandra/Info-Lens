"""
InfoLens AI & Document Intelligence Engine
Package Version: 1.0.0
"""

from ai_engine.config import AIEngineConfig, get_config, set_config
from ai_engine.schemas import (
    AuthorizedScope,
    Citation,
    ConversationMessage,
    DocumentIndexingResult,
    DocumentMetadata,
    ExtractedDocument,
    Flashcard,
    FlashcardSetResponse,
    GeneratedQuestion,
    PageContent,
    ProcessingStatus,
    QuestionDifficulty,
    QuestionEvaluationResult,
    QuestionSetResponse,
    QuestionType,
    QuizEvaluationResult,
    QuizSubmission,
    RAGResponse,
    RetrievalOptions,
    SubmittedAnswer,
    SummaryResponse,
    SummarySection,
    SummaryType,
    SupportedDocumentType,
    TextChunk,
    VectorQueryResult,
)
from ai_engine.services.document_indexing_service import DocumentIndexingService
from ai_engine.services.document_query_service import DocumentQueryService
from ai_engine.services.study_service import StudyService

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "AIEngineConfig",
    "get_config",
    "set_config",
    # Schemas
    "AuthorizedScope",
    "Citation",
    "ConversationMessage",
    "DocumentIndexingResult",
    "DocumentMetadata",
    "ExtractedDocument",
    "Flashcard",
    "FlashcardSetResponse",
    "GeneratedQuestion",
    "PageContent",
    "ProcessingStatus",
    "QuestionDifficulty",
    "QuestionEvaluationResult",
    "QuestionSetResponse",
    "QuestionType",
    "QuizEvaluationResult",
    "QuizSubmission",
    "RAGResponse",
    "RetrievalOptions",
    "SubmittedAnswer",
    "SummaryResponse",
    "SummarySection",
    "SummaryType",
    "SupportedDocumentType",
    "TextChunk",
    "VectorQueryResult",
    # Services
    "DocumentIndexingService",
    "DocumentQueryService",
    "StudyService",
]
