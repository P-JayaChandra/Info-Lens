import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  MessageSquare,
  Plus,
  FileText,
  Sparkles,
  ShieldCheck,
  RefreshCw,
  Trash2,
  Edit2,
  FolderOpen
} from 'lucide-react';
import { Button } from '../../components/common/Button';
import { Select } from '../../components/common/Select';
import { ChatMessage } from '../../components/chat/ChatMessage';
import { ChatInput } from '../../components/chat/ChatInput';
import { Skeleton } from '../../components/common/Skeleton';
import { EmptyState } from '../../components/common/EmptyState';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { useDocuments } from '../../context/DocumentContext';
import { useToast } from '../../context/ToastContext';
import { chatApi } from '../../api/chatApi';

export function ChatPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const targetConvId = searchParams.get('conv');

  const { documents, selectedDocument, selectDocument } = useDocuments();
  const { addToast } = useToast();

  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState(null);

  const [isRenameOpen, setIsRenameOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const messagesEndRef = useRef(null);

  const loadConversations = async () => {
    setLoading(true);
    setError(null);
    try {
      const convs = await chatApi.getConversations();
      setConversations(convs);

      if (targetConvId) {
        const found = convs.find((c) => c.id === targetConvId);
        if (found) setActiveConv(found);
      } else if (convs.length > 0) {
        setActiveConv(convs[0]);
      }
    } catch (err) {
      setError(err.message || 'Failed to load conversations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, [targetConvId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeConv?.messages]);

  const handleCreateNewConv = async () => {
    const docId = selectedDocument?.id || documents[0]?.id;
    if (!docId) {
      addToast('Please upload a document first to start an AI research chat.', 'warning');
      return;
    }

    try {
      const newConv = await chatApi.createConversation(docId, `Chat on ${selectedDocument?.title || 'Document'}`);
      setConversations((prev) => [newConv, ...prev]);
      setActiveConv(newConv);
      setSearchParams({ conv: newConv.id });
      addToast('New research chat created.', 'success');
    } catch (err) {
      addToast(err.message || 'Failed to create conversation', 'error');
    }
  };

  const handleSendMessage = async (text) => {
    if (!activeConv) return;
    setIsSending(true);

    try {
      const res = await chatApi.sendMessage(activeConv.id, text, selectedDocument?.id || activeConv.documentId);
      
      const updatedMessages = [...(activeConv.messages || []), res.userMessage, res.assistantMessage];
      const updatedConv = { ...activeConv, messages: updatedMessages, updatedAt: new Date().toISOString() };

      setActiveConv(updatedConv);
      setConversations((prev) => prev.map((c) => (c.id === activeConv.id ? updatedConv : c)));
    } catch (err) {
      addToast(err.message || 'Failed to send message', 'error');
    } finally {
      setIsSending(false);
    }
  };

  const handleDeleteConv = async (id) => {
    try {
      await chatApi.deleteConversation(id);
      const remaining = conversations.filter((c) => c.id !== id);
      setConversations(remaining);
      if (activeConv?.id === id) {
        setActiveConv(remaining.length > 0 ? remaining[0] : null);
      }
      addToast('Conversation deleted.', 'info');
    } catch (err) {
      addToast(err.message || 'Failed to delete chat', 'error');
    }
  };

  const handleRenameConv = async (e) => {
    e.preventDefault();
    if (!newTitle.trim() || !activeConv) return;
    try {
      const updated = await chatApi.renameConversation(activeConv.id, newTitle.trim());
      setActiveConv(updated);
      setConversations((prev) => prev.map((c) => (c.id === activeConv.id ? updated : c)));
      setIsRenameOpen(false);
      addToast('Conversation title updated.', 'success');
    } catch (err) {
      addToast(err.message || 'Failed to rename conversation', 'error');
    }
  };

  const docOptions = documents.map((d) => ({ value: d.id, label: `${d.title} (${d.fileType})` }));

  return (
    <div className="space-y-6 text-left animate-fade-in">
      {/* Top Header & Document Context Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">AI Conversational Intelligence</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Ask questions about uploaded documents. Answers feature auditable source citations.
          </p>
        </div>

        {/* Selected Document Context Picker */}
        <div className="flex items-center gap-2 max-w-md w-full sm:w-auto">
          <FileText className="w-4 h-4 text-indigo-600 shrink-0" />
          <select
            value={selectedDocument?.id || ''}
            onChange={(e) => {
              const doc = documents.find((d) => d.id === e.target.value);
              if (doc) selectDocument(doc);
            }}
            className="w-full text-xs font-semibold text-slate-800 bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          >
            {docOptions.length === 0 ? (
              <option value="">No documents uploaded</option>
            ) : (
              docOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  Context: {opt.label}
                </option>
              ))
            )}
          </select>
          <Button variant="primary" size="sm" onClick={handleCreateNewConv} icon={Plus} className="shrink-0">
            New Chat
          </Button>
        </div>
      </div>

      {error && <ErrorMessage title="Failed to load chat history" message={error} onRetry={loadConversations} />}

      {/* Main Chat Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Conversations Sidebar (4 cols) */}
        <div className="lg:col-span-4 bg-white border border-slate-200 rounded-xl p-4 space-y-3 shadow-xs">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700">Conversations</span>
            <span className="text-xs text-slate-400 font-medium">{conversations.length} Active</span>
          </div>

          {loading ? (
            <div className="space-y-2">
              <Skeleton className="h-12" />
              <Skeleton className="h-12" />
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center p-4 text-xs text-slate-500">No active conversations.</div>
          ) : (
            <div className="space-y-1.5 max-h-[500px] overflow-y-auto pr-1">
              {conversations.map((conv) => {
                const isActive = activeConv?.id === conv.id;
                return (
                  <div
                    key={conv.id}
                    onClick={() => {
                      setActiveConv(conv);
                      setSearchParams({ conv: conv.id });
                    }}
                    className={`p-3 rounded-xl border text-left cursor-pointer transition-all flex items-start justify-between gap-2 group ${
                      isActive
                        ? 'bg-indigo-50/80 border-indigo-200 text-indigo-950 font-semibold shadow-2xs'
                        : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <div className="overflow-hidden">
                      <h4 className="text-xs font-bold truncate">{conv.title}</h4>
                      <p className="text-[11px] text-slate-500 truncate mt-0.5">{conv.documentTitle}</p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteConv(conv.id);
                      }}
                      className="text-slate-400 hover:text-rose-600 p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                      title="Delete chat"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Active Chat Conversation Container (8 cols) */}
        <div className="lg:col-span-8 bg-white border border-slate-200 rounded-xl shadow-xs flex flex-col h-[650px] overflow-hidden">
          {/* Active Chat Header */}
          <div className="p-4 border-b border-slate-200 bg-slate-50/60 flex items-center justify-between">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="p-2 bg-indigo-600 text-white rounded-lg shrink-0">
                <Sparkles className="w-4 h-4" />
              </div>
              <div className="overflow-hidden">
                <h3 className="text-sm font-bold text-slate-900 truncate">
                  {activeConv?.title || 'New Conversational Session'}
                </h3>
                <span className="text-xs text-slate-500 font-medium truncate block">
                  Document Context: {activeConv?.documentTitle || selectedDocument?.title || 'None Selected'}
                </span>
              </div>
            </div>

            {activeConv && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setNewTitle(activeConv.title);
                  setIsRenameOpen(true);
                }}
                icon={Edit2}
              >
                Rename
              </Button>
            )}
          </div>

          {/* Messages Feed Area */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-50/30">
            {!activeConv || !activeConv.messages || activeConv.messages.length === 0 ? (
              <EmptyState
                icon={MessageSquare}
                title="Start a grounded document conversation"
                description={`Ask any specific question about "${selectedDocument?.title || 'your uploaded document'}". InfoLens will search dense vector chunks and respond with verified citations.`}
              />
            ) : (
              activeConv.messages.map((msg, idx) => <ChatMessage key={msg.id || idx} message={msg} />)
            )}

            {isSending && (
              <div className="p-4 rounded-xl bg-white border border-slate-200 text-xs text-indigo-600 flex items-center gap-2 animate-soft-pulse">
                <Sparkles className="w-4 h-4 animate-spin text-indigo-600" />
                <span>Searching dense embeddings & extracting verified citations...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input Container */}
          <div className="p-4 border-t border-slate-200 bg-white">
            <ChatInput onSendMessage={handleSendMessage} isLoading={isSending} isDisabled={!selectedDocument} />
          </div>
        </div>
      </div>

      {/* Rename Modal */}
      <Modal isOpen={isRenameOpen} onClose={() => setIsRenameOpen(false)} title="Rename Conversation">
        <form onSubmit={handleRenameConv} className="space-y-4 text-left">
          <Input
            label="Conversation Title"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            required
          />
          <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
            <Button variant="outline" size="sm" onClick={() => setIsRenameOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit">
              Save Title
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
