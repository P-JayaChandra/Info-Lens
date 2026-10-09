"""
Retrieval quality evaluator measuring Precision@k, Recall@k, Hit Rate, and MRR.
"""

from typing import Dict, List, Set
from ai_engine.retrieval.retriever import DocumentRetriever
from ai_engine.schemas import AuthorizedScope, RetrievalOptions


class RetrievalEvaluator:
    """
    Evaluates semantic retrieval effectiveness against a golden test set.
    """

    def __init__(self, retriever: DocumentRetriever):
        self.retriever = retriever

    def evaluate_benchmark(
        self,
        test_queries: List[Dict[str, any]],  # List of {"query": str, "expected_chunk_ids": Set[str]}
        scope: AuthorizedScope,
        top_k: int = 5,
    ) -> Dict[str, float]:
        """
        Calculates:
        - Hit Rate @ k: Proportion of queries with at least one expected chunk in top-k.
        - Precision @ k: Average ratio of relevant chunks among top-k.
        - Recall @ k: Average ratio of retrieved relevant chunks over all expected chunks.
        - MRR (Mean Reciprocal Rank): Average reciprocal rank of the first relevant chunk.
        """
        if not test_queries:
            return {"hit_rate": 0.0, "precision": 0.0, "recall": 0.0, "mrr": 0.0}

        total_queries = len(test_queries)
        hits = 0
        total_precision = 0.0
        total_recall = 0.0
        reciprocal_ranks = 0.0

        for item in test_queries:
            query = item["query"]
            expected_ids: Set[str] = set(item["expected_chunk_ids"])

            results = self.retriever.retrieve(
                query=query,
                scope=scope,
                options=RetrievalOptions(top_k=top_k, similarity_threshold=0.0, enable_reranking=False),
            )

            retrieved_ids = [r.chunk.chunk_id for r in results]
            relevant_retrieved = [cid for cid in retrieved_ids if cid in expected_ids]

            # Hit Rate
            if len(relevant_retrieved) > 0:
                hits += 1

            # Precision @ k
            precision = len(relevant_retrieved) / top_k if top_k > 0 else 0.0
            total_precision += precision

            # Recall @ k
            recall = len(relevant_retrieved) / len(expected_ids) if expected_ids else 0.0
            total_recall += recall

            # MRR
            first_rank = 0
            for rank_idx, cid in enumerate(retrieved_ids):
                if cid in expected_ids:
                    first_rank = rank_idx + 1
                    break
            if first_rank > 0:
                reciprocal_ranks += (1.0 / first_rank)

        return {
            "hit_rate": round(hits / total_queries, 4),
            "precision_at_k": round(total_precision / total_queries, 4),
            "recall_at_k": round(total_recall / total_queries, 4),
            "mrr": round(reciprocal_ranks / total_queries, 4),
        }
