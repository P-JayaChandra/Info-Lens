import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  FileText,
  MessageSquare,
  Sparkles,
  HelpCircle,
  Award,
  Layers,
  Upload,
  Plus,
  ArrowRight,
  TrendingUp,
  Clock,
  RefreshCw,
  FolderOpen
} from 'lucide-react';
import { Button } from '../../components/common/Button';
import { DocumentCard } from '../../components/documents/DocumentCard';
import { DocumentUploadZone } from '../../components/documents/DocumentUploadZone';
import { Skeleton } from '../../components/common/Skeleton';
import { EmptyState } from '../../components/common/EmptyState';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { useAuth } from '../../context/AuthContext';
import { useDocuments } from '../../context/DocumentContext';
import { chatApi } from '../../api/chatApi';

export function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { documents, loading: docsLoading, error: docsError, fetchDocuments, selectDocument } = useDocuments();
  
  const [recentConversations, setRecentConversations] = useState([]);
  const [chatsLoading, setChatsLoading] = useState(true);
  const [chatsError, setChatsError] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);

  const loadConversations = async () => {
    setChatsLoading(true);
    setChatsError(null);
    try {
      const convs = await chatApi.getConversations();
      setRecentConversations(convs);
    } catch (err) {
      setChatsError(err.message || 'Failed to load recent conversations');
    } finally {
      setChatsLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  const totalDocumentsCount = documents.length;
  const recentDocs = documents.slice(0, 3);

  return (
    <div className="space-y-8 text-left animate-fade-in">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-indigo-900 via-slate-900 to-slate-900 text-white rounded-2xl p-6 sm:p-8 shadow-md relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-xl z-10">
          <span className="text-xs font-semibold uppercase tracking-wider text-indigo-300">Academic Workspace</span>
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Welcome back, {user?.fullName || 'Researcher'}
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            Upload academic documents, execute document-grounded AI Q&A, and generate auditable study materials.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3 z-10 shrink-0">
          <Button
            variant="primary"
            size="md"
            onClick={() => setShowUploadModal(!showUploadModal)}
            icon={Upload}
            className="bg-indigo-600 hover:bg-indigo-500 border-none shadow-md"
          >
            Upload Document
          </Button>
          <Link to="/chat">
            <Button variant="outline" size="md" className="bg-white/10 text-white border-white/20 hover:bg-white/20">
              New AI Chat
            </Button>
          </Link>
        </div>
      </div>

      {/* Upload Zone Dropdown Container */}
      {showUploadModal && (
        <div className="animate-fade-in">
          <DocumentUploadZone onUploadSuccess={() => setShowUploadModal(false)} />
        </div>
      )}

      {/* Stats Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="academic-card p-5 space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Total Documents</span>
            <FileText className="w-4 h-4 text-indigo-600" />
          </div>
          <p className="text-2xl font-extrabold text-slate-900">
            {docsLoading ? <Skeleton className="w-12 h-8" /> : totalDocumentsCount}
          </p>
          <p className="text-[11px] text-slate-500">Supported PDF, DOCX, TXT</p>
        </div>

        <div className="academic-card p-5 space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Active Conversations</span>
            <MessageSquare className="w-4 h-4 text-indigo-600" />
          </div>
          <p className="text-2xl font-extrabold text-slate-900">
            {chatsLoading ? <Skeleton className="w-12 h-8" /> : recentConversations.length}
          </p>
          <p className="text-[11px] text-slate-500">Document-grounded Q&A</p>
        </div>

        <div className="academic-card p-5 space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Study Tools</span>
            <Award className="w-4 h-4 text-indigo-600" />
          </div>
          <p className="text-2xl font-extrabold text-slate-900">4 Modules</p>
          <p className="text-[11px] text-slate-500">Summaries, Questions, Quiz, Cards</p>
        </div>

        <div className="academic-card p-5 space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Grounded Accuracy</span>
            <Sparkles className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-2xl font-extrabold text-slate-900">100%</p>
          <p className="text-[11px] text-emerald-700 font-medium">Verifiable Citation Search</p>
        </div>
      </div>

      {/* Quick Study Shortcuts Grid */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-slate-900">Study Assistance Modules</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { title: 'Summaries', desc: 'Generate executive overviews & section breakdowns', path: '/summaries', icon: Sparkles, color: 'text-indigo-600' },
            { title: 'Question Generator', desc: 'Create multiple-choice & short answer sets', path: '/questions', icon: HelpCircle, color: 'text-blue-600' },
            { title: 'Quiz & Practice', desc: 'Interactive scored exam runner with answer keys', path: '/quiz', icon: Award, color: 'text-emerald-600' },
            { title: 'Flashcard Decks', desc: '3D interactive cards with keyboard navigation', path: '/flashcards', icon: Layers, color: 'text-amber-600' },
          ].map((tool, i) => {
            const Icon = tool.icon;
            return (
              <Link key={i} to={tool.path} className="academic-card p-5 space-y-2 group hover:border-indigo-300">
                <div className="flex items-center justify-between">
                  <Icon className={`w-6 h-6 ${tool.color}`} />
                  <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600 group-hover:translate-x-1 transition-all" />
                </div>
                <h4 className="text-sm font-bold text-slate-900">{tool.title}</h4>
                <p className="text-xs text-slate-500 leading-relaxed">{tool.desc}</p>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Documents & Conversations Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Documents (2 columns) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900">Recent Documents</h3>
            <Link to="/documents" className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
              View All ({totalDocumentsCount}) <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {docsError && <ErrorMessage title="Failed to load documents" message={docsError} onRetry={fetchDocuments} />}

          {docsLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Skeleton variant="card" />
              <Skeleton variant="card" />
            </div>
          ) : recentDocs.length === 0 ? (
            <EmptyState
              icon={FolderOpen}
              title="No documents uploaded yet"
              description="Upload academic papers or research materials to start generating Q&A and study decks."
              actionLabel="Upload First Document"
              onAction={() => setShowUploadModal(true)}
            />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {recentDocs.map((doc) => (
                <DocumentCard key={doc.id} doc={doc} onSelect={() => navigate('/documents')} />
              ))}
            </div>
          )}
        </div>

        {/* Recent Conversations (1 column) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900">Recent Chats</h3>
            <Link to="/history" className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
              View History <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {chatsError && <ErrorMessage title="Error loading chats" message={chatsError} onRetry={loadConversations} />}

          {chatsLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-14" />
              <Skeleton className="h-14" />
            </div>
          ) : recentConversations.length === 0 ? (
            <EmptyState
              icon={MessageSquare}
              title="No active conversations"
              description="Start a chat on an uploaded document to explore grounded Q&A."
              actionLabel="New AI Chat"
              onAction={() => navigate('/chat')}
            />
          ) : (
            <div className="space-y-2.5">
              {recentConversations.slice(0, 4).map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => navigate(`/chat?conv=${conv.id}`)}
                  className="p-3.5 bg-white border border-slate-200 rounded-xl hover:border-indigo-300 cursor-pointer transition-all flex items-start justify-between gap-3 group"
                >
                  <div className="overflow-hidden">
                    <h4 className="text-xs font-bold text-slate-900 truncate group-hover:text-indigo-600 transition-colors">
                      {conv.title}
                    </h4>
                    <p className="text-[11px] text-slate-500 truncate mt-0.5">{conv.documentTitle}</p>
                  </div>
                  <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
