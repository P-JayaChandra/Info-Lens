"""
Unit tests for RAG Grounding, Prompt Construction, and Citation Validation.
"""

from ai_engine.embeddings.embedding_service import MockEmbeddingService
from ai_engine.rag.answer_service import GroundedAnswerService
from ai_engine.rag.citation_builder import CitationBuilder
from ai_engine.rag.generator import MockLLMGenerator
from ai_engine.retrieval.retriever import DocumentRetriever
from ai_engine.retrieval.vector_store import PersistentVectorStore
from ai_engine.schemas import (
    AuthorizedScope,
    ConversationMessage,
    TextChunk,
    VectorQueryResult,
)


def test_citation_builder_validates_real_chunks():
    chunk0 = TextChunk(
        chunk_id="doc1_p1_c0",
        document_id="doc1",
        chunk_index=0,
        text="FastAPI is an asynchronous modern Python framework.",
        page_number=1,
        metadata={"filename": "FastAPI_Guide.pdf"},
    )
    candidates = [
        VectorQueryResult(chunk=chunk0, similarity_score=0.92, rank=1)
    ]

    raw_answer = "FastAPI supports high concurrency [cite: 0]."
    cleaned, citations = CitationBuilder.extract_and_validate_citations(raw_answer, candidates)

    assert len(citations) == 1
    assert citations[0].document_id == "doc1"
    assert citations[0].chunk_id == "doc1_p1_c0"
    assert citations[0].page_number == 1
    assert "FastAPI" in citations[0].snippet


def test_citation_builder_discards_hallucinated_citations():
    chunk0 = TextChunk(
        chunk_id="doc1_p1_c0",
        document_id="doc1",
        chunk_index=0,
        text="PostgreSQL is an ACID-compliant relational database.",
        page_number=1,
    )
    candidates = [VectorQueryResult(chunk=chunk0, similarity_score=0.88, rank=1)]

    # Model hallucinated citation [cite: 99] and [cite: fake_doc_id]
    raw_answer = "PostgreSQL ensures durability [cite: 99] and transactional integrity [cite: fake_doc_id]."
    _, citations = CitationBuilder.extract_and_validate_citations(raw_answer, candidates)

    # Hallucinated indices should not become valid citations
    assert not any(c.chunk_id == "fake_doc_id" for c in citations)


def test_grounded_rag_pipeline(tmp_path):
    store = PersistentVectorStore(persistence_dir=tmp_path / "vecs")
    embed_svc = MockEmbeddingService(dimension=64)

    chunk = TextChunk(
        chunk_id="doc10_c0",
        document_id="doc10",
        chunk_index=0,
        text="The InfoLens AI engine processes documents and extracts verifiable citations.",
        page_number=1,
        metadata={"owner_id": "user_dev", "filename": "InfoLens_Spec.pdf"},
    )
    store.add_embeddings(embed_svc.embed_chunks([chunk]))

    retriever = DocumentRetriever(vector_store=store, embedding_service=embed_svc)
    llm = MockLLMGenerator()
    answer_svc = GroundedAnswerService(retriever=retriever, llm_generator=llm)

    scope = AuthorizedScope(user_id="user_dev", authorized_document_ids=["doc10"])
    response = answer_svc.answer_question(
        question="How does InfoLens process documents?",
        scope=scope,
        conversation_history=[
            ConversationMessage(role="user", content="Hello"),
            ConversationMessage(role="assistant", content="Hi! How can I help you study?"),
        ],
    )

    assert response.query == "How does InfoLens process documents?"
    assert response.insufficient_evidence is False
    assert len(response.citations) > 0
    assert response.citations[0].document_id == "doc10"
    assert response.processing_time_ms > 0


def test_rag_handles_insufficient_evidence(tmp_path):
    store = PersistentVectorStore(persistence_dir=tmp_path / "empty_vecs")
    embed_svc = MockEmbeddingService(dimension=64)
    retriever = DocumentRetriever(vector_store=store, embedding_service=embed_svc)
    answer_svc = GroundedAnswerService(retriever=retriever, llm_generator=MockLLMGenerator())

    # Query with empty vector store
    scope = AuthorizedScope(user_id="user_dev", authorized_document_ids=["doc_none"])
    response = answer_svc.answer_question(
        question="What is the speed of light in vacuum?",
        scope=scope,
    )

    assert response.insufficient_evidence is True
    assert "insufficient evidence" in response.answer.lower()
    assert len(response.citations) == 0
