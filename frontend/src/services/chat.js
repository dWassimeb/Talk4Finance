// frontend/src/services/chat.js - COMPLETE VERSION
import api from './api';

export const chatService = {
  async getConversations() {
    const response = await api.get('/api/chat/conversations');
    return response.data;
  },

  async createConversation(title = 'New Conversation') {
    const response = await api.post('/api/chat/conversations', {
      title: title
    });
    return response.data;
  },

  async getConversation(conversationId) {
    const response = await api.get(`/api/chat/conversations/${conversationId}`);
    return response.data;
  },

  async deleteConversation(conversationId) {
    const response = await api.delete(`/api/chat/conversations/${conversationId}`);
    return response.data;
  },

  // ADD THIS MISSING METHOD
  async updateConversationTitle(conversationId, title) {
    const response = await api.put(`/api/chat/conversations/${conversationId}/title`, {
      title: title
    });
    return response.data;
  }
};