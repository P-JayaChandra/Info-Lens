import { apiClient, apiCall } from './client';
import { DEV_DOCUMENTS } from '../utils/fixtures';

// In-memory array for fixture mode additions/edits
let localDocumentsList = [...DEV_DOCUMENTS];

export const documentApi = {
  getDocuments: async () => {
    return apiCall(
      async () => {
        const res = await apiClient.get('/api/documents');
        return res.data;
      },
      () => [...localDocumentsList]
    );
  },

  getDocumentById: async (id) => {
    return apiCall(
      async () => {
        const res = await apiClient.get(`/api/documents/${id}`);
        return res.data;
      },
      () => {
        const doc = localDocumentsList.find((d) => d.id === id);
        if (!doc) throw new Error('Document not found');
        return doc;
      }
    );
  },

  uploadDocument: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    return apiCall(
      async () => {
        const res = await apiClient.post('/api/documents/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            if (onUploadProgress && progressEvent.total) {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              onUploadProgress(percentCompleted);
            }
          },
        });
        return res.data;
      },
      async () => {
        // Simulate progress updates for dev fixtures
        if (onUploadProgress) {
          onUploadProgress(30);
          await new Promise((r) => setTimeout(r, 200));
          onUploadProgress(70);
          await new Promise((r) => setTimeout(r, 200));
          onUploadProgress(100);
        }

        const ext = file.name.split('.').pop().toUpperCase();
        const newDoc = {
          id: `doc_uploaded_${Date.now()}`,
          title: file.name,
          filename: file.name,
          fileType: ext || 'PDF',
          fileSize: file.size,
          uploadDate: new Date().toISOString(),
          status: 'Ready', // Confirmed ready state returned by backend
          pageCount: Math.floor(Math.random() * 15) + 3,
          extractedText: `Extracted content from uploaded file: ${file.name}. InfoLens backend confirmed successful ingestion and vector indexing. You can now execute document-grounded search and question answering.`
        };

        localDocumentsList = [newDoc, ...localDocumentsList];
        return newDoc;
      }
    );
  },

  deleteDocument: async (id) => {
    return apiCall(
      async () => {
        const res = await apiClient.delete(`/api/documents/${id}`);
        return res.data;
      },
      () => {
        localDocumentsList = localDocumentsList.filter((d) => d.id !== id);
        return { success: true, message: 'Document deleted successfully' };
      }
    );
  },

  renameDocument: async (id, newTitle) => {
    return apiCall(
      async () => {
        const res = await apiClient.patch(`/api/documents/${id}`, { title: newTitle });
        return res.data;
      },
      () => {
        localDocumentsList = localDocumentsList.map((d) =>
          d.id === id ? { ...d, title: newTitle, filename: newTitle } : d
        );
        const updated = localDocumentsList.find((d) => d.id === id);
        return updated;
      }
    );
  },

  searchDocumentText: async (id, query) => {
    return apiCall(
      async () => {
        const res = await apiClient.get(`/api/documents/${id}/search`, { params: { q: query } });
        return res.data;
      },
      () => {
        const doc = localDocumentsList.find((d) => d.id === id);
        if (!doc) return [];
        if (!query.trim()) return [];

        const sentences = (doc.extractedText || '').split('.');
        return sentences
          .filter((s) => s.toLowerCase().includes(query.toLowerCase()))
          .map((snippet, idx) => ({
            id: `match_${idx}`,
            page: Math.floor(idx / 3) + 1,
            snippet: snippet.trim() + '.',
          }));
      }
    );
  }
};
