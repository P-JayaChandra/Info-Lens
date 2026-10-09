import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/authApi';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function checkSession() {
      try {
        const currentUser = await authApi.getCurrentUser();
        setUser(currentUser);
      } catch (err) {
        console.warn('Session verification failed:', err.message);
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    checkSession();

    const handleAuthExpired = () => {
      setUser(null);
      setError('Session expired. Please log in again.');
    };

    window.addEventListener('infolens:auth_expired', handleAuthExpired);
    return () => window.removeEventListener('infolens:auth_expired', handleAuthExpired);
  }, []);

  const login = async (credentials) => {
    setError(null);
    setLoading(true);
    try {
      const res = await authApi.login(credentials);
      setUser(res.user);
      return res;
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Login failed';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setError(null);
    setLoading(true);
    try {
      const res = await authApi.register(userData);
      setUser(res.user);
      return res;
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Registration failed';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        loading,
        error,
        login,
        register,
        logout,
        setError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
