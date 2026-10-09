"""
Unified document processing package for InfoLens AI Engine.
Exposes extraction for PDF, DOCX, and TXT files.
"""

from pathlib import Path
from typing import List, Optional

from ai_engine.document_processing.docx_extractor import extract_docx
from ai_engine.document_processing.metadata import validate_file_access
from ai_engine.document_processing.pdf_extractor import extract_pdf
from ai_engine.document_processing.txt_extractor import extract_txt
from ai_engine.exceptions import UnsupportedFormatError
from ai_engine.schemas import ExtractedDocument, SupportedDocumentType


def extract_document(
    file_path: Path | str,
    document_id: str,
    owner_id: str,
    collection_ids: Optional[List[str]] = None,
    enable_ocr_override: Optional[bool] = None,
) -> ExtractedDocument:
    """
    Extract structured text and metadata from any supported document format (PDF, DOCX, TXT).
    
    Args:
        file_path: Path to the target file.
        document_id: System document identifier.
        owner_id: User/owner identifier for isolation.
        collection_ids: Optional collection tags.
        enable_ocr_override: Force enable/disable OCR.
        
    Returns:
        ExtractedDocument with structured pages and metadata.
    """
    path_obj, _, doc_type = validate_file_access(Path(file_path))

    if doc_type == SupportedDocumentType.PDF:
        return extract_pdf(
            file_path=path_obj,
            document_id=document_id,
            owner_id=owner_id,
            collection_ids=collection_ids,
            enable_ocr_override=enable_ocr_override,
        )
    elif doc_type == SupportedDocumentType.DOCX:
        return extract_docx(
            file_path=path_obj,
            document_id=document_id,
            owner_id=owner_id,
            collection_ids=collection_ids,
        )
    elif doc_type == SupportedDocumentType.TXT:
        return extract_txt(
            file_path=path_obj,
            document_id=document_id,
            owner_id=owner_id,
            collection_ids=collection_ids,
        )
    else:
        raise UnsupportedFormatError(f"Unsupported document format: {doc_type}")


__all__ = [
    "extract_document",
    "extract_pdf",
    "extract_docx",
    "extract_txt",
]
