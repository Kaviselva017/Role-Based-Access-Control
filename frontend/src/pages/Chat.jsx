import React, { useState, useEffect, useContext, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import '../styles/Chat.css';

const Chat = () => {
  const { user, token } = useContext(AuthContext);
  const location = useLocation();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

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
      const response = await fetch('/api/chat/history?limit=20', {
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
      const response = await fetch('/api/chat', {
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
        const error = await response.json();
        setMessages((prev) => [...prev, {
          role: 'bot',
          content: `Error: ${error.message}`,
          timestamp: new Date().toISOString(),
          isError: true
        }]);
      }
    } catch (err) {
      setMessages((prev) => [...prev, {
        role: 'bot',
        content: 'Failed to send message. Please try again.',
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
                      {msg.isError && ' (⚠ Error)'}
                    </div>
                    <p>{msg.content}</p>
                    {msg.role_info && msg.access_denied && (
                      <div className="role-info-box">
                        <small>📍 Access Level: {msg.role_info.access_level}</small>
                      </div>
                    )}
                    {msg.docs && msg.docs.length > 0 && (
                      <div className="referenced-docs">
                        <strong>📎 Referenced:</strong>
                        {msg.docs.map((doc, i) => (
                          <span key={i} className="doc-tag">{doc}</span>
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
  );
};

export default Chat;
