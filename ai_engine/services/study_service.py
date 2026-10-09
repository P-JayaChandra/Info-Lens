"""
Study service providing summarization, question generation, flashcard creation, and quiz evaluation.
"""

from typing import List, Optional

from ai_engine.evaluation.answer_evaluator import AnswerEvaluator
from ai_engine.exceptions import AuthorizationScopeError
from ai_engine.generation.flashcard_generator import FlashcardGenerator
from ai_engine.generation.question_generator import QuestionGenerator
from ai_engine.generation.summarizer import DocumentSummarizer
from ai_engine.retrieval.vector_store import BaseVectorStore, get_vector_store
from ai_engine.schemas import (
    AuthorizedScope,
    FlashcardSetResponse,
    GeneratedQuestion,
    QuestionDifficulty,
    QuestionSetResponse,
    QuestionType,
    QuizEvaluationResult,
    QuizSubmission,
    SummaryResponse,
    SummaryType,
    TextChunk,
)


class StudyService:
    """
    Unified study tools service for Member 2 and Member 1 integration.
    """

    def __init__(
        self,
        vector_store: Optional[BaseVectorStore] = None,
        summarizer: Optional[DocumentSummarizer] = None,
        question_generator: Optional[QuestionGenerator] = None,
        flashcard_generator: Optional[FlashcardGenerator] = None,
        answer_evaluator: Optional[AnswerEvaluator] = None,
    ):
        self.vector_store = vector_store or get_vector_store()
        self.summarizer = summarizer or DocumentSummarizer(vector_store=self.vector_store)
        self.question_generator = question_generator or QuestionGenerator()
        self.flashcard_generator = flashcard_generator or FlashcardGenerator()
        self.answer_evaluator = answer_evaluator or AnswerEvaluator()

    def _get_document_chunks(self, document_id: str, scope: AuthorizedScope) -> List[TextChunk]:
        """Fetch all chunks for a document while checking authorization."""
        if not scope.can_access_document(document_id):
            raise AuthorizationScopeError(
                f"User '{scope.user_id}' is not authorized to access document '{document_id}'."
            )
        # Fetch chunks from vector store
        if hasattr(self.vector_store, "_chunks") and hasattr(self.vector_store, "_doc_to_chunk_ids"):
            chunk_ids = self.vector_store._doc_to_chunk_ids.get(document_id, set())
            return [self.vector_store._chunks[cid] for cid in chunk_ids if cid in self.vector_store._chunks]
        return []

    def summarize_document(
        self,
        document_id: str,
        scope: AuthorizedScope,
        summary_type: SummaryType = SummaryType.DETAILED,
    ) -> SummaryResponse:
        """
        Summarize an authorized document.
        """
        chunks = self._get_document_chunks(document_id, scope)
        return self.summarizer.summarize_chunks(
            chunks=chunks,
            document_id=document_id,
            summary_type=summary_type,
        )

    def generate_questions(
        self,
        document_id: str,
        scope: AuthorizedScope,
        question_type: QuestionType = QuestionType.MULTIPLE_CHOICE,
        difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM,
        count: int = 5,
        topic_focus: Optional[str] = None,
    ) -> QuestionSetResponse:
        """
        Generate study or quiz questions grounded in an authorized document.
        """
        chunks = self._get_document_chunks(document_id, scope)
        return self.question_generator.generate_questions(
            chunks=chunks,
            document_id=document_id,
            question_type=question_type,
            difficulty=difficulty,
            count=count,
            topic_focus=topic_focus,
        )

    def generate_flashcards(
        self,
        document_id: str,
        scope: AuthorizedScope,
        count: int = 10,
        topic_focus: Optional[str] = None,
    ) -> FlashcardSetResponse:
        """
        Generate active recall flashcards from an authorized document.
        """
        chunks = self._get_document_chunks(document_id, scope)
        return self.flashcard_generator.generate_flashcards(
            chunks=chunks,
            document_id=document_id,
            count=count,
            topic_focus=topic_focus,
        )

    def evaluate_quiz(
        self,
        questions: List[GeneratedQuestion],
        submission: QuizSubmission,
    ) -> QuizEvaluationResult:
        """
        Evaluate a student's quiz submission.
        """
        return self.answer_evaluator.evaluate_quiz(
            questions=questions,
            submission=submission,
        )
