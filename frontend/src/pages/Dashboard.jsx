import React, { useState, useEffect, useContext, useCallback } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/Dashboard.css';
import { API_BASE_URL as API_BASE } from '../services/api';

const ROLE_COLORS = {
  'admin': '#ff3366',
  'c-level': '#ff8800',
  'finance': '#00ffff',
  'hr': '#00ff88',
  'marketing': '#ff69b4',
  'engineering': '#6495ed',
  'employee': '#a855f7',
  'unknown': '#5a7a8a',
};

const SEVERITY_CONFIG = {
  high: { icon: '🔴', color: '#ff3366', bg: 'rgba(255,51,102,0.06)', border: '#ff3366' },
  medium: { icon: '🟠', color: '#ff8800', bg: 'rgba(255,136,0,0.06)', border: '#ff8800' },
  warning: { icon: '🟡', color: '#ffcc00', bg: 'rgba(255,204,0,0.06)', border: '#ffcc00' },
  info: { icon: '🔵', color: '#00ffff', bg: 'rgba(0,255,255,0.06)', border: '#00ffff' },
};

const formatDate = (iso) => {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { day: '2-digit', month: 'short' }) + ' ' +
    d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
};

const formatShortDate = (iso) => {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

const Dashboard = () => {
  const { token } = useContext(AuthContext);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [userSearch, setUserSearch] = useState('');
  const [userSortField, setUserSortField] = useState('last_active');
  const [userSortDir, setUserSortDir] = useState('desc');
  const [isLive, setIsLive] = useState(true);

  const loadDashboard = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/dashboard/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const result = await response.json();
        setData(result);
        setLastRefresh(new Date());
        setError(null);
      } else {
        setError('Failed to load dashboard data');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  // Auto-refresh every 30 seconds if live
  useEffect(() => {
    if (!isLive) return;
    const interval = setInterval(loadDashboard, 30000);
    return () => clearInterval(interval);
  }, [isLive, loadDashboard]);

  // Sort + filter users
  const getFilteredUsers = () => {
    if (!data?.users) return [];
    let users = [...data.users];
    if (userSearch) {
      const q = userSearch.toLowerCase();
      users = users.filter(u =>
        u.username.toLowerCase().includes(q) ||
        u.email.toLowerCase().includes(q) ||
        u.role.toLowerCase().includes(q) ||
        u.department.toLowerCase().includes(q)
      );
    }
    users.sort((a, b) => {
      let valA = a[userSortField];
      let valB = b[userSortField];
      if (typeof valA === 'string') valA = valA?.toLowerCase() || '';
      if (typeof valB === 'string') valB = valB?.toLowerCase() || '';
      if (valA === null || valA === undefined) valA = '';
      if (valB === null || valB === undefined) valB = '';
      if (valA < valB) return userSortDir === 'asc' ? -1 : 1;
      if (valA > valB) return userSortDir === 'asc' ? 1 : -1;
      return 0;
    });
    return users;
  };

  const handleSort = (field) => {
    if (userSortField === field) {
      setUserSortDir(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      setUserSortField(field);
      setUserSortDir('desc');
    }
  };

  const getSortIcon = (field) => {
    if (userSortField !== field) return '⇅';
    return userSortDir === 'asc' ? '↑' : '↓';
  };

  if (loading) {
    return (
      <div className="dash-loading">
        <div className="dash-loading-spinner"></div>
        <p>Initializing Dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dash-error">
        <div className="dash-error-icon">⚠️</div>
        <h2>Dashboard Error</h2>
        <p>{error}</p>
        <button onClick={loadDashboard} className="dash-retry-btn">Retry</button>
      </div>
    );
  }

  const stats = data?.stats || {};
  const dailyActivity = data?.daily_activity || [];
  const topQueries = data?.top_queries || [];
  const topDenied = data?.top_denied || [];
  const securityIssues = data?.security_issues || [];
  const documents = data?.documents || { total: 0, by_department: [] };
  const peakHours = data?.peak_hours || [];
  const maxDaily = Math.max(...dailyActivity.map(d => d.count), 1);

  // SVG Activity Chart computations
  const chartW = 600;
  const chartH = 160;
  const chartPad = 30;
  const usableW = chartW - chartPad * 2;
  const usableH = chartH - chartPad * 2;
  const activityPoints = dailyActivity.map((d, i) => ({
    x: chartPad + (i / Math.max(dailyActivity.length - 1, 1)) * usableW,
    y: chartPad + usableH - (d.count / maxDaily) * usableH,
    ...d
  }));
  const linePath = activityPoints.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ');
  const areaPath = linePath + ` L${activityPoints[activityPoints.length - 1]?.x || 0},${chartH - chartPad} L${chartPad},${chartH - chartPad} Z`;

  // Role distribution donut
  const roleData = stats.role_distribution || [];
  const totalRoleUsers = roleData.reduce((s, r) => s + r.count, 0) || 1;

  return (
    <div className="dash-container">
      {/* ═══ HEADER ═══ */}
      <header className="dash-header">
        <div className="dash-header-left">
          <h1 className="dash-title">
            <span className="dash-title-icon">📊</span>
            ANALYTICS DASHBOARD
          </h1>
          <span className="dash-subtitle">Dragon Intelligence Platform — Admin Control Center</span>
        </div>
        <div className="dash-header-right">
          <button
            className={`dash-live-btn ${isLive ? 'active' : ''}`}
            onClick={() => setIsLive(!isLive)}
          >
            <span className="live-dot"></span>
            {isLive ? 'LIVE' : 'PAUSED'}
          </button>
          {lastRefresh && (
            <span className="dash-last-refresh">
              Updated {lastRefresh.toLocaleTimeString()}
            </span>
          )}
          <button className="dash-refresh-btn" onClick={loadDashboard}>
            ↻ Refresh
          </button>
        </div>
      </header>

      {/* ═══ TAB NAV ═══ */}
      <nav className="dash-tabs">
        {[
          { key: 'overview', label: 'Overview', icon: '📈' },
          { key: 'users', label: 'Users & Activity', icon: '👥' },
          { key: 'security', label: 'Security & Issues', icon: '🛡️' },
        ].map(tab => (
          <button
            key={tab.key}
            className={`dash-tab ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            <span>{tab.icon}</span> {tab.label}
            {tab.key === 'security' && securityIssues.length > 0 && (
              <span className="tab-badge">{securityIssues.length}</span>
            )}
          </button>
        ))}
      </nav>

      {/* ═══ OVERVIEW TAB ═══ */}
      {activeTab === 'overview' && (
        <>
          {/* Stat Cards */}
          <div className="dash-stats-grid">
            <div className="dash-stat-card stat-queries">
              <div className="stat-card-icon">💬</div>
              <div className="stat-card-content">
                <div className="stat-card-label">TOTAL QUERIES</div>
                <div className="stat-card-value">{stats.total_queries || 0}</div>
                <div className="stat-card-sub">all time</div>
              </div>
              <div className="stat-card-glow"></div>
            </div>

            <div className="dash-stat-card stat-users">
              <div className="stat-card-icon">👥</div>
              <div className="stat-card-content">
                <div className="stat-card-label">TOTAL USERS</div>
                <div className="stat-card-value">{stats.total_users || 0}</div>
                <div className="stat-card-sub">registered</div>
              </div>
              <div className="stat-card-glow"></div>
            </div>

            <div className="dash-stat-card stat-denied">
              <div className="stat-card-icon">🚫</div>
              <div className="stat-card-content">
                <div className="stat-card-label">ACCESS DENIED</div>
                <div className="stat-card-value">{stats.access_denied || 0}</div>
                <div className="stat-card-sub">blocked attempts</div>
              </div>
              <div className="stat-card-glow"></div>
            </div>

            <div className="dash-stat-card stat-active">
              <div className="stat-card-icon">⚡</div>
              <div className="stat-card-content">
                <div className="stat-card-label">ACTIVE TODAY</div>
                <div className="stat-card-value">{stats.active_today || 0}</div>
                <div className="stat-card-sub">unique users</div>
              </div>
              <div className="stat-card-glow"></div>
            </div>

            <div className="dash-stat-card stat-docs">
              <div className="stat-card-icon">📄</div>
              <div className="stat-card-content">
                <div className="stat-card-label">DOCUMENTS</div>
                <div className="stat-card-value">{stats.total_documents || 0}</div>
                <div className="stat-card-sub">in knowledge base</div>
              </div>
              <div className="stat-card-glow"></div>
            </div>

            <div className="dash-stat-card stat-resolution">
              <div className="stat-card-icon">✅</div>
              <div className="stat-card-content">
                <div className="stat-card-label">RESOLUTION RATE</div>
                <div className="stat-card-value">{stats.resolution_rate || 0}%</div>
                <div className="stat-card-sub">queries resolved</div>
              </div>
              <div className="stat-card-glow"></div>
            </div>
          </div>

          {/* Charts Row */}
          <div className="dash-charts-row">
            {/* Queries by Role */}
            <div className="dash-panel queries-role-panel">
              <div className="panel-header">
                <h3><span className="panel-icon">📊</span> QUERIES BY ROLE</h3>
              </div>
              <div className="role-bars-container">
                {(stats.queries_by_role || []).map(item => {
                  const maxCount = Math.max(...(stats.queries_by_role || []).map(r => r.count), 1);
                  const pct = (item.count / maxCount) * 100;
                  return (
                    <div key={item.role} className="role-bar-row">
                      <div className="role-bar-label">{item.role}</div>
                      <div className="role-bar-track">
                        <div
                          className="role-bar-fill"
                          style={{
                            width: `${pct}%`,
                            background: `linear-gradient(90deg, ${ROLE_COLORS[item.role] || '#888'}, ${ROLE_COLORS[item.role] || '#888'}88)`
                          }}
                        ></div>
                      </div>
                      <div className="role-bar-count">{item.count}</div>
                    </div>
                  );
                })}
                {(!stats.queries_by_role || stats.queries_by_role.length === 0) && (
                  <div className="dash-empty">No query data yet</div>
                )}
              </div>
            </div>

            {/* Activity Chart */}
            <div className="dash-panel activity-panel">
              <div className="panel-header">
                <h3><span className="panel-icon">📈</span> ACTIVITY — LAST 7 DAYS</h3>
              </div>
              <div className="activity-chart-wrapper">
                <svg viewBox={`0 0 ${chartW} ${chartH}`} className="activity-svg" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#00ffff" stopOpacity="0.25" />
                      <stop offset="100%" stopColor="#00ffff" stopOpacity="0.02" />
                    </linearGradient>
                    <filter id="glow">
                      <feGaussianBlur stdDeviation="3" result="blur" />
                      <feMerge>
                        <feMergeNode in="blur" />
                        <feMergeNode in="SourceGraphic" />
                      </feMerge>
                    </filter>
                  </defs>
                  {/* Grid lines */}
                  {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => (
                    <line key={i} x1={chartPad} y1={chartPad + usableH * pct} x2={chartW - chartPad} y2={chartPad + usableH * pct}
                      stroke="rgba(0,255,255,0.06)" strokeWidth="1" strokeDasharray="4,4" />
                  ))}
                  {/* Area */}
                  <path d={areaPath} fill="url(#areaGrad)" />
                  {/* Line */}
                  <path d={linePath} fill="none" stroke="#00ffff" strokeWidth="2" filter="url(#glow)" strokeLinejoin="round" />
                  {/* Data points */}
                  {activityPoints.map((p, i) => (
                    <g key={i}>
                      <circle cx={p.x} cy={p.y} r="4" fill="#050a18" stroke="#00ffff" strokeWidth="2" />
                      <circle cx={p.x} cy={p.y} r="2" fill="#00ffff" />
                      <text x={p.x} y={chartH - 8} textAnchor="middle" fill="#888" fontSize="10" fontFamily="inherit">
                        {formatShortDate(p.date)}
                      </text>
                      <text x={p.x} y={p.y - 12} textAnchor="middle" fill="#00ffff" fontSize="11" fontWeight="600" fontFamily="inherit">
                        {p.count}
                      </text>
                    </g>
                  ))}
                </svg>
              </div>
            </div>
          </div>

          {/* Role Distribution + Peak Hours */}
          <div className="dash-charts-row">
            {/* Role Distribution Donut */}
            <div className="dash-panel role-dist-panel">
              <div className="panel-header">
                <h3><span className="panel-icon">🎯</span> ROLE DISTRIBUTION</h3>
              </div>
              <div className="donut-container">
                <svg viewBox="0 0 200 200" className="donut-svg">
                  {(() => {
                    let cumAngle = -90;
                    return roleData.map((item, i) => {
                      const angle = (item.count / totalRoleUsers) * 360;
                      const startAngle = cumAngle;
                      cumAngle += angle;
                      const r = 70;
                      const cx = 100, cy = 100;
                      const startRad = (startAngle * Math.PI) / 180;
                      const endRad = ((startAngle + angle) * Math.PI) / 180;
                      const x1 = cx + r * Math.cos(startRad);
                      const y1 = cy + r * Math.sin(startRad);
                      const x2 = cx + r * Math.cos(endRad);
                      const y2 = cy + r * Math.sin(endRad);
                      const largeArc = angle > 180 ? 1 : 0;
                      const pathD = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`;
                      return (
                        <path key={i} d={pathD} fill={ROLE_COLORS[item.role] || '#5a7a8a'} stroke="#050a18" strokeWidth="2" opacity="0.85" />
                      );
                    });
                  })()}
                  <circle cx="100" cy="100" r="40" fill="#050a18" />
                  <text x="100" y="96" textAnchor="middle" fill="#f0f4ff" fontSize="20" fontWeight="700" fontFamily="inherit">{totalRoleUsers}</text>
                  <text x="100" y="112" textAnchor="middle" fill="#5a7a8a" fontSize="10" fontFamily="inherit">USERS</text>
                </svg>
                <div className="donut-legend">
                  {roleData.map((item, i) => (
                    <div key={i} className="legend-item">
                      <span className="legend-dot" style={{ background: ROLE_COLORS[item.role] || '#888' }}></span>
                      <span className="legend-label">{item.role}</span>
                      <span className="legend-count">{item.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Peak Hours */}
            <div className="dash-panel peak-panel">
              <div className="panel-header">
                <h3><span className="panel-icon">🕐</span> PEAK USAGE HOURS</h3>
              </div>
              <div className="peak-hours-list">
                {peakHours.map((ph, i) => {
                  const maxPeak = peakHours[0]?.count || 1;
                  const pct = (ph.count / maxPeak) * 100;
                  const hourLabel = `${ph.hour.toString().padStart(2, '0')}:00`;
                  return (
                    <div key={i} className="peak-row">
                      <div className="peak-hour">{hourLabel}</div>
                      <div className="peak-bar-track">
                        <div className="peak-bar-fill" style={{ width: `${pct}%` }}>
                          <span className="peak-bar-label">{ph.count} queries</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
                {peakHours.length === 0 && <div className="dash-empty">No activity data</div>}
              </div>
            </div>
          </div>

          {/* Top Queries + Top Denied */}
          <div className="dash-charts-row">
            <div className="dash-panel top-queries-panel">
              <div className="panel-header">
                <h3><span className="panel-icon">🔥</span> TOP QUERIES</h3>
              </div>
              <div className="queries-list">
                {topQueries.map((q, i) => (
                  <div key={i} className="query-list-item">
                    <span className="query-rank">#{i + 1}</span>
                    <span className="query-arrow">▶</span>
                    <span className="query-text-content">{q.query}</span>
                    <span className="query-count-badge">{q.count}×</span>
                  </div>
                ))}
                {topQueries.length === 0 && <div className="dash-empty">No queries recorded</div>}
              </div>
            </div>

            <div className="dash-panel top-denied-panel">
              <div className="panel-header denied-header">
                <h3><span className="panel-icon">🚫</span> TOP DENIED QUERIES</h3>
              </div>
              <div className="queries-list">
                {topDenied.map((q, i) => (
                  <div key={i} className="query-list-item denied-item">
                    <span className="query-denied-icon">⊘</span>
                    <span className="query-text-content">{q.query}</span>
                    <div className="denied-badges">
                      {q.roles?.map((r, ri) => (
                        <span key={ri} className="denied-role-badge" style={{ background: ROLE_COLORS[r] || '#888', color: ['hr', 'finance'].includes(r) ? '#0a0e27' : '#fff' }}>
                          {r}
                        </span>
                      ))}
                    </div>
                    <span className="query-count-badge denied-count">{q.count}×</span>
                  </div>
                ))}
                {topDenied.length === 0 && <div className="dash-empty">No denied queries — great!</div>}
              </div>
            </div>
          </div>

          {/* Documents Panel */}
          {documents.by_department && documents.by_department.length > 0 && (
            <div className="dash-panel docs-panel">
              <div className="panel-header">
                <h3><span className="panel-icon">📁</span> DOCUMENTS BY DEPARTMENT</h3>
              </div>
              <div className="docs-dept-grid">
                {documents.by_department.map((dept, i) => (
                  <div key={i} className="doc-dept-card">
                    <div className="doc-dept-name">{dept.department}</div>
                    <div className="doc-dept-count">{dept.count}</div>
                    <div className="doc-dept-indexed">
                      <span className={`doc-indexed-dot ${dept.indexed === dept.count ? 'all' : 'partial'}`}></span>
                      {dept.indexed}/{dept.count} indexed
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* ═══ USERS TAB ═══ */}
      {activeTab === 'users' && (
        <div className="dash-users-section">
          <div className="dash-panel users-panel">
            <div className="panel-header">
              <h3><span className="panel-icon">👥</span> ALL USER ACCOUNTS & ACTIVITY</h3>
              <div className="users-header-controls">
                <div className="users-search-box">
                  <span className="search-icon">🔍</span>
                  <input
                    type="text"
                    placeholder="Search users..."
                    value={userSearch}
                    onChange={e => setUserSearch(e.target.value)}
                    className="users-search-input"
                  />
                </div>
                <span className="users-count-label">{getFilteredUsers().length} users</span>
              </div>
            </div>

            <div className="users-table-wrapper">
              <table className="users-table">
                <thead>
                  <tr>
                    <th onClick={() => handleSort('username')}>USERNAME {getSortIcon('username')}</th>
                    <th onClick={() => handleSort('email')}>EMAIL {getSortIcon('email')}</th>
                    <th onClick={() => handleSort('role')}>ROLE {getSortIcon('role')}</th>
                    <th onClick={() => handleSort('department')}>DEPT {getSortIcon('department')}</th>
                    <th onClick={() => handleSort('total_queries')}>QUERIES {getSortIcon('total_queries')}</th>
                    <th onClick={() => handleSort('denied_queries')}>DENIED {getSortIcon('denied_queries')}</th>
                    <th onClick={() => handleSort('active_keys')}>KEYS {getSortIcon('active_keys')}</th>
                    <th onClick={() => handleSort('first_seen')}>FIRST SEEN {getSortIcon('first_seen')}</th>
                    <th onClick={() => handleSort('last_active')}>LAST ACTIVE {getSortIcon('last_active')}</th>
                    <th onClick={() => handleSort('last_login')}>LAST LOGIN {getSortIcon('last_login')}</th>
                    <th>STATUS</th>
                  </tr>
                </thead>
                <tbody>
                  {getFilteredUsers().map((u) => {
                    const denialPct = u.total_queries > 0 ? Math.round(u.denied_queries / u.total_queries * 100) : 0;
                    const isHighDenial = denialPct > 50 && u.total_queries >= 3;
                    return (
                      <tr key={u.id} className={isHighDenial ? 'user-row-warning' : ''}>
                        <td className="user-cell-name">
                          <div className="user-avatar" style={{ background: ROLE_COLORS[u.role] || '#888' }}>
                            {u.username.charAt(0).toUpperCase()}
                          </div>
                          <span>{u.username}</span>
                        </td>
                        <td className="user-cell-email">{u.email}</td>
                        <td>
                          <span className="user-role-badge" style={{ background: ROLE_COLORS[u.role] || '#888', color: ['hr', 'finance'].includes(u.role) ? '#0a0e27' : '#fff' }}>
                            {u.role}
                          </span>
                        </td>
                        <td className="user-cell-dept">{u.department || '—'}</td>
                        <td className="user-cell-number">{u.total_queries}</td>
                        <td className="user-cell-number">
                          {u.denied_queries > 0 ? (
                            <span className={`denied-indicator ${isHighDenial ? 'high' : ''}`}>
                              {u.denied_queries} <small>({denialPct}%)</small>
                            </span>
                          ) : (
                            <span className="clean-indicator">0</span>
                          )}
                        </td>
                        <td className="user-cell-number">{u.active_keys}</td>
                        <td className="user-cell-date">{formatDate(u.first_seen)}</td>
                        <td className="user-cell-date">{formatDate(u.last_active)}</td>
                        <td className="user-cell-date">{formatDate(u.last_login)}</td>
                        <td>
                          <span className={`user-status ${u.is_active ? 'active' : 'inactive'}`}>
                            {u.is_active ? '● Active' : '○ Inactive'}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ═══ SECURITY TAB ═══ */}
      {activeTab === 'security' && (
        <div className="dash-security-section">
          {/* Security Summary Cards */}
          <div className="security-summary-grid">
            <div className="security-summary-card">
              <div className="sec-card-icon">🔐</div>
              <div className="sec-card-label">Active Keys</div>
              <div className="sec-card-value">{stats.total_active_keys || 0}</div>
            </div>
            <div className="security-summary-card">
              <div className="sec-card-icon">📊</div>
              <div className="sec-card-label">Denial Rate</div>
              <div className="sec-card-value" style={{ color: stats.denial_rate > 20 ? '#ff4757' : '#4ade80' }}>
                {stats.denial_rate || 0}%
              </div>
            </div>
            <div className="security-summary-card">
              <div className="sec-card-icon">⏱️</div>
              <div className="sec-card-label">Avg Response</div>
              <div className="sec-card-value">{stats.avg_response_time || 0}s</div>
            </div>
            <div className="security-summary-card">
              <div className="sec-card-icon">🛡️</div>
              <div className="sec-card-label">Issues Found</div>
              <div className="sec-card-value" style={{ color: securityIssues.length > 0 ? '#ffa502' : '#4ade80' }}>
                {securityIssues.length}
              </div>
            </div>
          </div>

          {/* Issues List */}
          <div className="dash-panel issues-panel">
            <div className="panel-header">
              <h3><span className="panel-icon">⚠️</span> SECURITY ANALYSIS & ISSUES</h3>
            </div>
            {securityIssues.length === 0 ? (
              <div className="no-issues">
                <div className="no-issues-icon">✅</div>
                <h3>All Clear</h3>
                <p>No security issues or anomalies detected. System is healthy.</p>
              </div>
            ) : (
              <div className="issues-list">
                {securityIssues.map((issue, i) => {
                  const config = SEVERITY_CONFIG[issue.severity] || SEVERITY_CONFIG.info;
                  return (
                    <div
                      key={i}
                      className="issue-card"
                      style={{ borderLeftColor: config.border, background: config.bg }}
                    >
                      <div className="issue-severity">
                        <span className="issue-sev-icon">{config.icon}</span>
                        <span className="issue-sev-label" style={{ color: config.color }}>
                          {issue.severity.toUpperCase()}
                        </span>
                      </div>
                      <div className="issue-body">
                        <div className="issue-type">{issue.type.replace(/_/g, ' ')}</div>
                        <div className="issue-message">{issue.message}</div>
                      </div>
                      <div className="issue-actions-tray">
                        {issue.type === 'inactive_users' && (
                          <button className="dash-resolve-btn" onClick={() => setActiveTab('users')}>Review Users ➔</button>
                        )}
                        {issue.type === 'high_denial_rate' && (
                          <button className="dash-resolve-btn" onClick={() => setActiveTab('users')}>Audit Roles ➔</button>
                        )}
                        {issue.type === 'user_high_denial' && (
                          <button className="dash-resolve-btn" onClick={() => setActiveTab('users')}>Monitor User ➔</button>
                        )}
                      </div>
                      <div className="issue-count-badge" style={{ color: config.color, borderColor: config.border }}>
                        {issue.count}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Denied Queries Breakdown */}
          {topDenied.length > 0 && (
            <div className="dash-panel denied-breakdown-panel">
              <div className="panel-header denied-header">
                <h3><span className="panel-icon">🚫</span> DENIED QUERIES BREAKDOWN</h3>
              </div>
              <div className="denied-breakdown-list">
                {topDenied.map((q, i) => (
                  <div key={i} className="denied-breakdown-item">
                    <div className="denied-bk-query">
                      <span className="denied-bk-icon">⊘</span>
                      {q.query}
                    </div>
                    <div className="denied-bk-meta">
                      <div className="denied-bk-roles">
                        {q.roles?.map((r, ri) => (
                          <span key={ri} className="denied-role-badge" style={{ background: ROLE_COLORS[r] || '#888', color: ['hr', 'finance'].includes(r) ? '#0a0e27' : '#fff' }}>
                            {r}
                          </span>
                        ))}
                      </div>
                      <span className="denied-bk-count">{q.count} attempts</span>
                      <span className="denied-bk-date">Last: {formatDate(q.last_attempt)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
