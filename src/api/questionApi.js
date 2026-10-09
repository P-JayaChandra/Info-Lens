import { apiClient, apiCall } from './client';
import { DEV_QUESTIONS, DEV_DOCUMENTS } from '../utils/fixtures';

export const questionApi = {
  generateQuestions: async ({ documentId, questionType, count = 3, difficulty = 'medium' }) => {
    return apiCall(
      async () => {
        const res = await apiClient.post('/api/questions/generate', {
          document_id: documentId,
          question_type: questionType,
          count,
          difficulty,
        });
        return res.data;
      },
      () => {
        const doc = DEV_DOCUMENTS.find((d) => d.id === documentId) || DEV_DOCUMENTS[0];
        
        // Return filtered/generated questions based on parameter request
        let questions = DEV_QUESTIONS;
        if (questionType && questionType !== 'all') {
          const typeMap = {
            'multiple_choice': 'multiple_choice',
            'true_false': 'true_false',
            'short_answer': 'short_answer'
          };
          const matchType = typeMap[questionType];
          if (matchType) {
            questions = questions.filter((q) => q.type === matchType);
          }
        }

        if (questions.length === 0) {
          questions = DEV_QUESTIONS;
        }

        return {
          documentId: doc.id,
          documentTitle: doc.title,
          questionType,
          difficulty,
          questions: questions.slice(0, count)
        };
      }
    );
  }
};
