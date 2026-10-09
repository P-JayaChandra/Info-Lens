import React, { useState } from 'react';
import { User, Sparkles, Copy, Check, ShieldCheck, AlertCircle } from 'lucide-react';
import { CitationCard } from './CitationCard';
import { formatRelativeTime } from '../../utils/formatters';

export function ChatMessage({ message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.sender === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex gap-3.5 p-4 rounded-xl text-left transition-all ${isUser ? 'bg-slate-100/80 ml-8 sm:ml-16' : 'bg-white border border-slate-200 shadow-xs mr-4 sm:mr-12'}`}>
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 text-white font-bold text-xs ${isUser ? 'bg-slate-700' : 'bg-indigo-600'}`}>
        {isUser ? <User className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
      </div>

      <div className="flex-1 space-y-2 overflow-hidden">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-900">
              {isUser ? 'You' : 'InfoLens Assistant'}
            </span>
            {!isUser && (
              <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                <ShieldCheck className="w-3 h-3 text-emerald-600" />
                Document Grounded
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-slate-400">{formatRelativeTime(message.timestamp)}</span>
            {!isUser && (
              <button
                onClick={handleCopy}
                className="text-slate-400 hover:text-slate-600 p-1 rounded transition-colors"
                title="Copy answer"
                aria-label="Copy response text"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            )}
          </div>
        </div>

        {/* Message Content */}
        <p className="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap font-sans">
          {message.text}
        </p>

        {/* Source Citations Block */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="pt-2 mt-3 border-t border-slate-100 space-y-2">
            <span className="text-xs font-semibold text-slate-700 tracking-wide uppercase">
              Retrieved Document Sources ({message.citations.length})
            </span>
            <div className="grid grid-cols-1 gap-2">
              {message.citations.map((citation, i) => (
                <CitationCard key={citation.id || i} citation={citation} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
