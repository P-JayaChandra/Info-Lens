import axios from 'axios';
import { DEV_DOCUMENTS, DEV_USER, DEV_CONVERSATIONS, DEV_SUMMARIES, DEV_QUESTIONS, DEV_FLASHCARDS } from '../utils/fixtures';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const USE_FIXTURES = import.meta.env.VITE_USE_FIXTURES === 'true' || import.meta.env.VITE_USE_FIXTURES === true;

// Create centralized Axios instance
export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000, // 30s timeout for document AI operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor to attach auth tokens securely
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('infolens_auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor for global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server returned standard HTTP status error
      if (error.response.status === 401) {
        localStorage.removeItem('infolens_auth_token');
        // Dispatch session expired event if needed
        window.dispatchEvent(new CustomEvent('infolens:auth_expired'));
      }
    } else if (error.request) {
      // Network failure / server offline
      console.warn('InfoLens API: Network connection to backend failed or timed out.');
    }
    return Promise.reject(error);
  }
);

/**
 * Helper to safely wrap API calls with explicit fixture fallbacks when backend is unavailable or USE_FIXTURES is active.
 */
export async function apiCall(requestFn, fixtureFallbackFn) {
  if (USE_FIXTURES) {
    // Artificial delay to mimic realistic network latency
    await new Promise((resolve) => setTimeout(resolve, 350));
    return fixtureFallbackFn();
  }

  try {
    return await requestFn();
  } catch (error) {
    console.warn('Backend API request failed. Falling back to development fixtures where permitted.', error.message);
    if (fixtureFallbackFn) {
      await new Promise((resolve) => setTimeout(resolve, 300));
      return fixtureFallbackFn();
    }
    throw error;
  }
}
