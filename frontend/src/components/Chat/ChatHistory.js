// frontend/src/components/Chat/ChatHistory.js
import React from 'react';
import { useChat } from '../../hooks/useChat';
import { MessageCircle, Trash2, Clock, Sparkles, TrendingUp, BarChart3, DollarSign } from 'lucide-react';

const ChatHistory = () => {
  const { conversations, currentConversation, selectConversation, deleteConversation } = useChat();

  const handleDeleteConversation = (e, conversationId) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      deleteConversation(conversationId);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 7 * 24) {
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  // Get appropriate icon based on conversation title
  const getConversationIcon = (title) => {
    const lowerTitle = title.toLowerCase();
    if (lowerTitle.includes('revenue') || lowerTitle.includes('sales') || lowerTitle.includes('income')) {
      return TrendingUp;
    } else if (lowerTitle.includes('performance') || lowerTitle.includes('metric') || lowerTitle.includes('kpi')) {
      return BarChart3;
    } else if (lowerTitle.includes('margin') || lowerTitle.includes('profit') || lowerTitle.includes('cost')) {
      return DollarSign;
    } else if (lowerTitle.includes('analysis') || lowerTitle.includes('insight')) {
      return Sparkles;
    }
    return MessageCircle;
  };

  return (
    <div className="space-y-2">
      {conversations.map((conversation) => {
        const IconComponent = getConversationIcon(conversation.title);

        return (
          <div
            key={conversation.id}
            onClick={() => selectConversation(conversation.id)}
            className={`group relative p-4 rounded-2xl cursor-pointer transition-all duration-200 ${
              currentConversation?.id === conversation.id
                ? 'bg-gradient-to-r from-[#00ACB5]/10 to-[#00929A]/10 border-2 border-[#00ACB5]/20 shadow-lg'
                : 'bg-white/60 hover:bg-white/80 border border-gray-200/50 hover:border-[#00ACB5]/30 hover:shadow-md'
            }`}
          >
            <div className="flex items-start space-x-3">
              {/* Modern Message Icon */}
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-200 ${
                currentConversation?.id === conversation.id
                  ? 'bg-gradient-to-br from-[#00ACB5] to-[#00929A] scale-110'
                  : 'bg-gradient-to-br from-gray-100 to-gray-200 group-hover:from-[#00ACB5]/20 group-hover:to-[#00929A]/20 group-hover:scale-105'
              }`}>
                <IconComponent className={`w-5 h-5 transition-colors duration-200 ${
                  currentConversation?.id === conversation.id
                    ? 'text-white'
                    : 'text-gray-500 group-hover:text-[#00ACB5]'
                }`} />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <h3 className={`text-sm font-medium truncate mb-1 ${
                  currentConversation?.id === conversation.id
                    ? 'text-[#00929A]'
                    : 'text-gray-900'
                }`}>
                  {conversation.title}
                </h3>
                <div className="flex items-center space-x-2">
                  <Clock className="w-3 h-3 text-gray-400" />
                  <p className="text-xs text-gray-500">
                    {formatDate(conversation.updated_at)}
                  </p>
                </div>
              </div>

              {/* Delete Button */}
              <button
                onClick={(e) => handleDeleteConversation(e, conversation.id)}
                className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-100 rounded-lg transition-all duration-200 absolute top-2 right-2"
                title="Delete conversation"
              >
                <Trash2 className="w-4 h-4 text-red-500" />
              </button>
            </div>

            {/* Active Indicator */}
            {currentConversation?.id === conversation.id && (
              <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-[#00ACB5] to-[#00929A] rounded-r-full"></div>
            )}
          </div>
        );
      })}

      {conversations.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <MessageCircle className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-sm font-medium text-gray-600 mb-2">No conversations yet</h3>
          <p className="text-xs text-gray-500 leading-relaxed">
            Start a new conversation to analyze your financial data and get insights.
          </p>
        </div>
      )}
    </div>
  );
};

export default ChatHistory;