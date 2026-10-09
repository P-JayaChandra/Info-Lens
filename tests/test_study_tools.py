"""
Unit tests for Study Tools: Summarizer, Question Generator, Quiz Evaluator, and Flashcard Generator.
"""

from ai_engine.evaluation.answer_evaluator import AnswerEvaluator
from ai_engine.generation.flashcard_generator import FlashcardGenerator
from ai_engine.generation.question_generator import QuestionGenerator
from ai_engine.generation.summarizer import DocumentSummarizer
from ai_engine.rag.generator import MockLLMGenerator
from ai_engine.schemas import (
    GeneratedQuestion,
    QuestionDifficulty,
    QuestionType,
    QuizSubmission,
    SubmittedAnswer,
    SummaryType,
    TextChunk,
)


def test_summarization():
    summarizer = DocumentSummarizer(llm_generator=MockLLMGenerator())
    chunks = [
        TextChunk(
            chunk_id="c1",
            document_id="doc_sum",
            chunk_index=0,
            text="InfoLens architecture comprises three microservices. It ensures strict data isolation.",
        )
    ]
    summary = summarizer.summarize_chunks(chunks, document_id="doc_sum", summary_type=SummaryType.DETAILED)
    assert summary.document_id == "doc_sum"
    assert len(summary.executive_summary) > 0
    assert summary.word_count > 0


def test_question_generation():
    q_gen = QuestionGenerator(llm_generator=MockLLMGenerator())
    chunks = [
        TextChunk(
            chunk_id="c1",
            document_id="doc_q",
            chunk_index=0,
            text="Vector databases store embeddings and support nearest neighbor queries.",
        )
    ]
    q_set = q_gen.generate_questions(
        chunks=chunks,
        document_id="doc_q",
        question_type=QuestionType.MULTIPLE_CHOICE,
        difficulty=QuestionDifficulty.MEDIUM,
        count=2,
    )
    assert q_set.document_id == "doc_q"
    assert len(q_set.questions) == 2
    assert q_set.questions[0].question_type == QuestionType.MULTIPLE_CHOICE
    assert len(q_set.questions[0].options) >= 2


def test_flashcard_generation():
    fc_gen = FlashcardGenerator(llm_generator=MockLLMGenerator())
    chunks = [
        TextChunk(
            chunk_id="c1",
            document_id="doc_fc",
            chunk_index=0,
            text="Active recall enhances long-term memory retention through testing.",
        )
    ]
    fc_set = fc_gen.generate_flashcards(chunks=chunks, document_id="doc_fc", count=2)
    assert fc_set.document_id == "doc_fc"
    assert len(fc_set.cards) == 2
    assert len(fc_set.cards[0].front) > 0
    assert len(fc_set.cards[0].back) > 0


def test_quiz_deterministic_evaluation():
    evaluator = AnswerEvaluator(llm_generator=MockLLMGenerator())

    q1 = GeneratedQuestion(
        question_id="q1",
        document_id="doc_eval",
        question_type=QuestionType.MULTIPLE_CHOICE,
        difficulty=QuestionDifficulty.EASY,
        question_text="What does RAG stand for?",
        options=["A. Retrieval-Augmented Generation", "B. Random Array Graph", "C. Real-time Audio Gateway"],
        correct_answer="A. Retrieval-Augmented Generation",
        explanation="RAG stands for Retrieval-Augmented Generation.",
    )

    q2 = GeneratedQuestion(
        question_id="q2",
        document_id="doc_eval",
        question_type=QuestionType.TRUE_FALSE,
        difficulty=QuestionDifficulty.EASY,
        question_text="Vector embeddings preserve semantic relationships.",
        options=["True", "False"],
        correct_answer="True",
        explanation="Embeddings map semantic concepts to vector space.",
    )

    # Submission with 1 correct (q1 option A) and 1 incorrect (q2 False)
    submission = QuizSubmission(
        quiz_id="quiz_101",
        document_id="doc_eval",
        answers=[
            SubmittedAnswer(question_id="q1", user_answer="A"),
            SubmittedAnswer(question_id="q2", user_answer="False"),
        ],
    )

    quiz_result = evaluator.evaluate_quiz(questions=[q1, q2], submission=submission)
    assert quiz_result.quiz_id == "quiz_101"
    assert quiz_result.total_score == 1.0
    assert quiz_result.max_possible_score == 2.0
    assert quiz_result.percentage_score == 50.0
    assert quiz_result.passed is False
    assert quiz_result.results[0].is_correct is True
    assert quiz_result.results[1].is_correct is False
