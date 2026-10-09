"""
Question generation service for creating MCQs, True/False, and free-text practice questions.
"""

import logging
from typing import List, Optional

from ai_engine.config import get_config
from ai_engine.rag.generator import BaseLLMGenerator, create_llm_generator
from ai_engine.rag.prompt_templates import QUESTION_GEN_SYSTEM_PROMPT, QUESTION_GEN_USER_PROMPT_TEMPLATE
from ai_engine.schemas import (
    GeneratedQuestion,
    QuestionDifficulty,
    QuestionSetResponse,
    QuestionType,
    TextChunk,
)

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """
    Generates structured assessments and study questions grounded in document text.
    """

    def __init__(self, llm_generator: Optional[BaseLLMGenerator] = None):
        self.llm_generator = llm_generator or create_llm_generator()

    def generate_questions(
        self,
        chunks: List[TextChunk],
        document_id: str,
        question_type: QuestionType = QuestionType.MULTIPLE_CHOICE,
        difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM,
        count: int = 5,
        topic_focus: Optional[str] = None,
    ) -> QuestionSetResponse:
        """
        Generate a validated set of practice questions grounded in document chunks.
        """
        config = get_config()
        if not chunks:
            return QuestionSetResponse(document_id=document_id, total_count=0, questions=[])

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

        user_prompt = QUESTION_GEN_USER_PROMPT_TEMPLATE.format(
            context_passages=context_text,
            question_type=question_type.value,
            difficulty=difficulty.value,
            count=count,
            topic_focus=topic_focus or "Comprehensive document coverage",
        )

        try:
            result = self.llm_generator.generate_structured(
                system_prompt=QUESTION_GEN_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                schema=QuestionSetResponse,
            )
            result.document_id = document_id
            result.total_count = len(result.questions)
            # Ensure question IDs and document IDs are set
            for idx, q in enumerate(result.questions):
                q.document_id = document_id
                if not q.question_id:
                    q.question_id = f"q_{document_id}_{idx+1}"
                q.question_type = question_type
                q.difficulty = difficulty
            return result
        except Exception as e:
            logger.error(f"Failed to generate structured questions: {e}")
            raise
