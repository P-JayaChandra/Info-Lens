"""
Unit tests for Embedding Services.
"""

import pytest
from ai_engine.embeddings.embedding_service import (
    MockEmbeddingService,
    SentenceTransformerEmbeddingService,
)
from ai_engine.exceptions import EmbeddingDimensionMismatchError, EmbeddingError
from ai_engine.schemas import TextChunk


def test_mock_embedding_service():
    service = MockEmbeddingService(dimension=384)
    assert service.dimension == 384

    texts = ["Quantum computing", "Neural networks architecture"]
    vectors = service.embed_texts(texts)

    assert len(vectors) == 2
    assert len(vectors[0]) == 384
    assert len(vectors[1]) == 384

    # Test single query embedding
    q_vec = service.embed_query("Quantum computing")
    assert len(q_vec) == 384
    # Determinism check: same input yields exact same vector
    assert q_vec == vectors[0]


def test_embedding_chunks():
    service = MockEmbeddingService(dimension=128)
    chunks = [
        TextChunk(chunk_id="c1", document_id="d1", chunk_index=0, text="First chunk text"),
        TextChunk(chunk_id="c2", document_id="d1", chunk_index=1, text="Second chunk text"),
    ]
    embedded_chunks = service.embed_chunks(chunks)
    assert len(embedded_chunks) == 2
    assert embedded_chunks[0].chunk.chunk_id == "c1"
    assert len(embedded_chunks[0].vector) == 128


def test_empty_query_error():
    service = MockEmbeddingService()
    with pytest.raises(EmbeddingError):
        service.embed_query("   ")
