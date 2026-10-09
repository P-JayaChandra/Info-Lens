import { apiClient, apiCall } from './client';
import { DEV_CONVERSATIONS, DEV_DOCUMENTS } from '../utils/fixtures';

let localConversations = [...DEV_CONVERSATIONS];

export const chatApi = {
  getConversations: async () => {
    return apiCall(
      async () => {
        const res = await apiClient.get('/api/chat/conversations');
        return res.data;
      },
      () => [...localConversations]
    );
  },

  getConversationById: async (id) => {
    return apiCall(
      async () => {
        const res = await apiClient.get(`/api/chat/conversations/${id}`);
        return res.data;
      },
      () => {
        const conv = localConversations.find((c) => c.id === id);
        if (!conv) throw new Error('Conversation not found');
        return conv;
      }
    );
  },

  createConversation: async (documentId, title = 'New Research Chat') => {
    return apiCall(
      async () => {
        const res = await apiClient.post('/api/chat/conversations', { document_id: documentId, title });
        return res.data;
      },
      () => {
        const doc = DEV_DOCUMENTS.find((d) => d.id === documentId) || DEV_DOCUMENTS[0];
        const newConv = {
          id: `conv_${Date.now()}`,
          title: title || `Chat on ${doc.title}`,
          documentId: doc.id,
          documentTitle: doc.title,
          updatedAt: new Date().toISOString(),
          messages: []
        };
        localConversations = [newConv, ...localConversations];
        return newConv;
      }
    );
  },

  sendMessage: async (conversationId, text, documentId) => {
    return apiCall(
      async () => {
        const res = await apiClient.post(`/api/chat/conversations/${conversationId}/messages`, {
          message: text,
          document_id: documentId
        });
        return res.data;
      },
      () => {
        const targetConv = localConversations.find((c) => c.id === conversationId);
        const doc = DEV_DOCUMENTS.find((d) => d.id === (documentId || targetConv?.documentId)) || DEV_DOCUMENTS[0];

        const userMsg = {
          id: `msg_user_${Date.now()}`,
          sender: 'user',
          text,
          timestamp: new Date().toISOString()
        };

        const aiResponseText = `Based on our document intelligence analysis of "${doc.title}", the document explicitly states relevant details regarding "${text.slice(0, 40)}...". The passage emphasizes accurate retrieval with grounded citations.`;

        const assistantMsg = {
          id: `msg_ai_${Date.now()}`,
          sender: 'assistant',
          text: aiResponseText,
          timestamp: new Date().toISOString(),
          citations: [
            {
              id: `cit_${Date.now()}`,
              documentId: doc.id,
              documentTitle: doc.title,
              page: Math.floor(Math.random() * (doc.pageCount || 5)) + 1,
              passage: (doc.extractedText || '').slice(0, 160) + '...',
              sourceId: `chunk_${doc.id}_sec1`
            }
          ]
        };

        if (targetConv) {
          targetConv.messages.push(userMsg, assistantMsg);
          targetConv.updatedAt = new Date().toISOString();
        }

        return {
          userMessage: userMsg,
          assistantMessage: assistantMsg
        };
      }
    );
  },

  deleteConversation: async (id) => {
    return apiCall(
      async () => {
        const res = await apiClient.delete(`/api/chat/conversations/${id}`);
        return res.data;
      },
      () => {
        localConversations = localConversations.filter((c) => c.id !== id);
        return { success: true };
      }
    );
  },

  renameConversation: async (id, newTitle) => {
    return apiCall(
      async () => {
        const res = await apiClient.patch(`/api/chat/conversations/${id}`, { title: newTitle });
        return res.data;
      },
      () => {
        localConversations = localConversations.map((c) =>
          c.id === id ? { ...c, title: newTitle } : c
        );
        return localConversations.find((c) => c.id === id);
      }
    );
  }
};
