import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './Button';

export function Pagination({ currentPage, totalPages, onPageChange, className = '' }) {
  if (totalPages <= 1) return null;

  return (
    <div className={`flex items-center justify-between px-4 py-3 border-t border-slate-200 text-xs text-slate-600 ${className}`}>
      <span>
        Page <strong className="font-semibold text-slate-900">{currentPage}</strong> of <strong className="font-semibold text-slate-900">{totalPages}</strong>
      </span>
      <div className="flex items-center gap-1.5">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          isDisabled={currentPage <= 1}
          icon={ChevronLeft}
        >
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          isDisabled={currentPage >= totalPages}
        >
          <span className="flex items-center gap-1">
            Next <ChevronRight className="w-3.5 h-3.5" />
          </span>
        </Button>
      </div>
    </div>
  );
}
