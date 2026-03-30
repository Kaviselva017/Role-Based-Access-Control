import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/ChatHistory.css';

const ChatHistory = () => {
  const { token } = useContext(AuthContext);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await fetch('/api/chat/history?limit=100', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setHistory(data.history);
      } else {
        setError('Failed to load chat history');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  if (loading) {
    return <div className="loading">Loading chat history...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="chat-history-container">
      <div className="history-header">
        <h1>QUERY HISTORY</h1>
        <div className="header-status">
          <span className="status-dot online"></span>
          <span>SYSTEM ONLINE</span>
        </div>
      </div>

      <div className="filter-section">
        <label>Filter:</label>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All Queries</option>
          <option value="recent">Last 24 Hours</option>
          <option value="week">Last 7 Days</option>
          <option value="month">Last 30 Days</option>
        </select>
      </div>

      {history.length === 0 ? (
        <div className="empty-history">
          <p>No chat history yet. Start a conversation to see it here.</p>
        </div>
      ) : (
        <div className="history-list">
          {history.map((item, idx) => (
            <div key={idx} className="history-item">
              <div className="history-timestamp">
                {formatTime(item.timestamp)}
              </div>
              <div className="history-query">
                <span className="query-icon">❓</span>
                <p className="query-text">{item.query}</p>
              </div>
              <div className="history-response">
                <span className="response-icon">💬</span>
                <p className="response-text">{item.response}</p>
              </div>
              {item.referenced_docs && item.referenced_docs.length > 0 && (
                <div className="referenced-docs">
                  <strong>📎 Documents:</strong>
                  {item.referenced_docs.map((doc, i) => (
                    <span key={i} className="doc-tag">{doc}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatHistory;
