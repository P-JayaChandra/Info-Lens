"""
Integration tests for High-Level Services (Member 2 integration interfaces).
"""

from pathlib import Path
import pytest
import pymupdf

from ai_engine.chunking.text_chunker import TextChunker
from ai_engine.embeddings.embedding_service import MockEmbeddingService
from ai_engine.rag.answer_service import GroundedAnswerService
from ai_engine.rag.generator import MockLLMGenerator
from ai_engine.retrieval.retriever import DocumentRetriever
from ai_engine.retrieval.vector_store import PersistentVectorStore
from ai_engine.schemas import AuthorizedScope, ProcessingStatus
from ai_engine.services.document_indexing_service import DocumentIndexingService
from ai_engine.services.document_query_service import DocumentQueryService
from ai_engine.services.study_service import StudyService


@pytest.fixture
def test_environment(tmp_path):
    store_dir = tmp_path / "service_store"
    vector_store = PersistentVectorStore(persistence_dir=store_dir)
    embedding_service = MockEmbeddingService(dimension=64)
    chunker = TextChunker(chunk_size=150, chunk_overlap=30)
    llm_generator = MockLLMGenerator()

    indexing_svc = DocumentIndexingService(
        vector_store=vector_store,
        embedding_service=embedding_service,
        chunker=chunker,
    )

    retriever = DocumentRetriever(
        vector_store=vector_store,
        embedding_service=embedding_service,
    )
    answer_svc = GroundedAnswerService(
        retriever=retriever,
        llm_generator=llm_generator,
    )

    query_svc = DocumentQueryService(
        retriever=retriever,
        answer_service=answer_svc,
    )

    study_svc = StudyService(
        vector_store=vector_store,
    )

    # Create a real sample PDF for indexing
    doc_path = tmp_path / "deep_learning.pdf"
    pdf = pymupdf.open()
    p1 = pdf.new_page()
    p1.insert_text((50, 50), "Deep Learning Fundamentals\n\nNeural networks learn representations of data.\nBackpropagation computes gradients efficiently.")
    p2 = pdf.new_page()
    p2.insert_text((50, 50), "Transformers and Attention\n\nAttention mechanisms allow models to focus on relevant tokens across sequences.")
    pdf.save(str(doc_path))
    pdf.close()

    return {
        "indexing_svc": indexing_svc,
        "query_svc": query_svc,
        "study_svc": study_svc,
        "vector_store": vector_store,
        "sample_pdf": doc_path,
    }


def test_end_to_end_indexing_and_query_flow(test_environment):
    indexing_svc = test_environment["indexing_svc"]
    query_svc = test_environment["query_svc"]
    study_svc = test_environment["study_svc"]
    pdf_path = test_environment["sample_pdf"]

    status_transitions = []

    def status_tracker(doc_id, status, err):
        status_transitions.append(status)

    # 1. Index document
    index_result = indexing_svc.index_document_from_file(
        file_path=pdf_path,
        document_id="doc_dl_101",
        owner_id="user_alice",
        status_callback=status_tracker,
    )

    assert index_result.status == ProcessingStatus.READY
    assert index_result.chunk_count >= 2
    assert index_result.vector_count >= 2

    # Check status transitions
    assert ProcessingStatus.EXTRACTING in status_transitions
    assert ProcessingStatus.CHUNKING in status_transitions
    assert ProcessingStatus.EMBEDDING in status_transitions
    assert ProcessingStatus.INDEXING in status_transitions
    assert ProcessingStatus.READY in status_transitions

    # 2. Query document with authorized scope
    scope_alice = AuthorizedScope(user_id="user_alice", authorized_document_ids=["doc_dl_101"])
    rag_resp = query_svc.answer_question(
        question="What is backpropagation used for?",
        scope=scope_alice,
    )
    assert rag_resp.retrieval_status == "success"
    assert len(rag_resp.citations) > 0
    assert rag_resp.citations[0].document_id == "doc_dl_101"

    # 3. Generate summary via StudyService
    summary = study_svc.summarize_document(
        document_id="doc_dl_101",
        scope=scope_alice,
    )
    assert summary.document_id == "doc_dl_101"

    # 4. Generate flashcards via StudyService
    fc_set = study_svc.generate_flashcards(
        document_id="doc_dl_101",
        scope=scope_alice,
        count=3,
    )
    assert fc_set.document_id == "doc_dl_101"
    assert len(fc_set.cards) > 0

    # 5. Delete document
    deleted = indexing_svc.delete_document_index("doc_dl_101", scope=scope_alice)
    assert deleted >= 2
    assert test_environment["vector_store"].count() == 0
