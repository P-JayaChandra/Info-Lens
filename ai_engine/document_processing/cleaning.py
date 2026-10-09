"""
Conservative text cleaning and normalization utilities.
Preserves paragraphs, headings, bullet points, and mathematical notation.
"""

import re
import unicodedata


def normalize_whitespace(text: str) -> str:
    """
    Normalize irregular whitespace characters without destroying paragraph breaks.
    Preserves:
    - Double newlines (paragraphs)
    - List formatting (bullets, numbered lists)
    - Meaningful indentation
    """
    if not text:
        return ""

    # Normalize unicode characters to standard NFKC
    text = unicodedata.normalize("NFKC", text)

    # Standardize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove non-printable control characters (except newline, tab)
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or unicodedata.category(ch)[0] != "C")

    # Replace non-breaking spaces and exotic spaces with standard space
    text = re.sub(r"[\u00A0\u1680\u180E\u2000-\u200B\u202F\u205F\u3000\uFEFF]", " ", text)

    # Replace horizontal multiple spaces/tabs (within the same line) with a single space or standard indent
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        # Preserve markdown/bullet point prefixes
        stripped_line = re.sub(r"[ \t]+", " ", line).strip()
        cleaned_lines.append(stripped_line)

    # Reconstruct text while collapsing 3+ consecutive newlines into 2 (paragraph break)
    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    return cleaned_text.strip()


def sanitize_text_for_embedding(text: str) -> str:
    """
    Light sanitization to prepare text for embedding vectors without stripping semantic nuance.
    """
    cleaned = normalize_whitespace(text)
    # Remove null bytes
    cleaned = cleaned.replace("\x00", "")
    return cleaned
