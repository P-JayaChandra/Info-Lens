# Document Intelligence & Question-Answering Backend

A high-performance, modular Python backend for AI-powered document analysis, intelligent question answering (RAG), and educational assessment generation.

## Features
- **Extensible Architecture**: Clean domain separation across API, Services, Repositories, and Infrastructure.
- **Provider-Agnostic AI**: Unified interfaces for OpenAI, Anthropic, local models, and mock testing providers.
- **Multi-Format Extraction**: Native parsers for PDF, DOCX, and TXT with structure, table, and metadata extraction.
- **Adaptive Vector Search**: Support for pgvector, SQLite-vec, and FAISS vector stores with metadata filtering and hybrid retrieval.
- **Study & Assessment Generation**: Automated quizzes, flashcards, long/short-form question generation with verifiable citations.
- **Enterprise-Grade Foundation**: Structured JSON logging, correlation IDs, RFC 7807 problem details, health probes, and JWT authentication.

## Quickstart

### Prerequisites
- Python 3.12+
- PostgreSQL with `pgvector` (or SQLite for development)
- Redis

### Setup & Run
```bash
# Install dependencies
pip install -e .

# Run development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Running Tests
```bash
python -m pytest tests -v
```

### Measuring Verified LOC
```bash
python scripts/loc_counter.py
```
