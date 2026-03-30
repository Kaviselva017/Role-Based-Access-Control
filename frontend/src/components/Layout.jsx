import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/Layout.css';

const Layout = ({ children }) => {
  const { user, logout, hasPermission } = useContext(AuthContext);

  if (!user) return children;

  return (
    <div className="layout-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="dragon-icon">🐉</div>
          <h1>DRAGON</h1>
          <p>INTELLIGENCE PLATFORM</p>
        </div>

        <div className="user-info">
          <p className="username">{user.username}</p>
          <span className={`role-badge role-${user.role}`}>{user.role.toUpperCase()}</span>
        </div>

        <nav className="navigation">
          <a href="/chat" className="nav-item">
            <span className="nav-icon">💬</span>
            <span>Chat</span>
          </a>

          <a href="/history" className="nav-item">
            <span className="nav-icon">📜</span>
            <span>History</span>
          </a>

          {hasPermission('upload_docs') && (
            <a href="/upload" className="nav-item">
              <span className="nav-icon">📤</span>
              <span>Upload Docs</span>
            </a>
          )}

          {hasPermission('view_dashboard') && (
            <a href="/dashboard" className="nav-item">
              <span className="nav-icon">📊</span>
              <span>Dashboard</span>
            </a>
          )}

          {hasPermission('manage_users') && (
            <a href="/users" className="nav-item">
              <span className="nav-icon">👥</span>
              <span>Users</span>
            </a>
          )}

          {hasPermission('generate_keys') && (
            <a href="/access-keys" className="nav-item">
              <span className="nav-icon">🔑</span>
              <span>Access Keys</span>
            </a>
          )}
        </nav>

        <button onClick={logout} className="logout-btn">
          <span className="nav-icon">🚪</span>
          <span>LOGOUT</span>
        </button>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};

export default Layout;
