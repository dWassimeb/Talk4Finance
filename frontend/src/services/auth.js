// frontend/src/services/auth.js
import api from './api';

export const authService = {
  async login(email, password) {
    const response = await api.post('/api/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  async register(email, username, password) {
    const response = await api.post('/api/auth/register', {
      email,
      username,
      password,
    });
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  async updateProfile(profileData) {
    const response = await api.put('/api/auth/profile', profileData);
    return response.data;
  },

  async changePassword(passwordData) {
    const response = await api.put('/api/auth/change-password', passwordData);
    return response.data;
  },
};