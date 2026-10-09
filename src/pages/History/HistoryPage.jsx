import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { History, Search, MessageSquare, Trash2, Edit2, Clock, Calendar, ArrowRight, X } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { Skeleton } from '../../components/common/Skeleton';
import { EmptyState } from '../../components/common/EmptyState';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { ConfirmDialog } from '../../components/common/ConfirmDialog';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { formatDate, formatRelativeTime } from '../../utils/formatters';
import { useToast } from '../../context/ToastContext';
import { chatApi } from '../../api/chatApi';

export function HistoryPage() {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const [deleteTarget, setDeleteTarget] = useState(null);
  const [renameTarget, setRenameTarget] = useState(null);
  const [newTitle, setNewTitle] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const convs = await chatApi.getConversations();
      setConversations(convs);
    } catch (err) {
      setError(err.message || 'Failed to load conversation history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const filteredHistory = conversations.filter(
    (c) =>
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.documentTitle.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    try {
      await chatApi.deleteConversation(deleteTarget.id);
      setConversations((prev) => prev.filter((c) => c.id !== deleteTarget.id));
      addToast(`Conversation "${deleteTarget.title}" deleted.`, 'info');
      setDeleteTarget(null);
    } catch (err) {
      addToast(err.message || 'Failed to delete conversation', 'error');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleRename = async (e) => {
    e.preventDefault();
    if (!renameTarget || !newTitle.trim()) return;
    setIsRenaming(true);
    try {
      const updated = await chatApi.renameConversation(renameTarget.id, newTitle.trim());
      setConversations((prev) => prev.map((c) => (c.id === renameTarget.id ? updated : c)));
      addToast('Conversation title updated.', 'success');
      setRenameTarget(null);
    } catch (err) {
      addToast(err.message || 'Failed to rename conversation', 'error');
    } finally {
      setIsRenaming(false);
    }
  };

  return (
    <div className="space-y-6 text-left animate-fade-in max-w-5xl mx-auto">
      {/* Top Header & Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <History className="w-6 h-6 text-indigo-600" />
            Chat History & Saved Sessions
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Review past document questions, answer citations, and research conversations.
          </p>
        </div>

        {/* Search input */}
        <div className="relative max-w-xs w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search past conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full text-xs pl-9 pr-8 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
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
      </div>

      {error && <ErrorMessage title="Error loading history" message={error} onRetry={loadHistory} />}

      {/* History Items Feed */}
      {loading ? (
        <div className="space-y-3">
          <Skeleton className="h-20" />
          <Skeleton className="h-20" />
        </div>
      ) : filteredHistory.length === 0 ? (
        <EmptyState
          icon={MessageSquare}
          title="No chat history found"
          description={searchQuery ? `No sessions matching "${searchQuery}".` : 'Start your first research chat on a document.'}
          actionLabel="Start New AI Chat"
          onAction={() => navigate('/chat')}
        />
      ) : (
        <div className="space-y-3">
          {filteredHistory.map((conv) => (
            <div
              key={conv.id}
              className="p-5 bg-white border border-slate-200 rounded-xl shadow-xs hover:border-indigo-300 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 group text-left"
            >
              <div className="space-y-1 overflow-hidden">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-indigo-600 shrink-0" />
                  <h3 className="text-sm font-bold text-slate-900 truncate group-hover:text-indigo-600 transition-colors">
                    {conv.title}
                  </h3>
                </div>
                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 pl-6">
                  <span>Document: <strong className="text-slate-700">{conv.documentTitle}</strong></span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3 text-slate-400" />
                    Updated {formatRelativeTime(conv.updatedAt)}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate(`/chat?conv=${conv.id}`)}
                  icon={ArrowRight}
                >
                  Open Chat
                </Button>
                <button
                  onClick={() => {
                    setRenameTarget(conv);
                    setNewTitle(conv.title);
                  }}
                  className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
                  title="Rename chat"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setDeleteTarget(conv)}
                  className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                  title="Delete chat"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete Conversation History"
        message={`Are you sure you want to delete "${deleteTarget?.title}"? All message history will be removed.`}
        confirmText="Delete Chat"
        isLoading={isDeleting}
      />

      {/* Rename Modal */}
      <Modal isOpen={!!renameTarget} onClose={() => setRenameTarget(null)} title="Rename Conversation">
        <form onSubmit={handleRename} className="space-y-4 text-left">
          <Input
            label="Conversation Title"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            required
          />
          <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
            <Button variant="outline" size="sm" onClick={() => setRenameTarget(null)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" isLoading={isRenaming}>
              Save Title
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
