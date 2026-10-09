"""
Vector store implementation with persistence, metadata filtering, and strict document-scope isolation.
"""

import abc
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
import numpy as np

from ai_engine.config import get_config
from ai_engine.exceptions import (
    AuthorizationScopeError,
    EmbeddingDimensionMismatchError,
    VectorStoreError,
)
from ai_engine.schemas import AuthorizedScope, ChunkEmbedding, TextChunk, VectorQueryResult

logger = logging.getLogger(__name__)


class BaseVectorStore(abc.ABC):
    """Abstract interface for Vector Store backends."""

    @abc.abstractmethod
    def add_embeddings(self, embeddings: List[ChunkEmbedding]) -> int:
        """Add chunks and vector representations into the store."""
        pass

    @abc.abstractmethod
    def search(
        self,
        query_vector: List[float],
        scope: AuthorizedScope,
        top_k: int = 5,
        target_document_ids: Optional[List[str]] = None,
        min_similarity: float = 0.0,
    ) -> List[VectorQueryResult]:
        """Search similar chunks within authorized document scope."""
        pass

    @abc.abstractmethod
    def delete_document(self, document_id: str, scope: Optional[AuthorizedScope] = None) -> int:
        """Delete all indexed chunks and vectors for a document."""
        pass

    @abc.abstractmethod
    def delete_owner(self, owner_id: str) -> int:
        """Delete all documents and vectors belonging to an owner."""
        pass

    @abc.abstractmethod
    def get_document_chunk_count(self, document_id: str) -> int:
        """Return the number of indexed chunks for a document."""
        pass

    @abc.abstractmethod
    def count(self) -> int:
        """Total vectors in store."""
        pass

    @abc.abstractmethod
    def clear(self) -> None:
        """Clear all stored vectors and metadata."""
        pass


