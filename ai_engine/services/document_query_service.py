"""
Document query service providing unified access to semantic retrieval and grounded RAG answers.
"""

from typing import List, Optional

from ai_engine.rag.answer_service import GroundedAnswerService
from ai_engine.retrieval.retriever import DocumentRetriever
from ai_engine.schemas import (
    AuthorizedScope,
    ConversationMessage,
    RAGResponse,
    RetrievalOptions,
    VectorQueryResult,
)


class DocumentQueryService:
    """
    Unified query service for semantic retrieval and conversational RAG answering.
    """

    def __init__(
        self,
        retriever: Optional[DocumentRetriever] = None,
        answer_service: Optional[GroundedAnswerService] = None,
    ):
        self.retriever = retriever or DocumentRetriever()
        self.answer_service = answer_service or GroundedAnswerService(retriever=self.retriever)

    def retrieve_context(
        self,
        question: str,
        scope: AuthorizedScope,
        options: Optional[RetrievalOptions] = None,
    ) -> List[VectorQueryResult]:
        """
        Direct semantic retrieval endpoint for Member 2 integration.
        """
        return self.retriever.retrieve(query=question, scope=scope, options=options)

    def answer_question(
        self,
        question: str,
        scope: AuthorizedScope,
        target_document_ids: Optional[List[str]] = None,
        conversation_history: Optional[List[ConversationMessage]] = None,
        retrieval_options: Optional[RetrievalOptions] = None,
    ) -> RAGResponse:
        """
        End-to-end grounded RAG answering endpoint for Member 2 integration.
        """
        return self.answer_service.answer_question(
            question=question,
            scope=scope,
            target_document_ids=target_document_ids,
            conversation_history=conversation_history,
            retrieval_options=retrieval_options,
        )
