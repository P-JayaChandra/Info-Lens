import { apiClient, apiCall } from './client';
import { DEV_QUESTIONS, DEV_DOCUMENTS } from '../utils/fixtures';

export const quizApi = {
  generateQuiz: async (documentId, questionCount = 5) => {
    return apiCall(
      async () => {
        const res = await apiClient.post('/api/quizzes/generate', { document_id: documentId, count: questionCount });
        return res.data;
      },
      () => {
        const doc = DEV_DOCUMENTS.find((d) => d.id === documentId) || DEV_DOCUMENTS[0];
        return {
          quizId: `quiz_${Date.now()}`,
          documentId: doc.id,
          documentTitle: doc.title,
          title: `Practice Quiz: ${doc.title}`,
          totalQuestions: DEV_QUESTIONS.length,
          questions: DEV_QUESTIONS
        };
      }
    );
  },

  submitQuizAnswers: async (quizId, userAnswers) => {
    return apiCall(
      async () => {
        const res = await apiClient.post(`/api/quizzes/${quizId}/submit`, { answers: userAnswers });
        return res.data;
      },
      () => {
        let correctCount = 0;
        const details = DEV_QUESTIONS.map((q) => {
          const userAns = userAnswers[q.id];
          const isCorrect = userAns && userAns.toString().trim().toLowerCase() === q.correctAnswer.toString().trim().toLowerCase();
          if (isCorrect) correctCount++;
          return {
            questionId: q.id,
            question: q.question,
            userAnswer: userAns || 'No response',
            correctAnswer: q.correctAnswer,
            isCorrect,
            explanation: q.explanation
          };
        });

        const scorePercent = Math.round((correctCount / DEV_QUESTIONS.length) * 100);

        return {
          quizId,
          score: scorePercent,
          correctCount,
          totalQuestions: DEV_QUESTIONS.length,
          details
        };
      }
    );
  }
};
