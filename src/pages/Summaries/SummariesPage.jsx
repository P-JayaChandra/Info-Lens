import React, { useState, useEffect } from 'react';
import { Sparkles, FileText, Copy, Check, Download, RefreshCw, Bookmark } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Skeleton } from '../../components/common/Skeleton';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { useDocuments } from '../../context/DocumentContext';
import { useToast } from '../../context/ToastContext';
import { summaryApi } from '../../api/summaryApi';

export function SummariesPage() {
  const { documents, selectedDocument, selectDocument } = useDocuments();
  const { addToast } = useToast();

  const [lengthMode, setLengthMode] = useState('detailed'); // 'short' | 'detailed'
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const activeDoc = selectedDocument || documents[0];

  const handleGenerateSummary = async () => {
    if (!activeDoc) {
      addToast('Please select an uploaded document first.', 'warning');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await summaryApi.generateSummary(activeDoc.id, lengthMode);
      setSummary(res);
      addToast(`Summary generated for "${activeDoc.title}".`, 'success');
    } catch (err) {
      setError(err.message || 'Failed to generate document summary.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeDoc) {
      handleGenerateSummary();
    }
  }, [activeDoc?.id, lengthMode]);

  const handleCopy = () => {
    if (!summary) return;
    const textToCopy = `${summary.shortOverview || ''}\n\n${summary.detailedSummary || ''}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    addToast('Summary copied to clipboard.', 'info');
  };

  const handleExportText = () => {
    if (!summary) return;
    const content = `INFOLENS DOCUMENT SUMMARY\nDocument: ${activeDoc?.title}\nDate: ${new Date().toLocaleDateString()}\n\nOVERVIEW:\n${summary.shortOverview}\n\nDETAILED BREAKDOWN:\n${summary.detailedSummary}`;
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${activeDoc?.title || 'Document'}_Summary.txt`;
    link.click();
    URL.revokeObjectURL(url);
    addToast('Summary exported as text file.', 'success');
  };

  return (
    <div className="space-y-6 text-left animate-fade-in max-w-5xl mx-auto">
      {/* Top Controls Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-indigo-600" />
            Document Summarization Engine
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Synthesize key research findings and structured takeaways directly from source text.
          </p>
        </div>

        {/* Document Selector & Controls */}
        <div className="flex flex-wrap items-center gap-3">
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

          {/* Length Mode Toggle */}
          <div className="flex items-center border border-slate-200 rounded-lg p-0.5 bg-slate-50 text-xs">
            <button
              onClick={() => setLengthMode('short')}
              className={`px-3 py-1.5 rounded-md font-semibold transition-colors ${
                lengthMode === 'short' ? 'bg-white text-indigo-600 shadow-xs' : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              Short Overview
            </button>
            <button
              onClick={() => setLengthMode('detailed')}
              className={`px-3 py-1.5 rounded-md font-semibold transition-colors ${
                lengthMode === 'detailed' ? 'bg-white text-indigo-600 shadow-xs' : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              Detailed Breakdown
            </button>
          </div>

          <Button variant="primary" size="sm" onClick={handleGenerateSummary} isLoading={loading} icon={RefreshCw}>
            Regenerate
          </Button>
        </div>
      </div>

      {error && <ErrorMessage title="Failed to generate summary" message={error} onRetry={handleGenerateSummary} />}

      {/* Main Summary Render Box */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-8 shadow-xs space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <Badge variant="indigo">{lengthMode === 'short' ? 'Executive Overview' : 'Detailed Analysis'}</Badge>
            <span className="text-xs text-slate-500 font-medium">Source: {activeDoc?.title}</span>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleCopy} icon={copied ? Check : Copy}>
              {copied ? 'Copied' : 'Copy'}
            </Button>
            <Button variant="outline" size="sm" onClick={handleExportText} icon={Download}>
              Export .TXT
            </Button>
          </div>
        </div>

        {loading ? (
          <div className="space-y-4">
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-20" />
            <Skeleton className="h-32" />
          </div>
        ) : !summary ? (
          <div className="text-center p-8 text-slate-500 text-sm">
            Select a document to generate a grounded AI summary.
          </div>
        ) : (
          <div className="space-y-6">
            {/* Short Overview Box */}
            <div className="p-4 bg-indigo-50/60 border border-indigo-200 rounded-xl space-y-1">
              <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-900">Executive Summary</h4>
              <p className="text-sm text-indigo-950 leading-relaxed font-medium">{summary.shortOverview}</p>
            </div>

            {/* Detailed Section Breakdown */}
            {lengthMode === 'detailed' && (
              <div className="prose prose-slate max-w-none text-sm text-slate-800 leading-relaxed whitespace-pre-wrap font-sans">
                {summary.detailedSummary}
              </div>
            )}

            {/* Source References */}
            {summary.citations && summary.citations.length > 0 && (
              <div className="pt-4 border-t border-slate-100 space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-700">Source References</span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {summary.citations.map((c, idx) => (
                    <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700 space-y-1">
                      <span className="font-bold text-indigo-700">Page {c.page} Reference:</span>
                      <p className="italic text-slate-600">"{c.passage}"</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
