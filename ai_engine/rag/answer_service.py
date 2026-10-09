"""
Grounded Question Answering and Retrieval-Augmented Generation Service.
"""

import time
import logging
from typing import List, Optional

from ai_engine.config import get_config
from ai_engine.rag.citation_builder import CitationBuilder
from ai_engine.rag.generator import BaseLLMGenerator, create_llm_generator
from ai_engine.rag.prompt_templates import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT_TEMPLATE
from ai_engine.retrieval.retriever import DocumentRetriever
from ai_engine.schemas import (
    AuthorizedScope,
    ConversationMessage,
    RAGResponse,
    RetrievalOptions,
    VectorQueryResult,
)

logger = logging.getLogger(__name__)


class GroundedAnswerService:
    """
    Coordinates semantic document retrieval, bounded context assembly,
    LLM prompt generation, and citation validation.
    """

    def __init__(
        self,
        retriever: Optional[DocumentRetriever] = None,
        llm_generator: Optional[BaseLLMGenerator] = None,
    ):
        self.retriever = retriever or DocumentRetriever()
        self.llm_generator = llm_generator or create_llm_generator()

    def answer_question(
        self,
        question: str,
        scope: AuthorizedScope,
        target_document_ids: Optional[List[str]] = None,
        conversation_history: Optional[List[ConversationMessage]] = None,
        retrieval_options: Optional[RetrievalOptions] = None,
    ) -> RAGResponse:
        """
        Produce a grounded answer with validated source citations for a user query.
        """
        start_time = time.time()
        config = get_config()

        opts = retrieval_options or RetrievalOptions(
            top_k=config.retrieval_top_k,
            similarity_threshold=config.retrieval_similarity_threshold,
            target_document_ids=target_document_ids,
            enable_reranking=config.enable_bm25_reranking,
        )

        # 1. Retrieve candidate chunks
        candidates: List[VectorQueryResult] = self.retriever.retrieve(
            query=question,
            scope=scope,
            options=opts,
        )

        # 2. Check for empty retrieval results
        if not candidates:
            duration_ms = (time.time() - start_time) * 1000.0
            return RAGResponse(
                query=question,
                answer="Based on the provided documents, there is insufficient evidence to answer this question.",
                citations=[],
                insufficient_evidence=True,
                retrieval_status="no_matching_evidence",
                model_name=self.llm_generator.model_name,
                confidence_score=0.0,
                processing_time_ms=round(duration_ms, 2),
                diagnostics={"retrieved_count": 0},
            )

        # 3. Assemble bounded context
        context_parts = []
        current_chars = 0
        used_candidates: List[VectorQueryResult] = []

        for idx, cand in enumerate(candidates):
            chunk = cand.chunk
            passage_str = f"[{idx}] (Document: {chunk.document_id}, Page: {chunk.page_number or 'N/A'})\n{chunk.text}\n"
            if current_chars + len(passage_str) > config.max_context_budget_characters:
                break
            context_parts.append(passage_str)
            used_candidates.append(cand)
            current_chars += len(passage_str)

        context_text = "\n".join(context_parts)

        # 4. Format conversation history if provided
        history_str = ""
        if conversation_history:
            # Include only last 4 turns to avoid polluting context
            recent_turns = conversation_history[-4:]
            turns_text = "\n".join(f"{msg.role.capitalize()}: {msg.content}" for msg in recent_turns)
            history_str = f"PRIOR CONVERSATION CONTEXT:\n{turns_text}\n"

        # 5. Build user prompt
        user_prompt = RAG_USER_PROMPT_TEMPLATE.format(
            context_passages=context_text,
            conversation_history=history_str,
            question=question,
        )

        # 6. Call LLM
        try:
            raw_answer = self.llm_generator.generate_text(
                system_prompt=RAG_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            duration_ms = (time.time() - start_time) * 1000.0
            return RAGResponse(
                query=question,
                answer="An error occurred while generating the answer. Please check your LLM provider configuration.",
                citations=[],
                insufficient_evidence=False,
                retrieval_status=f"llm_error: {str(e)}",
                model_name=self.llm_generator.model_name,
                confidence_score=0.0,
                processing_time_ms=round(duration_ms, 2),
            )

        # 7. Check if LLM signaled insufficient evidence
        is_insufficient = (
            "insufficient evidence" in raw_answer.lower()
            or "not enough information" in raw_answer.lower()
            or "cannot find" in raw_answer.lower()
        )

        # 8. Extract and validate citations
        cleaned_answer, citations = CitationBuilder.extract_and_validate_citations(
            answer_text=raw_answer,
            retrieved_candidates=used_candidates if not is_insufficient else [],
        )

        duration_ms = (time.time() - start_time) * 1000.0

        # Compute confidence score from top candidate
        top_similarity = used_candidates[0].similarity_score if used_candidates else 0.0
        confidence = 0.0 if is_insufficient else min(1.0, round(top_similarity + 0.1, 2))

        return RAGResponse(
            query=question,
            answer=cleaned_answer,
            citations=citations,
            insufficient_evidence=is_insufficient,
            retrieval_status="success",
            model_name=self.llm_generator.model_name,
            confidence_score=confidence,
            processing_time_ms=round(duration_ms, 2),
            diagnostics={
                "retrieved_candidates_count": len(candidates),
                "used_candidates_count": len(used_candidates),
                "top_similarity_score": top_similarity,
            },
        )
