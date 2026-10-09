"""
Unit tests for Intelligent Text Chunker.
"""

import pytest
from ai_engine.chunking.text_chunker import TextChunker
from ai_engine.exceptions import ChunkingError
from ai_engine.schemas import DocumentMetadata, ExtractedDocument, PageContent, SupportedDocumentType


def test_chunking_basic_split():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20, min_chunk_size=10)
    text = (
        "This is paragraph one containing several important statements.\n\n"
        "This is paragraph two detailing additional background concepts.\n\n"
        "This is paragraph three describing practical implementation details."
    )
    doc_metadata = DocumentMetadata(
        document_id="doc_chunk_1",
        filename="test.txt",
        file_size_bytes=len(text),
        doc_type=SupportedDocumentType.TXT,
        owner_id="user_1",
    )
    doc = ExtractedDocument(
        document_id="doc_chunk_1",
        metadata=doc_metadata,
        pages=[PageContent(page_number=1, text=text, character_count=len(text))],
        full_text=text,
        extraction_method="test",
    )

    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert chunk.document_id == "doc_chunk_1"
        assert chunk.page_number == 1
        assert len(chunk.text) >= 10
        assert chunk.chunk_id.startswith("doc_chunk_1_p1_c")


def test_chunking_oversized_paragraph():
    chunker = TextChunker(chunk_size=80, chunk_overlap=15, min_chunk_size=10)
    oversized_sentence = (
        "Sentence one is concise. "
        "Sentence two introduces deep algorithmic explanations and mathematical models. "
        "Sentence three wraps up the discussion."
    )
    chunks = chunker.chunk_page_text(oversized_sentence, document_id="doc_large", page_number=1)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk.text) > 0


def test_chunking_invalid_parameters():
    with pytest.raises(ChunkingError):
        TextChunker(chunk_size=50, chunk_overlap=50)

    with pytest.raises(ChunkingError):
        TextChunker(chunk_size=-10, chunk_overlap=0)


def test_chunking_empty_text():
    chunker = TextChunker(chunk_size=200, chunk_overlap=50)
    chunks = chunker.chunk_page_text("", document_id="doc_empty")
    assert len(chunks) == 0
