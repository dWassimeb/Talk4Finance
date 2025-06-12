// frontend/src/services/api.js - NO SUBPATH (nginx handles routing)
import axios from 'axios';

const getApiBaseUrl = () => {
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000';
  }

  // For production: nginx strips /talk4finance/ before forwarding to FastAPI
  // So React app sees URLs like: /api/auth/login (not /talk4finance/api/auth/login)
  return window.location.origin + window.location.pathname.replace(/\/$/, '');
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

    console.log(`🚀 API Call: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('❌ API Error:', error.response || error.message);

    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;