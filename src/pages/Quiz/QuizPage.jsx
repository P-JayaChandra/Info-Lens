import React, { useState, useEffect } from 'react';
import { Award, FileText, RefreshCw, CheckCircle2, XCircle, RotateCcw } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { QuizRunner } from '../../components/study/QuizRunner';
import { Skeleton } from '../../components/common/Skeleton';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { useDocuments } from '../../context/DocumentContext';
import { useToast } from '../../context/ToastContext';
import { quizApi } from '../../api/quizApi';

export function QuizPage() {
  const { documents, selectedDocument, selectDocument } = useDocuments();
  const { addToast } = useToast();

  const [quiz, setQuiz] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const activeDoc = selectedDocument || documents[0];

  const handleGenerateQuiz = async () => {
    if (!activeDoc) {
      addToast('Please select a document to create a practice quiz.', 'warning');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const res = await quizApi.generateQuiz(activeDoc.id, 5);
      setQuiz(res);
      addToast(`Practice quiz generated for "${activeDoc.title}".`, 'success');
    } catch (err) {
      setError(err.message || 'Failed to generate quiz.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeDoc) {
      handleGenerateQuiz();
    }
  }, [activeDoc?.id]);

  const handleSubmitQuiz = async (userAnswers) => {
    if (!quiz) return;
    setIsSubmitting(true);
    try {
      const evalRes = await quizApi.submitQuizAnswers(quiz.quizId, userAnswers);
      setResults(evalRes);
      addToast(`Quiz submitted! Score: ${evalRes.score}%`, 'success');
    } catch (err) {
      addToast(err.message || 'Failed to submit quiz answers.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 text-left animate-fade-in max-w-4xl mx-auto">
      {/* Quiz Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <Award className="w-6 h-6 text-indigo-600" />
            Quiz & Practice Mode
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Test knowledge retention with document-grounded evaluation.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-indigo-600 shrink-0" />
            <select
              value={activeDoc?.id || ''}
              onChange={(e) => {
                const doc = documents.find((d) => d.id === e.target.value);
                if (doc) selectDocument(doc);
              }}
              className="text-xs font-semibold text-slate-800 bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:outline-none max-w-xs"
            >
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title}
                </option>
              ))}
            </select>
          </div>

          <Button variant="primary" size="sm" onClick={handleGenerateQuiz} isLoading={loading} icon={RefreshCw}>
            New Quiz
          </Button>
        </div>
      </div>

      {error && <ErrorMessage title="Failed to load quiz" message={error} onRetry={handleGenerateQuiz} />}

      {loading ? (
        <Skeleton variant="card" className="h-96" />
      ) : results ? (
        /* Quiz Results Breakdown Page */
        <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-xs space-y-6">
          <div className="text-center space-y-2 pb-6 border-b border-slate-100">
            <Badge variant={results.score >= 70 ? 'emerald' : 'amber'}>Evaluation Completed</Badge>
            <h3 className="text-3xl font-extrabold text-slate-900">Your Score: {results.score}%</h3>
            <p className="text-xs text-slate-500">
              Answered {results.correctCount} of {results.totalQuestions} questions correctly.
            </p>
          </div>

          {/* Question Breakdown List */}
          <div className="space-y-4">
            <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Answer Key & Review</h4>
            {results.details?.map((item, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-xl border text-xs space-y-2 ${
                  item.isCorrect ? 'bg-emerald-50/60 border-emerald-200' : 'bg-rose-50/60 border-rose-200'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {item.isCorrect ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
                    )}
                    <span className="font-bold text-slate-900">{item.question}</span>
                  </div>
                  <Badge variant={item.isCorrect ? 'emerald' : 'rose'}>
                    {item.isCorrect ? 'Correct' : 'Incorrect'}
                  </Badge>
                </div>

                <div className="pl-6 space-y-1">
                  <p>
                    Your Answer: <strong className="text-slate-900">{item.userAnswer}</strong>
                  </p>
                  {!item.isCorrect && (
                    <p className="text-emerald-800">
                      Correct Answer: <strong>{item.correctAnswer}</strong>
                    </p>
                  )}
                  {item.explanation && <p className="text-slate-600 italic mt-1">Explanation: {item.explanation}</p>}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-center pt-4 border-t border-slate-100">
            <Button variant="primary" size="md" onClick={handleGenerateQuiz} icon={RotateCcw}>
              Retake Practice Quiz
            </Button>
          </div>
        </div>
      ) : (
        <QuizRunner quiz={quiz} onSubmitQuiz={handleSubmitQuiz} onRestartQuiz={handleGenerateQuiz} />
      )}
    </div>
  );
}
