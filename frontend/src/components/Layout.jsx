import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
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
          <Link to="/chat" state={{ newChat: true }} className="new-chat-btn">
            <span className="nav-icon">➕</span>
            <span>New Chat</span>
          </Link>

          <Link to="/chat" className="nav-item">
            <span className="nav-icon">💬</span>
            <span>Chat</span>
          </Link>

          <Link to="/history" className="nav-item">
            <span className="nav-icon">📜</span>
            <span>History</span>
          </Link>

          {hasPermission('upload_docs') && (
            <Link to="/upload" className="nav-item">
              <span className="nav-icon">📤</span>
              <span>Upload Docs</span>
            </Link>
          )}

          {hasPermission('view_dashboard') && (
            <Link to="/dashboard" className="nav-item">
              <span className="nav-icon">📊</span>
              <span>Dashboard</span>
            </Link>
          )}

          {hasPermission('manage_users') && (
            <Link to="/users" className="nav-item">
              <span className="nav-icon">👥</span>
              <span>Users</span>
            </Link>
          )}

          {hasPermission('generate_keys') && (
            <Link to="/access-keys" className="nav-item">
              <span className="nav-icon">🔑</span>
              <span>Access Keys</span>
            </Link>
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
