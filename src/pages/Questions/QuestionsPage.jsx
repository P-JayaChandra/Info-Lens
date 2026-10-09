import React, { useState, useEffect } from 'react';
import { HelpCircle, FileText, Sparkles, Copy, Check, Download, RefreshCw, Eye, EyeOff } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Skeleton } from '../../components/common/Skeleton';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { useDocuments } from '../../context/DocumentContext';
import { useToast } from '../../context/ToastContext';
import { questionApi } from '../../api/questionApi';

export function QuestionsPage() {
  const { documents, selectedDocument, selectDocument } = useDocuments();
  const { addToast } = useToast();

  const [questionType, setQuestionType] = useState('multiple_choice');
  const [count, setCount] = useState(3);
  const [difficulty, setDifficulty] = useState('medium');
  const [showAnswerKeys, setShowAnswerKeys] = useState(false);

  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const activeDoc = selectedDocument || documents[0];

  const handleGenerateQuestions = async () => {
    if (!activeDoc) {
      addToast('Please select a document first.', 'warning');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await questionApi.generateQuestions({
        documentId: activeDoc.id,
        questionType,
        count,
        difficulty,
      });
      setQuestions(res.questions || []);
      addToast(`Generated ${res.questions?.length || 0} study questions.`, 'success');
    } catch (err) {
      setError(err.message || 'Failed to generate study questions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeDoc) {
      handleGenerateQuestions();
    }
  }, [activeDoc?.id, questionType, count, difficulty]);

  const handleCopy = () => {
    if (questions.length === 0) return;
    const text = questions
      .map((q, idx) => {
        let str = `Q${idx + 1}: ${q.question}\n`;
        if (q.options) str += q.options.map((o, i) => `  ${String.fromCharCode(65 + i)}) ${o}`).join('\n') + '\n';
        if (showAnswerKeys) str += `Answer: ${q.correctAnswer}\nExplanation: ${q.explanation}\n`;
        return str;
      })
      .join('\n');

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    addToast('Questions copied to clipboard.', 'info');
  };

  return (
    <div className="space-y-6 text-left animate-fade-in max-w-5xl mx-auto">
      {/* Top Header & Generator Controls Bar */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              <HelpCircle className="w-6 h-6 text-indigo-600" />
              Automated Study Question Generator
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Create customized practice problem sets directly from document text.
            </p>
          </div>

          <Button variant="primary" size="sm" onClick={handleGenerateQuestions} isLoading={loading} icon={RefreshCw}>
            Generate Questions
          </Button>
        </div>

        {/* Form Controls Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-3 border-t border-slate-100">
          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-slate-600 block mb-1">
              Select Document
            </label>
            <select
              value={activeDoc?.id || ''}
              onChange={(e) => {
                const doc = documents.find((d) => d.id === e.target.value);
                if (doc) selectDocument(doc);
              }}
              className="w-full text-xs font-semibold text-slate-800 bg-slate-50 border border-slate-300 rounded-lg p-2 focus:ring-1 focus:ring-indigo-500"
            >
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-slate-600 block mb-1">
              Question Type
            </label>
            <select
              value={questionType}
              onChange={(e) => setQuestionType(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2 focus:ring-1 focus:ring-indigo-500"
            >
              <option value="multiple_choice">Multiple Choice</option>
              <option value="true_false">True / False</option>
              <option value="short_answer">Short Answer</option>
            </select>
          </div>

          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-slate-600 block mb-1">
              Question Count
            </label>
            <select
              value={count}
              onChange={(e) => setCount(parseInt(e.target.value, 10))}
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2 focus:ring-1 focus:ring-indigo-500"
            >
              <option value={3}>3 Questions</option>
              <option value={5}>5 Questions</option>
              <option value={10}>10 Questions</option>
            </select>
          </div>

          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-slate-600 block mb-1">
              Difficulty Level
            </label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2 focus:ring-1 focus:ring-indigo-500"
            >
              <option value="easy">Easy (Definitions)</option>
              <option value="medium">Medium (Application)</option>
              <option value="hard">Hard (Synthesis)</option>
            </select>
          </div>
        </div>
      </div>

      {error && <ErrorMessage title="Failed to generate questions" message={error} onRetry={handleGenerateQuestions} />}

      {/* Generated Questions List Container */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <Badge variant="indigo">Generated Set ({questions.length})</Badge>
            <span className="text-xs text-slate-500 font-medium">Source: {activeDoc?.title}</span>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAnswerKeys(!showAnswerKeys)}
              icon={showAnswerKeys ? EyeOff : Eye}
            >
              {showAnswerKeys ? 'Hide Answer Keys' : 'Show Answer Keys'}
            </Button>
            <Button variant="outline" size="sm" onClick={handleCopy} icon={copied ? Check : Copy}>
              {copied ? 'Copied' : 'Copy Questions'}
            </Button>
          </div>
        </div>

        {loading ? (
          <div className="space-y-4">
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
          </div>
        ) : questions.length === 0 ? (
          <div className="text-center p-8 text-slate-500 text-sm">
            Select parameters above to generate document study questions.
          </div>
        ) : (
          <div className="space-y-4">
            {questions.map((q, idx) => (
              <div key={q.id || idx} className="p-5 border border-slate-200 rounded-xl bg-slate-50/50 space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-full bg-indigo-600 text-white font-bold text-xs flex items-center justify-center">
                      {idx + 1}
                    </span>
                    <h4 className="text-sm font-semibold text-slate-900">{q.question}</h4>
                  </div>
                  <Badge variant="blue">{q.type ? q.type.replace('_', ' ') : 'Question'}</Badge>
                </div>

                {/* Options display for multiple choice */}
                {q.options && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pl-8">
                    {q.options.map((opt, i) => (
                      <div
                        key={i}
                        className={`p-2.5 rounded-lg border text-xs text-slate-800 ${
                          showAnswerKeys && opt === q.correctAnswer
                            ? 'bg-emerald-50 border-emerald-300 font-semibold text-emerald-950'
                            : 'bg-white border-slate-200'
                        }`}
                      >
                        <strong className="text-slate-500 mr-1.5">{String.fromCharCode(65 + i)}.</strong> {opt}
                      </div>
                    ))}
                  </div>
                )}

                {/* Answer Key & Explanation drawer */}
                {showAnswerKeys && (
                  <div className="mt-3 p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-900 space-y-1">
                    <p className="font-bold">Correct Answer: {q.correctAnswer}</p>
                    <p className="leading-relaxed text-emerald-800">Explanation: {q.explanation}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
