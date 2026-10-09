import React from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { Menu, Search, User, LogOut, Settings as SettingsIcon, FileText } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useDocuments } from '../../context/DocumentContext';

export function TopNav({ onMenuToggle }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { selectedDocument } = useDocuments();

  const titleMap = {
    '/dashboard': 'Dashboard',
    '/documents': 'My Documents',
    '/chat': 'AI Chat',
    '/summaries': 'Document Summaries',
    '/questions': 'Question Generator',
    '/quiz': 'Quiz & Practice',
    '/flashcards': 'Flashcards',
    '/history': 'Chat History',
    '/settings': 'Settings',
  };

  const pageTitle = titleMap[location.pathname] || 'Research Workspace';

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/90 backdrop-blur-md border-b border-slate-200 px-4 sm:px-6 flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuToggle}
          className="lg:hidden p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 focus:outline-none"
          aria-label="Open sidebar menu"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="flex flex-col text-left">
          <h1 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight leading-tight">
            {pageTitle}
          </h1>
          {selectedDocument && (
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 mt-0.5">
              <FileText className="w-3 h-3 text-indigo-600" />
              <span className="truncate max-w-xs font-medium text-slate-700">{selectedDocument.title}</span>
            </div>
          )}
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Active Document Indicator Chip */}
        {selectedDocument && (
          <Link
            to="/documents"
            className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200 text-xs font-medium text-slate-700 hover:bg-slate-200 transition-colors"
            title="Active Selected Document"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span className="truncate max-w-[180px]">{selectedDocument.title}</span>
          </Link>
        )}

        {/* User Dropdown Menu */}
        <div className="flex items-center gap-2 border-l border-slate-200 pl-3">
          <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 font-semibold text-xs flex items-center justify-center border border-indigo-200">
            {user?.fullName?.charAt(0) || user?.email?.charAt(0) || 'U'}
          </div>
          <div className="hidden sm:flex flex-col text-left">
            <span className="text-xs font-semibold text-slate-800 leading-tight">
              {user?.fullName || 'Researcher'}
            </span>
            <span className="text-[11px] text-slate-500 truncate max-w-[140px]">
              {user?.email || 'user@infolens.edu'}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors ml-1 focus:outline-none"
            title="Log out"
            aria-label="Log out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
