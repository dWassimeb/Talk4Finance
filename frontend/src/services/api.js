// frontend/src/services/api.js - SIMPLE FIX
import axios from 'axios';

const getApiBaseUrl = () => {
  // For local development
  if (process.env.NODE_ENV === 'development' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }

  // For production deployment with reverse proxy
  // Just use current origin + subpath (no port manipulation needed)
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

    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/talk4finance/login';
    }
    return Promise.reject(error);
  }
);

export default api;