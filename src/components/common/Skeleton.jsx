import React from 'react';

export function Skeleton({ className = '', variant = 'text' }) {
  const base = 'animate-pulse bg-slate-200 rounded';
  
  if (variant === 'circle') {
    return <div className={`${base} rounded-full ${className}`} />;
  }
  
  if (variant === 'card') {
    return (
      <div className={`p-4 border border-slate-200 rounded-xl space-y-3 ${className}`}>
        <div className="h-4 bg-slate-200 rounded w-3/4 animate-pulse" />
        <div className="h-3 bg-slate-200 rounded w-1/2 animate-pulse" />
        <div className="h-16 bg-slate-100 rounded w-full animate-pulse mt-2" />
      </div>
    );
  }

  return <div className={`${base} h-4 ${className}`} />;
}
