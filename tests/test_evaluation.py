"""
Unit tests for Retrieval Evaluator benchmarking.
"""

from ai_engine.embeddings.embedding_service import MockEmbeddingService
from ai_engine.evaluation.retrieval_evaluator import RetrievalEvaluator
from ai_engine.retrieval.retriever import DocumentRetriever
from ai_engine.retrieval.vector_store import PersistentVectorStore
from ai_engine.schemas import AuthorizedScope, TextChunk


def test_retrieval_evaluator_metrics(tmp_path):
    store = PersistentVectorStore(persistence_dir=tmp_path / "eval_store")
    embed_svc = MockEmbeddingService(dimension=64)

    chunk1 = TextChunk(
        chunk_id="chunk_a",
        document_id="doc_test",
        chunk_index=0,
        text="Photosynthesis is the process by which green plants transform light energy into chemical energy.",
        metadata={"owner_id": "eval_user"},
    )
    chunk2 = TextChunk(
        chunk_id="chunk_b",
        document_id="doc_test",
        chunk_index=1,
        text="Cellular respiration converts nutrients into ATP within the mitochondria.",
        metadata={"owner_id": "eval_user"},
    )

    store.add_embeddings(embed_svc.embed_chunks([chunk1, chunk2]))
    retriever = DocumentRetriever(vector_store=store, embedding_service=embed_svc)
    evaluator = RetrievalEvaluator(retriever=retriever)

    test_queries = [
        {"query": "How do plants convert sunlight into energy?", "expected_chunk_ids": ["chunk_a"]},
        {"query": "Mitochondria ATP production", "expected_chunk_ids": ["chunk_b"]},
    ]

    scope = AuthorizedScope(user_id="eval_user", authorized_document_ids=["doc_test"])
    metrics = evaluator.evaluate_benchmark(test_queries=test_queries, scope=scope, top_k=2)

    assert "hit_rate" in metrics
    assert "precision_at_k" in metrics
    assert "recall_at_k" in metrics
    assert "mrr" in metrics
    assert metrics["hit_rate"] >= 0.0
