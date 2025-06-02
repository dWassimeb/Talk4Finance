// frontend/src/components/Chat/ChatInterface.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useChat } from '../../hooks/useChat';
import ChatHistory from './ChatHistory';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import Header from '../Layout/Header';
import Sidebar from '../Layout/Sidebar';
import { Menu } from 'lucide-react';

const ChatInterface = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { user } = useAuth();
  const { currentConversation, messages, isTyping, sendMessage, createNewConversation } = useChat();

  useEffect(() => {
    // Auto-create first conversation if none exists
    if (!currentConversation) {
      createNewConversation();
    }
  }, []);

  const handleSendMessage = (message) => {
    sendMessage(message);
  };

  const handleNewChat = () => {
    createNewConversation();
  };

  return (
    <div className="flex h-screen bg-[#F9F9F9]"> {/* Updated background color */}
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onNewChat={handleNewChat}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Header
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          user={user}
        />

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="text-gray-400 text-lg mb-2">
                  Welcome to FinSight, your personal PowerBI Agent
                </div>
                <div className="text-gray-500 text-sm">
                  Ask me anything about Docaposte financial performance
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  isUser={message.is_user}
                />
              ))}
              {isTyping && (
                <ChatMessage
                  message={{ content: "Thinking..." }}
                  isUser={false}
                  isTyping={true}
                />
              )}
            </>
          )}
        </div>

        {/* Chat Input */}
        <ChatInput onSendMessage={handleSendMessage} disabled={isTyping} />
      </div>
    </div>
  );
};

export default ChatInterface;