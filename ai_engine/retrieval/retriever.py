"""
Semantic and hybrid document retriever with authorization scopes.
"""

import logging
from typing import List, Optional
from rank_bm25 import BM25Okapi

from ai_engine.config import get_config
from ai_engine.embeddings.embedding_service import BaseEmbeddingService, create_embedding_service
from ai_engine.exceptions import EmptyRetrievalResultError, RetrievalError
from ai_engine.retrieval.vector_store import BaseVectorStore, get_vector_store
from ai_engine.schemas import AuthorizedScope, RetrievalOptions, VectorQueryResult

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """
    Coordinates semantic vector retrieval and BM25 lexical reranking
    strictly confined to authorized user scopes.
    """

    def __init__(
        self,
        vector_store: Optional[BaseVectorStore] = None,
        embedding_service: Optional[BaseEmbeddingService] = None,
    ):
        self.vector_store = vector_store or get_vector_store()
        self.embedding_service = embedding_service or create_embedding_service()

    def retrieve(
        self,
        query: str,
        scope: AuthorizedScope,
        options: Optional[RetrievalOptions] = None,
    ) -> List[VectorQueryResult]:
        """
        Execute semantic retrieval for a user question within authorized document boundaries.
        
        Args:
            query: The user's query string.
            scope: Verified authorization boundary for the caller.
            options: Optional retrieval parameters (top_k, threshold, target docs, reranking).
            
        Returns:
            List of VectorQueryResult containing relevant TextChunks and scores.
        """
        if not query or not query.strip():
            raise RetrievalError("Search query cannot be empty.")

        config = get_config()
        opts = options or RetrievalOptions(
            top_k=config.retrieval_top_k,
            similarity_threshold=config.retrieval_similarity_threshold,
            enable_reranking=config.enable_bm25_reranking,
        )

        try:
            # 1. Embed query
            query_vector = self.embedding_service.embed_query(query.strip())

            # 2. Retrieve initial candidates (retrieve 2x top_k if reranking is enabled)
            initial_k = opts.top_k * 2 if opts.enable_reranking else opts.top_k
            candidates = self.vector_store.search(
                query_vector=query_vector,
                scope=scope,
                top_k=initial_k,
                target_document_ids=opts.target_document_ids,
                min_similarity=opts.similarity_threshold,
            )

            if not candidates:
                logger.info(f"No matching chunks found for query within authorized scope.")
                return []

            # 3. Optional BM25 hybrid reranking
            if opts.enable_reranking and len(candidates) > 1:
                candidates = self._rerank_with_bm25(query, candidates, top_k=opts.top_k)
            else:
                candidates = candidates[: opts.top_k]

            # Reassign ranks
            for idx, item in enumerate(candidates):
                item.rank = idx + 1

            return candidates

        except Exception as e:
            if isinstance(e, (RetrievalError, EmptyRetrievalResultError)):
                raise
            logger.error(f"Retrieval failed: {e}")
            raise RetrievalError(f"Retrieval operation failed: {str(e)}")

    def _rerank_with_bm25(
        self, query: str, candidates: List[VectorQueryResult], top_k: int
    ) -> List[VectorQueryResult]:
        """
        Rerank retrieved candidates combining normalized dense vector score (70%)
        and BM25 lexical matching score (30%).
        """
        try:
            tokenized_corpus = [c.chunk.text.lower().split() for c in candidates]
            tokenized_query = query.lower().split()

            bm25 = BM25Okapi(tokenized_corpus)
            bm25_scores = bm25.get_scores(tokenized_query)

            max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
            norm_bm25 = [s / max_bm25 for s in bm25_scores]

            for item, bm25_norm in zip(candidates, norm_bm25):
                dense_score = item.similarity_score
                # Hybrid fusion score
                hybrid_score = 0.7 * dense_score + 0.3 * bm25_norm
                item.similarity_score = round(hybrid_score, 4)

            candidates.sort(key=lambda x: x.similarity_score, reverse=True)
            return candidates[:top_k]
        except Exception as e:
            logger.warning(f"BM25 reranking encountered an issue: {e}. Falling back to dense ranking.")
            return candidates[:top_k]
