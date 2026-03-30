import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import '../styles/LoginPage.css';

const LoginPage = () => {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('employee');
  const [accessKey, setAccessKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [authMethod, setAuthMethod] = useState('password'); // 'password' or 'apikey'

  const roles = [
    { value: 'admin', label: 'Admin', color: '#ff6b6b' },
    { value: 'c-level', label: 'C-Level', color: '#ffa500' },
    { value: 'finance', label: 'Finance', color: '#00d4ff' },
    { value: 'hr', label: 'HR', color: '#90ee90' },
    { value: 'employee', label: 'Employee', color: '#888' }
  ];

  const handlePasswordLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!username || !password) {
      setError('Please enter username and password');
      setLoading(false);
      return;
    }

    const success = await login(username, password);
    setLoading(false);

    if (success) {
      navigate('/chat');
    } else {
      setError('Invalid username or password');
      setPassword('');
    }
  };

  const handleAccessKeyLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!accessKey) {
      setError('Please enter an access key');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/auth/apikey', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: accessKey })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/chat');
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Invalid access key');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    if (authMethod === 'password') {
      handlePasswordLogin(e);
    } else {
      handleAccessKeyLogin(e);
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
            <h1>DRAGON INTEL</h1>
            <p>ROLE-BASED INTELLIGENCE PLATFORM</p>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Username */}
            <div className="form-group">
              <label htmlFor="username">// USERNAME</label>
              <div className="input-wrapper">
                <input
                  id="username"
                  type="text"
                  placeholder="enter username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={loading || authMethod === 'apikey'}
                  required={authMethod === 'password'}
                />
              </div>
            </div>

            {/* Password */}
            <div className="form-group">
              <label htmlFor="password">// PASSWORD</label>
              <div className="input-wrapper">
                <input
                  id="password"
                  type="password"
                  placeholder="enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading || authMethod === 'apikey'}
                  required={authMethod === 'password'}
                />
              </div>
            </div>

            {/* Role Selector */}
            <div className="form-group">
              <label htmlFor="role">// ROLE</label>
              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                disabled={loading}
                className="role-select"
              >
                {roles.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Access Key */}
            <div className="form-group">
              <label htmlFor="accessKey">// ACCESS KEY</label>
              <div className="input-wrapper">
                <input
                  id="accessKey"
                  type="password"
                  placeholder="enter access key (optional)"
                  value={accessKey}
                  onChange={(e) => setAccessKey(e.target.value)}
                  disabled={loading}
                />
              </div>
            </div>

            {error && <div className="error-message">⚠️ {error}</div>}

            {/* Submit Button */}
            <button
              type="submit"
              className="enter-btn"
              disabled={loading}
            >
              {loading ? '⏳ AUTHENTICATING...' : '✓ ENTER SYSTEM'}
            </button>
          </form>

          {/* Footer */}
          <div className="login-footer">
            <p className="footer-text">DRAGON INTEL v2.0 | AUTHORIZED PERSONNEL ONLY</p>
            <div className="demo-section">
              <p className="demo-title">ACCESS KEYS FOR TESTING:</p>
              <div className="demo-grid">
                <div className="demo-item">
                  <strong>Admin:</strong>
                  <code>ADM-2030</code>
                </div>
                <div className="demo-item">
                  <strong>C-Level:</strong>
                  <code>CLV-2030</code>
                </div>
                <div className="demo-item">
                  <strong>Finance:</strong>
                  <code>FIN-2030</code>
                </div>
                <div className="demo-item">
                  <strong>HR:</strong>
                  <code>HR-2030</code>
                </div>
                <div className="demo-item">
                  <strong>Employee:</strong>
                  <code>EMP-2030</code>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
