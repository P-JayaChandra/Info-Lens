"""
Document summarization service supporting short, detailed, and hierarchical map-reduce summarization.
"""

import time
import logging
from typing import List, Optional

from ai_engine.config import get_config
from ai_engine.exceptions import GenerationValidationError
from ai_engine.rag.citation_builder import CitationBuilder
from ai_engine.rag.generator import BaseLLMGenerator, create_llm_generator
from ai_engine.rag.prompt_templates import SUMMARY_SYSTEM_PROMPT, SUMMARY_USER_PROMPT_TEMPLATE
from ai_engine.retrieval.vector_store import BaseVectorStore, get_vector_store
from ai_engine.schemas import (
    AuthorizedScope,
    Citation,
    SummaryResponse,
    SummarySection,
    SummaryType,
    TextChunk,
)

logger = logging.getLogger(__name__)


class DocumentSummarizer:
    """
    Produces grounded document summaries with configurable granularity.
    Employs a hierarchical map-reduce strategy for lengthy documents.
    """

    def __init__(
        self,
        llm_generator: Optional[BaseLLMGenerator] = None,
        vector_store: Optional[BaseVectorStore] = None,
    ):
        self.llm_generator = llm_generator or create_llm_generator()
        self.vector_store = vector_store or get_vector_store()

    def summarize_chunks(
        self,
        chunks: List[TextChunk],
        document_id: str,
        summary_type: SummaryType = SummaryType.DETAILED,
    ) -> SummaryResponse:
        """
        Generate a summary from a list of document chunks.
        """
        start_time = time.time()
        config = get_config()

        if not chunks:
            return SummaryResponse(
                document_id=document_id,
                summary_type=summary_type,
                executive_summary="The document contains no text content to summarize.",
                sections=[],
                key_takeaways=[],
                citations=[],
                word_count=0,
                processing_time_ms=0.0,
            )

        # 1. Check if total text exceeds single context budget
        total_text = "\n\n".join(c.text for c in chunks)

        if len(total_text) > config.max_context_budget_characters:
            # Map-Reduce: Summarize in blocks of ~6000 chars
            logger.info(f"Document text is large ({len(total_text)} chars); applying hierarchical map-reduce.")
            intermediate_summaries = []
            block_size = 6000
            start = 0
            while start < len(total_text):
                block = total_text[start : start + block_size]
                sub_prompt = f"Summarize the key points of this section concisely:\n\n{block}"
                sub_summary = self.llm_generator.generate_text(
                    system_prompt=SUMMARY_SYSTEM_PROMPT,
                    user_prompt=sub_prompt,
                )
                intermediate_summaries.append(sub_summary)
                start += block_size

            condensed_text = "\n\n".join(intermediate_summaries)
        else:
            condensed_text = total_text

        # 2. Final synthesis prompt
        user_prompt = SUMMARY_USER_PROMPT_TEMPLATE.format(
            document_text=condensed_text,
            summary_type=summary_type.value,
        )

        try:
            summary_obj = self.llm_generator.generate_structured(
                system_prompt=SUMMARY_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=SummaryResponse,
            )
            # Ensure document_id is attached
            summary_obj.document_id = document_id
            summary_obj.summary_type = summary_type
            summary_obj.word_count = len(summary_obj.executive_summary.split())
            summary_obj.processing_time_ms = round((time.time() - start_time) * 1000.0, 2)
            return summary_obj
        except Exception as e:
            logger.warning(f"Structured summarization returned error: {e}. Falling back to text generation.")
            # Fallback text generation
            raw_text = self.llm_generator.generate_text(
                system_prompt=SUMMARY_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
            duration_ms = (time.time() - start_time) * 1000.0
            return SummaryResponse(
                document_id=document_id,
                summary_type=summary_type,
                executive_summary=raw_text,
                sections=[],
                key_takeaways=[],
                citations=[],
                word_count=len(raw_text.split()),
                processing_time_ms=round(duration_ms, 2),
            )
