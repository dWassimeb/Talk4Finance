// frontend/src/components/Chat/ChatHistory.jsx
import React from 'react';
import { useChat } from '../../hooks/useChat';
import { MessageSquare, Trash2, Clock } from 'lucide-react';

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

  return (
    <div className="space-y-2">
      {conversations.map((conversation) => (
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
            {/* Message Icon */}
            <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 ${
              currentConversation?.id === conversation.id
                ? 'bg-gradient-to-br from-[#00ACB5] to-[#00929A]'
                : 'bg-gray-100 group-hover:bg-[#00ACB5]/10'
            }`}>
              <MessageSquare className={`w-4 h-4 ${
                currentConversation?.id === conversation.id
                  ? 'text-white'
                  : 'text-gray-500 group-hover:text-[#00ACB5]'
              }`} />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <h3 className={`text-sm font-medium truncate ${
                currentConversation?.id === conversation.id
                  ? 'text-[#00929A]'
                  : 'text-gray-900'
              }`}>
                {conversation.title}
              </h3>
              <div className="flex items-center space-x-2 mt-1">
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
      ))}

      {conversations.length === 0 && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <MessageSquare className="w-8 h-8 text-gray-400" />
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