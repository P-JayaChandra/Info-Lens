"""
Flashcard generation service for active recall study.
"""

import logging
from typing import List, Optional

from ai_engine.config import get_config
from ai_engine.rag.generator import BaseLLMGenerator, create_llm_generator
from ai_engine.rag.prompt_templates import FLASHCARD_SYSTEM_PROMPT, FLASHCARD_USER_PROMPT_TEMPLATE
from ai_engine.schemas import (
    Flashcard,
    FlashcardSetResponse,
    QuestionDifficulty,
    TextChunk,
)

logger = logging.getLogger(__name__)


class FlashcardGenerator:
    """
    Generates study flashcard decks grounded in document content.
    """

    def __init__(self, llm_generator: Optional[BaseLLMGenerator] = None):
        self.llm_generator = llm_generator or create_llm_generator()

    def generate_flashcards(
        self,
        chunks: List[TextChunk],
        document_id: str,
        count: int = 10,
        topic_focus: Optional[str] = None,
    ) -> FlashcardSetResponse:
        """
        Generate active-recall flashcards from document chunks.
        """
        config = get_config()
        if not chunks:
            return FlashcardSetResponse(document_id=document_id, total_count=0, cards=[])

        # Bounded context assembly
        context_parts = []
        current_len = 0
        for idx, chunk in enumerate(chunks):
            passage = f"[{idx}] (Page {chunk.page_number or 'N/A'})\n{chunk.text}\n"
            if current_len + len(passage) > config.max_context_budget_characters:
                break
            context_parts.append(passage)
            current_len += len(passage)

        context_text = "\n".join(context_parts)

        user_prompt = FLASHCARD_USER_PROMPT_TEMPLATE.format(
            context_passages=context_text,
            count=count,
            topic_focus=topic_focus or "Core concepts and definitions",
        )

        try:
            result = self.llm_generator.generate_structured(
                system_prompt=FLASHCARD_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=FlashcardSetResponse,
            )
            result.document_id = document_id
            result.total_count = len(result.cards)
            for idx, card in enumerate(result.cards):
                card.document_id = document_id
                if not card.card_id:
                    card.card_id = f"fc_{document_id}_{idx+1}"
            return result
        except Exception as e:
            logger.error(f"Failed to generate flashcards: {e}")
            raise
