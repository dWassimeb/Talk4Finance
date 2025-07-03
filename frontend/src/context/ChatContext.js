// frontend/src/context/ChatContext.js - COMPLETE FIXED VERSION
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { chatService } from '../services/chat';

const ChatContext = createContext();

// Environment-aware WebSocket URL function
const getWebSocketUrl = (userId) => {
  const isProduction = window.location.hostname !== 'localhost';
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

  if (isProduction) {
    // Production: Use the same host with subpath
    const baseUrl = `${protocol}//${window.location.host}`;
    return `${baseUrl}/talk4finance/ws/${userId}`;
  } else {
    // Development: Direct connection to backend
    return `ws://localhost:8000/ws/${userId}`;
  }
};

// Enhanced conversation title generation
const generateConversationTitle = (message) => {
  if (!message || typeof message !== 'string') {
    return 'New Conversation';
  }

  // Financial topic mapping
  const topics = {
    'revenue': 'Revenue Analysis',
    'sales': 'Sales Analysis',
    'profit': 'Profit Analysis',
    'margin': 'Margin Analysis',
    'budget': 'Budget Review',
    'cost': 'Cost Analysis',
    'performance': 'Performance Metrics',
    'growth': 'Growth Analysis',
    'trend': 'Trend Analysis',
    'forecast': 'Forecast Review',
    'kpi': 'KPI Dashboard',
    'metric': 'Metrics Review',
    'report': 'Report Analysis',
    'data': 'Data Insights',
    'analytics': 'Analytics Review',
    'financial': 'Financial Review',
    'quarterly': 'Quarterly Review',
    'annual': 'Annual Review',
    'comparison': 'Comparison Analysis',
    'benchmark': 'Benchmark Review'
  };

  // Check for topic keywords
  const originalMessage = message.toLowerCase();
  for (const [keyword, topicTitle] of Object.entries(topics)) {
    if (originalMessage.includes(keyword)) {
      return topicTitle;
    }
  }

  // Extract meaningful words for title
  const words = message
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(word =>
      word.length > 2 &&
      !['show', 'give', 'tell', 'what', 'how', 'when', 'where', 'why', 'the', 'and', 'for', 'with', 'can', 'you', 'me', 'please'].includes(word)
    );

  if (words.length >= 2) {
    return words.slice(0, 3).join(' ').replace(/\b\w/g, l => l.toUpperCase());
  } else if (words.length === 1) {
    return words[0].charAt(0).toUpperCase() + words[0].slice(1) + ' Analysis';
  }

  // Fallback to date-based naming
  const now = new Date();
  return `Chat ${now.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
};

export { ChatContext };

export const ChatProvider = ({ children }) => {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [ws, setWs] = useState(null);
  const [hasAutoCreatedConversation, setHasAutoCreatedConversation] = useState(false);
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

  const loadConversations = async () => {
    if (!user) return;

    try {
      const convs = await chatService.getConversations();
      setConversations(convs);
      console.log(`📋 Loaded ${convs.length} conversations`);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const createNewConversation = async () => {
    try {
      const newConv = await chatService.createConversation();
      setConversations(prev => [newConv, ...prev]);
      setCurrentConversation(newConv);
      setMessages([]);
      console.log(`➕ Created new conversation: ${newConv.id}`);
      return newConv;
    } catch (error) {
      console.error('Failed to create conversation:', error);
      return null;
    }
  };

  // FIXED: Complete updateConversationTitle function that was missing
  const updateConversationTitle = async (conversationId, newTitle) => {
    try {
      console.log(`🏷️ Updating conversation ${conversationId} title to: "${newTitle}"`);

      // Update local state immediately for better UX
      setConversations(prev =>
        prev.map(conv =>
          conv.id === conversationId ? { ...conv, title: newTitle } : conv
        )
      );

      if (currentConversation && currentConversation.id === conversationId) {
        setCurrentConversation(prev => ({ ...prev, title: newTitle }));
      }

      // FIXED: Actually call the API instead of TODO comment
      await chatService.updateConversationTitle(conversationId, newTitle);
      console.log(`✅ Successfully updated conversation title on backend`);

    } catch (error) {
      console.error('❌ Failed to update conversation title:', error);

      // Revert local state on failure
      setConversations(prev =>
        prev.map(conv =>
          conv.id === conversationId ? { ...conv, title: 'New Conversation' } : conv
        )
      );

      if (currentConversation && currentConversation.id === conversationId) {
        setCurrentConversation(prev => ({ ...prev, title: 'New Conversation' }));
      }
    }
  };

  const connectWebSocket = () => {
    if (!user) return;

    const websocketUrl = getWebSocketUrl(user.id);
    console.log('🔌 Connecting to WebSocket:', websocketUrl);

    const websocket = new WebSocket(websocketUrl);

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'typing') {
        setIsTyping(data.typing);
      } else if (data.type === 'message') {
        const { user_message, agent_message, conversation_id } = data.response;
        setMessages(prev => [...prev, user_message, agent_message]);
        setIsTyping(false);

        // FIXED: Update conversation title with the first message if it's still "New Conversation"
        if (currentConversation && currentConversation.title === 'New Conversation' && user_message) {
          const newTitle = generateConversationTitle(user_message.content);
          console.log(`🏷️ Generated title: "${newTitle}" from message: "${user_message.content}"`);
          updateConversationTitle(conversation_id, newTitle);
        }

        // Refresh conversations list to update the "updated_at" timestamp
        loadConversations();
      } else if (data.type === 'error') {
        setIsTyping(false);
        console.error('Chat error:', data.error);
      }
    };

    websocket.onopen = () => {
      console.log('✅ WebSocket connected successfully');
    };

    websocket.onclose = () => {
      console.log('❌ WebSocket disconnected');
    };

    websocket.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
    };

    setWs(websocket);
  };

  const selectConversation = async (conversationId) => {
    try {
      const conv = await chatService.getConversation(conversationId);
      setCurrentConversation(conv);
      setMessages(conv.messages || []);
      console.log(`📖 Loaded conversation: "${conv.title}" with ${conv.messages?.length || 0} messages`);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const sendMessage = async (message) => {
    if (!ws || !message.trim()) return;

    // Create a new conversation if there isn't one
    let conversation = currentConversation;
    if (!conversation) {
      conversation = await createNewConversation();
      if (!conversation) {
        console.error('Failed to create conversation');
        return;
      }
    }

    const messageData = {
      message: message.trim(),
      conversation_id: conversation.id
    };

    console.log('📤 Sending message via WebSocket:', messageData);
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
      console.log(`🗑️ Deleted conversation: ${conversationId}`);
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
      updateConversationTitle,
      hasAutoCreatedConversation,
      setHasAutoCreatedConversation
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