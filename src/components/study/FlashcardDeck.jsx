import React, { useState, useEffect } from 'react';
import { RotateCcw, ChevronLeft, ChevronRight, CheckCircle2, BookmarkPlus, Shuffle, HelpCircle } from 'lucide-react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';

export function FlashcardDeck({ cards = [], documentTitle = '', onUpdateMastery }) {
  const [deck, setDeck] = useState(cards);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [knownSet, setKnownSet] = useState(new Set());

  useEffect(() => {
    setDeck(cards);
    setCurrentIndex(0);
    setIsFlipped(false);
  }, [cards]);

  // Keyboard navigation support
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === ' ' || e.key === 'Spacebar') {
        e.preventDefault();
        setIsFlipped((prev) => !prev);
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        handleNext();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        handlePrev();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, deck.length]);

  if (!deck || deck.length === 0) {
    return (
      <div className="p-8 text-center bg-white border border-slate-200 rounded-xl text-slate-500">
        No flashcards generated for this deck yet.
      </div>
    );
  }

  const currentCard = deck[currentIndex];
  const isKnown = knownSet.has(currentCard?.id);

  const handleNext = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev + 1) % deck.length);
  };

  const handlePrev = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev - 1 + deck.length) % deck.length);
  };

  const handleToggleKnown = () => {
    const newKnown = new Set(knownSet);
    const targetStatus = !isKnown;
    if (targetStatus) {
      newKnown.add(currentCard.id);
    } else {
      newKnown.delete(currentCard.id);
    }
    setKnownSet(newKnown);

    if (onUpdateMastery) {
      onUpdateMastery(currentCard.id, targetStatus);
    }
  };

  const handleShuffle = () => {
    const shuffled = [...deck].sort(() => Math.random() - 0.5);
    setDeck(shuffled);
    setCurrentIndex(0);
    setIsFlipped(false);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-xs p-6 text-left space-y-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-100">
        <div>
          <h3 className="text-base font-bold text-slate-900">Flashcard Deck</h3>
          <p className="text-xs text-slate-500 mt-0.5">{documentTitle || 'Selected Document'}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="indigo">
            Card {currentIndex + 1} of {deck.length}
          </Badge>
          <Badge variant="emerald">
            Mastered: {knownSet.size} / {deck.length}
          </Badge>
          <Button variant="ghost" size="sm" onClick={handleShuffle} icon={Shuffle}>
            Shuffle
          </Button>
        </div>
      </div>

      {/* Interactive 3D Flip Card */}
      <div
        onClick={() => setIsFlipped(!isFlipped)}
        className="w-full min-h-[260px] cursor-pointer perspective-1000 group focus:outline-none"
        role="button"
        tabIndex={0}
        aria-label="Click or press space to flip card"
      >
        <div
          className={`w-full h-full min-h-[260px] p-8 rounded-2xl border transition-all duration-500 flex flex-col items-center justify-center text-center shadow-sm relative ${
            isFlipped
              ? 'bg-indigo-900 text-white border-indigo-800'
              : 'bg-slate-50 text-slate-900 border-slate-200 hover:border-slate-300 hover:bg-slate-100/60'
          }`}
        >
          <span
            className={`absolute top-4 left-4 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
              isFlipped ? 'bg-indigo-800 text-indigo-200' : 'bg-slate-200 text-slate-700'
            }`}
          >
            {isFlipped ? 'Card Back (Answer)' : 'Card Front (Question)'}
          </span>

          <p className={`text-base sm:text-lg font-medium leading-relaxed max-w-lg ${isFlipped ? 'text-white' : 'text-slate-900'}`}>
            {isFlipped ? currentCard.back : currentCard.front}
          </p>

          <span className={`absolute bottom-4 text-xs font-medium ${isFlipped ? 'text-indigo-300' : 'text-slate-400'}`}>
            Click or press [Space] to flip
          </span>
        </div>
      </div>

      {/* Mastery & Navigation Controls */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-100">
        <Button variant="outline" size="md" onClick={handlePrev} icon={ChevronLeft}>
          Previous
        </Button>

        <Button
          variant={isKnown ? 'emerald' : 'outline'}
          size="md"
          onClick={handleToggleKnown}
          icon={isKnown ? CheckCircle2 : BookmarkPlus}
          className={isKnown ? 'bg-emerald-600 text-white hover:bg-emerald-700' : ''}
        >
          {isKnown ? 'Mastered' : 'Mark as Known'}
        </Button>

        <Button variant="outline" size="md" onClick={handleNext}>
          <span className="flex items-center gap-1">
            Next <ChevronRight className="w-4 h-4" />
          </span>
        </Button>
      </div>

      {/* Keyboard Shortcut Hints */}
      <div className="text-center text-[11px] text-slate-400 pt-1">
        Keyboard shortcuts: <strong>Space</strong> (flip), <strong>Left Arrow</strong> (prev), <strong>Right Arrow</strong> (next)
      </div>
    </div>
  );
}
