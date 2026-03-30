import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import '../styles/LoginPage.css';

const LoginPage = () => {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const success = await login(username, password);
    setLoading(false);

    if (success) {
      navigate('/chat');
    } else {
      setError('Invalid username or password');
      setPassword('');
    }
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="grid-bg"></div>
      </div>

      <div className="login-form-wrapper">
        <div className="login-form">
          <div className="form-header">
            <div className="logo">
              <div className="dragon-icon">🐉</div>
            </div>
            <h1>DRAGON</h1>
            <p>INTELLIGENCE PLATFORM</p>
            <p className="subtitle">Role-Based Access Control</p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="username">USERNAME</label>
              <div className="input-wrapper">
                <input
                  id="username"
                  type="text"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={loading}
                  required
                />
                <span className="input-icon">👤</span>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="password">PASSWORD</label>
              <div className="input-wrapper">
                <input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  required
                />
                <span className="input-icon">🔒</span>
              </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <button
              type="submit"
              className="login-btn"
              disabled={loading}
            >
              {loading ? '⏳ SIGNING IN...' : '✓ SIGN IN'}
            </button>
          </form>

          <div className="demo-credentials">
            <p className="demo-title">DEMO CREDENTIALS:</p>
            <div className="demo-item">
              <strong>Admin:</strong> admin / admin123
            </div>
            <div className="demo-item">
              <strong>Finance:</strong> finance_user / pass123
            </div>
            <div className="demo-item">
              <strong>Employee:</strong> employee_user / pass123
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
