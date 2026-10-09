# InfoLens — Intelligent Conversational Document Intelligence Platform

A comprehensive, production-oriented document intelligence platform that allows users to upload documents, ask questions about their contents, retrieve relevant passages with verified page-level citations, generate summaries, create practice questions, evaluate quizzes, and study using interactive flashcards.

---

## 🏛️ Platform Architecture Overview

```text
Info-Lens/
├── src/                               # Member 1: React + Vite + Tailwind Frontend
├── backend/                           # Member 2: FastAPI + SQLAlchemy + PostgreSQL Backend
├── ai_engine/                         # Member 3: AI, Document Processing, Embeddings, RAG & Study Engine
│   ├── chunking/                      # Paragraph & sentence boundary chunking
│   ├── document_processing/           # Multi-format extractors (PDF, DOCX, TXT) & OCR
│   ├── embeddings/                    # Vector embedding providers (Local, OpenAI, Mock)
│   ├── evaluation/                    # Retrieval benchmarking & quiz grading
│   ├── generation/                    # Summarization, question generation & flashcards
│   ├── rag/                           # Grounded Q&A, prompt templates & citation verification
│   ├── retrieval/                     # Persistent vector store & BM25 hybrid search
│   └── services/                      # High-level facades for backend integration
└── tests/                             # Automated test suites
```

---

## 🚀 Quick Start

### 1. AI Engine & Backend Setup
```bash
pip install -r requirements.txt
cp .env.example .env
python -m pytest -v
```

### 2. Frontend Setup
```bash
npm install
npm run dev
```

---

## 🧪 Testing and Quality Assurance

- **AI Engine Tests**: `python -m pytest -v` (30 test suites passing)
- **Frontend Tests**: `npx vitest run`
- **Backend Tests**: `pytest backend/tests`
