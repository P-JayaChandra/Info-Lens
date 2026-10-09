"""
Citation assembly and validation service.
Extracts, verifies, and formats grounded source references from LLM responses and candidate chunks.
"""

import re
import logging
from typing import List, Set, Tuple
from ai_engine.schemas import Citation, VectorQueryResult

logger = logging.getLogger(__name__)


class CitationBuilder:
    """
    Parses citation markers from model output, validates them against retrieved chunks,
    and constructs structured Citation objects for frontend rendering.
    """

    CITATION_PATTERN = r"\[cite:\s*([a-zA-Z0-9_\-]+)\]"

    @classmethod
    def extract_and_validate_citations(
        cls,
        answer_text: str,
        retrieved_candidates: List[VectorQueryResult],
    ) -> Tuple[str, List[Citation]]:
        """
        Extracts citation markers from answer_text, verifies them against retrieved_candidates,
        and constructs validated Citation objects.
        
        Returns:
            Tuple of (cleaned_answer_text, list_of_valid_citations)
        """
        if not retrieved_candidates:
            # Remove any hallucinated citations
            cleaned_text = re.sub(cls.CITATION_PATTERN, "", answer_text).strip()
            return cleaned_text, []

        # Find all cited markers
        matches = re.findall(cls.CITATION_PATTERN, answer_text)
        cited_indices: Set[int] = set()

        for match in matches:
            # Check if match is integer index
            if match.isdigit():
                idx = int(match)
                if 0 <= idx < len(retrieved_candidates):
                    cited_indices.add(idx)
            else:
                # Match by chunk_id
                for idx, cand in enumerate(retrieved_candidates):
                    if cand.chunk.chunk_id == match:
                        cited_indices.add(idx)
                        break

        # If model did not emit citation markers but provided an answer,
        # associate top retrieved candidates if they have high similarity
        if not cited_indices and retrieved_candidates:
            # Attach top candidate if similarity > 0.3
            if retrieved_candidates[0].similarity_score >= 0.3:
                cited_indices.add(0)

        # Build structured citations
        validated_citations: List[Citation] = []
        for idx in sorted(cited_indices):
            if idx < len(retrieved_candidates):
                cand = retrieved_candidates[idx]
                chunk = cand.chunk
                filename = chunk.metadata.get("filename", f"Document {chunk.document_id}")
                
                # Make a clean snippet of the source passage
                snippet = chunk.text.strip()
                if len(snippet) > 220:
                    snippet = snippet[:220].rsplit(" ", 1)[0] + "..."

                citation = Citation(
                    document_id=chunk.document_id,
                    document_title=filename,
                    chunk_id=chunk.chunk_id,
                    page_number=chunk.page_number,
                    snippet=snippet,
                    relevance_score=cand.similarity_score,
                )
                validated_citations.append(citation)

        return answer_text, validated_citations
