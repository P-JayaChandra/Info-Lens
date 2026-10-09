import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, X, AlertCircle, CheckCircle2, Loader2, RefreshCw } from 'lucide-react';
import { Button } from '../common/Button';
import { validateFile, SUPPORTED_FILE_EXTENSIONS } from '../../utils/validators';
import { formatBytes } from '../../utils/formatters';
import { useDocuments } from '../../context/DocumentContext';
import { useToast } from '../../context/ToastContext';

export function DocumentUploadZone({ onUploadSuccess }) {
  const { uploadFile, uploadState, setUploadState } = useDocuments();
  const { addToast } = useToast();
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [validationError, setValidationError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    setValidationError(null);
    if (!file) return;

    const validation = validateFile(file);
    if (!validation.valid) {
      setValidationError(validation.error);
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
    setUploadState({ status: 'Selected', progress: 0, error: null, currentFile: file });
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setValidationError(null);
    setUploadState({ status: null, progress: 0, error: null, currentFile: null });
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSubmitUpload = async () => {
    if (!selectedFile) return;
    try {
      const doc = await uploadFile(selectedFile);
      addToast(`Document "${doc.title}" processed successfully!`, 'success');
      setSelectedFile(null);
      if (onUploadSuccess) onUploadSuccess(doc);
    } catch (err) {
      addToast(err.message || 'Upload failed', 'error');
    }
  };

  const { status, progress, error: uploadError } = uploadState;
  const isUploading = status === 'Uploading' || status === 'Processing';

  return (
    <div className="w-full bg-white border border-slate-200 rounded-xl p-6 shadow-xs text-left">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-slate-900">Upload Research Document</h3>
        <span className="text-xs text-slate-500 font-medium">
          Supported: {SUPPORTED_FILE_EXTENSIONS.join(', ').toUpperCase()} (Max 25 MB)
        </span>
      </div>

      {!selectedFile ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all ${
            dragActive
              ? 'border-indigo-500 bg-indigo-50/50'
              : 'border-slate-300 bg-slate-50/50 hover:border-slate-400 hover:bg-slate-100/50'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
            className="hidden"
          />
          <div className="p-3 bg-white rounded-full shadow-xs border border-slate-200 text-indigo-600 mb-3">
            <UploadCloud className="w-6 h-6" />
          </div>
          <p className="text-sm font-semibold text-slate-800">
            Click to upload <span className="font-normal text-slate-500">or drag and drop</span>
          </p>
          <p className="text-xs text-slate-500 mt-1">PDF, DOCX, or TXT documents up to 25 MB</p>
        </div>
      ) : (
        <div className="p-4 border border-slate-200 rounded-xl bg-slate-50 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="p-2.5 bg-white border border-slate-200 rounded-lg text-indigo-600 shrink-0">
                <FileText className="w-5 h-5" />
              </div>
              <div className="overflow-hidden text-left">
                <h4 className="text-sm font-semibold text-slate-900 truncate">{selectedFile.name}</h4>
                <p className="text-xs text-slate-500">{formatBytes(selectedFile.size)}</p>
              </div>
            </div>
            {!isUploading && (
              <button
                onClick={handleRemoveFile}
                className="text-slate-400 hover:text-rose-600 p-1 rounded-md transition-colors"
                title="Remove file"
                aria-label="Remove selected file"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Upload & Processing Progress Bar */}
          {isUploading && (
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs font-medium text-slate-700">
                <span className="flex items-center gap-1.5 text-indigo-600">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  {status === 'Uploading' ? `Uploading... (${progress}%)` : 'Backend processing & vector indexing...'}
                </span>
                <span>{progress}%</span>
              </div>
              <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-600 transition-all duration-300 rounded-full"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Action Buttons */}
          {!isUploading && status !== 'Ready' && (
            <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-slate-200">
              <Button variant="outline" size="sm" onClick={handleRemoveFile}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" onClick={handleSubmitUpload}>
                Upload & Process
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Validation & Server Error Messages */}
      {(validationError || uploadError) && (
        <div className="mt-3 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{validationError || uploadError}</span>
        </div>
      )}
    </div>
  );
}
