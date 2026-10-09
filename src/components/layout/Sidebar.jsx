import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  BookOpen,
  LayoutDashboard,
  FileText,
  MessageSquareText,
  Sparkles,
  HelpCircle,
  Award,
  Layers,
  History,
  Settings,
  X,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { USE_FIXTURES } from '../../api/client';

export function Sidebar({ isOpen, onClose }) {
  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'My Documents', path: '/documents', icon: FileText },
    { label: 'AI Chat', path: '/chat', icon: MessageSquareText },
    { label: 'Summaries', path: '/summaries', icon: Sparkles },
    { label: 'Question Generator', path: '/questions', icon: HelpCircle },
    { label: 'Quiz & Practice', path: '/quiz', icon: Award },
    { label: 'Flashcards', path: '/flashcards', icon: Layers },
    { label: 'Chat History', path: '/history', icon: History },
    { label: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile Drawer Overlay Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="flex items-center justify-between h-16 px-5 border-b border-slate-800/80 bg-slate-950/40">
          <NavLink to="/dashboard" className="flex items-center gap-2.5 group focus:outline-none">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-base shadow-sm group-hover:bg-indigo-500 transition-colors">
              <BookOpen className="w-4 h-4" />
            </div>
            <div className="flex flex-col text-left">
              <span className="text-base font-bold text-white tracking-tight leading-none">InfoLens</span>
              <span className="text-[10px] uppercase font-semibold tracking-wider text-indigo-400 mt-0.5">
                Doc Intelligence
              </span>
            </div>
          </NavLink>
          <button
            onClick={onClose}
            className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Integration Status Badge */}
        <div className="px-4 py-2.5 mx-3 my-3 rounded-lg bg-slate-850 border border-slate-800 flex items-center gap-2 text-xs">
          <Cpu className={`w-3.5 h-3.5 ${USE_FIXTURES ? 'text-amber-400' : 'text-emerald-400'}`} />
          <span className="text-slate-400 text-[11px] font-medium">
            {USE_FIXTURES ? 'Dev Fixtures Mode' : 'Backend Online (FastAPI)'}
          </span>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-sm font-semibold'
                      : 'text-slate-400 hover:bg-slate-800/80 hover:text-slate-100'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* User Academic Workspace Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/40 text-left">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
            <span className="truncate">Grounded Source Verification</span>
          </div>
        </div>
      </aside>
    </>
  );
}
