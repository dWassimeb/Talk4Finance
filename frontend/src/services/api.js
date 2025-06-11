// frontend/src/services/api.js - FIXED VERSION
import axios from 'axios';

// FIXED: Dynamic API URL based on environment
const getApiBaseUrl = () => {
  // In production (Docker), use the current host with the mapped port
  if (process.env.NODE_ENV === 'production') {
    // When running in Docker with port mapping, use the external port
    return window.location.origin.replace(window.location.port, '3001');
  }

  // For development, check if we're running in a containerized environment
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    // Running in Docker or deployed environment
    return `${window.location.protocol}//${window.location.hostname}:3001`;
  }

  // Local development
  return process.env.REACT_APP_API_URL || 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

console.log('API Base URL:', API_BASE_URL); // Debug log

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Add auth token to requests
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

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response || error.message);

    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;