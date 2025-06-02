// frontend/src/context/ChatContext.jsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import { chatService } from '../services/chat';
import { useAuth } from '../hooks/useAuth';

const ChatContext = createContext();

// Function to generate conversation title from message
const generateConversationTitle = (message) => {
  // Remove common question words and clean up
  const cleanMessage = message
    .toLowerCase()
    .replace(/^(what|how|when|where|why|who|can|could|would|should|tell me|show me|give me)/i, '')
    .replace(/\?/g, '')
    .trim();

  // Take first 40 characters and add ellipsis if needed
  let title = cleanMessage.charAt(0).toUpperCase() + cleanMessage.slice(1);
  if (title.length > 40) {
    title = title.substring(0, 40) + '...';
  }

  // If title is too short or empty, use topic-based names
  if (title.length < 10) {
    const topics = {
      'revenue': 'Revenue Analysis',
      'sales': 'Sales Performance',
      'profit': 'Profit Analysis',
      'margin': 'Margin Analysis',
      'budget': 'Budget Review',
      'cost': 'Cost Analysis',
      'expense': 'Expense Review',
      'performance': 'Performance Metrics',
      'kpi': 'KPI Dashboard',
      'financial': 'Financial Overview',
      'docaposte': 'Docaposte Analysis',
      'trend': 'Trend Analysis',
      'comparison': 'Comparative Analysis',
      'quarterly': 'Quarterly Report',
      'monthly': 'Monthly Report',
      'yearly': 'Annual Report'
    };

    const originalMessage = message.toLowerCase();
    for (const [keyword, topicTitle] of Object.entries(topics)) {
      if (originalMessage.includes(keyword)) {
        return topicTitle;
      }
    }

    // Fallback to date-based naming
    const now = new Date();
    return `Analysis ${now.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
  }

  return title || 'New Analysis';
};

export { ChatContext };

export const ChatProvider = ({ children }) => {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [ws, setWs] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      loadConversations();
      connectWebSocket();
    }

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [user]);

  const connectWebSocket = () => {
    if (!user) return;

    const websocket = new WebSocket(`ws://localhost:8000/ws/${user.id}`);

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'typing') {
        setIsTyping(data.typing);
      } else if (data.type === 'message') {
        const { user_message, agent_message, conversation_id } = data.response;
        setMessages(prev => [...prev, user_message, agent_message]);
        setIsTyping(false);

        // Update conversation title with the first message if it's still "New Conversation"
        if (currentConversation && currentConversation.title === 'New Conversation' && user_message) {
          const newTitle = generateConversationTitle(user_message.content);
          updateConversationTitle(conversation_id, newTitle);
        }
      } else if (data.type === 'error') {
        setIsTyping(false);
        console.error('Chat error:', data.error);
      }
    };

    websocket.onopen = () => {
      console.log('WebSocket connected');
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setTimeout(connectWebSocket, 3000);
    };

    setWs(websocket);
  };

  const loadConversations = async () => {
    try {
      const convs = await chatService.getConversations();
      setConversations(convs);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const createNewConversation = async (title = 'New Conversation') => {
    try {
      const newConv = await chatService.createConversation(title);
      setConversations(prev => [newConv, ...prev]);
      setCurrentConversation(newConv);
      setMessages([]);
      return newConv;
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const updateConversationTitle = async (conversationId, newTitle) => {
    try {
      // Update local state immediately
      setConversations(prev => prev.map(conv =>
        conv.id === conversationId ? { ...conv, title: newTitle } : conv
      ));

      if (currentConversation && currentConversation.id === conversationId) {
        setCurrentConversation(prev => ({ ...prev, title: newTitle }));
      }

      // TODO: Add API call to update title on backend when ready
      // await chatService.updateConversationTitle(conversationId, newTitle);
    } catch (error) {
      console.error('Failed to update conversation title:', error);
    }
  };

  const selectConversation = async (conversationId) => {
    try {
      const conv = await chatService.getConversation(conversationId);
      setCurrentConversation(conv);
      setMessages(conv.messages || []);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const sendMessage = (message) => {
    if (!ws || !message.trim()) return;

    // If this is the first message and conversation title is still default, generate a title
    if (currentConversation && currentConversation.title === 'New Conversation' && messages.length === 0) {
      const newTitle = generateConversationTitle(message);
      updateConversationTitle(currentConversation.id, newTitle);
    }

    const messageData = {
      message: message.trim(),
      conversation_id: currentConversation?.id
    };

    ws.send(JSON.stringify(messageData));
  };

  const deleteConversation = async (conversationId) => {
    try {
      await chatService.deleteConversation(conversationId);
      setConversations(prev => prev.filter(c => c.id !== conversationId));
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  return (
    <ChatContext.Provider value={{
      conversations,
      currentConversation,
      messages,
      isTyping,
      createNewConversation,
      selectConversation,
      sendMessage,
      deleteConversation,
      loadConversations,
      updateConversationTitle
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};