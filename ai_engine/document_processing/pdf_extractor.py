"""
PDF text and metadata extractor using PyMuPDF (fitz) with optional OCR fallback.
"""

import time
import logging
from pathlib import Path
from typing import List, Optional
import pymupdf

from ai_engine.config import get_config
from ai_engine.document_processing.cleaning import normalize_whitespace
from ai_engine.document_processing.metadata import compute_sha256, validate_file_access
from ai_engine.document_processing.ocr import extract_text_from_pdf_page_pixmap, is_tesseract_available
from ai_engine.exceptions import (
    CorruptedDocumentError,
    EmptyDocumentError,
    OCRError,
)
from ai_engine.schemas import (
    DocumentMetadata,
    ExtractedDocument,
    PageContent,
    SupportedDocumentType,
)

logger = logging.getLogger(__name__)


def extract_pdf(
    file_path: Path | str,
    document_id: str,
    owner_id: str,
    collection_ids: Optional[List[str]] = None,
    enable_ocr_override: Optional[bool] = None,
) -> ExtractedDocument:
    """
    Extract text, page numbers, and metadata from a PDF file.
    
    Args:
        file_path: Path to the PDF file.
        document_id: Unique ID assigned to this document by backend.
        owner_id: User/Tenant owner ID.
        collection_ids: Optional list of collection tags or IDs.
        enable_ocr_override: Force enable/disable OCR for this extraction.
        
    Returns:
        ExtractedDocument containing structured pages and unified text.
    """
    start_time = time.time()
    config = get_config()
    should_ocr = config.ocr_enabled if enable_ocr_override is None else enable_ocr_override

    path_obj, file_size, doc_type = validate_file_access(Path(file_path), config.max_file_size_bytes)
    checksum = compute_sha256(path_obj)

    try:
        doc = pymupdf.open(str(path_obj))
    except Exception as e:
        logger.error(f"Failed to open PDF document {file_path}: {e}")
        raise CorruptedDocumentError(f"Cannot read PDF file: {str(e)}", details={"path": str(file_path)})

    total_pages = len(doc)
    if total_pages == 0:
        doc.close()
        raise EmptyDocumentError(f"PDF document is empty (0 pages): {file_path}")

    pages_content: List[PageContent] = []
    full_text_parts: List[str] = []
    is_scanned_doc = False
    ocr_used = False

    try:
        for page_idx in range(total_pages):
            page_num = page_idx + 1
            page = doc[page_idx]

            # Primary extraction: direct text
            raw_page_text = page.get_text("text")
            cleaned_page_text = normalize_whitespace(raw_page_text)
            is_page_ocr = False

            # Check if page has minimal text and might be scanned
            if len(cleaned_page_text) < config.ocr_min_extracted_chars:
                if should_ocr:
                    if is_tesseract_available():
                        try:
                            logger.info(f"Running OCR on PDF page {page_num} of {path_obj.name}")
                            ocr_text = extract_text_from_pdf_page_pixmap(page, config.ocr_language)
                            cleaned_ocr_text = normalize_whitespace(ocr_text)
                            if len(cleaned_ocr_text) > len(cleaned_page_text):
                                cleaned_page_text = cleaned_ocr_text
                                is_page_ocr = True
                                ocr_used = True
                        except OCRError as ocr_err:
                            logger.warning(f"OCR attempt failed on page {page_num}: {ocr_err}")
                    else:
                        logger.warning(
                            f"Page {page_num} appears scanned, but OCR is unavailable on this system."
                        )
                is_scanned_doc = is_scanned_doc or (len(cleaned_page_text) < config.ocr_min_extracted_chars)

            page_item = PageContent(
                page_number=page_num,
                text=cleaned_page_text,
                character_count=len(cleaned_page_text),
                is_ocr=is_page_ocr,
                metadata={
                    "rotation": page.rect.width,
                    "height": page.rect.height,
                    "width": page.rect.width,
                },
            )
            pages_content.append(page_item)
            if cleaned_page_text:
                full_text_parts.append(cleaned_page_text)

    finally:
        doc.close()

    unified_full_text = "\n\n".join(full_text_parts).strip()

    if not unified_full_text:
        raise EmptyDocumentError(
            f"No extractable text found in PDF document '{path_obj.name}'. "
            + ("OCR was disabled or unable to extract characters." if should_ocr else "OCR is currently disabled.")
        )

    duration_ms = (time.time() - start_time) * 1000.0

    metadata = DocumentMetadata(
        document_id=document_id,
        filename=path_obj.name,
        file_size_bytes=file_size,
        doc_type=SupportedDocumentType.PDF,
        owner_id=owner_id,
        collection_ids=collection_ids or [],
        total_pages=total_pages,
        checksum_sha256=checksum,
    )

    extraction_method = "pymupdf_ocr" if ocr_used else "pymupdf_native"

    return ExtractedDocument(
        document_id=document_id,
        metadata=metadata,
        pages=pages_content,
        full_text=unified_full_text,
        extraction_method=extraction_method,
        is_scanned=is_scanned_doc,
        extraction_time_ms=round(duration_ms, 2),
    )
