import React, { useState, useEffect } from 'react';
import { Layers, FileText, RefreshCw } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { FlashcardDeck } from '../../components/study/FlashcardDeck';
import { Skeleton } from '../../components/common/Skeleton';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { useDocuments } from '../../context/DocumentContext';
import { useToast } from '../../context/ToastContext';
import { flashcardApi } from '../../api/flashcardApi';

export function FlashcardsPage() {
  const { documents, selectedDocument, selectDocument } = useDocuments();
  const { addToast } = useToast();

  const [deck, setDeck] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const activeDoc = selectedDocument || documents[0];

  const loadDeck = async () => {
    if (!activeDoc) {
      addToast('Please select an uploaded document.', 'warning');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await flashcardApi.getDeck(activeDoc.id);
      setDeck(res);
    } catch (err) {
      setError(err.message || 'Failed to load flashcard deck.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeDoc) {
      loadDeck();
    }
  }, [activeDoc?.id]);

  const handleUpdateMastery = async (cardId, knownStatus) => {
    if (!activeDoc) return;
    try {
      await flashcardApi.updateCardMastery(activeDoc.id, cardId, knownStatus);
    } catch (err) {
      console.warn('Failed to persist card status:', err);
    }
  };

  return (
    <div className="space-y-6 text-left animate-fade-in max-w-4xl mx-auto">
      {/* Top Controls Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <Layers className="w-6 h-6 text-indigo-600" />
            Interactive Flashcards
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Reinforce key concepts with 3D interactive study decks.
          </p>
        </div>

        <div className="flex items-center gap-3">
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

          <Button variant="primary" size="sm" onClick={loadDeck} isLoading={loading} icon={RefreshCw}>
            Reload Deck
          </Button>
        </div>
      </div>

      {error && <ErrorMessage title="Failed to load flashcard deck" message={error} onRetry={loadDeck} />}

      {loading ? (
        <Skeleton variant="card" className="h-80" />
      ) : (
        <FlashcardDeck
          cards={deck?.cards || []}
          documentTitle={deck?.documentTitle || activeDoc?.title}
          onUpdateMastery={handleUpdateMastery}
        />
      )}
    </div>
  );
}
