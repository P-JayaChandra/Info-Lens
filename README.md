# InfoLens — AI, RAG & Document Intelligence Engine

Modular Python document intelligence, semantic vector retrieval, grounded RAG, summarization, and active-recall study engine for InfoLens.

Built as **Member 3**'s dedicated package for integration with **Member 2**'s FastAPI backend and **Member 1**'s React frontend.

---

## 🚀 Key Capabilities

1. **Document Ingestion & Extraction**
   - **PDF**: Page-by-page extraction via PyMuPDF (`pymupdf`/`fitz`) with layout preservation and page tracking.
   - **DOCX**: Paragraphs, headings, bullet lists, and structured table extraction via `python-docx`.
   - **TXT**: Robust multi-encoding decoding (UTF-8, UTF-8-sig, Latin-1, CP1252) with form-feed page segmentation.
   - **Scanned PDF & OCR**: Automatic detection of scanned or low-text pages with optional Tesseract OCR fallback.
   - **Conservative Cleaning**: Normalizes whitespace while strictly preserving mathematical notation, lists, indentation, and paragraph breaks.

2. **Intelligent Chunking & Embeddings**
   - Paragraph- and sentence-boundary aware chunking with configurable size and bounded overlap.
   - Deterministic, traceable chunk IDs (`{doc_id}_p{page_num}_c{chunk_idx}`) linking chunks to originating pages.
   - Flexible embedding provider abstraction: Local HuggingFace `sentence-transformers` (`all-MiniLM-L6-v2`), OpenAI embeddings, or deterministic feature-hashed Mock provider for offline testing.

3. **Persistent Vector Store & Multi-Tenant Isolation**
   - High-performance, zero-external-dependency cosine vector index.
   - Atomic disk persistence (`JSON` metadata + `NumPy` `.npy` matrix).
   - **Strict Scope Isolation**: Authorization-aware search that enforces tenant/owner boundaries. Cross-user queries outside authorized scopes are strictly blocked.
   - BM25 hybrid ranking / reranking fusing dense semantic scores with lexical token matches.

4. **Grounded RAG & Verified Citations**
   - Bounded context window assembly with token/character budgeting.
   - Strict anti-prompt injection system prompts preventing untrusted document content from overriding system instructions.
   - Grounded answering with explicit insufficient-evidence handling.
   - **Citation Verification**: Every citation marker is validated against real retrieved chunks; hallucinated citations are discarded.

5. **Study Content Generation**
   - **Summarization**: Executive summaries, section-by-section breakdown, key takeaways, and hierarchical Map-Reduce for large documents.
   - **Question Generation**: Multiple Choice (MCQ), Short Answer (with rubrics), Long Answer, and True/False questions with explanations.
   - **Quiz Evaluation**: Deterministic matching for objective questions + rubric-based AI grading for free-text answers.
   - **Flashcards**: Active-recall front/back study cards with topic tags and difficulty ratings.

---

## 📁 Package Architecture

```text
ai_engine/
├── __init__.py                # Root exports and version
├── config.py                  # Pydantic BaseSettings loaded from .env
├── schemas.py                 # Typed data contracts for Member 1 & 2 integration
├── exceptions.py              # Custom AI engine exception hierarchy
├── document_processing/       # PDF, DOCX, TXT, OCR, and cleaning
│   ├── __init__.py
│   ├── cleaning.py
│   ├── docx_extractor.py
│   ├── metadata.py
│   ├── ocr.py
│   ├── pdf_extractor.py
│   └── txt_extractor.py
├── chunking/                  # Paragraph/sentence chunking
│   ├── __init__.py
│   └── text_chunker.py
├── embeddings/                # Local, OpenAI, and Mock embedding providers
│   ├── __init__.py
│   └── embedding_service.py
├── retrieval/                 # Persistent vector store & hybrid BM25 retriever
│   ├── __init__.py
│   ├── retriever.py
│   └── vector_store.py
├── rag/                       # Prompts, generator abstraction, citation verification
│   ├── __init__.py
│   ├── answer_service.py
│   ├── citation_builder.py
│   ├── generator.py
│   └── prompt_templates.py
├── generation/                # Summarization, question generation, flashcards
│   ├── __init__.py
│   ├── flashcard_generator.py
│   ├── question_generator.py
│   └── summarizer.py
├── evaluation/                # Quiz evaluation and retrieval benchmark metrics
│   ├── __init__.py
│   ├── answer_evaluator.py
│   └── retrieval_evaluator.py
└── services/                  # High-level facades for Member 2 integration
    ├── __init__.py
    ├── document_indexing_service.py
    ├── document_query_service.py
    └── study_service.py
```

---

## 🔌 Integration Interfaces for Member 2 (FastAPI Backend)

