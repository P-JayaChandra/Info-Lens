import { apiClient, apiCall } from './client';
import { DEV_SUMMARIES, DEV_DOCUMENTS } from '../utils/fixtures';

let localSummaries = { ...DEV_SUMMARIES };

export const summaryApi = {
  getSummary: async (documentId) => {
    return apiCall(
      async () => {
        const res = await apiClient.get(`/api/summaries/${documentId}`);
        return res.data;
      },
      () => {
        return localSummaries[documentId] || null;
      }
    );
  },

  generateSummary: async (documentId, lengthMode = 'detailed') => {
    return apiCall(
      async () => {
        const res = await apiClient.post('/api/summaries/generate', {
          document_id: documentId,
          length_mode: lengthMode
        });
        return res.data;
      },
      () => {
        const doc = DEV_DOCUMENTS.find((d) => d.id === documentId) || DEV_DOCUMENTS[0];
        const summary = {
          documentId: doc.id,
          documentTitle: doc.title,
          shortOverview: `Short overview of "${doc.title}": Covers main research problem statement, core experimental methodologies, and primary document metrics.`,
          detailedSummary: `### Document Overview: ${doc.title}

#### Section 1: Research Context & Scope
The document outlines fundamental parameters and analytical structures across ${doc.pageCount || 10} pages. Key concepts focus on verifiable source citation and domain understanding.

#### Section 2: Technical Highlights
- **Primary Method**: Intelligent chunking and dense indexing.
- **Key Findings**: Grounded responses eliminate baseline model hallucinations by up to 92%.
- **Implementation Strategy**: High-density semantic search combined with auditable citations.

#### Section 3: Summary Conclusion
The analyzed document provides actionable technical strategies for document-grounded search and structured academic study.`,
          citations: [
            { page: 1, passage: (doc.extractedText || '').slice(0, 140) + '...' },
            { page: 3, passage: (doc.extractedText || '').slice(140, 280) + '...' }
          ]
        };

        localSummaries[doc.id] = summary;
        return summary;
      }
    );
  }
};
