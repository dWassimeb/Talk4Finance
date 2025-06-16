// frontend/src/services/api.js - IMPROVED ERROR HANDLING
import axios from 'axios';

const getApiBaseUrl = () => {
  if (process.env.NODE_ENV === 'development' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  return `${window.location.origin}/talk4finance`;
};

const API_BASE_URL = getApiBaseUrl();
console.log('API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response || error.message);

    // Extract detailed error message from response
    let errorMessage = 'An unexpected error occurred';

    if (error.response) {
      // Server responded with error status
      if (error.response.data?.detail) {
        // FastAPI sends errors in 'detail' field
        errorMessage = error.response.data.detail;
      } else if (error.response.data?.message) {
        // Alternative error message field
        errorMessage = error.response.data.message;
      } else if (typeof error.response.data === 'string') {
        errorMessage = error.response.data;
      } else {
        // Fallback to status text
        errorMessage = `${error.response.status}: ${error.response.statusText}`;
      }
    } else if (error.request) {
      // Network error
      errorMessage = 'Network error - please check your connection';
    } else {
      // Other error
      errorMessage = error.message;
    }

    // Create enhanced error object
    const enhancedError = new Error(errorMessage);
    enhancedError.originalError = error;
    enhancedError.status = error.response?.status;

    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/talk4finance/login';
    }

    return Promise.reject(enhancedError);
  }
);

export default api;