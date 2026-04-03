import React, { useContext } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import '../styles/Layout.css';

const Layout = ({ children }) => {
  const { user, logout, hasPermission } = useContext(AuthContext);
  const location = useLocation();
  const [isSidebarOpen, setSidebarOpen] = React.useState(false);

  if (!user) return children;

  const isActive = (path) => location.pathname === path;
  const toggleSidebar = () => setSidebarOpen(!isSidebarOpen);

  return (
    <div className={`layout-container ${isSidebarOpen ? 'sidebar-open' : ''}`}>
      {/* Mobile Top Bar */}
      <header className="mobile-header">
        <button className="hamburger-btn" onClick={toggleSidebar}>
          {isSidebarOpen ? '✕' : '☰'}
        </button>
        <div className="mobile-logo">DRAGON</div>
        <div className="user-icon-mobile">{user.username.charAt(0).toUpperCase()}</div>
      </header>

      {/* Sidebar Navigation */}
      <aside className={`sidebar ${isSidebarOpen ? 'active' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <span className="logo-hex">⬡</span>
            <div className="logo-text">
              <h1>DRAGON</h1>
              <p>TERMINAL</p>
            </div>
          </div>
          <div className="header-line"></div>
        </div>

        <div className="user-info">
          <div className="user-avatar-cyber">
            {user.username.charAt(0).toUpperCase()}
          </div>
          <div className="user-meta">
            <p className="username">{user.username}</p>
            <span className={`role-badge role-${user.role}`}>{user.role.toUpperCase()}</span>
          </div>
          <div className="user-status-indicator">
            <span className="status-dot-online"></span>
          </div>
        </div>

        <nav className="navigation">
          <Link to="/chat" state={{ newChat: true }} className="new-chat-btn">
            <span className="nav-icon-cyber">+</span>
            <span>NEW SESSION</span>
          </Link>

          <div className="nav-section-label">OPERATIONS</div>

          <Link to="/chat" className={`nav-item ${isActive('/chat') ? 'active' : ''}`}>
            <span className="nav-icon-cyber">⌘</span>
            <span>Chat Terminal</span>
            <span className="nav-indicator"></span>
          </Link>

          <Link to="/history" className={`nav-item ${isActive('/history') ? 'active' : ''}`}>
            <span className="nav-icon-cyber">◷</span>
            <span>Query History</span>
            <span className="nav-indicator"></span>
          </Link>

          {hasPermission('upload_docs') && (
            <>
              <div className="nav-section-label">ADMIN PORTAL</div>
              <Link to="/upload" className={`nav-item ${isActive('/upload') ? 'active' : ''}`}>
                <span className="nav-icon-cyber">↑</span>
                <span>Upload Docs</span>
                <span className="nav-indicator"></span>
              </Link>
            </>
          )}

          {hasPermission('view_dashboard') && (
            <Link to="/dashboard" className={`nav-item ${isActive('/dashboard') ? 'active' : ''}`}>
              <span className="nav-icon-cyber">◈</span>
              <span>Dashboard</span>
              <span className="nav-indicator"></span>
            </Link>
          )}

          {hasPermission('manage_users') && (
            <Link to="/users" className={`nav-item ${isActive('/users') ? 'active' : ''}`}>
              <span className="nav-icon-cyber">⊞</span>
              <span>User Mgmt</span>
              <span className="nav-indicator"></span>
            </Link>
          )}

          {hasPermission('generate_keys') && (
            <Link to="/access-keys" className={`nav-item ${isActive('/access-keys') ? 'active' : ''}`}>
              <span className="nav-icon-cyber">⚿</span>
              <span>Access Keys</span>
              <span className="nav-indicator"></span>
            </Link>
          )}
        </nav>

        <div className="sidebar-footer">
          <div className="system-info-bar">
            <span className="sys-label">NODE</span>
            <span className="sys-value">DI-492</span>
            <span className="sys-separator">·</span>
            <span className="sys-label">ENC</span>
            <span className="sys-value">AES-256</span>
          </div>
          <button onClick={logout} className="logout-btn">
            <span className="nav-icon-cyber">⏻</span>
            <span>DISCONNECT</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};

export default Layout;
