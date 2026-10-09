"""
Plain text (.txt) document extractor with multi-encoding fallback.
"""

import time
import logging
from pathlib import Path
from typing import List, Optional

from ai_engine.config import get_config
from ai_engine.document_processing.cleaning import normalize_whitespace
from ai_engine.document_processing.metadata import compute_sha256, validate_file_access
from ai_engine.exceptions import (
    CorruptedDocumentError,
    EmptyDocumentError,
)
from ai_engine.schemas import (
    DocumentMetadata,
    ExtractedDocument,
    PageContent,
    SupportedDocumentType,
)

logger = logging.getLogger(__name__)


def extract_txt(
    file_path: Path | str,
    document_id: str,
    owner_id: str,
    collection_ids: Optional[List[str]] = None,
) -> ExtractedDocument:
    """
    Extract text from a plain text file (.txt) with robust encoding detection.
    """
    start_time = time.time()
    config = get_config()

    path_obj, file_size, doc_type = validate_file_access(Path(file_path), config.max_file_size_bytes)
    checksum = compute_sha256(path_obj)

    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
    raw_content = None

    with open(path_obj, "rb") as f:
        bytes_data = f.read()

    for enc in encodings:
        try:
            raw_content = bytes_data.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if raw_content is None:
        raise CorruptedDocumentError(
            f"Failed to decode text file '{path_obj.name}' with supported encodings {encodings}."
        )

    cleaned_text = normalize_whitespace(raw_content)

    if not cleaned_text:
        raise EmptyDocumentError(f"Plain text file '{path_obj.name}' is empty or contains only whitespace.")

    # Check for form feed character '\x0c' (traditional page breaks)
    raw_pages = cleaned_text.split("\x0c") if "\x0c" in cleaned_text else []
    pages_content: List[PageContent] = []

    if raw_pages and len(raw_pages) > 1:
        for idx, page_str in enumerate(raw_pages):
            page_clean = normalize_whitespace(page_str)
            if page_clean:
                pages_content.append(
                    PageContent(
                        page_number=idx + 1,
                        text=page_clean,
                        character_count=len(page_clean),
                        is_ocr=False,
                    )
                )
    else:
        # Segment logically by roughly 2500 characters
        chars_per_page = 2500
        paragraphs = cleaned_text.split("\n\n")
        current_page_text = []
        current_length = 0
        page_num = 1

        for para in paragraphs:
            para_len = len(para)
            if current_length + para_len > chars_per_page and current_page_text:
                page_str = "\n\n".join(current_page_text).strip()
                pages_content.append(
                    PageContent(
                        page_number=page_num,
                        text=page_str,
                        character_count=len(page_str),
                        is_ocr=False,
                    )
                )
                page_num += 1
                current_page_text = [para]
                current_length = para_len
            else:
                current_page_text.append(para)
                current_length += para_len + 2

        if current_page_text:
            page_str = "\n\n".join(current_page_text).strip()
            pages_content.append(
                PageContent(
                    page_number=page_num,
                    text=page_str,
                    character_count=len(page_str),
                    is_ocr=False,
                )
            )

    total_pages = max(1, len(pages_content))
    duration_ms = (time.time() - start_time) * 1000.0

    metadata = DocumentMetadata(
        document_id=document_id,
        filename=path_obj.name,
        file_size_bytes=file_size,
        doc_type=SupportedDocumentType.TXT,
        owner_id=owner_id,
        collection_ids=collection_ids or [],
        total_pages=total_pages,
        checksum_sha256=checksum,
    )

    return ExtractedDocument(
        document_id=document_id,
        metadata=metadata,
        pages=pages_content,
        full_text=cleaned_text,
        extraction_method="txt_native",
        is_scanned=False,
        extraction_time_ms=round(duration_ms, 2),
    )
