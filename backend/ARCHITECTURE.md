# System Architecture

## AI-Powered Document Analysis and Question-Answering Platform

### Architectural Philosophy
1. **Modularity & High Cohesion**: Every subsystem lives in its own dedicated package with explicit interfaces and contracts.
2. **Domain-Driven Design with Clean Separation**: Core business logic is isolated from HTTP frameworks, databases, and third-party AI provider SDKs.
3. **Pluggable AI & Vector Infrastructure**: LLM and embedding providers are behind abstract interfaces (`BaseLLMProvider`, `BaseEmbeddingProvider`, `BaseVectorStore`), enabling local inference, mock testing, or external APIs (OpenAI, Anthropic, Ollama, etc.) without code refactoring.
4. **Resilience & Fault Tolerance**: Document ingestion pipelines feature idempotency, transaction boundaries, exponential backoff retries, and comprehensive error categorization.
5. **Security by Default**: Content-based file validation (not just file extension checking), prompt injection sanitization, scoped authorization tokens, and strict audit trails.

### High-Level Component Flow

```
[Client / API Consumer]
         │ (HTTP / SSE / WebSocket)
         ▼
[FastAPI Application Layer (v1)]
   ├── Middleware Stack (Correlation ID, Timing, Auth, Rate Limiter)
   └── Endpoint Routers (Health, Auth, Documents, RAG, Quiz, Chat)
         │
         ▼
[Service & Domain Layer]
   ├── DocumentService (Upload, Validation, Lifecycle)
   ├── IngestionPipeline (Extraction, Normalization, Chunking)
   ├── RAGService (Context Assembly, Citation Grounding, Guardrails)
   ├── StudyToolsService (Questions, Quizzes, Flashcards, Exams)
   └── AuthService & UserService (RBAC, Tokens, Verification)
         │
    ┌────┴───────────────────────────┬────────────────────────────┐
    ▼                                ▼                            ▼
[Storage & DB]              [Retrieval & AI]             [Async Workers & Jobs]
├── SQLAlchemy 2.0 (Postgres)├── Embedding Provider       ├── Ingestion Workers
├── Alembic Migrations       ├── Vector Store Engine      ├── Background Tasks
└── Object/File Storage      └── LLM Generation Engine   └── Event Bus
```

### Subsystems Breakdown
- **`app/core/`**: Configuration, logging, security crypto, exceptions, constants.
- **`app/database/`**: Session lifecycles, connection pooling, declarative base with UUID & audit mixins.
- **`app/middleware/`**: Request context, timing, correlation tracking, standardized error responses.
- **`app/api/v1/`**: Versioned REST and streaming endpoints.
- **`app/documents/`**: Document lifecycle, metadata, retention, versioning.
- **`app/extraction/`**: PDF, DOCX, TXT parsers extracting text, structure, tables, and metadata.
- **`app/chunking/`**: Configurable chunking (fixed, sliding window, recursive, semantic, document-structure-aware).
- **`app/embeddings/`**: Vector representations, batch generation, caching.
- **`app/vector_store/`**: Similarity search, HNSW indexing, pgvector & SQLite-vec adapters, metadata filtering.
- **`app/rag/`**: Source-grounded retrieval-augmented generation, citation extraction, hallucination mitigation.
- **`app/chat/`**: Multi-turn dialogue, streaming responses, context memory, session management.
- **`app/quiz/` & `app/study/`**: Automated assessment generation, scoring, flashcard management, exam paper synthesis.
