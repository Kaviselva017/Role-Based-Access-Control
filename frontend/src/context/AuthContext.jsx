import React, { createContext, useState, useEffect } from 'react';
import { API_BASE_URL as API_BASE } from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (token) {
      // Verify token is still valid
      validateToken();
    } else {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const validateToken = async () => {
    try {
      // Changed from /api/health to /api/access-keys to test a protected route
      const response = await fetch(`${API_BASE}/api/access-keys`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!response.ok) {
        logout();
      }
      setLoading(false);
    } catch (err) {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) {
        throw new Error('Invalid credentials');
      }

      const data = await response.json();
      const userData = { ...data.user, role: data.user.role?.toLowerCase() || 'employee' };
      setToken(data.token);
      setUser(userData);
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(userData));
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  const setAuthState = (newToken, newUser) => {
    const userData = newUser ? { ...newUser, role: newUser.role?.toLowerCase() || 'employee' } : null;
    setToken(newToken);
    setUser(userData);
    localStorage.setItem('token', newToken);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const hasPermission = (permission) => {
    if (!user) return false;
    
    const rolePermissions = {
      'admin': ['view_dashboard', 'upload_docs', 'manage_users', 'generate_keys', 'chat', 'view_history'],
      'c-level': ['view_dashboard', 'chat', 'view_history'],
      'finance': ['chat', 'view_history'],
      'hr': ['chat', 'view_history'],
      'marketing': ['chat', 'view_history'],
      'engineering': ['chat', 'view_history'],
      'sales': ['chat', 'view_history'],
      'operations': ['chat', 'view_history'],
      'it': ['chat', 'view_history'],
      'legal': ['chat', 'view_history'],
      'customer-success': ['chat', 'view_history'],
      'employee': ['chat', 'view_history']
    };

    const userRole = user.role ? user.role.toLowerCase() : 'employee';
    const userPermissions = rolePermissions[userRole] || [];
    return userPermissions.includes(permission);
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      loading, 
      error, 
      login, 
      logout,
      setAuthState,
      hasPermission,
      isAdmin: user?.role === 'admin',
      isAuthenticated: !!user
    }}>
      {children}
    </AuthContext.Provider>
  );
};
