import { apiClient, apiCall } from './client';
import { DEV_FLASHCARDS, DEV_DOCUMENTS } from '../utils/fixtures';

let localDecks = {
  'doc_rag_2026': [...DEV_FLASHCARDS],
};

export const flashcardApi = {
  getDeck: async (documentId) => {
    return apiCall(
      async () => {
        const res = await apiClient.get(`/api/flashcards/${documentId}`);
        return res.data;
      },
      () => {
        const doc = DEV_DOCUMENTS.find((d) => d.id === documentId) || DEV_DOCUMENTS[0];
        const cards = localDecks[documentId] || DEV_FLASHCARDS;
        return {
          documentId: doc.id,
          documentTitle: doc.title,
          cards: [...cards]
        };
      }
    );
  },

  updateCardMastery: async (documentId, cardId, knownStatus) => {
    return apiCall(
      async () => {
        const res = await apiClient.post(`/api/flashcards/${documentId}/cards/${cardId}`, { known: knownStatus });
        return res.data;
      },
      () => {
        if (!localDecks[documentId]) {
          localDecks[documentId] = [...DEV_FLASHCARDS];
        }
        localDecks[documentId] = localDecks[documentId].map((card) =>
          card.id === cardId ? { ...card, known: knownStatus } : card
        );
        return { success: true, cardId, knownStatus };
      }
    );
  }
};
