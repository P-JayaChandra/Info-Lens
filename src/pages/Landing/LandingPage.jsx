import React from 'react';
import { Link } from 'react-router-dom';
import {
  BookOpen,
  FileText,
  MessageSquare,
  Sparkles,
  Award,
  ShieldCheck,
  Search,
  ArrowRight,
  CheckCircle2,
  Cpu,
  Layers,
  HelpCircle
} from 'lucide-react';
import { Button } from '../../components/common/Button';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Public Top Navbar */}
      <header className="sticky top-0 z-30 h-16 bg-white/90 backdrop-blur-md border-b border-slate-200 px-6 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold">
            <BookOpen className="w-5 h-5" />
          </div>
          <span className="text-lg font-bold text-slate-900 tracking-tight">InfoLens</span>
        </div>

        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600">
          <a href="#features" className="hover:text-indigo-600 transition-colors">Features</a>
          <a href="#workflow" className="hover:text-indigo-600 transition-colors">Workflow</a>
          <a href="#study-tools" className="hover:text-indigo-600 transition-colors">Study Tools</a>
          <a href="#privacy" className="hover:text-indigo-600 transition-colors">Security & Privacy</a>
        </nav>

        <div className="flex items-center gap-3">
          <Link to="/login">
            <Button variant="ghost" size="sm">Sign In</Button>
          </Link>
          <Link to="/register">
            <Button variant="primary" size="sm">Get Started</Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 sm:py-24 px-6 max-w-6xl mx-auto text-center space-y-8 animate-fade-in">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-xs font-semibold text-indigo-700">
          <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
          <span>Intelligent Document Understanding & Research Workspace</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight max-w-4xl mx-auto leading-tight">
          Transform Academic Papers & Research Documents into <span className="text-indigo-600">Grounded Knowledge</span>
        </h1>

        <p className="text-base sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
          InfoLens allows students and researchers to ask questions about uploaded documents, inspect precise source citations, generate summaries, and practice with automated quizzes and flashcards.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <Link to="/dashboard">
            <Button variant="primary" size="lg" className="shadow-md">
              Launch Research Workspace <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </Link>
          <Link to="/register">
            <Button variant="outline" size="lg">
              Create Account
            </Button>
          </Link>
        </div>

        {/* Hero Visual Mock Container */}
        <div className="pt-8 max-w-4xl mx-auto">
          <div className="academic-card p-6 bg-white shadow-xl rounded-2xl border border-slate-200 text-left space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
                <FileText className="w-4 h-4 text-indigo-600" />
                <span>Retrieval_Augmented_Generation_Survey.pdf</span>
              </div>
              <span className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded font-medium">
                Confirmed Grounded Response
              </span>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl space-y-2 text-xs text-slate-700">
              <p className="font-semibold text-slate-900">Q: How does semantic chunking improve retrieval accuracy?</p>
              <p className="leading-relaxed">
                "According to Page 4 of the uploaded survey, semantic chunking preserves complete contextual boundaries and sentence structures, preventing key concepts from being split across chunk limits."
              </p>
              <div className="p-2.5 bg-indigo-50 border border-indigo-200 rounded-lg text-[11px] text-indigo-900 flex items-center justify-between">
                <span>Citation: Page 4, Section 2 (chunk_rag_p4_sec2)</span>
                <span className="text-indigo-600 font-semibold underline cursor-pointer">View Source in Reader</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Central Workflow Section */}
      <section id="workflow" className="py-16 bg-white border-y border-slate-200 px-6">
        <div className="max-w-6xl mx-auto text-center space-y-12">
          <div>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">End-to-End Document Workflow</h2>
            <p className="text-sm text-slate-500 max-w-xl mx-auto mt-2">
              From raw document ingestion to verifiable study materials.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {[
              { step: '01', title: 'Upload Document', desc: 'Drag and drop PDF, DOCX, or TXT materials.', icon: FileText },
              { step: '02', title: 'Ask Questions', desc: 'Execute natural language queries grounded in text.', icon: MessageSquare },
              { step: '03', title: 'Verify Citations', desc: 'Inspect exact page numbers and retrieved passages.', icon: Search },
              { step: '04', title: 'Generate Summaries', desc: 'Read concise overviews or detailed topic breakdowns.', icon: Sparkles },
              { step: '05', title: 'Study & Practice', desc: 'Test knowledge with auto-generated quizzes & flashcards.', icon: Award },
            ].map((s, i) => {
              const Icon = s.icon;
              return (
                <div key={i} className="p-5 bg-slate-50 border border-slate-200 rounded-xl text-left space-y-3 relative">
                  <span className="text-xs font-extrabold text-indigo-600">{s.step}</span>
                  <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center">
                    <Icon className="w-4 h-4" />
                  </div>
                  <h3 className="text-sm font-bold text-slate-900">{s.title}</h3>
                  <p className="text-xs text-slate-500 leading-relaxed">{s.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Overview */}
      <section id="features" className="py-16 px-6 max-w-6xl mx-auto text-center space-y-12">
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">Designed for Rigorous Research</h2>
          <p className="text-sm text-slate-500 max-w-xl mx-auto mt-2">
            Built specifically to avoid ungrounded AI hallucinations and provide auditable study tools.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="academic-card p-6 space-y-3">
            <ShieldCheck className="w-6 h-6 text-indigo-600" />
            <h3 className="text-base font-bold text-slate-900">Auditable Source Citations</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Every answer highlights the exact passage and page reference returned by the document intelligence engine.
            </p>
          </div>

          <div className="academic-card p-6 space-y-3">
            <Cpu className="w-6 h-6 text-indigo-600" />
            <h3 className="text-base font-bold text-slate-900">Multi-Format Ingestion</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Seamless support for academic PDF papers, Word DOCX files, and plain text lecture notes up to 25 MB.
            </p>
          </div>

          <div className="academic-card p-6 space-y-3">
            <Layers className="w-6 h-6 text-indigo-600" />
            <h3 className="text-base font-bold text-slate-900">Interactive Study Decks</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Transform dense articles into 3D interactive flashcards and scored practice quizzes with full answer keys.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-8 bg-slate-900 text-slate-400 text-xs text-center border-t border-slate-800">
        <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-white font-bold">
            <BookOpen className="w-4 h-4 text-indigo-400" />
            <span>InfoLens System</span>
          </div>
          <p>© 2026 InfoLens Team. Built for Intelligent Document Understanding & Study Assistance.</p>
        </div>
      </footer>
    </div>
  );
}
