import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Search,
  ChevronLeft,
  ChevronRight,
  MessageSquare,
  Sparkles,
  HelpCircle,
  Highlighter,
  ExternalLink,
  Info
} from 'lucide-react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { formatBytes, formatDate } from '../../utils/formatters';
import { useDocuments } from '../../context/DocumentContext';

export function DocumentReader({ doc, activeCitationPage, highlightedPassage }) {
  const navigate = useNavigate();
  const { selectDocument } = useDocuments();
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(activeCitationPage || 1);

  if (!doc) {
    return (
      <div className="p-8 text-center bg-white border border-slate-200 rounded-xl">
        <p className="text-slate-500 text-sm">No document selected for reading.</p>
      </div>
    );
  }

  const pageCount = doc.pageCount || 1;
  const extractedText = doc.extractedText || 'Extracted document text is loading or unavailable for this file.';

  // Highlight matching search query or citation passage in text
  const renderFormattedContent = () => {
    let content = extractedText;
    if (searchQuery.trim()) {
      const parts = content.split(new RegExp(`(${searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'));
      return (
        <p className="whitespace-pre-wrap leading-relaxed text-slate-800 text-sm">
          {parts.map((part, i) =>
            part.toLowerCase() === searchQuery.toLowerCase() ? (
              <mark key={i} className="bg-amber-200 text-slate-900 px-0.5 rounded">
                {part}
              </mark>
            ) : (
              part
            )
          )}
        </p>
      );
    }

    if (highlightedPassage) {
      const index = content.toLowerCase().indexOf(highlightedPassage.toLowerCase().slice(0, 30));
      if (index !== -1) {
        const before = content.slice(0, index);
        const match = content.slice(index, index + highlightedPassage.length);
        const after = content.slice(index + highlightedPassage.length);

        return (
          <p className="whitespace-pre-wrap leading-relaxed text-slate-800 text-sm">
            {before}
            <mark className="bg-indigo-100 text-indigo-900 border-l-2 border-indigo-600 px-1 py-0.5 rounded">
              {match || highlightedPassage}
            </mark>
            {after}
          </p>
        );
      }
    }

    return <p className="whitespace-pre-wrap leading-relaxed text-slate-800 text-sm">{content}</p>;
  };

  const handleAction = (route) => {
    selectDocument(doc);
    navigate(route);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-xs flex flex-col h-full overflow-hidden text-left">
      {/* Reader Controls Header */}
      <div className="p-4 border-b border-slate-200 bg-slate-50/70 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="p-2 bg-indigo-50 border border-indigo-100 rounded-lg text-indigo-600 shrink-0">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-900 truncate max-w-xs sm:max-w-md">{doc.title}</h3>
            <div className="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
              <Badge variant="indigo">{doc.fileType}</Badge>
              <span>{formatBytes(doc.fileSize)}</span>
              <span>•</span>
              <span>{doc.pageCount ? `${doc.pageCount} Pages` : 'Extracted Text'}</span>
            </div>
          </div>
        </div>

        {/* Quick Action Shortcuts */}
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => handleAction('/chat')} icon={MessageSquare}>
            Ask Chat
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleAction('/summaries')} icon={Sparkles}>
            Summary
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleAction('/questions')} icon={HelpCircle}>
            Questions
          </Button>
        </div>
      </div>

      {/* Reader Subbar: Search within doc & Page controls */}
      <div className="px-4 py-2 bg-white border-b border-slate-200 flex items-center justify-between gap-4">
        {/* Search within document */}
        <div className="relative max-w-xs w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search text in document..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full text-xs pl-8 pr-3 py-1.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        {/* Page controls */}
        {doc.pageCount && (
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage <= 1}
              className="p-1 border rounded hover:bg-slate-100 disabled:opacity-40"
              aria-label="Previous page"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span>
              Page <strong>{currentPage}</strong> of <strong>{pageCount}</strong>
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(pageCount, p + 1))}
              disabled={currentPage >= pageCount}
              className="p-1 border rounded hover:bg-slate-100 disabled:opacity-40"
              aria-label="Next page"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>

      {/* Reading Text View Canvas */}
      <div className="p-6 overflow-y-auto max-h-[600px] font-sans bg-slate-50/30">
        {highlightedPassage && (
          <div className="mb-4 p-3 rounded-lg bg-indigo-50 border border-indigo-200 text-xs text-indigo-900 flex items-center gap-2">
            <Highlighter className="w-4 h-4 text-indigo-600 shrink-0" />
            <span>Citation source passage highlighted from Page {activeCitationPage || 1}</span>
          </div>
        )}

        <div className="max-w-3xl mx-auto bg-white p-8 rounded-lg shadow-xs border border-slate-200 min-h-[400px]">
          {renderFormattedContent()}
        </div>
      </div>
    </div>
  );
}
