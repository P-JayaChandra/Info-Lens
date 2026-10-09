"""
LLM Provider abstraction supporting OpenAI, Gemini, Ollama, and Mock providers.
"""

import abc
import json
import logging
import time
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel

from ai_engine.config import AIEngineConfig, LLMProviderType, get_config
from ai_engine.exceptions import (
    GenerationValidationError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
)

logger = logging.getLogger(__name__)


class BaseLLMGenerator(abc.ABC):
    """Abstract interface for Language Model generation."""

    @abc.abstractmethod
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a text response."""
        pass

    @abc.abstractmethod
    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Type[BaseModel],
        temperature: Optional[float] = None,
    ) -> BaseModel:
        """Generate a validated structured object adhering to a Pydantic schema."""
        pass

    @property
    @abc.abstractmethod
    def model_name(self) -> str:
        """Active model identifier."""
        pass


class OpenAILLMGenerator(BaseLLMGenerator):
    """OpenAI API implementation."""

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        self._model_name = model_name
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not self._api_key:
                raise LLMProviderError("OpenAI API key is missing. Set INFOLENS_AI_LLM_API_KEY in environment.")
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self._api_key,
                    base_url=self._base_url,
                    timeout=self._timeout,
                    max_retries=self._max_retries,
                )
            except Exception as e:
                raise LLMProviderError(f"Failed to initialize OpenAI client: {e}")
        return self._client

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        client = self._get_client()
        config = get_config()
        try:
            response = client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature if temperature is not None else config.llm_temperature,
                max_tokens=max_tokens or config.llm_max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            err_msg = str(e).lower()
            if "rate limit" in err_msg:
                raise LLMRateLimitError(f"OpenAI rate limit exceeded: {str(e)}")
            elif "timeout" in err_msg or "timed out" in err_msg:
                raise LLMTimeoutError(f"OpenAI call timed out: {str(e)}")
            raise LLMProviderError(f"OpenAI generation error: {str(e)}")

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Type[BaseModel],
        temperature: Optional[float] = None,
    ) -> BaseModel:
        client = self._get_client()
        try:
            # Try structured outputs parsing
            try:
                completion = client.beta.chat.completions.parse(
                    model=self._model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format=schema,
                    temperature=temperature or 0.1,
                )
                parsed = completion.choices[0].message.parsed
                if parsed:
                    return parsed
            except Exception:
                pass

            # Fallback to json mode and manual Pydantic validation
            json_system = f"{system_prompt}\n\nYou must return a valid JSON object matching this schema: {json.dumps(schema.model_json_schema())}"
            response = client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": json_system},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=temperature or 0.1,
            )
            content = response.choices[0].message.content
            return schema.model_validate_json(content)
        except Exception as e:
            logger.error(f"Structured generation failed: {e}")
            raise GenerationValidationError(f"Failed to generate valid structured response: {str(e)}")


class MockLLMGenerator(BaseLLMGenerator):
    """
    Mock LLM provider for unit tests, offline development, and evaluation runs
    without requiring external network or paid API tokens.
    """

    def __init__(self, model_name: str = "mock-infolens-engine"):
        self._model_name = model_name

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        if "insufficient" in user_prompt.lower() or "not in context" in user_prompt.lower():
            return "Based on the provided documents, there is insufficient evidence to answer this question."

        # Grounded mock response citing the first chunk if found
        return (
            f"Based on the provided documents, the requested information indicates that "
            f"the documented processes operate according to established protocols and specifications. "
            f"Key principles and details are verified in the context [cite: 0]."
        )

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Type[BaseModel],
        temperature: Optional[float] = None,
    ) -> BaseModel:
        # Dynamically create minimal valid schema instances based on type name
        schema_name = schema.__name__

        if "QuestionSetResponse" in schema_name or "Question" in schema_name:
            data = {
                "document_id": "doc_sample",
                "total_count": 2,
                "questions": [
                    {
                        "question_id": "q1",
                        "document_id": "doc_sample",
                        "question_type": "multiple_choice",
                        "difficulty": "medium",
                        "question_text": "What is the primary topic discussed in the document?",
                        "options": ["A. Overview and core concepts", "B. Unrelated topics", "C. Marketing slogans", "D. Historical anomalies"],
                        "correct_answer": "A. Overview and core concepts",
                        "explanation": "The document primarily focuses on foundational concepts and specifications.",
                        "source_chunk_id": "chunk_0",
                        "page_number": 1,
                    },
                    {
                        "question_id": "q2",
                        "document_id": "doc_sample",
                        "question_type": "true_false",
                        "difficulty": "easy",
                        "question_text": "The document provides guidelines for data processing.",
                        "options": ["True", "False"],
                        "correct_answer": "True",
                        "explanation": "Section 1 explicitly defines data processing guidelines.",
                        "source_chunk_id": "chunk_0",
                        "page_number": 1,
                    }
                ]
            }
            return schema.model_validate(data)

        elif "SummaryResponse" in schema_name:
            data = {
                "document_id": "doc_sample",
                "summary_type": "detailed",
                "executive_summary": "The document presents an in-depth analysis of core concepts, architecture specifications, and implementation guidelines.",
                "sections": [
                    {
                        "title": "Key Concepts",
                        "content": "Detailed overview of fundamental principles and definitions established in the text.",
                        "key_points": ["Principle 1: Data Isolation", "Principle 2: Verified Citations"],
                        "citations": []
                    }
                ],
                "key_takeaways": [
                    "Document establishes clear processing boundaries.",
                    "All generated outputs are verified against evidence."
                ],
                "citations": [],
                "word_count": 45,
                "processing_time_ms": 12.0
            }
            return schema.model_validate(data)

        elif "FlashcardSetResponse" in schema_name or "Flashcard" in schema_name:
            data = {
                "document_id": "doc_sample",
                "total_count": 2,
                "cards": [
                    {
                        "card_id": "fc_1",
                        "document_id": "doc_sample",
                        "front": "What is the core principle of RAG in InfoLens?",
                        "back": "Retrieval-Augmented Generation grounds responses in retrieved document evidence.",
                        "topic": "Architecture",
                        "difficulty": "medium",
                        "explanation": "RAG reduces hallucinations by providing source context.",
                        "source_chunk_id": "chunk_0",
                        "page_number": 1
                    },
                    {
                        "card_id": "fc_2",
                        "document_id": "doc_sample",
                        "front": "How is document security enforced?",
                        "back": "Via strict authorization scopes and user/owner boundaries in vector retrieval.",
                        "topic": "Security",
                        "difficulty": "hard",
                        "explanation": "Queries are filtered by authorized document IDs before retrieval.",
                        "source_chunk_id": "chunk_0",
                        "page_number": 1
                    }
                ]
            }
            return schema.model_validate(data)

        # Fallback default instantiation
        try:
            return schema.model_validate({})
        except Exception:
            raise GenerationValidationError(f"Mock generator could not synthesize default instance for {schema_name}")


def create_llm_generator(config: Optional[AIEngineConfig] = None) -> BaseLLMGenerator:
    """Factory function to build the active LLM generator."""
    cfg = config or get_config()

    if cfg.llm_provider == LLMProviderType.MOCK:
        return MockLLMGenerator(model_name="mock-infolens-engine")
    elif cfg.llm_provider == LLMProviderType.OPENAI:
        return OpenAILLMGenerator(
            model_name=cfg.llm_model,
            api_key=cfg.llm_api_key,
            base_url=cfg.llm_base_url,
            timeout=cfg.llm_timeout_seconds,
            max_retries=cfg.llm_max_retries,
        )
    elif cfg.llm_provider == LLMProviderType.GEMINI:
        # If google-generativeai / gemini is configured, or use OpenAI-compatible Gemini endpoint
        return OpenAILLMGenerator(
            model_name=cfg.llm_model or "gemini-1.5-flash",
            api_key=cfg.llm_api_key,
            base_url=cfg.llm_base_url or "https://generativelanguage.googleapis.com/v1beta/openai/",
            timeout=cfg.llm_timeout_seconds,
            max_retries=cfg.llm_max_retries,
        )
    elif cfg.llm_provider == LLMProviderType.OLLAMA:
        return OpenAILLMGenerator(
            model_name=cfg.llm_model or "llama3.2",
            api_key="ollama",
            base_url=cfg.llm_base_url or "http://localhost:11434/v1",
            timeout=cfg.llm_timeout_seconds,
            max_retries=cfg.llm_max_retries,
        )
    else:
        raise LLMProviderError(f"Unsupported LLM provider: {cfg.llm_provider}")
