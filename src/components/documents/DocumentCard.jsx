import React, { useState } from 'react';
import { FileText, Eye, Trash2, Edit2, Calendar, HardDrive, CheckCircle2, Clock, AlertTriangle, Sparkles, MessageSquare } from 'lucide-react';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { ConfirmDialog } from '../common/ConfirmDialog';
import { Modal } from '../common/Modal';
import { Input } from '../common/Input';
import { formatBytes, formatDate } from '../../utils/formatters';
import { useDocuments } from '../../context/DocumentContext';
import { useToast } from '../../context/ToastContext';
import { useNavigate } from 'react-router-dom';

export function DocumentCard({ doc, isSelected, onSelect }) {
  const { deleteDoc, renameDoc, selectDocument } = useDocuments();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [isRenameOpen, setIsRenameOpen] = useState(false);
  const [newTitle, setNewTitle] = useState(doc.title);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await deleteDoc(doc.id);
      addToast(`Document "${doc.title}" deleted.`, 'info');
      setIsDeleteOpen(false);
    } catch (err) {
      addToast(err.message || 'Failed to delete document', 'error');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleRename = async (e) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setIsRenaming(true);
    try {
      await renameDoc(doc.id, newTitle.trim());
      addToast('Document title updated.', 'success');
      setIsRenameOpen(false);
    } catch (err) {
      addToast(err.message || 'Failed to rename', 'error');
    } finally {
      setIsRenaming(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Ready':
        return <Badge variant="emerald">Confirmed Ready</Badge>;
      case 'Processing':
        return <Badge variant="amber">Processing AI Embeddings...</Badge>;
      case 'Uploading':
        return <Badge variant="indigo">Uploading...</Badge>;
      case 'Failed':
        return <Badge variant="rose">Processing Failed</Badge>;
      default:
        return <Badge variant="neutral">{status || 'Ready'}</Badge>;
    }
  };

  const handleOpenChat = () => {
    selectDocument(doc);
    navigate('/chat');
  };

  const handleOpenReader = () => {
    selectDocument(doc);
    if (onSelect) onSelect(doc);
  };

  return (
    <>
      <div
        className={`academic-card p-5 flex flex-col justify-between gap-4 text-left transition-all ${
          isSelected ? 'ring-2 ring-indigo-500 border-indigo-200 bg-indigo-50/20' : ''
        }`}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 overflow-hidden">
            <div className="p-3 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-600 shrink-0">
              <FileText className="w-5 h-5" />
            </div>
            <div className="overflow-hidden">
              <h4 className="text-sm font-semibold text-slate-900 truncate leading-snug" title={doc.title}>
                {doc.title}
              </h4>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="blue">{doc.fileType || 'PDF'}</Badge>
                {getStatusBadge(doc.status)}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1 shrink-0">
            <button
              onClick={() => setIsRenameOpen(true)}
              className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors"
              title="Rename document"
            >
              <Edit2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setIsDeleteOpen(true)}
              className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-md transition-colors"
              title="Delete document"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Metadata Footer */}
        <div className="text-xs text-slate-500 flex items-center justify-between pt-3 border-t border-slate-100">
          <span className="flex items-center gap-1">
            <HardDrive className="w-3.5 h-3.5" />
            {formatBytes(doc.fileSize)}
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5" />
            {formatDate(doc.uploadDate)}
          </span>
        </div>

        {/* Card Actions */}
        <div className="grid grid-cols-2 gap-2 pt-1">
          <Button variant="outline" size="sm" onClick={handleOpenReader} icon={Eye}>
            Read Doc
          </Button>
          <Button variant="primary" size="sm" onClick={handleOpenChat} icon={MessageSquare}>
            Ask AI
          </Button>
        </div>
      </div>

      {/* Delete Dialog */}
      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={handleDelete}
        title="Delete Document"
        message={`Are you sure you want to delete "${doc.title}"? Associated chat history and study decks will be removed.`}
        confirmText="Delete Document"
        isLoading={isDeleting}
      />

      {/* Rename Modal */}
      <Modal isOpen={isRenameOpen} onClose={() => setIsRenameOpen(false)} title="Rename Document">
        <form onSubmit={handleRename} className="flex flex-col gap-4 text-left">
          <Input
            label="Document Title"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            required
          />
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
            <Button variant="outline" size="sm" onClick={() => setIsRenameOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" isLoading={isRenaming}>
              Save Changes
            </Button>
          </div>
        </form>
      </Modal>
    </>
  );
}
