import React, { useState, useRef, useEffect } from 'react';
import { Send, FileText, Loader2 } from 'lucide-react';
import { Button } from '../common/Button';
import { useDocuments } from '../../context/DocumentContext';

export function ChatInput({ onSendMessage, isLoading, isDisabled }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);
  const { selectedDocument } = useDocuments();

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [input]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading || isDisabled) return;
    onSendMessage(input.trim());
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full text-left">
      <div className="bg-white border border-slate-300 rounded-xl p-3 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-indigo-500 transition-all">
        {selectedDocument && (
          <div className="flex items-center gap-1.5 text-xs text-indigo-700 font-medium mb-2 px-1">
            <FileText className="w-3.5 h-3.5" />
            <span>Grounded context: <strong>{selectedDocument.title}</strong></span>
          </div>
        )}

        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isDisabled || isLoading}
          placeholder={
            selectedDocument
              ? `Ask any question grounded in "${selectedDocument.title}"... (Press Enter to send, Shift+Enter for newline)`
              : 'Select a document or ask a general document question...'
          }
          rows={2}
          className="w-full text-sm text-slate-900 bg-transparent resize-none focus:outline-none placeholder:text-slate-400"
        />

        <div className="flex items-center justify-between pt-2 border-t border-slate-100 mt-1">
          <span className="text-[11px] text-slate-400">
            Answers are strictly cited from uploaded document sources.
          </span>
          <Button
            type="submit"
            variant="primary"
            size="sm"
            isDisabled={!input.trim() || isDisabled || isLoading}
            isLoading={isLoading}
            icon={Send}
          >
            Send
          </Button>
        </div>
      </div>
    </form>
  );
}
