import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const { token } = useContext(AuthContext);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      const response = await fetch('/api/dashboard/stats', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data.stats);
      } else {
        setError('Failed to load dashboard stats');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>ANALYTICS DASHBOARD</h1>
        <div className="header-status">
          <span className="status-dot online"></span>
          <span>SYSTEM ONLINE</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card total-queries">
          <div className="stat-label">TOTAL QUERIES</div>
          <div className="stat-value">{stats?.total_queries || 0}</div>
          <div className="stat-subtitle">all time</div>
        </div>

        <div className="stat-card total-users">
          <div className="stat-label">TOTAL USERS</div>
          <div className="stat-value">{stats?.total_users || 0}</div>
          <div className="stat-subtitle">registered</div>
        </div>

        <div className="stat-card access-denied">
          <div className="stat-label">ACCESS DENIED</div>
          <div className="stat-value">{stats?.access_denied || 0}</div>
          <div className="stat-subtitle">blocked attempts</div>
        </div>

        <div className="stat-card active-today">
          <div className="stat-label">ACTIVE TODAY</div>
          <div className="stat-value">1</div>
          <div className="stat-subtitle">unique users</div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        {/* Queries by Role */}
        <div className="chart-container queries-by-role">
          <div className="chart-title">QUERIES BY ROLE</div>
          <div className="role-bars">
            {stats?.queries_by_role?.map((item) => (
              <div key={item.role} className="role-bar-item">
                <div className="role-label">{item.role}</div>
                <div className="role-bar-wrapper">
                  <div
                    className={`role-bar role-${item.role}`}
                    style={{
                      width: `${(item.count / Math.max(...stats.queries_by_role.map(r => r.count))) * 100}%`
                    }}
                  ></div>
                  <span className="bar-count">{item.count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Activity Chart */}
        <div className="chart-container activity-chart">
          <div className="chart-title">ACTIVITY — LAST 7 DAYS</div>
          <svg className="activity-graph">
            <polyline
              points="0,100 20,80 40,85 60,70 80,75 100,65 120,60 140,70"
              fill="none"
              stroke="#00d4ff"
              strokeWidth="2"
              vectorEffect="non-scaling-stroke"
            />
          </svg>
        </div>
      </div>

      {/* Top Queries */}
      <div className="queries-section">
        <div className="section-title">TOP QUERIES</div>
        <div className="queries-list">
          <div className="query-item">
            <span className="query-arrow">▶</span>
            <span className="query-text">HI</span>
            <span className="query-count">5x</span>
          </div>
          <div className="query-item">
            <span className="query-arrow">▶</span>
            <span className="query-text">What is the employee salary structure?</span>
            <span className="query-count">4x</span>
          </div>
          <div className="query-item">
            <span className="query-arrow">▶</span>
            <span className="query-text">What is the company revenue?</span>
            <span className="query-count">3x</span>
          </div>
          <div className="query-item">
            <span className="query-arrow">▶</span>
            <span className="query-text">WHAT IS THE REVENUE</span>
            <span className="query-count">3x</span>
          </div>
          <div className="query-item">
            <span className="query-arrow">▶</span>
            <span className="query-text">What is the remote work policy?</span>
            <span className="query-count">3x</span>
          </div>
        </div>
      </div>

      {/* Top Denied Queries */}
      <div className="queries-section denied-section">
        <div className="section-title">TOP DENIED QUERIES</div>
        <div className="queries-list">
          <div className="query-item denied">
            <span className="query-icon">⊘</span>
            <span className="query-text">HI</span>
            <span className="query-badge">Finance</span>
            <span className="query-count">5x</span>
          </div>
          <div className="query-item denied">
            <span className="query-icon">⊘</span>
            <span className="query-text">What is our marketing budget?</span>
            <span className="query-badge">HR</span>
            <span className="query-count">3x</span>
          </div>
          <div className="query-item denied">
            <span className="query-icon">⊘</span>
            <span className="query-text">What is my role?</span>
            <span className="query-badge">Employee</span>
            <span className="query-count">2x</span>
          </div>
          <div className="query-item denied">
            <span className="query-icon">⊘</span>
            <span className="query-text">Dynamic web Page creation</span>
            <span className="query-badge">Marketing</span>
            <span className="query-count">1x</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
