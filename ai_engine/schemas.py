"""
Data contracts and Pydantic schemas for the InfoLens AI Engine.
Defines all input and output types for integration with Member 2 (Backend) and Member 1 (Frontend).
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    EXTRACTING = "extracting"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    READY = "ready"
    FAILED = "failed"


class SupportedDocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class SummaryType(str, Enum):
    SHORT = "short"
    DETAILED = "detailed"
    SECTION_BASED = "section_based"


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    TRUE_FALSE = "true_false"


class QuestionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class EvaluationMethod(str, Enum):
    DETERMINISTIC = "deterministic"
    RUBRIC_AI = "rubric_ai"


# ==========================================
# 1. SCOPE & AUTHORIZATION
# ==========================================
class AuthorizedScope(BaseModel):
    """Encapsulates permissions and authorized document access boundary."""
    user_id: str
    authorized_document_ids: List[str] = Field(default_factory=list)
    authorized_collection_ids: List[str] = Field(default_factory=list)
    is_admin: bool = False

    def can_access_document(self, document_id: str) -> bool:
        if self.is_admin:
            return True
        return document_id in self.authorized_document_ids


# ==========================================
# 2. DOCUMENT EXTRACTION & INGESTION
# ==========================================
class DocumentMetadata(BaseModel):
    """Metadata describing an uploaded or ingested document."""
    document_id: str
    filename: str
    file_size_bytes: int
    doc_type: SupportedDocumentType
    owner_id: str
    collection_ids: List[str] = Field(default_factory=list)
    total_pages: int = 1
    checksum_sha256: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    extra: Dict[str, Any] = Field(default_factory=dict)


class PageContent(BaseModel):
    """Extracted text and metadata for a single document page."""
    page_number: int
    text: str
    character_count: int
    is_ocr: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExtractedDocument(BaseModel):
    """Output from the document extraction pipeline."""
    document_id: str
    metadata: DocumentMetadata
    pages: List[PageContent] = Field(default_factory=list)
    full_text: str
    extraction_method: str
    is_scanned: bool = False
    extraction_time_ms: float = 0.0


# ==========================================
# 3. CHUNKING & EMBEDDINGS
# ==========================================
class TextChunk(BaseModel):
    """A granular chunk of text extracted from a document with full lineage."""
    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    page_number: Optional[int] = None
    start_char: int = 0
    end_char: int = 0
    section_title: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChunkEmbedding(BaseModel):
    """Chunk accompanied by its dense vector representation."""
    chunk: TextChunk
    vector: List[float]


# ==========================================
# 4. VECTOR STORE & RETRIEVAL
# ==========================================
class VectorQueryResult(BaseModel):
    """Represents a matched chunk from semantic or hybrid retrieval."""
    chunk: TextChunk
    similarity_score: float
    rank: int = 1


class RetrievalOptions(BaseModel):
    """Configurable knobs for document context retrieval."""
    top_k: int = 5
    similarity_threshold: float = 0.2
    target_document_ids: Optional[List[str]] = None
    enable_reranking: bool = False


# ==========================================
# 5. RAG & CITATIONS
# ==========================================
class Citation(BaseModel):
    """Validated source attribution linking an answer back to document evidence."""
    document_id: str
    document_title: str
    chunk_id: str
    page_number: Optional[int] = None
    snippet: str
    relevance_score: float = 1.0


class ConversationMessage(BaseModel):
    """Role-scoped conversation turn for context-aware multi-turn RAG."""
    role: str  # "user" | "assistant" | "system"
    content: str


class RAGResponse(BaseModel):
    """Complete grounded answer structure for Member 1 & 2 integration."""
    query: str
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    insufficient_evidence: bool = False
    retrieval_status: str = "success"
    model_name: str
    confidence_score: float = 1.0
    processing_time_ms: float = 0.0
    diagnostics: Optional[Dict[str, Any]] = None


# ==========================================
# 6. SUMMARIZATION
# ==========================================
class SummarySection(BaseModel):
    """A thematic section summary with relevant source citations."""
    title: str
    content: str
    key_points: List[str] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)


class SummaryResponse(BaseModel):
    """Grounded multi-format summary output."""
    document_id: str
    summary_type: SummaryType
    executive_summary: str
    sections: List[SummarySection] = Field(default_factory=list)
    key_takeaways: List[str] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    word_count: int = 0
    processing_time_ms: float = 0.0


# ==========================================
# 7. STUDY TOOLS: QUESTIONS & QUIZZES
# ==========================================
class GeneratedQuestion(BaseModel):
    """Structured question grounded in document content."""
    question_id: str
    document_id: str
    question_type: QuestionType
    difficulty: QuestionDifficulty
    question_text: str
    options: Optional[List[str]] = None  # Populated for MCQ
    correct_answer: str
    explanation: str
    rubric: Optional[str] = None  # Guidelines for evaluating short/long answers
    source_chunk_id: Optional[str] = None
    page_number: Optional[int] = None


class QuestionSetResponse(BaseModel):
    """Set of generated questions ready for study or quiz sessions."""
    document_id: str
    total_count: int
    questions: List[GeneratedQuestion]


class SubmittedAnswer(BaseModel):
    """User submitted answer for a single question."""
    question_id: str
    user_answer: str


class QuizSubmission(BaseModel):
    """Payload for submitting and evaluating an entire quiz."""
    quiz_id: str
    document_id: str
    answers: List[SubmittedAnswer]


class QuestionEvaluationResult(BaseModel):
    """Scoring and feedback for an individual question."""
    question_id: str
    question_text: str
    question_type: QuestionType
    user_answer: str
    correct_answer: str
    is_correct: bool
    score: float
    max_score: float = 1.0
    feedback: str
    evaluation_method: EvaluationMethod
    rubric: Optional[str] = None


class QuizEvaluationResult(BaseModel):
    """Aggregated evaluation and score report for a quiz submission."""
    quiz_id: str
    document_id: str
    total_score: float
    max_possible_score: float
    percentage_score: float
    passed: bool
    results: List[QuestionEvaluationResult]
    summary_feedback: str


# ==========================================
# 8. STUDY TOOLS: FLASHCARDS
# ==========================================
class Flashcard(BaseModel):
    """A study flashcard with front/back and source attribution."""
    card_id: str
    document_id: str
    front: str  # Concept or Question
    back: str   # Definition, formula, or Answer
    topic: Optional[str] = None
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    explanation: Optional[str] = None
    source_chunk_id: Optional[str] = None
    page_number: Optional[int] = None


class FlashcardSetResponse(BaseModel):
    """Set of flashcards generated for a document."""
    document_id: str
    total_count: int
    cards: List[Flashcard]


# ==========================================
# 9. INDEXING RESULTS & STATUS
# ==========================================
class DocumentIndexingResult(BaseModel):
    """Result of an end-to-end document processing and indexing job."""
    document_id: str
    status: ProcessingStatus
    chunk_count: int = 0
    vector_count: int = 0
    duration_ms: float = 0.0
    error_message: Optional[str] = None
