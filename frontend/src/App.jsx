import React, { useContext, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext, AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import Chat from './pages/Chat';
import Dashboard from './pages/Dashboard';
import UserManagement from './pages/UserManagement';
import DocumentUpload from './pages/DocumentUpload';
import AccessKeys from './pages/AccessKeys';
import ChatHistory from './pages/ChatHistory';
import './styles/App.css';

// Protected Route Component
const ProtectedRoute = ({ children, requiredPermission }) => {
  const { user, loading, hasPermission } = useContext(AuthContext);

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      <div className="access-denied">
        <h1>⚠️ Access Denied</h1>
        <p>You don't have permission to access this page.</p>
        <a href="/chat">Go back to chat</a>
      </div>
    );
  }

  return <Layout>{children}</Layout>;
};

const AppRoutes = () => {
  const { user, loading } = useContext(AuthContext);

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<LoginPage />} />

      {/* Protected Routes */}
      <Route
        path="/chat"
        element={
          <ProtectedRoute requiredPermission="chat">
            <Chat />
          </ProtectedRoute>
        }
      />

      <Route
        path="/history"
        element={
          <ProtectedRoute requiredPermission="view_history">
            <ChatHistory />
          </ProtectedRoute>
        }
      />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute requiredPermission="view_dashboard">
            <Dashboard />
          </ProtectedRoute>
        }
      />

      <Route
        path="/upload"
        element={
          <ProtectedRoute requiredPermission="upload_docs">
            <DocumentUpload />
          </ProtectedRoute>
        }
      />

      <Route
        path="/users"
        element={
          <ProtectedRoute requiredPermission="manage_users">
            <UserManagement />
          </ProtectedRoute>
        }
      />

      <Route
        path="/access-keys"
        element={
          <ProtectedRoute requiredPermission="generate_keys">
            <AccessKeys />
          </ProtectedRoute>
        }
      />

      {/* Default redirect */}
      <Route
        path="/"
        element={user ? <Navigate to="/chat" /> : <Navigate to="/login" />}
      />

      {/* 404 Fallback */}
      <Route path="*" element={<Navigate to="/chat" />} />
    </Routes>
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;
