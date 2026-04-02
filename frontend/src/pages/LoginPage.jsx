import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import '../styles/LoginPage.css';

const API_BASE = process.env.REACT_APP_API_URL || '';

const LoginPage = () => {
  const { setAuthState } = useContext(AuthContext);
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [accessKey, setAccessKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [userDetails, setUserDetails] = useState(null);
  const [currentStep, setCurrentStep] = useState('login');
  const [authToken, setAuthToken] = useState(null);
  const [scanPhase, setScanPhase] = useState(0);
  const [systemTime, setSystemTime] = useState('');

  // Live clock
  useEffect(() => {
    const tick = () => {
      const now = new Date();
      setSystemTime(now.toLocaleTimeString('en-US', { hour12: false }) + '.' + String(now.getMilliseconds()).padStart(3, '0'));
    };
    tick();
    const interval = setInterval(tick, 100);
    return () => clearInterval(interval);
  }, []);

  // Fingerprint scan animation
  useEffect(() => {
    const interval = setInterval(() => {
      setScanPhase(p => (p + 1) % 4);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const scanLabels = ['SCANNING BIOMETRICS', 'ANALYZING PATTERN', 'VERIFYING IDENTITY', 'AWAITING INPUT'];

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!username || !password) {
      setError('CREDENTIALS REQUIRED');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/auth/login`, {
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
        setError(errorData.message || 'AUTHENTICATION FAILED');
        setPassword('');
      }
    } catch (err) {
      setError('CONNECTION LOST. RETRY.');
    } finally {
      setLoading(false);
    }
  };

  const handleAccessKeySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!accessKey) {
      setError('ACCESS KEY REQUIRED');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/auth/verify-key`, {
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
        setError(errorData.message || 'KEY VERIFICATION FAILED');
      }
    } catch (err) {
      setError('VERIFICATION LINK DOWN. RETRY.');
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
    <div className="login-container updated-hmr-trigger">
      {/* Animated Background */}
      <div className="login-background">
        <div className="grid-bg"></div>
        <div className="cyber-scanline"></div>
        <div className="particle-field">
          {[...Array(20)].map((_, i) => (
            <div key={i} className="particle" style={{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 8}s`,
              animationDuration: `${6 + Math.random() * 8}s`
            }}></div>
          ))}
        </div>
      </div>

      {/* STEP 1: LOGIN */}
      {currentStep === 'login' && (
        <div className="login-form-wrapper">
          <div className="login-form">
            {/* Header */}
            <div className="form-header">
              <div className="logo">
                <div className="dragon-icon-wrapper">
                  <svg className="fingerprint-svg" viewBox="0 0 100 100" width="80" height="80">
                    <defs>
                      <filter id="fpGlow">
                        <feGaussianBlur stdDeviation="2" result="blur" />
                        <feMerge>
                          <feMergeNode in="blur" />
                          <feMergeNode in="SourceGraphic" />
                        </feMerge>
                      </filter>
                    </defs>
                    <g filter="url(#fpGlow)" className="fp-lines">
                      <path d="M50 15 C30 15, 20 30, 20 50 C20 70, 35 85, 50 85" fill="none" stroke="var(--cyber-cyan)" strokeWidth="1.5" opacity="0.6" />
                      <path d="M50 20 C33 20, 25 33, 25 50 C25 67, 37 80, 50 80" fill="none" stroke="var(--cyber-cyan)" strokeWidth="1.5" opacity="0.7" />
                      <path d="M50 25 C36 25, 30 36, 30 50 C30 64, 39 75, 50 75" fill="none" stroke="var(--cyber-cyan)" strokeWidth="1.5" opacity="0.8" />
                      <path d="M50 30 C39 30, 35 39, 35 50 C35 61, 41 70, 50 70" fill="none" stroke="var(--cyber-cyan)" strokeWidth="1.5" opacity="0.9" />
                      <path d="M50 35 C42 35, 40 42, 40 50 C40 58, 43 65, 50 65" fill="none" stroke="var(--cyber-cyan)" strokeWidth="1.5" opacity="1" />
                      <path d="M50 40 C45 40, 44 45, 44 50 C44 55, 46 59, 50 60" fill="none" stroke="var(--cyber-cyan)" strokeWidth="1.5" opacity="1" />
                      <path d="M50 15 C70 15, 80 30, 80 50 C80 70, 65 85, 50 85" fill="none" stroke="var(--cyber-cyan)" strokeWidth="1.5" opacity="0.6" />
                      <path d="M50 20 C67 20, 75 33, 75 50 C75 67, 63 80, 50 80" fill="none" stroke="var(--cyber-cyan)" strokeWidth="1.5" opacity="0.7" />
                      <path d="M50 25 C64 25, 70 36, 70 50 C70 64, 61 75, 50 75" fill="none" stroke="var(--cyber-cyan)" strokeWidth="1.5" opacity="0.8" />
                      <path d="M50 30 C61 30, 65 39, 65 50 C65 61, 59 70, 50 70" fill="none" stroke="var(--cyber-cyan)" strokeWidth="1.5" opacity="0.9" />
                      <path d="M50 35 C58 35, 60 42, 60 50 C60 58, 57 65, 50 65" fill="none" stroke="var(--cyber-cyan)" strokeWidth="1.5" opacity="1" />
                      <path d="M50 40 C55 40, 56 45, 56 50 C56 55, 54 59, 50 60" fill="none" stroke="var(--cyber-cyan)" strokeWidth="1.5" opacity="1" />
                    </g>
                    {/* Scanning line */}
                    <line className="scan-line-anim" x1="15" y1="0" x2="85" y2="0" stroke="var(--cyber-cyan)" strokeWidth="2" opacity="0.8" />
                  </svg>
                  <div className="scan-status">{scanLabels[scanPhase]}</div>
                </div>
              </div>
              <h1>DRAGON<br/>INTEL</h1>
              <p className="auth-subtitle">AUTHORIZED OPERATORS ONLY</p>
            </div>

            {/* Step Indicator */}
            <div className="step-indicator">
              <div className="step active"><span className="step-num">01</span></div>
              <div className="step-line"></div>
              <div className="step"><span className="step-num">02</span></div>
              <div className="step-line"></div>
              <div className="step"><span className="step-num">03</span></div>
            </div>

            <form onSubmit={handleLoginSubmit}>
              <div className="form-group">
                <label htmlFor="username">
                  <span className="label-prefix">▸</span> OPERATOR ID
                </label>
                <div className="input-wrapper">
                  <span className="input-icon">⌘</span>
                  <input
                    id="username"
                    type="text"
                    placeholder="enter operator id"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    disabled={loading}
                    autoComplete="off"
                  />
                  <span className="input-glow"></span>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="password">
                  <span className="label-prefix">▸</span> SECURE PASSKEY
                </label>
                <div className="input-wrapper">
                  <span className="input-icon">🔐</span>
                  <input
                    id="password"
                    type="password"
                    placeholder="••••  ••••  ••••  ••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={loading}
                  />
                  <span className="input-glow"></span>
                </div>
              </div>

              {error && <div className="error-message"><span className="err-icon">⚠</span> {error}</div>}

              <button type="submit" className="enter-btn" disabled={loading}>
                {loading ? (
                  <><span className="btn-spinner"></span> AUTHENTICATING...</>
                ) : (
                  <>AUTHENTICATE <span className="btn-bolt">⚡</span></>
                )}
              </button>
            </form>

            <div className="login-footer">
              <div className="encrypt-status">
                <span className="encrypt-dot"></span>
                ENCRYPTION: 4096-BIT AES
              </div>
              <div className="system-stats">
                <div className="sys-stat">
                  <span className="stat-label">NODE_ID</span>
                  <span className="stat-value">DI-492-X</span>
                </div>
                <div className="sys-stat">
                  <span className="stat-label">LATENCY</span>
                  <span className="stat-value">0.04ms</span>
                </div>
                <div className="sys-stat">
                  <span className="stat-label">UPTIME</span>
                  <span className="stat-value">99.99%</span>
                </div>
              </div>
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
                <div className="dragon-icon-wrapper mini">
                  <svg className="fingerprint-svg small" viewBox="0 0 100 100" width="50" height="50">
                    <g className="fp-lines">
                      <path d="M50 20 C33 20, 25 33, 25 50 C25 67, 37 80, 50 80" fill="none" stroke="var(--cyber-green)" strokeWidth="2" opacity="0.8" />
                      <path d="M50 30 C39 30, 35 39, 35 50 C35 61, 41 70, 50 70" fill="none" stroke="var(--cyber-green)" strokeWidth="2" opacity="0.9" />
                      <path d="M50 40 C45 40, 44 45, 44 50 C44 55, 46 59, 50 60" fill="none" stroke="var(--cyber-green)" strokeWidth="2" opacity="1" />
                      <path d="M50 20 C67 20, 75 33, 75 50 C75 67, 63 80, 50 80" fill="none" stroke="var(--cyber-green)" strokeWidth="2" opacity="0.8" />
                      <path d="M50 30 C61 30, 65 39, 65 50 C65 61, 59 70, 50 70" fill="none" stroke="var(--cyber-green)" strokeWidth="2" opacity="0.9" />
                      <path d="M50 40 C55 40, 56 45, 56 50 C56 55, 54 59, 50 60" fill="none" stroke="var(--cyber-green)" strokeWidth="2" opacity="1" />
                    </g>
                  </svg>
                  <div className="scan-status verified">✓ IDENTITY VERIFIED</div>
                </div>
              </div>
              <h1>DRAGON<br/>INTEL</h1>
              <p className="auth-subtitle">SECURE ACCESS PROTOCOL</p>
            </div>

            <div className="step-indicator">
              <div className="step completed"><span className="step-check">✓</span></div>
              <div className="step-line completed"></div>
              <div className="step active"><span className="step-num">02</span></div>
              <div className="step-line"></div>
              <div className="step"><span className="step-num">03</span></div>
            </div>

            <div className="user-preview">
              <span className="user-preview-label">OPERATOR:</span>
              <span className="user-preview-name">{userDetails?.username}</span>
              <span className="user-preview-role" style={{borderColor: 'var(--cyber-cyan)'}}>
                {userDetails?.role?.toUpperCase()}
              </span>
            </div>

            <form onSubmit={handleAccessKeySubmit}>
              <div className="form-group">
                <label htmlFor="accessKey">
                  <span className="label-prefix">▸</span> SECURE ACCESS KEY
                </label>
                <div className="input-wrapper">
                  <span className="input-icon">🔑</span>
                  <input
                    id="accessKey"
                    type="text"
                    placeholder="enter access key"
                    value={accessKey}
                    onChange={(e) => setAccessKey(e.target.value)}
                    disabled={loading}
                    autoComplete="off"
                  />
                  <span className="input-glow"></span>
                </div>
              </div>

              {error && <div className="error-message"><span className="err-icon">⚠</span> {error}</div>}

              <button type="submit" className="enter-btn" disabled={loading}>
                {loading ? (
                  <><span className="btn-spinner"></span> VERIFYING...</>
                ) : (
                  <>VERIFY KEY <span className="btn-bolt">⚡</span></>
                )}
              </button>

              <button type="button" className="back-btn" onClick={handleBackToLogin}>
                ← BACK TO LOGIN
              </button>
            </form>

            <div className="login-footer">
              <div className="encrypt-status">
                <span className="encrypt-dot"></span>
                ENCRYPTION: 4096-BIT AES
              </div>
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
                <div className="dragon-icon-wrapper mini">
                  <svg className="fingerprint-svg small authorized" viewBox="0 0 100 100" width="50" height="50">
                    <g className="fp-lines">
                      <path d="M35 52 L45 62 L68 38" fill="none" stroke="var(--cyber-green)" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
                    </g>
                  </svg>
                  <div className="scan-status verified">✓ FULLY AUTHORIZED</div>
                </div>
              </div>
              <h1>DRAGON<br/>INTEL</h1>
              <p className="auth-subtitle">ACCESS GRANTED</p>
            </div>

            <div className="step-indicator">
              <div className="step completed"><span className="step-check">✓</span></div>
              <div className="step-line completed"></div>
              <div className="step completed"><span className="step-check">✓</span></div>
              <div className="step-line completed"></div>
              <div className="step active"><span className="step-num">03</span></div>
            </div>

            <div className="user-details-panel">
              <div className="detail-item">
                <label>OPERATOR</label>
                <p className="detail-value">{userDetails?.username || 'N/A'}</p>
              </div>
              <div className="detail-item">
                <label>EMAIL</label>
                <p className="detail-value">{userDetails?.email || 'N/A'}</p>
              </div>
              <div className="detail-item">
                <label>CLEARANCE</label>
                <p className="detail-value role-badge-confirm">
                  {userDetails?.role?.toUpperCase() || 'N/A'}
                </p>
              </div>
              <div className="detail-item">
                <label>DEPARTMENT</label>
                <p className="detail-value">{userDetails?.department || 'N/A'}</p>
              </div>
              <div className="detail-item status-item">
                <label>STATUS</label>
                <p className="detail-value authorized-status">
                  <span className="auth-dot"></span> AUTHORIZED
                </p>
              </div>
            </div>

            {error && <div className="error-message"><span className="err-icon">⚠</span> {error}</div>}

            <div className="action-buttons">
              <button className="enter-btn proceed-btn" onClick={handleProceedToChat}>
                ENTER SYSTEM <span className="btn-bolt">⚡</span>
              </button>
              <button className="back-btn" onClick={handleBackToAccessKey}>
                ← BACK TO ACCESS KEY
              </button>
            </div>

            <div className="login-footer">
              <div className="encrypt-status">
                <span className="encrypt-dot active"></span>
                SESSION ENCRYPTED · AES-256-GCM
              </div>
              <div className="system-stats">
                <div className="sys-stat">
                  <span className="stat-label">SESSION</span>
                  <span className="stat-value">{systemTime}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LoginPage;
