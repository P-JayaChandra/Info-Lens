import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

export function ErrorMessage({
  title = 'Request Failed',
  message = 'An unexpected error occurred while communicating with the service.',
  onRetry,
  className = ''
}) {
  return (
    <div className={`p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-left ${className}`}>
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-sm font-semibold text-rose-950">{title}</h4>
          <p className="text-xs text-rose-700 mt-0.5 leading-relaxed">{message}</p>
        </div>
      </div>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry} icon={RefreshCw} className="border-rose-300 text-rose-800 hover:bg-rose-100 shrink-0">
          Retry
        </Button>
      )}
    </div>
  );
}
