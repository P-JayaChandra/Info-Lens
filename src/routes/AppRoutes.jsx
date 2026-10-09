import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { LandingPage } from '../pages/Landing/LandingPage';
import { LoginPage } from '../pages/Auth/LoginPage';
import { RegisterPage } from '../pages/Auth/RegisterPage';
import { DashboardPage } from '../pages/Dashboard/DashboardPage';
import { DocumentsPage } from '../pages/Documents/DocumentsPage';
import { ChatPage } from '../pages/Chat/ChatPage';
import { SummariesPage } from '../pages/Summaries/SummariesPage';
import { QuestionsPage } from '../pages/Questions/QuestionsPage';
import { QuizPage } from '../pages/Quiz/QuizPage';
import { FlashcardsPage } from '../pages/Flashcards/FlashcardsPage';
import { HistoryPage } from '../pages/History/HistoryPage';
import { SettingsPage } from '../pages/Settings/SettingsPage';
import { NotFoundPage } from '../pages/NotFoundPage';

import { ApplicationShell } from '../components/layout/ApplicationShell';
import { ProtectedRoute } from './ProtectedRoute';

export function AppRoutes() {
  return (
    <Routes>
      {/* Public Landing & Auth Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Authenticated Application Shell Routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<ApplicationShell />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/summaries" element={<SummariesPage />} />
          <Route path="/questions" element={<QuestionsPage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/flashcards" element={<FlashcardsPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Route>

      {/* Fallback 404 Route */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
