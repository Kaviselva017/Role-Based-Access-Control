import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/AccessKeys.css';
import { API_BASE_URL as API_BASE } from '../services/api';

const AccessKeys = () => {
  const { token, user } = useContext(AuthContext);
  const [keys, setKeys] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState(user.id);
  const [keyName, setKeyName] = useState('');
  const [expiryDays, setExpiryDays] = useState(365);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generatedKey, setGeneratedKey] = useState(null);

  useEffect(() => {
    loadKeys();
    if (user.role === 'admin') {
      loadUsers();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedUserId]);

  const loadKeys = async () => {
    try {
      const url =
        user.role === 'admin'
          ? `${API_BASE}/api/access-keys?user_id=${selectedUserId}`
          : `${API_BASE}/api/access-keys`;
      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setKeys(data.keys);
      } else {
        setError('Failed to load access keys');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users);
      }
    } catch (err) {
      console.error('Failed to load users:', err);
    }
  };

  const handleGenerateKey = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE}/api/access-keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: selectedUserId,
          key_name: keyName,
          expiry_days: expiryDays
        })
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedKey(data.key);
        setKeyName('');
        setExpiryDays(365);
        // Reload keys after a short delay
        setTimeout(loadKeys, 1000);
      } else {
        const data = await response.json();
        setError(data.message);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRevokeKey = async (keyId) => {
    if (window.confirm('Are you sure you want to revoke this key?')) {
      try {
        const response = await fetch(`${API_BASE}/api/access-keys/${keyId}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.ok) {
          loadKeys();
        } else {
          setError('Failed to revoke key');
        }
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Key copied to clipboard!');
  };

  if (loading) {
    return <div className="loading">Loading access keys...</div>;
  }

  return (
    <div className="access-keys-container">
      <div className="keys-header">
        <h1>ACCESS KEYS</h1>
        <div className="header-status">
          <span className="status-dot online"></span>
          <span>SYSTEM ONLINE</span>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {generatedKey && (
        <div className="key-generated-box">
          <h3>⚠️ NEW ACCESS KEY GENERATED</h3>
          <p className="key-warning">
            Save this key now. You won't be able to see it again!
          </p>
          <div className="key-display">
            <code>{generatedKey.key}</code>
            <button
              className="copy-btn"
              onClick={() => copyToClipboard(generatedKey.key)}
            >
              📋 COPY
            </button>
          </div>
          <div className="key-details">
            <p>
              <strong>Name:</strong> {generatedKey.name}
            </p>
            <p>
              <strong>Created:</strong>{' '}
              {new Date(generatedKey.created_at).toLocaleString()}
            </p>
            <p>
              <strong>Expires:</strong>{' '}
              {new Date(generatedKey.expires_at).toLocaleString()}
            </p>
          </div>
          <button
            className="close-key-box"
            onClick={() => setGeneratedKey(null)}
          >
            ✕ CLOSE
          </button>
        </div>
      )}

      {/* Generate New Key Form */}
      <div className="generate-key-section">
        <h2>Generate New Access Key</h2>
        <form onSubmit={handleGenerateKey} className="generate-form">
          {user.role === 'admin' && (
            <div className="form-group">
              <label>User</label>
              <select
                value={selectedUserId}
                onChange={(e) => setSelectedUserId(e.target.value)}
              >
                <option value={user.id}>{user.username} (You)</option>
                {users.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.username} ({u.role})
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="form-group">
            <label>Key Name</label>
            <input
              type="text"
              placeholder="e.g., Laptop Key, Mobile App"
              value={keyName}
              onChange={(e) => setKeyName(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Expiry (Days)</label>
            <select
              value={expiryDays}
              onChange={(e) => setExpiryDays(Number(e.target.value))}
            >
              <option value={30}>30 Days</option>
              <option value={90}>90 Days</option>
              <option value={180}>180 Days</option>
              <option value={365}>1 Year</option>
              <option value={1095}>3 Years</option>
            </select>
          </div>

          <button type="submit" className="generate-btn">
            🔐 GENERATE KEY
          </button>
        </form>
      </div>

      {/* Keys List */}
      <div className="keys-list-section">
        <h2>Your Access Keys</h2>
        {keys.length === 0 ? (
          <div className="empty-state">
            <p>No access keys yet. Generate one to get started.</p>
          </div>
        ) : (
          <div className="keys-table">
            <table>
              <thead>
                <tr>
                  <th>KEY NAME</th>
                  <th>CREATED</th>
                  <th>EXPIRES</th>
                  <th>LAST USED</th>
                  <th>STATUS</th>
                  <th>ACTION</th>
                </tr>
              </thead>
              <tbody>
                {keys.map((key) => (
                  <tr key={key.id} className={!key.is_active ? 'revoked' : ''}>
                    <td className="key-name">{key.name}</td>
                    <td className="date-cell">
                      {new Date(key.created_at).toLocaleDateString()}
                    </td>
                    <td className="date-cell">
                      {new Date(key.expires_at).toLocaleDateString()}
                    </td>
                    <td className="date-cell">
                      {key.last_used
                        ? new Date(key.last_used).toLocaleDateString()
                        : 'Never'}
                    </td>
                    <td>
                      <span
                        className={`status-badge ${
                          key.is_active ? 'active' : 'revoked'
                        }`}
                      >
                        {key.is_active ? '✓ ACTIVE' : '✕ REVOKED'}
                      </span>
                    </td>
                    <td>
                      {key.is_active && (
                        <button
                          className="revoke-btn"
                          onClick={() => handleRevokeKey(key.id)}
                        >
                          REVOKE
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AccessKeys;