Member 2 can import the unified high-level services directly into FastAPI endpoint handlers:

### 1. Document Indexing Service
```python
from ai_engine.services.document_indexing_service import DocumentIndexingService
from ai_engine.schemas import AuthorizedScope, ProcessingStatus

indexing_service = DocumentIndexingService()

def on_status_update(doc_id: str, status: ProcessingStatus, error: str = None):
    # Member 2 updates PostgreSQL document status column or WebSocket
    print(f"Doc {doc_id} status: {status.value}")

# Index an uploaded file
result = indexing_service.index_document_from_file(
    file_path="/path/to/uploaded/document.pdf",
    document_id="doc_uuid_123",
    owner_id="user_uuid_456",
    collection_ids=["physics_101"],
    status_callback=on_status_update,
)

# Delete index on document removal
scope = AuthorizedScope(user_id="user_uuid_456", authorized_document_ids=["doc_uuid_123"])
indexing_service.delete_document_index("doc_uuid_123", scope=scope)
```

### 2. Document Query & Grounded RAG Service
```python
from ai_engine.services.document_query_service import DocumentQueryService
from ai_engine.schemas import AuthorizedScope, ConversationMessage

query_service = DocumentQueryService()

scope = AuthorizedScope(
    user_id="user_uuid_456",
    authorized_document_ids=["doc_uuid_123", "doc_uuid_789"],
)

response = query_service.answer_question(
    question="What are the key assumptions of the model?",
    scope=scope,
    conversation_history=[
        ConversationMessage(role="user", content="Hello"),
        ConversationMessage(role="assistant", content="Hi! How can I help you study?"),
    ],
)
# Returns RAGResponse:
# response.answer -> Grounded answer string
# response.citations -> List of verified Citation objects
# response.insufficient_evidence -> bool
```

### 3. Study Tools Service
```python
from ai_engine.services.study_service import StudyService
from ai_engine.schemas import AuthorizedScope, QuestionType, QuestionDifficulty, SummaryType

study_service = StudyService()
scope = AuthorizedScope(user_id="user_uuid_456", authorized_document_ids=["doc_uuid_123"])

# Summarization
summary = study_service.summarize_document(
    document_id="doc_uuid_123",
    scope=scope,
    summary_type=SummaryType.DETAILED,
)

# Question Generation (Practice Quizzes)
questions = study_service.generate_questions(
    document_id="doc_uuid_123",
    scope=scope,
    question_type=QuestionType.MULTIPLE_CHOICE,
    difficulty=QuestionDifficulty.MEDIUM,
    count=5,
)

# Flashcard Generation
flashcards = study_service.generate_flashcards(
    document_id="doc_uuid_123",
    scope=scope,
    count=10,
)

# Quiz Evaluation
eval_result = study_service.evaluate_quiz(
    questions=questions.questions,
    submission=user_submission_payload,
)
```

---

## 🎨 Response Schemas for Member 1 (React Frontend)

All schemas are standard Pydantic models serializable to clean JSON:

- **RAG Answer Card**:
  ```json
  {
    "query": "What is quantum superposition?",
    "answer": "Quantum superposition allows qubits to exist in a linear combination of states [cite: 0].",
    "citations": [
      {
        "document_id": "doc_123",
        "document_title": "Quantum_Computing_Overview.pdf",
        "chunk_id": "doc_123_p1_c0",
        "page_number": 1,
        "snippet": "Qubits can exist in superposition states, enabling exponential state representation...",
        "relevance_score": 0.88
      }
    ],
    "insufficient_evidence": false,
    "retrieval_status": "success",
    "confidence_score": 0.98,
    "processing_time_ms": 320.5
  }
  ```

- **Flashcard Deck**:
  ```json
  {
    "document_id": "doc_123",
    "total_count": 2,
    "cards": [
      {
        "card_id": "fc_1",
        "front": "What is a qubit?",
        "back": "The fundamental unit of quantum information capable of superposition.",
        "topic": "Fundamentals",
        "difficulty": "easy",
        "page_number": 1
      }
    ]
  }
  ```

---

## 🧪 Testing and Verification

Run the automated test suite:

```bash
python -m pytest -v
```

All **30 unit and integration test suites** pass with 100% success across:
- Extraction of PDF, DOCX, TXT
- Empty document and corrupted file error boundaries
- OCR failure & availability handling
- Conservative cleaning & mathematical formula preservation
- Paragraph- and sentence-boundary chunking
- Embedding generation & dimensional integrity
- Multi-tenant vector persistence & cross-user security isolation
- Citation validation & hallucination stripping
- Summarization, question generation, and flashcards
- Quiz grading (deterministic + rubric AI)
- Retrieval quality benchmarking (Precision@k, Recall@k, Hit Rate, MRR)
