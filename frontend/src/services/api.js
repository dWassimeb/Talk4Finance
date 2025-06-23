// frontend/src/services/api.js - COMPLETE FIXED VERSION FOR ALL ENVIRONMENTS
import axios from 'axios';

const getApiBaseUrl = () => {
  const hostname = window.location.hostname;
  const port = window.location.port;
  const protocol = window.location.protocol;

  console.log('Environment detection:');
  console.log('- Hostname:', hostname);
  console.log('- Port:', port);
  console.log('- Protocol:', protocol);
  console.log('- NODE_ENV:', process.env.NODE_ENV);

  // Environment 1: Local development (separate servers)
  // Frontend on 3000, Backend on 8000
  if (process.env.NODE_ENV === 'development' ||
      (hostname === 'localhost' && port === '3000') ||
      (hostname === '127.0.0.1' && port === '3000')) {
    console.log('🔧 Using LOCAL DEVELOPMENT environment');
    return 'http://localhost:8000';
  }

  // Environment 2: Docker Desktop (single container)
  // Everything served from the same container on port 3001
  if ((hostname === 'localhost' && port === '3001') ||
      (hostname === '127.0.0.1' && port === '3001')) {
    console.log('🐳 Using DOCKER DESKTOP environment');
    // In Docker, both frontend and API are served from the same origin
    // No need for /talk4finance prefix as we're accessing directly
    return window.location.origin;
  }

  // Environment 3: DocaCloud with reverse proxy
  // Accessing via http://castor.iagen-ov.fr/talk4finance/
  if (hostname.includes('castor.iagen-ov.fr') ||
      hostname.includes('iagen-ov.fr') ||
      window.location.pathname.startsWith('/talk4finance')) {
    console.log('☁️ Using DOCACLOUD (reverse proxy) environment');
    // Use current origin + subpath for reverse proxy
    return `${window.location.origin}/talk4finance`;
  }

  // Default fallback: assume reverse proxy setup
  console.log('🔄 Using FALLBACK (assuming reverse proxy) environment');
  return `${window.location.origin}/talk4finance`;
};

const API_BASE_URL = getApiBaseUrl();
console.log('🎯 Final API Base URL:', API_BASE_URL);

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

    // Log the full API call for debugging
    const fullUrl = config.baseURL + config.url;
    console.log(`📡 API Request: ${config.method?.toUpperCase()} ${fullUrl}`);

    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Success: ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Error Details:');
    console.error('- URL:', error.config?.url);
    console.error('- Method:', error.config?.method);
    console.error('- Base URL:', error.config?.baseURL);
    console.error('- Full URL:', error.config?.baseURL + error.config?.url);
    console.error('- Status:', error.response?.status);
    console.error('- Message:', error.message);

    if (error.response?.status === 401) {
      localStorage.removeItem('token');

      // FIXED: Determine the correct login path based on environment
      const hostname = window.location.hostname;
      const port = window.location.port;

      let loginPath;

      // Docker Desktop environment - use /talk4finance prefix
      if ((hostname === 'localhost' && port === '3001') ||
          (hostname === '127.0.0.1' && port === '3001')) {
        loginPath = '/talk4finance/login';
      }
      // DocaCloud environment - use /talk4finance prefix
      else if (hostname.includes('castor.iagen-ov.fr') ||
               hostname.includes('iagen-ov.fr') ||
               window.location.pathname.startsWith('/talk4finance')) {
        loginPath = '/talk4finance/login';
      }
      // Local development - no prefix
      else {
        loginPath = '/login';
      }

      console.log(`🔄 Redirecting to: ${loginPath}`);
      window.location.href = loginPath;
    }

    return Promise.reject(error);
  }
);

export default api;