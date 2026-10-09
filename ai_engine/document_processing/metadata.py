"""
Metadata extraction and document validation utilities.
"""

import hashlib
from pathlib import Path
from typing import Tuple
from ai_engine.exceptions import (
    FileNotFoundOrInaccessibleError,
    UnsupportedFormatError,
)
from ai_engine.schemas import SupportedDocumentType


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file for integrity check and deduplication."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def validate_file_access(file_path: Path, max_size_bytes: int = 50 * 1024 * 1024) -> Tuple[Path, int, SupportedDocumentType]:
    """
    Validates that:
    1. The path exists and is a regular file (not directory or symlink outside bounds).
    2. The file is accessible and within the maximum size limit.
    3. The file extension maps to a supported document type.
    """
    path_obj = Path(file_path).resolve()

    if not path_obj.exists() or not path_obj.is_file():
        raise FileNotFoundOrInaccessibleError(
            f"File not found or inaccessible at path: {file_path}",
            details={"path": str(file_path)}
        )

    file_size = path_obj.stat().st_size
    if file_size > max_size_bytes:
        raise FileNotFoundOrInaccessibleError(
            f"File size ({file_size} bytes) exceeds the maximum allowed limit of {max_size_bytes} bytes",
            details={"file_size": file_size, "max_size": max_size_bytes}
        )

    ext = path_obj.suffix.lower().lstrip(".")
    try:
        doc_type = SupportedDocumentType(ext)
    except ValueError:
        raise UnsupportedFormatError(
            f"Unsupported file format: .{ext}. Supported formats are: {[t.value for t in SupportedDocumentType]}",
            details={"extension": ext}
        )

    return path_obj, file_size, doc_type
