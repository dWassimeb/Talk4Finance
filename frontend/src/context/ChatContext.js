// frontend/src/context/ChatContext.js - FIXED WEBSOCKET URL
import React, { createContext, useState, useEffect, useContext } from 'react';
import { useAuth } from '../hooks/useAuth';
import { chatService } from '../services/chat';

const ChatContext = createContext();

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
};

// Function to get WebSocket URL
const getWebSocketUrl = () => {
  if (process.env.NODE_ENV === 'development' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'ws://localhost:8000';
  }

  // For production, use the same domain but with WebSocket protocol
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${window.location.host}/talk4finance`;
};

const generateConversationTitle = (message) => {
  if (!message || typeof message !== 'string') {
    return 'New Conversation';
  }

  const topics = {
    'revenue': 'Revenue Analysis',
    'sales': 'Sales Performance',
    'profit': 'Profit Analysis',
    'margin': 'Margin Review',
    'budget': 'Budget Analysis',
    'cost': 'Cost Analysis',
    'customer': 'Customer Insights',
    'product': 'Product Analysis',
    'performance': 'Performance Review',
    'trend': 'Trend Analysis',
    'growth': 'Growth Analysis',
    'compare': 'Comparison Report',
    'forecast': 'Forecast Analysis'
  };

  const title = message.substring(0, 50);
  const originalMessage = message.toLowerCase();

  for (const [keyword, topicTitle] of Object.entries(topics)) {
    if (originalMessage.includes(keyword)) {
      return topicTitle;
    }
  }

  const words = title.split(' ').filter(word =>
    word.length > 2 &&
    !['show', 'give', 'tell', 'what', 'how', 'when', 'where', 'why', 'the', 'and', 'for', 'with'].includes(word.toLowerCase())
  );

  if (words.length >= 2) {
    return words.slice(0, 3).join(' ');
  }

  const now = new Date();
  return `Analysis ${now.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
};

export const ChatProvider = ({ children }) => {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [ws, setWs] = useState(null);
  const [connectionError, setConnectionError] = useState(null);
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

  const connectWebSocket = () => {
    if (!user) return;

    const WS_URL = getWebSocketUrl();
    console.log('Connecting to WebSocket:', `${WS_URL}/ws/${user.id}`);

    try {
      const websocket = new WebSocket(`${WS_URL}/ws/${user.id}`);

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message received:', data);

          if (data.type === 'typing') {
            setIsTyping(data.typing);
          } else if (data.type === 'response') {
            // Handle new message format
            setMessages(prev => [...prev, {
              id: Date.now(),
              content: data.message,
              type: 'assistant',
              timestamp: new Date()
            }]);
            setIsTyping(false);
            loadConversations(); // Refresh conversations
          } else if (data.type === 'error') {
            setIsTyping(false);
            console.error('Chat error:', data.message);
            // Show error message to user
            setMessages(prev => [...prev, {
              id: Date.now(),
              content: `Error: ${data.message}`,
              type: 'error',
              timestamp: new Date()
            }]);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      websocket.onopen = () => {
        console.log('WebSocket connected successfully');
        setConnectionError(null);
      };

      websocket.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setConnectionError('Connection lost. Reconnecting...');
        setTimeout(connectWebSocket, 3000);
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionError('Failed to connect to chat service');
      };

      setWs(websocket);
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionError('Failed to initialize chat connection');
    }
  };

  const loadConversations = async () => {
    try {
      const convs = await chatService.getConversations();
      setConversations(convs);

      if (currentConversation && !convs.find(c => c.id === currentConversation.id)) {
        setCurrentConversation(null);
        setMessages([]);
      }
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
      throw error;
    }
  };

  const sendMessage = async (message) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      throw new Error('Chat connection not available. Please refresh the page.');
    }

    try {
      let conversation = currentConversation;

      if (!conversation) {
        conversation = await createNewConversation();
      }

      // Add user message to UI immediately
      const userMessage = {
        id: Date.now(),
        content: message,
        type: 'user',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, userMessage]);

      // Send message via WebSocket
      ws.send(JSON.stringify({
        message: message,
        conversation_id: conversation.id
      }));

      // Update conversation title if it's the first message
      if (conversation.title === 'New Conversation') {
        const newTitle = generateConversationTitle(message);
        await updateConversationTitle(conversation.id, newTitle);
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  };

  const updateConversationTitle = async (conversationId, newTitle) => {
    try {
      setConversations(prev => prev.map(conv =>
        conv.id === conversationId ? { ...conv, title: newTitle } : conv
      ));

      if (currentConversation && currentConversation.id === conversationId) {
        setCurrentConversation(prev => ({ ...prev, title: newTitle }));
      }
    } catch (error) {
      console.error('Failed to update conversation title:', error);
    }
  };

  const deleteConversation = async (conversationId) => {
    try {
      await chatService.deleteConversation(conversationId);
      setConversations(prev => prev.filter(conv => conv.id !== conversationId));

      if (currentConversation && currentConversation.id === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      throw error;
    }
  };

  const selectConversation = (conversation) => {
    setCurrentConversation(conversation);
    setMessages([]); // Clear messages - in a real app, you'd load conversation history
  };

  const value = {
    conversations,
    currentConversation,
    messages,
    isTyping,
    connectionError,
    sendMessage,
    createNewConversation,
    deleteConversation,
    selectConversation,
    loadConversations
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export { ChatContext };