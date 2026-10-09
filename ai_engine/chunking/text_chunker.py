"""
Intelligent paragraph- and sentence-aware text chunking.
Preserves page numbers, character offsets, and source metadata with deterministic IDs.
"""

import re
from typing import List, Optional
from ai_engine.config import get_config
from ai_engine.exceptions import ChunkingError
from ai_engine.schemas import ExtractedDocument, PageContent, TextChunk


class TextChunker:
    """
    Splits document text into overlapping, semantically coherent chunks
    respecting paragraph and sentence boundaries.
    """

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        min_chunk_size: Optional[int] = None,
    ):
        config = get_config()
        self.chunk_size = chunk_size or config.chunk_size
        self.chunk_overlap = chunk_overlap or config.chunk_overlap
        self.min_chunk_size = min_chunk_size or config.chunk_min_size

        if self.chunk_overlap >= self.chunk_size:
            raise ChunkingError(
                f"chunk_overlap ({self.chunk_overlap}) must be strictly less than chunk_size ({self.chunk_size})"
            )
        if self.chunk_size <= 0:
            raise ChunkingError(f"chunk_size ({self.chunk_size}) must be greater than 0")

    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using standard regex sentence boundary rules."""
        sentence_pattern = r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])"
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_page_text(
        self,
        text: str,
        document_id: str,
        page_number: Optional[int] = None,
        start_chunk_index: int = 0,
    ) -> List[TextChunk]:
        """
        Chunk text from a single page or section into coherent text chunks.
        """
        if not text or not text.strip():
            return []

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [text.strip()]

        chunks: List[TextChunk] = []
        current_chunk_parts: List[str] = []
        current_length = 0
        chunk_counter = start_chunk_index

        for para in paragraphs:
            # If paragraph itself is oversized, split into sentences
            if len(para) > self.chunk_size:
                sentences = self.split_sentences(para)
                for sentence in sentences:
                    # If a single sentence is even larger than chunk_size, hard break with overlap
                    if len(sentence) > self.chunk_size:
                        start_idx = 0
                        while start_idx < len(sentence):
                            end_idx = min(start_idx + self.chunk_size, len(sentence))
                            sub_text = sentence[start_idx:end_idx].strip()
                            if len(sub_text) >= self.min_chunk_size:
                                chunk_id = f"{document_id}_p{page_number or 1}_c{chunk_counter}"
                                chunks.append(
                                    TextChunk(
                                        chunk_id=chunk_id,
                                        document_id=document_id,
                                        chunk_index=chunk_counter,
                                        text=sub_text,
                                        page_number=page_number,
                                        start_char=start_idx,
                                        end_char=end_idx,
                                    )
                                )
                                chunk_counter += 1
                            if end_idx >= len(sentence):
                                break
                            start_idx += (self.chunk_size - self.chunk_overlap)
                    else:
                        sent_len = len(sentence)
                        if current_length + sent_len + 1 > self.chunk_size and current_chunk_parts:
                            chunk_text = " ".join(current_chunk_parts).strip()
                            if len(chunk_text) >= self.min_chunk_size:
                                chunk_id = f"{document_id}_p{page_number or 1}_c{chunk_counter}"
                                chunks.append(
                                    TextChunk(
                                        chunk_id=chunk_id,
                                        document_id=document_id,
                                        chunk_index=chunk_counter,
                                        text=chunk_text,
                                        page_number=page_number,
                                    )
                                )
                                chunk_counter += 1

                            # Overlap logic: keep trailing parts up to overlap size
                            overlap_parts = []
                            overlap_len = 0
                            for part in reversed(current_chunk_parts):
                                if overlap_len + len(part) <= self.chunk_overlap:
                                    overlap_parts.insert(0, part)
                                    overlap_len += len(part) + 1
                                else:
                                    break
                            current_chunk_parts = overlap_parts + [sentence]
                            current_length = sum(len(p) for p in current_chunk_parts) + len(current_chunk_parts) - 1
                        else:
                            current_chunk_parts.append(sentence)
                            current_length += sent_len + 1
            else:
                para_len = len(para)
                if current_length + para_len + 2 > self.chunk_size and current_chunk_parts:
                    chunk_text = "\n\n".join(current_chunk_parts).strip()
                    if len(chunk_text) >= self.min_chunk_size:
                        chunk_id = f"{document_id}_p{page_number or 1}_c{chunk_counter}"
                        chunks.append(
                            TextChunk(
                                chunk_id=chunk_id,
                                document_id=document_id,
                                chunk_index=chunk_counter,
                                text=chunk_text,
                                page_number=page_number,
                            )
                        )
                        chunk_counter += 1

                    # Overlap handling for paragraph boundaries
                    overlap_parts = []
                    overlap_len = 0
                    for part in reversed(current_chunk_parts):
                        if overlap_len + len(part) <= self.chunk_overlap:
                            overlap_parts.insert(0, part)
                            overlap_len += len(part) + 2
                        else:
                            break
                    current_chunk_parts = overlap_parts + [para]
                    current_length = sum(len(p) for p in current_chunk_parts) + (len(current_chunk_parts) - 1) * 2
                else:
                    current_chunk_parts.append(para)
                    current_length += para_len + 2

        # Flush remaining buffer
        if current_chunk_parts:
            chunk_text = "\n\n".join(current_chunk_parts).strip()
            if len(chunk_text) >= self.min_chunk_size:
                chunk_id = f"{document_id}_p{page_number or 1}_c{chunk_counter}"
                chunks.append(
                    TextChunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        chunk_index=chunk_counter,
                        text=chunk_text,
                        page_number=page_number,
                    )
                )
            elif not chunks:  # If nothing was added yet (e.g. short document), don't discard
                chunk_id = f"{document_id}_p{page_number or 1}_c{chunk_counter}"
                chunks.append(
                    TextChunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        chunk_index=chunk_counter,
                        text=chunk_text,
                        page_number=page_number,
                    )
                )

        return chunks

    def chunk_document(self, document: ExtractedDocument) -> List[TextChunk]:
        """
        Chunk an entire extracted document across all its pages,
        maintaining continuous chunk indexing and page source lineage.
        """
        all_chunks: List[TextChunk] = []
        global_chunk_idx = 0

        if document.pages:
            for page in document.pages:
                if not page.text.strip():
                    continue
                page_chunks = self.chunk_page_text(
                    text=page.text,
                    document_id=document.document_id,
                    page_number=page.page_number,
                    start_chunk_index=global_chunk_idx,
                )
                for chunk in page_chunks:
                    chunk.metadata = {
                        "filename": document.metadata.filename,
                        "owner_id": document.metadata.owner_id,
                        "collection_ids": document.metadata.collection_ids,
                        "is_ocr": page.is_ocr,
                    }
                    all_chunks.append(chunk)
                    global_chunk_idx += 1
        else:
            # Single stream fallback
            all_chunks = self.chunk_page_text(
                text=document.full_text,
                document_id=document.document_id,
                page_number=1,
                start_chunk_index=0,
            )
            for chunk in all_chunks:
                chunk.metadata = {
                    "filename": document.metadata.filename,
                    "owner_id": document.metadata.owner_id,
                    "collection_ids": document.metadata.collection_ids,
                }

        return all_chunks


def chunk_extracted_document(
    document: ExtractedDocument,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> List[TextChunk]:
    """Convenience helper to chunk an ExtractedDocument."""
    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.chunk_document(document)