class PersistentVectorStore(BaseVectorStore):
    """
    High-performance, zero-external-dependency vector store.
    Features:
    - Cosine similarity with vector normalization
    - Strict authorization and owner boundary filtering
    - Atomic persistence to disk (JSON metadata + NumPy binary matrix)
    - Full CRUD support (insert, query, delete document, delete owner, clear)
    """

    def __init__(self, persistence_dir: Optional[Path] = None):
        config = get_config()
        self.persistence_dir = Path(persistence_dir or config.vector_store_dir)
        self.persistence_dir.mkdir(parents=True, exist_ok=True)

        self._metadata_file = self.persistence_dir / "chunks_metadata.json"
        self._vectors_file = self.persistence_dir / "vectors.npy"

        # In-memory indices
        self._chunks: Dict[str, TextChunk] = {}  # chunk_id -> TextChunk
        self._doc_to_chunk_ids: Dict[str, Set[str]] = {}  # doc_id -> set of chunk_ids
        self._owner_to_chunk_ids: Dict[str, Set[str]] = {}  # owner_id -> set of chunk_ids
        self._chunk_id_order: List[str] = []  # Index in matrix corresponds to chunk_id
        self._matrix: Optional[np.ndarray] = None  # (N, D) float32 matrix

        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Load persisted index from storage if files exist."""
        if self._metadata_file.exists() and self._vectors_file.exists():
            try:
                with open(self._metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self._chunk_id_order = data.get("order", [])
                chunks_raw = data.get("chunks", {})
                self._chunks = {cid: TextChunk(**cdata) for cid, cdata in chunks_raw.items()}

                # Rebuild indexes
                self._doc_to_chunk_ids.clear()
                self._owner_to_chunk_ids.clear()

                for chunk in self._chunks.values():
                    self._doc_to_chunk_ids.setdefault(chunk.document_id, set()).add(chunk.chunk_id)
                    owner = chunk.metadata.get("owner_id", "default_owner")
                    self._owner_to_chunk_ids.setdefault(owner, set()).add(chunk.chunk_id)

                self._matrix = np.load(self._vectors_file)
                logger.info(f"Loaded vector store with {len(self._chunks)} vectors from {self.persistence_dir}")
            except Exception as e:
                logger.error(f"Failed to load persisted vector index: {e}. Starting fresh.")
                self.clear()

    def persist(self) -> None:
        """Persist current vectors and chunk metadata to disk."""
        try:
            data = {
                "order": self._chunk_id_order,
                "chunks": {cid: chunk.model_dump() for cid, chunk in self._chunks.items()},
            }
            # Write metadata atomically
            tmp_meta = self.persistence_dir / "chunks_metadata.json.tmp"
            with open(tmp_meta, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            if tmp_meta.exists():
                os.replace(tmp_meta, self._metadata_file)

            # Write matrix
            if self._matrix is not None and len(self._chunk_id_order) > 0:
                # np.save automatically handles .npy extension
                np.save(str(self._vectors_file), self._matrix)
        except Exception as e:
            logger.error(f"Vector store persistence error: {e}")
            raise VectorStoreError(f"Failed to persist vector store to disk: {str(e)}")

    def add_embeddings(self, embeddings: List[ChunkEmbedding]) -> int:
        """
        Add chunks and vectors into index.
        Idempotent: Replaces any existing chunks with matching IDs.
        """
        if not embeddings:
            return 0

        # Validate vector consistency
        sample_dim = len(embeddings[0].vector)
        for idx, item in enumerate(embeddings):
            if len(item.vector) != sample_dim:
                raise EmbeddingDimensionMismatchError(
                    f"Inconsistent vector dimensions: chunk {item.chunk.chunk_id} has {len(item.vector)}, expected {sample_dim}"
                )

        new_vectors = []
        for item in embeddings:
            chunk = item.chunk
            cid = chunk.chunk_id
            doc_id = chunk.document_id
            owner_id = chunk.metadata.get("owner_id", "default_owner")

            # Remove prior instance if updating
            if cid in self._chunks:
                self._remove_single_chunk(cid)

            self._chunks[cid] = chunk
            self._chunk_id_order.append(cid)
            self._doc_to_chunk_ids.setdefault(doc_id, set()).add(cid)
            self._owner_to_chunk_ids.setdefault(owner_id, set()).add(cid)

            vec = np.array(item.vector, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            new_vectors.append(vec)

        new_matrix = np.vstack(new_vectors)
        if self._matrix is None or self._matrix.size == 0:
            self._matrix = new_matrix
        else:
            self._matrix = np.vstack([self._matrix, new_matrix])

        self.persist()
        return len(embeddings)

    def _remove_single_chunk(self, chunk_id: str) -> None:
        """Internal helper to unregister a single chunk from indexes."""
        if chunk_id not in self._chunks:
            return
        idx = self._chunk_id_order.index(chunk_id)
        del self._chunk_id_order[idx]
        chunk = self._chunks.pop(chunk_id)

        if chunk.document_id in self._doc_to_chunk_ids:
            self._doc_to_chunk_ids[chunk.document_id].discard(chunk_id)
        owner_id = chunk.metadata.get("owner_id", "default_owner")
        if owner_id in self._owner_to_chunk_ids:
            self._owner_to_chunk_ids[owner_id].discard(chunk_id)

        if self._matrix is not None and self._matrix.shape[0] > 0:
            self._matrix = np.delete(self._matrix, idx, axis=0)

    def search(
        self,
        query_vector: List[float],
        scope: AuthorizedScope,
        top_k: int = 5,
        target_document_ids: Optional[List[str]] = None,
        min_similarity: float = 0.0,
    ) -> List[VectorQueryResult]:
        """
        Search for top-k chunks with strict authorization filter and cosine similarity.
        """
        if self._matrix is None or len(self._chunk_id_order) == 0:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        if q_vec.shape[0] != self._matrix.shape[1]:
            raise EmbeddingDimensionMismatchError(
                f"Query vector dimension ({q_vec.shape[0]}) does not match index dimension ({self._matrix.shape[1]})"
            )

        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        # 1. Compute cosine similarity scores via dot product against normalized matrix
        raw_scores = np.dot(self._matrix, q_vec)

        # 2. Filter candidates based on authorization scope and optional target doc IDs
        results: List[VectorQueryResult] = []
        for idx, (cid, score) in enumerate(zip(self._chunk_id_order, raw_scores)):
            chunk = self._chunks[cid]
            doc_id = chunk.document_id

            # Security Authorization check:
            if not scope.can_access_document(doc_id):
                continue

            # Target document filter check:
            if target_document_ids is not None and doc_id not in target_document_ids:
                continue

            # Minimum similarity check:
            float_score = float(score)
            if float_score < min_similarity:
                continue

            results.append(
                VectorQueryResult(
                    chunk=chunk,
                    similarity_score=round(float_score, 4),
                    rank=1,  # Will be assigned after sorting
                )
            )

        # 3. Sort by similarity score descending
        results.sort(key=lambda r: r.similarity_score, reverse=True)

        # Assign ranks
        top_results = results[:top_k]
        for rank_idx, res in enumerate(top_results):
            res.rank = rank_idx + 1

        return top_results

    def delete_document(self, document_id: str, scope: Optional[AuthorizedScope] = None) -> int:
        """
        Delete all chunks associated with a document ID.
        If scope is provided, verifies user authorization before deletion.
        """
        if scope and not scope.can_access_document(document_id):
            raise AuthorizationScopeError(
                f"User '{scope.user_id}' is not authorized to delete document '{document_id}'."
            )

        chunk_ids_to_remove = list(self._doc_to_chunk_ids.get(document_id, set()))
        if not chunk_ids_to_remove:
            return 0

        for cid in chunk_ids_to_remove:
            self._remove_single_chunk(cid)

        if document_id in self._doc_to_chunk_ids:
            del self._doc_to_chunk_ids[document_id]

        self.persist()
        return len(chunk_ids_to_remove)

    def delete_owner(self, owner_id: str) -> int:
        """Delete all documents and chunks owned by an owner/user."""
        chunk_ids_to_remove = list(self._owner_to_chunk_ids.get(owner_id, set()))
        for cid in chunk_ids_to_remove:
            self._remove_single_chunk(cid)
        if owner_id in self._owner_to_chunk_ids:
            del self._owner_to_chunk_ids[owner_id]

        self.persist()
        return len(chunk_ids_to_remove)

    def get_document_chunk_count(self, document_id: str) -> int:
        return len(self._doc_to_chunk_ids.get(document_id, set()))

    def count(self) -> int:
        return len(self._chunks)

    def clear(self) -> None:
        self._chunks.clear()
        self._doc_to_chunk_ids.clear()
        self._owner_to_chunk_ids.clear()
        self._chunk_id_order.clear()
        self._matrix = None
        if self._metadata_file.exists():
            self._metadata_file.unlink()
        if self._vectors_file.exists():
            self._vectors_file.unlink()


# Singleton vector store instance
_global_vector_store: Optional[BaseVectorStore] = None


def get_vector_store() -> BaseVectorStore:
    global _global_vector_store
    if _global_vector_store is None:
        _global_vector_store = PersistentVectorStore()
    return _global_vector_store


def set_vector_store(store: BaseVectorStore) -> None:
    global _global_vector_store
    _global_vector_store = store
