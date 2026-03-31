import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import '../styles/LoginPage.css';

const LoginPage = () => {
  const { setAuthState } = useContext(AuthContext);
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [accessKey, setAccessKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [userDetails, setUserDetails] = useState(null);
  const [currentStep, setCurrentStep] = useState('login'); // 'login' -> 'accesskey' -> 'confirm'
  const [authToken, setAuthToken] = useState(null);

  const roles = [
    { value: 'admin', label: 'Admin', color: '#ff6b6b' },
    { value: 'c-level', label: 'C-Level', color: '#ffa500' },
    { value: 'finance', label: 'Finance', color: '#00d4ff' },
    { value: 'hr', label: 'HR', color: '#90ee90' },
    { value: 'employee', label: 'Employee', color: '#888' }
  ];

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!username || !password) {
      setError('Please enter username and password');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (response.ok) {
        const data = await response.json();
        setAuthToken(data.token);
        setUserDetails(data.user);
        setCurrentStep('accesskey');
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Invalid credentials');
        setPassword('');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAccessKeySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!accessKey) {
      setError('Please enter an access key');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/auth/verify-key', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ accessKey: accessKey })
      });

      if (response.ok) {
        setCurrentStep('confirm');
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Invalid access key');
      }
    } catch (err) {
      setError('Key verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };



  const handleProceedToChat = () => {
    setAuthState(authToken, userDetails);
    navigate('/chat');
  };

  const handleBackToLogin = () => {
    setCurrentStep('login');
    setUsername('');
    setPassword('');
    setAccessKey('');
    setUserDetails(null);
    setAuthToken(null);
    setError('');
  };

  const handleBackToAccessKey = () => {
    setCurrentStep('accesskey');
    setAccessKey('');
    setError('');
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="grid-bg"></div>
      </div>

      {/* STEP 1: LOGIN */}
      {currentStep === 'login' && (
        <div className="login-form-wrapper">
          <div className="login-form">
            <div className="form-header">
              <div className="logo">
                <div className="dragon-icon">🐉</div>
              </div>
              <h1>DRAGON INTEL</h1>
              <p>ROLE-BASED INTELLIGENCE PLATFORM</p>
            </div>

            <div className="step-indicator">
              <div className="step active">1</div>
              <div className="step-line"></div>
              <div className="step">2</div>
              <div className="step-line"></div>
              <div className="step">3</div>
            </div>

            <div className="step-title">STEP 1: LOGIN</div>

            <form onSubmit={handleLoginSubmit}>
              <div className="form-group">
                <label htmlFor="username">// USERNAME</label>
                <div className="input-wrapper">
                  <input
                    id="username"
                    type="text"
                    placeholder="enter username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="password">// PASSWORD</label>
                <div className="input-wrapper">
                  <input
                    id="password"
                    type="password"
                    placeholder="enter password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={loading}
                  />
                </div>
              </div>

              {error && <div className="error-message">⚠️ {error}</div>}

              <button
                type="submit"
                className="enter-btn"
                disabled={loading}
              >
                {loading ? '⏳ AUTHENTICATING...' : '→ CONTINUE'}
              </button>
            </form>

            <div className="login-footer">
              <p className="footer-text">DRAGON INTEL v2.0 | AUTHORIZED PERSONNEL ONLY</p>
            </div>
          </div>
        </div>
      )}

      {/* STEP 2: ACCESS KEY */}
      {currentStep === 'accesskey' && userDetails && (
        <div className="login-form-wrapper">
          <div className="login-form">
            <div className="form-header">
              <div className="logo">
                <div className="dragon-icon">🐉</div>
              </div>
              <h1>DRAGON INTEL</h1>
              <p>ROLE-BASED INTELLIGENCE PLATFORM</p>
            </div>

            <div className="step-indicator">
              <div className="step completed">✓</div>
              <div className="step-line completed"></div>
              <div className="step active">2</div>
              <div className="step-line"></div>
              <div className="step">3</div>
            </div>

            <div className="step-title">STEP 2: AUTHORIZE ACCESS</div>

            <div className="user-preview">
              <p>Logged in as: <strong>{userDetails?.username}</strong></p>
            </div>

            <form onSubmit={handleAccessKeySubmit}>
              <div className="form-group">
                <label htmlFor="accessKey">// ACCESS KEY</label>
                <div className="input-wrapper">
                  <input
                    id="accessKey"
                    type="text"
                    placeholder="enter access key"
                    value={accessKey}
                    onChange={(e) => setAccessKey(e.target.value)}
                    disabled={loading}
                  />
                </div>
              </div>

              {error && <div className="error-message">⚠️ {error}</div>}

              <button
                type="submit"
                className="enter-btn"
                disabled={loading}
              >
                {loading ? '⏳ VERIFYING...' : '→ VERIFY'}
              </button>

              <button
                type="button"
                className="back-btn"
                onClick={handleBackToLogin}
              >
                ← BACK TO LOGIN
              </button>
            </form>

            <div className="login-footer">
              <p className="footer-text">DRAGON INTEL v2.0 | AUTHORIZED PERSONNEL ONLY</p>
            </div>
          </div>
        </div>
      )}

      {/* STEP 3: CONFIRM */}
      {currentStep === 'confirm' && userDetails && (
        <div className="login-form-wrapper">
          <div className="login-form">
            <div className="form-header">
              <div className="logo">
                <div className="dragon-icon">🐉</div>
              </div>
              <h1>DRAGON INTEL</h1>
              <p>VERIFY IDENTITY</p>
            </div>

            <div className="step-indicator">
              <div className="step completed">✓</div>
              <div className="step-line completed"></div>
              <div className="step completed">✓</div>
              <div className="step-line completed"></div>
              <div className="step active">3</div>
            </div>

            <div className="step-title">STEP 3: AUTHORIZED ACCESS</div>

            <div className="user-details-panel">
              <div className="detail-item">
                <label>USERNAME</label>
                <p className="detail-value">{userDetails?.username || 'N/A'}</p>
              </div>

              <div className="detail-item">
                <label>EMAIL</label>
                <p className="detail-value">{userDetails?.email || 'N/A'}</p>
              </div>

              <div className="detail-item">
                <label>ROLE</label>
                <p className="detail-value role-badge">
                  {userDetails?.role?.toUpperCase() || 'N/A'}
                </p>
              </div>

              <div className="detail-item">
                <label>DEPARTMENT</label>
                <p className="detail-value">{userDetails?.department || 'N/A'}</p>
              </div>

              <div className="detail-item">
                <label>STATUS</label>
                <p className="detail-value" style={{ color: '#00c864' }}>✓ AUTHORIZED</p>
              </div>
            </div>

            {error && <div className="error-message">⚠️ {error}</div>}

            <div className="action-buttons">
              <button 
                className="enter-btn proceed-btn"
                onClick={handleProceedToChat}
              >
                ✓ ENTER SYSTEM
              </button>
              <button 
                className="back-btn"
                onClick={handleBackToAccessKey}
              >
                ← BACK TO ACCESS KEY
              </button>
            </div>

            <div className="login-footer">
              <p className="footer-text">DRAGON INTEL v2.0 | AUTHORIZED PERSONNEL ONLY</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LoginPage;
