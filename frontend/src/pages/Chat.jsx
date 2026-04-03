import React, { useState, useEffect, useContext, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import '../styles/Chat.css';
import { API_BASE_URL as API_BASE } from '../services/api';

const Chat = () => {
  const { user, token } = useContext(AuthContext);
  const location = useLocation();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Test queries per role for verification
  const roleTestQueries = {
    "Admin": "Show all company technical system logs and security overview",
    "C-Level": "Show full company performance KPIs across all departments",
    "HR": "List all employee payroll and attendance records for March",
    "Finance": "Generate the complete Profit and Loss statement for Q4",
    "Marketing": "Show me the ROI and lead conversion rates for campaign alpha",
    "Engineering": "Show the API architecture and system deployment history",
    "Employee": "What are the company WFH and leave policies?"
  };

  const handleQuickTest = (roleName) => {
    setInput(roleTestQueries[roleName]);
  };

  const parseBotResponse = (content) => {
    // If it doesn't have the 📌 marker, return plaintext
    if (!content.includes('📌')) return { type: 'plain', text: content };

    const sections = {
      answer: content.split('📌 Answer:')[1]?.split('📊')[0]?.strip() || '',
      details: content.split('📊 Key Details:')[1]?.split('💡')[0]?.strip() || '',
      insight: content.split('💡 Insight:')[1]?.split('🔗')[0]?.strip() || '',
      related: content.split('🔗 Related Words:')[1]?.split('📂')[0]?.strip() || '',
      source: content.split('📂 Source:')[1]?.strip() || ''
    };

    return { type: 'structured', ...sections };
  };

  useEffect(() => {
    if (location.state && location.state.newChat) {
      // Instantly clear the screen
      setMessages([]);
    } else {
      // Load chat history normally
      loadChatHistory();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.key]);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/chat/history?limit=20`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        // Reverse to show oldest first
        const formattedMessages = data.history.reverse().map((chat) => [
          { role: 'user', content: chat.query, timestamp: chat.timestamp },
          { role: 'bot', content: chat.response, timestamp: chat.timestamp, docs: chat.referenced_docs }
        ]).flat();
        setMessages(formattedMessages);
      }
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message to UI immediately
    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ query: input })
      });

      if (response.ok) {
        const data = await response.json();
        const botMessage = {
          role: 'bot',
          content: data.response,
          timestamp: new Date().toISOString(),
          docs: data.referenced_docs,
          access_denied: data.access_denied,
          role_info: data.role_info
        };
        setMessages((prev) => [...prev, botMessage]);
      } else {
        // Try to get JSON error, if not, use status text
        let errorMsg = 'Failed to get a response from the Dragon Intelligence terminal.';
        let debugInfo = '';
        try {
          const errorData = await response.json();
          errorMsg = errorData.message || errorMsg;
          if (errorData.clue) {
            debugInfo = `\n🔍 CLUE: ${errorData.clue}\n📍 TRACE: ${errorData.trace || 'Unknown'}`;
          }
        } catch (e) {
          errorMsg = `Server error code: ${response.status} (${response.statusText})`;
        }
        
        setMessages((prev) => [...prev, {
          role: 'bot',
          content: `⚠️ CONNECT REJECTED: ${errorMsg}${debugInfo}`,
          timestamp: new Date().toISOString(),
          isError: true
        }]);
      }
    } catch (err) {
      console.error('Fetch error:', err);
      setMessages((prev) => [...prev, {
        role: 'bot',
        content: `📡 SIGNAL LOST: Terminal timed out or server is resetting. (${err.message})`,
        timestamp: new Date().toISOString(),
        isError: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  return (
      <div className="chat-content-layout">
        <div className="chat-container">
          <div className="chat-header">
            <h1>CHAT INTERFACE</h1>
            <div className="header-status">
              <span className="status-dot online"></span>
              <span>SYSTEM ONLINE</span>
            </div>
          </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="dragon-icon">🐉</div>
            <p>ASK DRAGON INTEL ANYTHING</p>
            <p className="subtitle">within your access level...</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role} ${msg.access_denied ? 'access-denied' : ''} ${msg.isError ? 'error' : ''}`}>
              <div className="message-content">
                {msg.role === 'user' ? (
                  <>
                    <div className="message-label">{user.username} - {formatTime(msg.timestamp)}</div>
                    <p>{msg.content}</p>
                  </>
                ) : (
                  <>
                    <div className="message-label">
                      Dragon Intel - {formatTime(msg.timestamp)}
                      {msg.access_denied && ' (⊘ ACCESS DENIED)'}
                      {msg.isError && ' (⚠ ERROR)'}
                    </div>
                    <div className="message-text-premium">
                      {(() => {
                        const parsed = parseBotResponse(msg.content);
                        if (parsed.type === 'plain') return <p>{parsed.text}</p>;
                        
                        return (
                          <>
                            {parsed.answer && (
                              <div className="ans-highlight">
                                <span className="premium-label">📌 DIRECT ANSWER:</span>
                                {parsed.answer}
                              </div>
                            )}
                            {parsed.details && (
                              <div className="ans-details-block">
                                <span className="premium-label">📊 KEY DETAILS:</span>
                                {parsed.details}
                              </div>
                            )}
                            {parsed.insight && (
                              <div className="ans-insight-block">
                                <span className="premium-label">💡 STRATEGIC INSIGHT:</span>
                                {parsed.insight}
                              </div>
                            )}
                            {parsed.related && (
                              <div className="ans-related-block">
                                <span className="premium-label">🔗 RELATED WORDS:</span>
                                <div className="related-tags">
                                  {parsed.related.split(',').map((tag, i) => (
                                    <span key={i} className="tag-word">{tag.trim()}</span>
                                  ))}
                                </div>
                              </div>
                            )}
                            {parsed.source && (
                              <div className="src-indicator">
                                <span className="src-label">📂 SOURCE:</span>
                                <span className="src-value">{parsed.source}</span>
                              </div>
                            )}
                          </>
                        );
                      })()}
                    </div>
                    {msg.role_info && msg.access_denied && (
                      <div className="role-info-card">
                        <small>📍 REQUIRED LEVEL: {msg.role_info.access_level}</small>
                      </div>
                    )}
                    {msg.docs && msg.docs.length > 0 && !msg.content.includes('- Source:') && (
                      <div className="referenced-docs-list">
                        {msg.docs.map((doc, i) => (
                          <span key={i} className="doc-tag-elite">{doc}</span>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          placeholder="Ask anything within your access level..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          className="chat-input"
        />
        <button type="submit" disabled={loading} className="send-btn">
          {loading ? '⏳' : '📤'} SEND
        </button>
          </form>
        </div>

        {user.role === 'Admin' && (
          <div className="test-sidebar">
            <div className="sidebar-header">
              <h2>RBAC TEST DECK</h2>
              <p>Verify role-specific boundaries</p>
            </div>
            <div className="test-buttons-grid">
              {Object.keys(roleTestQueries).map((r) => (
                <button 
                  key={r} 
                  className={`test-role-btn role-${r.toLowerCase()}`}
                  onClick={() => handleQuickTest(r)}
                  title={`Test ${r} boundary query`}
                >
                  <span className="btn-role-name">{r}</span>
                  <span className="btn-action">RUN QUERY</span>
                </button>
              ))}
            </div>
            <div className="sidebar-footer">
              <p>📍 Admin mode only</p>
            </div>
          </div>
        )}
      </div>
  );
};

export default Chat;
