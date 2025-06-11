// frontend/src/services/api.js - FIXED FOR SUBPATH DEPLOYMENT
import axios from 'axios';

// Smart API URL detection for subpath deployment
const getApiBaseUrl = () => {
  // 1. Check for explicit environment variable first
  if (process.env.REACT_APP_API_URL) {
    console.log('Using explicit API URL:', process.env.REACT_APP_API_URL);
    return process.env.REACT_APP_API_URL;
  }

  // 2. For production deployment with subpath (like /talk4finance/)
  if (process.env.NODE_ENV === 'production') {
    // When deployed behind reverse proxy with subpath
    const currentUrl = window.location.origin + window.location.pathname;

    // Remove trailing slash and add if not present
    const baseUrl = currentUrl.endsWith('/') ? currentUrl.slice(0, -1) : currentUrl;

    console.log('Production subpath mode:', baseUrl);
    return baseUrl;
  }

  // 3. Development mode
  console.log('Development mode: using localhost:8000');
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();
console.log('Final API Base URL:', API_BASE_URL);

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // Increased timeout for network latency
});

// Add request interceptor for auth and debugging
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Log the full URL being called for debugging
    const fullUrl = `${config.baseURL}${config.url}`;
    console.log(`API Call: ${config.method?.toUpperCase()} ${fullUrl}`);

    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling and debugging
api.interceptors.response.use(
  (response) => {
    console.log(`API Success: ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Error Details:', {
      url: error.config?.url,
      method: error.config?.method,
      baseURL: error.config?.baseURL,
      status: error.response?.status,
      statusText: error.response?.statusText,
      message: error.message,
      data: error.response?.data
    });

    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      // Use relative path for redirect to work with subpath
      window.location.href = './login';
    }

    return Promise.reject(error);
  }
);

export default api;