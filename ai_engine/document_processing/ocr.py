"""
OCR processing module for scanned PDFs and image-based document pages.
Integrates with Tesseract OCR when available and configured.
"""

import io
import logging
from typing import Optional
from PIL import Image
from ai_engine.config import get_config
from ai_engine.exceptions import OCRError

logger = logging.getLogger(__name__)


def is_tesseract_available() -> bool:
    """Check if pytesseract and the tesseract binary are available on the system."""
    try:
        import pytesseract
        config = get_config()
        if config.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd
        version = pytesseract.get_tesseract_version()
        return version is not None
    except Exception as e:
        logger.debug(f"Tesseract is not available: {e}")
        return False


def extract_text_from_image_bytes(image_bytes: bytes, language: Optional[str] = None) -> str:
    """
    Perform OCR on raw image bytes.
    Raises OCRError if OCR is unavailable or fails.
    """
    config = get_config()
    lang = language or config.ocr_language

    if not is_tesseract_available():
        raise OCRError(
            "Tesseract OCR engine is not installed or configured on this system. "
            "Please install Tesseract OCR or set INFOLENS_AI_OCR_ENABLED=false."
        )

    try:
        import pytesseract
        if config.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = config.tesseract_cmd

        image = Image.open(io.BytesIO(image_bytes))
        extracted_text = pytesseract.image_to_string(image, lang=lang)
        return extracted_text.strip()
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise OCRError(f"OCR extraction failed: {str(e)}", details={"error": str(e)})


def extract_text_from_pdf_page_pixmap(page, language: Optional[str] = None) -> str:
    """
    Render a PyMuPDF page as a pixmap and run OCR on the rendered image.
    """
    try:
        # Render page to an image at 2.0x zoom (144 DPI) for crisp OCR
        import pymupdf
        matrix = pymupdf.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=matrix)
        image_bytes = pix.tobytes("png")
        return extract_text_from_image_bytes(image_bytes, language=language)
    except Exception as e:
        if isinstance(e, OCRError):
            raise
        raise OCRError(f"Failed to render PDF page for OCR: {str(e)}")
