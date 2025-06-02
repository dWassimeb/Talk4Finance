// frontend/src/components/Chat/ChatHistory.jsx
import React from 'react';
import { useChat } from '../../hooks/useChat';
import { MessageSquare, Trash2 } from 'lucide-react';

const ChatHistory = () => {
  const { conversations, currentConversation, selectConversation, deleteConversation } = useChat();

  const handleDeleteConversation = (e, conversationId) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      deleteConversation(conversationId);
    }
  };

  return (
    <div className="space-y-2">
      {conversations.map((conversation) => (
        <div
          key={conversation.id}
          onClick={() => selectConversation(conversation.id)}
          className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition duration-200 ${
            currentConversation?.id === conversation.id
              ? 'bg-[#00ACB5] bg-opacity-10 border-[#00ACB5] text-[#00929A]'
              : 'bg-[#FFFFFF] hover:bg-gray-50 border-gray-200'
          } border`}
        >
          <div className="flex items-center space-x-3 flex-1 min-w-0">
            <MessageSquare className={`w-5 h-5 flex-shrink-0 ${
              currentConversation?.id === conversation.id ? 'text-[#00ACB5]' : 'text-gray-500'
            }`} />
            <div className="min-w-0 flex-1">
              <p className={`text-sm font-medium truncate ${
                currentConversation?.id === conversation.id ? 'text-[#00929A]' : 'text-gray-900'
              }`}>
                {conversation.title}
              </p>
              <p className="text-xs text-gray-500">
                {new Date(conversation.updated_at).toLocaleDateString()}
              </p>
            </div>
          </div>
          <button
            onClick={(e) => handleDeleteConversation(e, conversation.id)}
            className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition duration-200"
          >
            <Trash2 className="w-4 h-4 text-red-500" />
          </button>
        </div>
      ))}

      {conversations.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>No conversations yet</p>
          <p className="text-sm">Start chatting to see your history</p>
        </div>
      )}
    </div>
  );
};

export default ChatHistory;