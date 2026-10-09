import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, CheckCircle2, XCircle, AlertCircle, HelpCircle, Award, RotateCcw } from 'lucide-react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { ConfirmDialog } from '../common/ConfirmDialog';

export function QuizRunner({ quiz, onSubmitQuiz, onRestartQuiz }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [isSubmitModalOpen, setIsSubmitModalOpen] = useState(false);

  if (!quiz || !quiz.questions || quiz.questions.length === 0) {
    return (
      <div className="p-8 text-center bg-white border border-slate-200 rounded-xl text-slate-500">
        No quiz questions available.
      </div>
    );
  }

  const questions = quiz.questions;
  const currentQ = questions[currentIndex];
  const answeredCount = Object.keys(userAnswers).length;
  const totalCount = questions.length;

  const handleSelectOption = (option) => {
    setUserAnswers((prev) => ({ ...prev, [currentQ.id]: option }));
  };

  const handleNext = () => {
    if (currentIndex < totalCount - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      setIsSubmitModalOpen(true);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-xs p-6 text-left space-y-6">
      {/* Quiz Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-100">
        <div>
          <h3 className="text-base font-bold text-slate-900">{quiz.title || 'Interactive Practice Quiz'}</h3>
          <p className="text-xs text-slate-500 mt-0.5">Document: {quiz.documentTitle || 'Selected Material'}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="indigo">
            Question {currentIndex + 1} of {totalCount}
          </Badge>
          <Badge variant="emerald">
            {answeredCount} / {totalCount} Answered
          </Badge>
        </div>
      </div>

      {/* Question Progress Bar */}
      <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-indigo-600 transition-all duration-300 rounded-full"
          style={{ width: `${((currentIndex + 1) / totalCount) * 100}%` }}
        />
      </div>

      {/* Active Question Box */}
      <div className="space-y-4">
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
          <span className="text-xs font-semibold uppercase text-indigo-700 tracking-wider">
            {currentQ.type ? currentQ.type.replace('_', ' ') : 'Multiple Choice'}
          </span>
          <h4 className="text-base font-semibold text-slate-900 mt-1">{currentQ.question}</h4>
        </div>

        {/* Answer Options */}
        {currentQ.options ? (
          <div className="space-y-2.5">
            {currentQ.options.map((opt, idx) => {
              const isSelected = userAnswers[currentQ.id] === opt;
              return (
                <button
                  key={idx}
                  onClick={() => handleSelectOption(opt)}
                  className={`w-full text-left p-3.5 rounded-xl border text-sm transition-all flex items-center justify-between ${
                    isSelected
                      ? 'border-indigo-600 bg-indigo-50/80 text-indigo-950 font-semibold shadow-xs'
                      : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span
                      className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                        isSelected ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 border border-slate-200'
                      }`}
                    >
                      {String.fromCharCode(65 + idx)}
                    </span>
                    <span>{opt}</span>
                  </div>
                  {isSelected && <CheckCircle2 className="w-4 h-4 text-indigo-600 shrink-0" />}
                </button>
              );
            })}
          </div>
        ) : (
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-700">Your Answer</label>
            <textarea
              value={userAnswers[currentQ.id] || ''}
              onChange={(e) => handleSelectOption(e.target.value)}
              placeholder="Type your response here..."
              rows={3}
              className="w-full text-sm p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>
        )}
      </div>

      {/* Navigation & Submit Bar */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-100">
        <Button variant="outline" size="md" onClick={handlePrev} isDisabled={currentIndex === 0} icon={ChevronLeft}>
          Previous
        </Button>
        <div className="flex items-center gap-2">
          {currentIndex === totalCount - 1 ? (
            <Button variant="primary" size="md" onClick={() => setIsSubmitModalOpen(true)}>
              Submit Quiz
            </Button>
          ) : (
            <Button variant="primary" size="md" onClick={handleNext}>
              Next Question
            </Button>
          )}
        </div>
      </div>

      {/* Submit Confirmation Dialog */}
      <ConfirmDialog
        isOpen={isSubmitModalOpen}
        onClose={() => setIsSubmitModalOpen(false)}
        onConfirm={() => {
          setIsSubmitModalOpen(false);
          onSubmitQuiz(userAnswers);
        }}
        title="Submit Quiz Responses"
        message={`You have answered ${answeredCount} of ${totalCount} questions. Submit now for evaluation?`}
        confirmText="Confirm & Submit"
        variant="primary"
      />
    </div>
  );
}
