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

  // Admin functions
  async getPendingUsers() {
    const response = await api.get('/api/auth/admin/pending-users');
    return response.data;
  },

  async getAllUsers() {
    const response = await api.get('/api/auth/admin/all-users');
    return response.data;
  },

  async approveUser(userId, action, rejectionReason = null) {
    const payload = {
      user_id: userId,
      action: action
    };

    if (action === 'reject' && rejectionReason) {
      payload.rejection_reason = rejectionReason;
    }

    const response = await api.post('/api/auth/admin/approve-user', payload);
    return response.data;
  },

  async updateUserStatus(userId, newStatus) {
    const response = await api.put(`/api/auth/admin/user/${userId}/status`, {
      status: newStatus
    });
    return response.data;
  }
};