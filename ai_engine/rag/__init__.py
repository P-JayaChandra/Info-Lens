"""
RAG and Grounded Question Answering package for InfoLens AI Engine.
"""

from ai_engine.rag.answer_service import GroundedAnswerService
from ai_engine.rag.citation_builder import CitationBuilder
from ai_engine.rag.generator import (
    BaseLLMGenerator,
    MockLLMGenerator,
    OpenAILLMGenerator,
    create_llm_generator,
)
from ai_engine.rag.prompt_templates import (
    RAG_SYSTEM_PROMPT,
    RAG_USER_PROMPT_TEMPLATE,
)

__all__ = [
    "GroundedAnswerService",
    "CitationBuilder",
    "BaseLLMGenerator",
    "MockLLMGenerator",
    "OpenAILLMGenerator",
    "create_llm_generator",
    "RAG_SYSTEM_PROMPT",
    "RAG_USER_PROMPT_TEMPLATE",
]
