import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { documentApi } from '../api/documentApi';

const DocumentContext = createContext(null);

export function DocumentProvider({ children }) {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Upload status states: 'Selected' | 'Uploading' | 'Uploaded' | 'Processing' | 'Ready' | 'Failed'
  const [uploadState, setUploadState] = useState({
    status: null,
    progress: 0,
    error: null,
    currentFile: null,
  });

  const fetchDocuments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const docs = await documentApi.getDocuments();
      setDocuments(docs);
      if (!selectedDocument && docs.length > 0) {
        setSelectedDocument(docs[0]);
      }
    } catch (err) {
      console.error('Failed to load documents:', err);
      setError(err.message || 'Failed to retrieve documents');
    } finally {
      setLoading(false);
    }
  }, [selectedDocument]);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const selectDocument = useCallback((doc) => {
    setSelectedDocument(doc);
  }, []);

  const uploadFile = async (file) => {
    setUploadState({ status: 'Uploading', progress: 0, error: null, currentFile: file });
    try {
      const newDoc = await documentApi.uploadDocument(file, (percent) => {
        setUploadState((prev) => ({
          ...prev,
          progress: percent,
          status: percent === 100 ? 'Uploaded' : 'Uploading',
        }));
      });

      // Mark processing and then confirmed ready by backend response
      setUploadState({ status: 'Processing', progress: 100, error: null, currentFile: file });
      await new Promise((r) => setTimeout(r, 400));

      setUploadState({ status: 'Ready', progress: 100, error: null, currentFile: null });
      setDocuments((prev) => [newDoc, ...prev.filter((d) => d.id !== newDoc.id)]);
      setSelectedDocument(newDoc);
      return newDoc;
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'Document upload failed';
      setUploadState({ status: 'Failed', progress: 0, error: errMsg, currentFile: file });
      throw new Error(errMsg);
    }
  };

  const deleteDoc = async (id) => {
    try {
      await documentApi.deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
      if (selectedDocument?.id === id) {
        const remaining = documents.filter((d) => d.id !== id);
        setSelectedDocument(remaining.length > 0 ? remaining[0] : null);
      }
    } catch (err) {
      throw new Error(err.message || 'Failed to delete document');
    }
  };

  const renameDoc = async (id, newTitle) => {
    try {
      const updated = await documentApi.renameDocument(id, newTitle);
      setDocuments((prev) => prev.map((d) => (d.id === id ? updated : d)));
      if (selectedDocument?.id === id) {
        setSelectedDocument(updated);
      }
      return updated;
    } catch (err) {
      throw new Error(err.message || 'Failed to rename document');
    }
  };

  return (
    <DocumentContext.Provider
      value={{
        documents,
        selectedDocument,
        loading,
        error,
        uploadState,
        setUploadState,
        fetchDocuments,
        selectDocument,
        uploadFile,
        deleteDoc,
        renameDoc,
      }}
    >
      {children}
    </DocumentContext.Provider>
  );
}

export function useDocuments() {
  const context = useContext(DocumentContext);
  if (!context) {
    throw new Error('useDocuments must be used within a DocumentProvider');
  }
  return context;
}
