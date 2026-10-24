// Gốc ứng dụng: TanStack Query, router với các tuyến /login, /, /sources/:id, /admin/access,
// /admin/audit, /reports; AuthGate bọc toàn bộ.
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AccessPage } from '../features/admin/AccessPage';
import { AuditPage } from '../features/admin/AuditPage';
import { LoginPage } from '../features/auth/LoginPage';
import { MainPage } from '../features/chat/MainPage';
import { ReportsPage } from '../features/reports/ReportsPage';
import { SourceViewerPage } from '../features/sources/SourceViewerPage';
import '../styles/app.css';
import { AuthProvider, RequireRole } from './auth';

export function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, refetchOnWindowFocus: false },
      mutations: { retry: false },
    },
  });
}

export function AppRoutes() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <RequireRole roles={['bd']}>
              <MainPage />
            </RequireRole>
          }
        />
        <Route
          path="/sources/:documentId"
          element={
            <RequireRole roles={['bd']}>
              <SourceViewerPage />
            </RequireRole>
          }
        />
        <Route
          path="/admin/access"
          element={
            <RequireRole roles={['security_admin']}>
              <AccessPage />
            </RequireRole>
          }
        />
        <Route
          path="/admin/audit"
          element={
            <RequireRole roles={['security_admin']}>
              <AuditPage />
            </RequireRole>
          }
        />
        <Route
          path="/reports"
          element={
            <RequireRole roles={['manager']}>
              <ReportsPage />
            </RequireRole>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export function App() {
  const [queryClient] = useState(makeQueryClient);
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
