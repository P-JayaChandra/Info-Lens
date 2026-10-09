"""
Unit tests for Vector Store, Persistence, and Multi-Tenant Isolation.
"""

import pytest
from ai_engine.embeddings.embedding_service import MockEmbeddingService
from ai_engine.exceptions import AuthorizationScopeError
from ai_engine.retrieval.vector_store import PersistentVectorStore
from ai_engine.schemas import AuthorizedScope, ChunkEmbedding, TextChunk


@pytest.fixture
def vector_store(tmp_path):
    store_dir = tmp_path / "test_vec_store"
    return PersistentVectorStore(persistence_dir=store_dir)


@pytest.fixture
def sample_embeddings():
    service = MockEmbeddingService(dimension=64)
    # User A's Document (Doc 1)
    chunk1 = TextChunk(
        chunk_id="d1_c0",
        document_id="doc_1",
        chunk_index=0,
        text="Quantum cryptography uses quantum mechanics for secure communications.",
        page_number=1,
        metadata={"owner_id": "user_alice"},
    )
    chunk2 = TextChunk(
        chunk_id="d1_c1",
        document_id="doc_1",
        chunk_index=1,
        text="Quantum key distribution (QKD) is the most prominent application.",
        page_number=1,
        metadata={"owner_id": "user_alice"},
    )

    # User B's Document (Doc 2) - Confidential salary data
    chunk3 = TextChunk(
        chunk_id="d2_c0",
        document_id="doc_2",
        chunk_index=0,
        text="Executive compensation and private bonus tables for 2026.",
        page_number=1,
        metadata={"owner_id": "user_bob"},
    )

    chunks = [chunk1, chunk2, chunk3]
    return service.embed_chunks(chunks)


def test_add_and_search_vector_store(vector_store, sample_embeddings):
    vector_store.add_embeddings(sample_embeddings)
    assert vector_store.count() == 3

    # Alice queries her document
    scope_alice = AuthorizedScope(user_id="user_alice", authorized_document_ids=["doc_1"])
    service = MockEmbeddingService(dimension=64)
    q_vec = service.embed_query("quantum mechanics security")

    results = vector_store.search(
        query_vector=q_vec,
        scope=scope_alice,
        top_k=5,
    )

    assert len(results) > 0
    # Every returned chunk MUST belong to Alice's authorized document doc_1
    for res in results:
        assert res.chunk.document_id == "doc_1"
        assert res.similarity_score >= -1.0


def test_strict_cross_user_isolation(vector_store, sample_embeddings):
    """
    CRITICAL SECURITY TEST: Ensure User Alice CANNOT retrieve User Bob's confidential document
    even if the query is an exact keyword match to Bob's document.
    """
    vector_store.add_embeddings(sample_embeddings)

    scope_alice = AuthorizedScope(user_id="user_alice", authorized_document_ids=["doc_1"])
    service = MockEmbeddingService(dimension=64)
    # Alice asks about executive salaries (which is inside Bob's doc_2)
    q_vec = service.embed_query("Executive compensation and private bonus tables")

    results = vector_store.search(
        query_vector=q_vec,
        scope=scope_alice,
        top_k=5,
    )

    # doc_2 MUST NOT be present in results for Alice!
    for res in results:
        assert res.chunk.document_id != "doc_2"


def test_document_deletion(vector_store, sample_embeddings):
    vector_store.add_embeddings(sample_embeddings)
    assert vector_store.count() == 3

    # Delete doc_1
    scope_alice = AuthorizedScope(user_id="user_alice", authorized_document_ids=["doc_1"])
    deleted_count = vector_store.delete_document("doc_1", scope=scope_alice)
    assert deleted_count == 2
    assert vector_store.count() == 1
    assert vector_store.get_document_chunk_count("doc_1") == 0


def test_unauthorized_deletion_rejected(vector_store, sample_embeddings):
    vector_store.add_embeddings(sample_embeddings)

    # Alice attempts to delete Bob's doc_2
    scope_alice = AuthorizedScope(user_id="user_alice", authorized_document_ids=["doc_1"])
    with pytest.raises(AuthorizationScopeError):
        vector_store.delete_document("doc_2", scope=scope_alice)


def test_persistence_and_reload(tmp_path, sample_embeddings):
    store_dir = tmp_path / "persist_test"
    store1 = PersistentVectorStore(persistence_dir=store_dir)
    store1.add_embeddings(sample_embeddings)
    assert store1.count() == 3

    # Load in new instance from same directory
    store2 = PersistentVectorStore(persistence_dir=store_dir)
    assert store2.count() == 3
    assert store2.get_document_chunk_count("doc_1") == 2
    assert store2.get_document_chunk_count("doc_2") == 1
