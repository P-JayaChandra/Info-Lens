"""
Document indexing service managing end-to-end extraction, chunking, embedding, and vector indexing.
Provides explicit processing state transitions and idempotent index updates.
"""

import time
import logging
from pathlib import Path
from typing import Callable, List, Optional

from ai_engine.chunking.text_chunker import TextChunker
from ai_engine.document_processing import extract_document
from ai_engine.embeddings.embedding_service import BaseEmbeddingService, create_embedding_service
from ai_engine.exceptions import AIEngineError
from ai_engine.retrieval.vector_store import BaseVectorStore, get_vector_store
from ai_engine.schemas import (
    AuthorizedScope,
    DocumentIndexingResult,
    ExtractedDocument,
    ProcessingStatus,
    TextChunk,
)

logger = logging.getLogger(__name__)

StatusCallback = Callable[[str, ProcessingStatus, Optional[str]], None]


class DocumentIndexingService:
    """
    Coordinates extraction, chunking, embedding, and persistence for uploaded documents.
    """

    def __init__(
        self,
        vector_store: Optional[BaseVectorStore] = None,
        embedding_service: Optional[BaseEmbeddingService] = None,
        chunker: Optional[TextChunker] = None,
    ):
        self.vector_store = vector_store or get_vector_store()
        self.embedding_service = embedding_service or create_embedding_service()
        self.chunker = chunker or TextChunker()

    def index_document_from_file(
        self,
        file_path: Path | str,
        document_id: str,
        owner_id: str,
        collection_ids: Optional[List[str]] = None,
        status_callback: Optional[StatusCallback] = None,
        enable_ocr_override: Optional[bool] = None,
    ) -> DocumentIndexingResult:
        """
        Process a document from file path and index its vectors into the vector store.
        """
        start_time = time.time()

        def update_status(status: ProcessingStatus, err: Optional[str] = None):
            if status_callback:
                try:
                    status_callback(document_id, status, err)
                except Exception as cb_err:
                    logger.warning(f"Status callback failed: {cb_err}")

        update_status(ProcessingStatus.EXTRACTING)

        try:
            # 1. Extraction
            logger.info(f"Extracting document {document_id} from {file_path}")
            extracted_doc: ExtractedDocument = extract_document(
                file_path=file_path,
                document_id=document_id,
                owner_id=owner_id,
                collection_ids=collection_ids,
                enable_ocr_override=enable_ocr_override,
            )

            # 2. Chunking
            update_status(ProcessingStatus.CHUNKING)
            logger.info(f"Chunking document {document_id}")
            chunks: List[TextChunk] = self.chunker.chunk_document(extracted_doc)

            if not chunks:
                raise AIEngineError("No chunks were generated from the document content.")

            # 3. Embedding
            update_status(ProcessingStatus.EMBEDDING)
            logger.info(f"Generating embeddings for {len(chunks)} chunks of doc {document_id}")
            embeddings = self.embedding_service.embed_chunks(chunks)

            # 4. Indexing (Idempotent: delete previous vectors first)
            update_status(ProcessingStatus.INDEXING)
            self.vector_store.delete_document(document_id)
            vector_count = self.vector_store.add_embeddings(embeddings)

            # 5. Ready
            update_status(ProcessingStatus.READY)
            duration_ms = (time.time() - start_time) * 1000.0
            logger.info(f"Successfully indexed document {document_id} ({vector_count} vectors, {duration_ms:.1f}ms)")

            return DocumentIndexingResult(
                document_id=document_id,
                status=ProcessingStatus.READY,
                chunk_count=len(chunks),
                vector_count=vector_count,
                duration_ms=round(duration_ms, 2),
            )

        except Exception as e:
            err_msg = str(e)
            logger.error(f"Failed to index document {document_id}: {err_msg}")
            update_status(ProcessingStatus.FAILED, err_msg)
            duration_ms = (time.time() - start_time) * 1000.0
            return DocumentIndexingResult(
                document_id=document_id,
                status=ProcessingStatus.FAILED,
                chunk_count=0,
                vector_count=0,
                duration_ms=round(duration_ms, 2),
                error_message=err_msg,
            )

    def delete_document_index(self, document_id: str, scope: Optional[AuthorizedScope] = None) -> int:
        """
        Delete all indexed vectors and metadata for a document ID.
        """
        return self.vector_store.delete_document(document_id, scope=scope)

    def delete_owner_index(self, owner_id: str) -> int:
        """
        Delete all indexed vectors and metadata for an entire owner.
        """
        return self.vector_store.delete_owner(owner_id)
