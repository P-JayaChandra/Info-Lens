import { apiClient, apiCall } from './client';
import { DEV_USER } from '../utils/fixtures';

export const authApi = {
  login: async (credentials) => {
    return apiCall(
      async () => {
        const res = await apiClient.post('/api/auth/login', credentials);
        if (res.data.access_token) {
          localStorage.setItem('infolens_auth_token', res.data.access_token);
        }
        return res.data;
      },
      () => {
        const token = 'dev_jwt_token_infolens_123';
        localStorage.setItem('infolens_auth_token', token);
        return {
          access_token: token,
          token_type: 'bearer',
          user: { ...DEV_USER, email: credentials.email || DEV_USER.email }
        };
      }
    );
  },

  register: async (userData) => {
    return apiCall(
      async () => {
        const res = await apiClient.post('/api/auth/register', userData);
        if (res.data.access_token) {
          localStorage.setItem('infolens_auth_token', res.data.access_token);
        }
        return res.data;
      },
      () => {
        const token = 'dev_jwt_token_infolens_123';
        localStorage.setItem('infolens_auth_token', token);
        return {
          access_token: token,
          token_type: 'bearer',
          user: {
            ...DEV_USER,
            email: userData.email,
            fullName: userData.fullName || 'New Researcher'
          }
        };
      }
    );
  },

  logout: async () => {
    try {
      await apiClient.post('/api/auth/logout');
    } catch {
      // Ignore errors on logout
    } finally {
      localStorage.removeItem('infolens_auth_token');
    }
  },

  getCurrentUser: async () => {
    const token = localStorage.getItem('infolens_auth_token');
    if (!token) return null;

    return apiCall(
      async () => {
        const res = await apiClient.get('/api/auth/me');
        return res.data;
      },
      () => DEV_USER
    );
  }
};
