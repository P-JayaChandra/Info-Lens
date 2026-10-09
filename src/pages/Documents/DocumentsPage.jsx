import React, { useState, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  FileText,
  Search,
  Grid,
  List as ListIcon,
  Filter,
  Plus,
  ArrowUpDown,
  FolderOpen,
  X
} from 'lucide-react';
import { Button } from '../../components/common/Button';
import { DocumentCard } from '../../components/documents/DocumentCard';
import { DocumentUploadZone } from '../../components/documents/DocumentUploadZone';
import { DocumentReader } from '../../components/documents/DocumentReader';
import { Skeleton } from '../../components/common/Skeleton';
import { EmptyState } from '../../components/common/EmptyState';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { Modal } from '../../components/common/Modal';
import { useDocuments } from '../../context/DocumentContext';
import { useDebounce } from '../../hooks/useDebounce';

export function DocumentsPage() {
  const [searchParams] = useSearchParams();
  const activeDocId = searchParams.get('doc');
  const activePage = parseInt(searchParams.get('page') || '1', 10);
  const activePassage = searchParams.get('passage');

  const { documents, selectedDocument, loading, error, fetchDocuments, selectDocument } = useDocuments();

  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'list'
  const [searchQuery, setSearchQuery] = useState('');
  const [fileTypeFilter, setFileTypeFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('newest');
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [activeReaderDoc, setActiveReaderDoc] = useState(null);

  const debouncedSearch = useDebounce(searchQuery, 250);

  // Filter and sort documents dynamically
  const filteredDocuments = useMemo(() => {
    return documents
      .filter((doc) => {
        const matchesSearch = doc.title.toLowerCase().includes(debouncedSearch.toLowerCase());
        const matchesType = fileTypeFilter === 'ALL' || doc.fileType === fileTypeFilter;
        return matchesSearch && matchesType;
      })
      .sort((a, b) => {
        if (sortBy === 'newest') return new Date(b.uploadDate) - new Date(a.uploadDate);
        if (sortBy === 'oldest') return new Date(a.uploadDate) - new Date(b.uploadDate);
        if (sortBy === 'title') return a.title.localeCompare(b.title);
        if (sortBy === 'size') return b.fileSize - a.fileSize;
        return 0;
      });
  }, [documents, debouncedSearch, fileTypeFilter, sortBy]);

  const targetReaderDoc = activeReaderDoc || (activeDocId ? documents.find((d) => d.id === activeDocId) : selectedDocument);

  return (
    <div className="space-y-6 text-left animate-fade-in">
      {/* Header & Controls Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Document Library</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Manage uploaded papers, search extracted text, and inspect verified source passages.
          </p>
        </div>
        <Button variant="primary" size="md" onClick={() => setIsUploadOpen(true)} icon={Plus}>
          Upload New Document
        </Button>
      </div>

      {/* Upload Zone Modal */}
      <Modal isOpen={isUploadOpen} onClose={() => setIsUploadOpen(false)} title="Upload Document" maxWidth="max-w-xl">
        <DocumentUploadZone onUploadSuccess={() => setIsUploadOpen(false)} />
      </Modal>

      {/* Search, Filters, & View Toggle Row */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3 flex-1 min-w-[260px]">
          {/* Search Input */}
          <div className="relative flex-1 min-w-[200px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search document titles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full text-xs pl-9 pr-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-1.5 text-xs text-slate-600">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={fileTypeFilter}
              onChange={(e) => setFileTypeFilter(e.target.value)}
              className="text-xs bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="ALL">All Types</option>
              <option value="PDF">PDF Only</option>
              <option value="DOCX">DOCX Only</option>
              <option value="TXT">TXT Only</option>
            </select>
          </div>

          {/* Sort By */}
          <div className="flex items-center gap-1.5 text-xs text-slate-600">
            <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="text-xs bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="title">Title (A-Z)</option>
              <option value="size">File Size</option>
            </select>
          </div>
        </div>

        {/* Grid / List View Toggle */}
        <div className="flex items-center border border-slate-200 rounded-lg p-0.5 bg-slate-50">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-1.5 rounded-md text-xs font-medium transition-colors ${
              viewMode === 'grid' ? 'bg-white shadow-xs text-indigo-600' : 'text-slate-500 hover:text-slate-900'
            }`}
            title="Grid View"
          >
            <Grid className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-1.5 rounded-md text-xs font-medium transition-colors ${
              viewMode === 'list' ? 'bg-white shadow-xs text-indigo-600' : 'text-slate-500 hover:text-slate-900'
            }`}
            title="List View"
          >
            <ListIcon className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Error state */}
      {error && <ErrorMessage title="Failed to load document library" message={error} onRetry={fetchDocuments} />}

      {/* Document Library Grid/List vs Document Reader Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Document List/Grid Column */}
        <div className={targetReaderDoc ? 'lg:col-span-5' : 'lg:col-span-12'}>
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Skeleton variant="card" />
              <Skeleton variant="card" />
            </div>
          ) : filteredDocuments.length === 0 ? (
            <EmptyState
              icon={FolderOpen}
              title="No matching documents"
              description={searchQuery ? `No files matching "${searchQuery}".` : 'Your library is empty. Upload your first paper to get started.'}
              actionLabel="Upload Document"
              onAction={() => setIsUploadOpen(true)}
            />
          ) : (
            <div className={`grid ${viewMode === 'grid' && !targetReaderDoc ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'} gap-4`}>
              {filteredDocuments.map((doc) => (
                <DocumentCard
                  key={doc.id}
                  doc={doc}
                  isSelected={targetReaderDoc?.id === doc.id}
                  onSelect={(d) => {
                    selectDocument(d);
                    setActiveReaderDoc(d);
                  }}
                />
              ))}
            </div>
          )}
        </div>

        {/* Active Document Reader Column */}
        {targetReaderDoc && (
          <div className="lg:col-span-7">
            <DocumentReader
              doc={targetReaderDoc}
              activeCitationPage={activePage}
              highlightedPassage={activePassage}
            />
          </div>
        )}
      </div>
    </div>
  );
}
