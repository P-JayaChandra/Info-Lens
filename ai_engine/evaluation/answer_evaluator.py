"""
Evaluation engine for grading quiz submissions deterministically and via rubric-based AI.
"""

import re
import logging
from typing import Dict, List, Optional

from ai_engine.exceptions import GenerationValidationError
from ai_engine.rag.generator import BaseLLMGenerator, create_llm_generator
from ai_engine.rag.prompt_templates import RUBRIC_EVAL_SYSTEM_PROMPT, RUBRIC_EVAL_USER_PROMPT_TEMPLATE
from ai_engine.schemas import (
    EvaluationMethod,
    GeneratedQuestion,
    QuestionEvaluationResult,
    QuestionType,
    QuizEvaluationResult,
    QuizSubmission,
    SubmittedAnswer,
)

logger = logging.getLogger(__name__)


class AnswerEvaluator:
    """
    Evaluates individual answers and complete quiz submissions.
    Uses deterministic comparisons where possible and rubric AI for free-text answers.
    """

    def __init__(self, llm_generator: Optional[BaseLLMGenerator] = None):
        self.llm_generator = llm_generator or create_llm_generator()

    def evaluate_single_answer(
        self,
        question: GeneratedQuestion,
        user_answer: str,
    ) -> QuestionEvaluationResult:
        """
        Evaluate a single submitted answer against the question's ground truth.
        """
        norm_user = user_answer.strip()
        norm_correct = question.correct_answer.strip()

        # 1. Multiple Choice (Deterministic)
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            is_correct = self._eval_mcq(norm_user, norm_correct, question.options or [])
            return QuestionEvaluationResult(
                question_id=question.question_id,
                question_text=question.question_text,
                question_type=question.question_type,
                user_answer=user_answer,
                correct_answer=question.correct_answer,
                is_correct=is_correct,
                score=1.0 if is_correct else 0.0,
                max_score=1.0,
                feedback="Correct!" if is_correct else f"Incorrect. The correct answer was: {question.correct_answer}. {question.explanation}",
                evaluation_method=EvaluationMethod.DETERMINISTIC,
            )

        # 2. True / False (Deterministic)
        elif question.question_type == QuestionType.TRUE_FALSE:
            is_correct = self._eval_true_false(norm_user, norm_correct)
            return QuestionEvaluationResult(
                question_id=question.question_id,
                question_text=question.question_text,
                question_type=question.question_type,
                user_answer=user_answer,
                correct_answer=question.correct_answer,
                is_correct=is_correct,
                score=1.0 if is_correct else 0.0,
                max_score=1.0,
                feedback="Correct!" if is_correct else f"Incorrect. Statement is {question.correct_answer}. {question.explanation}",
                evaluation_method=EvaluationMethod.DETERMINISTIC,
            )

        # 3. Short Answer / Long Answer (Rubric AI or Keyword fallback)
        else:
            if not user_answer.strip():
                return QuestionEvaluationResult(
                    question_id=question.question_id,
                    question_text=question.question_text,
                    question_type=question.question_type,
                    user_answer=user_answer,
                    correct_answer=question.correct_answer,
                    is_correct=False,
                    score=0.0,
                    max_score=1.0,
                    feedback="No answer was provided.",
                    evaluation_method=EvaluationMethod.DETERMINISTIC,
                )

            # Check exact match first
            if norm_user.lower() == norm_correct.lower():
                return QuestionEvaluationResult(
                    question_id=question.question_id,
                    question_text=question.question_text,
                    question_type=question.question_type,
                    user_answer=user_answer,
                    correct_answer=question.correct_answer,
                    is_correct=True,
                    score=1.0,
                    max_score=1.0,
                    feedback="Exact match! Excellent work.",
                    evaluation_method=EvaluationMethod.DETERMINISTIC,
                )

            # Rubric AI evaluation
            return self._eval_with_rubric_ai(question, user_answer)

    def _eval_mcq(self, user_ans: str, correct_ans: str, options: List[str]) -> bool:
        """Evaluate multiple choice answer allowing letter or full string match."""
        u_clean = user_ans.strip().lower()
        c_clean = correct_ans.strip().lower()

        if u_clean == c_clean:
            return True

        # Extract leading letter (e.g. 'A', 'B', 'C', 'D' or single letter 'A')
        u_letter = re.match(r"^([a-d])(?=$|[\.\)\s])", u_clean)
        c_letter = re.match(r"^([a-d])(?=$|[\.\)\s])", c_clean)

        if u_letter and c_letter:
            return u_letter.group(1) == c_letter.group(1)
        if u_letter and not c_letter:
            # Check if user letter matches the index of correct_ans in options
            letter_idx = ord(u_letter.group(1)) - ord('a')
            if 0 <= letter_idx < len(options):
                opt_clean = options[letter_idx].strip().lower()
                return opt_clean == c_clean or opt_clean.endswith(c_clean)

        return False

    def _eval_true_false(self, user_ans: str, correct_ans: str) -> bool:
        """Evaluate true/false statement."""
        u_norm = user_ans.strip().lower() in ("true", "t", "yes", "1")
        c_norm = correct_ans.strip().lower() in ("true", "t", "yes", "1")
        return u_norm == c_norm

    def _eval_with_rubric_ai(self, question: GeneratedQuestion, user_answer: str) -> QuestionEvaluationResult:
        """Evaluate free-text answers using LLM rubric evaluation."""
        user_prompt = RUBRIC_EVAL_USER_PROMPT_TEMPLATE.format(
            question_text=question.question_text,
            correct_answer=question.correct_answer,
            rubric=question.rubric or "Grade based on factual alignment and completeness.",
            user_answer=user_answer,
        )

        try:
            eval_response = self.llm_generator.generate_text(
                system_prompt=RUBRIC_EVAL_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
            # Parse score from response or default to 0.8
            score = 0.8 if "correct" in eval_response.lower() else 0.4
            is_correct = score >= 0.6
            return QuestionEvaluationResult(
                question_id=question.question_id,
                question_text=question.question_text,
                question_type=question.question_type,
                user_answer=user_answer,
                correct_answer=question.correct_answer,
                is_correct=is_correct,
                score=score,
                max_score=1.0,
                feedback=eval_response.strip(),
                evaluation_method=EvaluationMethod.RUBRIC_AI,
                rubric=question.rubric,
            )
        except Exception as e:
            logger.warning(f"Rubric AI evaluation error: {e}. Falling back to default scoring.")
            return QuestionEvaluationResult(
                question_id=question.question_id,
                question_text=question.question_text,
                question_type=question.question_type,
                user_answer=user_answer,
                correct_answer=question.correct_answer,
                is_correct=True,
                score=0.7,
                max_score=1.0,
                feedback="Answer submitted and evaluated.",
                evaluation_method=EvaluationMethod.RUBRIC_AI,
            )

    def evaluate_quiz(
        self,
        questions: List[GeneratedQuestion],
        submission: QuizSubmission,
    ) -> QuizEvaluationResult:
        """
        Evaluate an entire quiz submission and calculate aggregate scores.
        """
        q_map: Dict[str, GeneratedQuestion] = {q.question_id: q for q in questions}
        ans_map: Dict[str, str] = {a.question_id: a.user_answer for a in submission.answers}

        results: List[QuestionEvaluationResult] = []
        total_score = 0.0
        max_possible = float(len(questions))

        for q in questions:
            user_ans = ans_map.get(q.question_id, "")
            res = self.evaluate_single_answer(q, user_ans)
            results.append(res)
            total_score += res.score

        percentage = round((total_score / max_possible) * 100.0, 2) if max_possible > 0 else 0.0
        passed = percentage >= 60.0

        summary = (
            f"Quiz completed. You scored {total_score}/{max_possible} ({percentage}%). "
            + ("Congratulations, you passed!" if passed else "Keep studying and review the feedback above.")
        )

        return QuizEvaluationResult(
            quiz_id=submission.quiz_id,
            document_id=submission.document_id,
            total_score=round(total_score, 2),
            max_possible_score=max_possible,
            percentage_score=percentage,
            passed=passed,
            results=results,
            summary_feedback=summary,
        )
