import React from 'react';
import { FileText, Bookmark, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useDocuments } from '../../context/DocumentContext';

export function CitationCard({ citation }) {
  const navigate = useNavigate();
  const { documents, selectDocument } = useDocuments();

  if (!citation) return null;

  const handleOpenSource = () => {
    const doc = documents.find((d) => d.id === citation.documentId) || {
      id: citation.documentId,
      title: citation.documentTitle,
      fileType: 'PDF',
    };
    selectDocument(doc);
    navigate(`/documents?doc=${citation.documentId}&page=${citation.page || 1}&passage=${encodeURIComponent(citation.passage || '')}`);
  };

  return (
    <div
      onClick={handleOpenSource}
      className="p-3 bg-indigo-50/70 border border-indigo-200 rounded-lg cursor-pointer hover:bg-indigo-100/80 transition-all text-left group"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && handleOpenSource()}
    >
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-indigo-900 truncate">
          <Bookmark className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
          <span className="truncate">{citation.documentTitle || 'Source Document'}</span>
        </div>
        {citation.page && (
          <span className="text-[11px] font-semibold text-indigo-700 bg-white border border-indigo-200 px-1.5 py-0.5 rounded shrink-0">
            Page {citation.page}
          </span>
        )}
      </div>
      <p className="text-xs text-slate-700 line-clamp-2 italic leading-relaxed">
        "{citation.passage}"
      </p>
      <div className="flex items-center gap-1 text-[11px] text-indigo-700 font-medium mt-2 group-hover:underline">
        <span>Verify in Document Reader</span>
        <ExternalLink className="w-3 h-3" />
      </div>
    </div>
  );
}
