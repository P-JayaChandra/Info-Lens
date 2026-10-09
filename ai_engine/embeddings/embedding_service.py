"""
Embedding service abstraction supporting local sentence-transformers, OpenAI, and deterministic mock models.
"""

import abc
import hashlib
import logging
import re
from typing import List, Optional
import numpy as np

from ai_engine.config import AIEngineConfig, EmbeddingProviderType, get_config
from ai_engine.exceptions import (
    EmbeddingDimensionMismatchError,
    EmbeddingError,
)
from ai_engine.schemas import ChunkEmbedding, TextChunk

logger = logging.getLogger(__name__)


class BaseEmbeddingService(abc.ABC):
    """Abstract base class for all embedding providers."""

    @property
    @abc.abstractmethod
    def dimension(self) -> int:
        """Vector dimensionality."""
        pass

    @abc.abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Compute embeddings for a batch of text strings."""
        pass

    def embed_query(self, query: str) -> List[float]:
        """Compute embedding for a single search query."""
        if not query or not query.strip():
            raise EmbeddingError("Search query cannot be empty.")
        embeddings = self.embed_texts([query])
        return embeddings[0]

    def embed_chunks(self, chunks: List[TextChunk]) -> List[ChunkEmbedding]:
        """Compute embeddings for a list of TextChunk models."""
        if not chunks:
            return []
        texts = [chunk.text for chunk in chunks]
        vectors = self.embed_texts(texts)
        if len(vectors) != len(chunks):
            raise EmbeddingError(f"Embedding count mismatch: expected {len(chunks)}, got {len(vectors)}")
        return [
            ChunkEmbedding(chunk=chunk, vector=vector)
            for chunk, vector in zip(chunks, vectors)
        ]

    def _validate_vectors(self, vectors: List[List[float]]) -> None:
        """Ensure vectors are non-empty, finite, and match declared dimension."""
        for idx, vec in enumerate(vectors):
            if len(vec) != self.dimension:
                raise EmbeddingDimensionMismatchError(
                    f"Vector dimension mismatch at index {idx}: expected {self.dimension}, got {len(vec)}"
                )
            arr = np.array(vec, dtype=np.float32)
            if not np.all(np.isfinite(arr)):
                raise EmbeddingError(f"Non-finite values (NaN/Inf) detected in embedding at index {idx}")


class SentenceTransformerEmbeddingService(BaseEmbeddingService):
    """Local embedding service using HuggingFace sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", batch_size: int = 32):
        self._model_name = model_name
        self._batch_size = batch_size
        self._model = None
        self._dimension = None

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer model: {self._model_name}")
                self._model = SentenceTransformer(self._model_name)
                # Test dimension
                sample_emb = self._model.encode("test", normalize_embeddings=True)
                self._dimension = int(sample_emb.shape[0])
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers model '{self._model_name}': {e}")
                raise EmbeddingError(
                    f"Could not load SentenceTransformer '{self._model_name}': {str(e)}",
                    details={"model": self._model_name, "error": str(e)},
                )

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            self._load_model()
        return self._dimension

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        self._load_model()
        try:
            # Batch encode with normalization for cosine similarity via dot product
            embeddings = self._model.encode(
                texts,
                batch_size=self._batch_size,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            vector_list = embeddings.tolist()
            self._validate_vectors(vector_list)
            return vector_list
        except Exception as e:
            if isinstance(e, EmbeddingError):
                raise
            raise EmbeddingError(f"SentenceTransformer embedding error: {str(e)}")


class OpenAIEmbeddingService(BaseEmbeddingService):
    """Remote embedding service using OpenAI API."""

    def __init__(self, model_name: str = "text-embedding-3-small", api_key: Optional[str] = None):
        self._model_name = model_name
        self._api_key = api_key
        self._client = None
        self._dim_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }

    def _get_client(self):
        if self._client is None:
            if not self._api_key:
                raise EmbeddingError(
                    "OpenAI API key is missing. Set INFOLENS_AI_LLM_API_KEY or INFOLENS_AI_EMBEDDING_API_KEY."
                )
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self._api_key)
            except Exception as e:
                raise EmbeddingError(f"Failed to initialize OpenAI client: {e}")
        return self._client

    @property
    def dimension(self) -> int:
        return self._dim_map.get(self._model_name, 1536)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        client = self._get_client()
        try:
            # Replace empty strings to avoid OpenAI API error
            sanitized = [t if t.strip() else " " for t in texts]
            response = client.embeddings.create(input=sanitized, model=self._model_name)
            vectors = [item.embedding for item in response.data]
            self._validate_vectors(vectors)
            return vectors
        except Exception as e:
            raise EmbeddingError(f"OpenAI embedding request failed: {str(e)}")


class MockEmbeddingService(BaseEmbeddingService):
    """
    Deterministic token-feature-hashing embedding generator for fast, isolated unit testing.
    Uses Murmur/MD5 feature hashing with stopword weighting so that text sharing vocabulary
    produces realistic positive cosine similarity without requiring neural weights.
    """

    STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
        "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
        "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
        "further", "had", "has", "have", "having", "he", "her", "here", "hers",
        "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
        "it", "its", "itself", "let's", "me", "more", "most", "my", "myself", "no",
        "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
        "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so",
        "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves",
        "then", "there", "these", "they", "this", "those", "through", "to", "too",
        "under", "until", "up", "very", "was", "we", "were", "what", "when", "where",
        "which", "while", "who", "whom", "why", "with", "would", "you", "your",
        "yours", "yourself", "yourselves"
    }

    def __init__(self, dimension: int = 384):
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        vectors: List[List[float]] = []
        for text in texts:
            vec = np.zeros(self._dimension, dtype=np.float32)
            words = re.findall(r"\w+", text.lower())
            if not words:
                words = ["__empty__"]

            for word in words:
                weight = 0.05 if word in self.STOPWORDS else 2.5
                h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
                idx = h % self._dimension
                sign = 1.0 if ((h // self._dimension) % 2 == 0) else -1.0
                vec[idx] += sign * weight

            # Also add character 3-grams for subword matching
            if len(text) >= 3:
                for i in range(min(len(text) - 2, 40)):
                    tri = text[i : i + 3].lower()
                    h = int(hashlib.md5(tri.encode("utf-8")).hexdigest(), 16)
                    idx = h % self._dimension
                    sign = 0.2 if ((h // self._dimension) % 2 == 0) else -0.2
                    vec[idx] += sign

            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            else:
                vec[0] = 1.0

            vectors.append(vec.tolist())
        self._validate_vectors(vectors)
        return vectors


def create_embedding_service(config: Optional[AIEngineConfig] = None) -> BaseEmbeddingService:
    """Factory function to instantiate the configured embedding service."""
    cfg = config or get_config()

    if cfg.embedding_provider == EmbeddingProviderType.MOCK:
        return MockEmbeddingService(dimension=cfg.embedding_dimension)
    elif cfg.embedding_provider == EmbeddingProviderType.SENTENCE_TRANSFORMERS:
        return SentenceTransformerEmbeddingService(
            model_name=cfg.embedding_model,
            batch_size=cfg.embedding_batch_size,
        )
    elif cfg.embedding_provider == EmbeddingProviderType.OPENAI:
        return OpenAIEmbeddingService(
            model_name=cfg.embedding_model,
            api_key=cfg.embedding_api_key or cfg.llm_api_key,
        )
    else:
        raise EmbeddingError(f"Unsupported embedding provider: {cfg.embedding_provider}")
