// frontend/src/components/Chat/ChatInterface.js
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useChat } from '../../hooks/useChat';
import ChatHistory from './ChatHistory';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import Header from '../Layout/Header';
import Sidebar from '../Layout/Sidebar';
import UserProfile from '../User/UserProfile';
import AdminDashboard from '../Admin/AdminDashboard';
import { Sparkles, TrendingUp, BarChart3, DollarSign } from 'lucide-react';

const ChatInterface = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [profileOpen, setProfileOpen] = useState(false);
  const [adminDashboardOpen, setAdminDashboardOpen] = useState(false);
  const { user } = useAuth();
  const { currentConversation, messages, isTyping, sendMessage, createNewConversation } = useChat();

  const handleSendMessage = (message) => {
    sendMessage(message);
  };

  const handleNewChat = () => {
    createNewConversation();
  };

  const handleProfileClick = () => {
    setProfileOpen(true);
  };

  const handleAdminClick = () => {
    setAdminDashboardOpen(true);
  };

  // Suggested prompts for empty state
  const suggestedPrompts = [
    {
      icon: TrendingUp,
      title: "Revenue Analysis",
      prompt: "Show me the revenue trends for Q4 2024"
    },
    {
      icon: BarChart3,
      title: "Performance Metrics",
      prompt: "Compare our performance vs budget this year"
    },
    {
      icon: DollarSign,
      title: "Margin Analysis",
      prompt: "What are the top 5 products by gross margin?"
    },
    {
      icon: Sparkles,
      title: "YoY Growth",
      prompt: "Show year-over-year growth for HCS business unit"
    }
  ];

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 to-white">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onNewChat={handleNewChat}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <Header
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          user={user}
          onProfileClick={handleProfileClick}
          onAdminClick={handleAdminClick}
        />

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            // Empty State - Original Design
            <div className="flex items-center justify-center h-full p-8">
              <div className="text-center max-w-3xl">
                <div className="w-16 h-16 bg-gradient-to-br from-[#00ACB5] to-[#00929A] rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  Welcome to Talk4Finance
                </h2>
                <p className="text-gray-600 mb-8 text-lg">
                  Your AI-powered financial agent. Ask me anything about Docaposte financial data and performance metrics.
                </p>

                {/* Suggested Prompts - Original Style */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto">
                  {suggestedPrompts.map((prompt, index) => (
                    <button
                      key={index}
                      onClick={() => handleSendMessage(prompt.prompt)}
                      className="group p-4 text-left bg-white/80 backdrop-blur-sm hover:bg-white border border-gray-200/50 hover:border-[#00ACB5]/30 rounded-2xl transition-all duration-200 hover:shadow-lg hover:shadow-[#00ACB5]/10"
                    >
                      <div className="flex items-start space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-[#00ACB5]/10 to-[#00929A]/10 rounded-xl flex items-center justify-center group-hover:from-[#00ACB5]/20 group-hover:to-[#00929A]/20 transition-all duration-200">
                          <prompt.icon className="w-5 h-5 text-[#00ACB5]" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-gray-900 mb-1">
                            {prompt.title}
                          </h3>
                          <p className="text-sm text-gray-600">
                            {prompt.prompt}
                          </p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            // Messages - Original Style
            <div className="p-6 space-y-6 max-w-4xl mx-auto w-full">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  isUser={message.is_user}
                />
              ))}
              {isTyping && (
                <ChatMessage
                  message={{ content: "Analyzing your data..." }}
                  isUser={false}
                  isTyping={true}
                />
              )}
            </div>
          )}
        </div>

        {/* Chat Input - Original Style */}
        <div className="border-t border-gray-200/50 bg-white/80 backdrop-blur-xl">
          <ChatInput onSendMessage={handleSendMessage} disabled={isTyping} />
        </div>
      </div>

      {/* Modals */}
      <UserProfile
        isOpen={profileOpen}
        onClose={() => setProfileOpen(false)}
      />

      {user?.role === 'admin' && (
        <AdminDashboard
          isOpen={adminDashboardOpen}
          onClose={() => setAdminDashboardOpen(false)}
        />
      )}
    </div>
  );
};

export default ChatInterface;