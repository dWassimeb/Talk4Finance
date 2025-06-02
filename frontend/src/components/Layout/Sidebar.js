// frontend/src/components/Layout/Sidebar.jsx
import React from 'react';
import { useChat } from '../../hooks/useChat';
import ChatHistory from '../Chat/ChatHistory';
import { Plus, X, MessageSquare } from 'lucide-react';

const Sidebar = ({ isOpen, onClose, onNewChat }) => {
  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      } fixed lg:relative lg:translate-x-0 inset-y-0 left-0 z-50 w-80 bg-white/90 backdrop-blur-xl border-r border-gray-200/50 transition-transform duration-300 ease-in-out flex flex-col`}>

        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200/50">
          <div className="flex items-center space-x-3">
            <MessageSquare className="w-5 h-5 text-[#00ACB5]" />
            <h2 className="text-lg font-semibold text-gray-900">Conversations</h2>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={onNewChat}
              className="group relative p-2.5 bg-gradient-to-r from-[#00ACB5] to-[#00929A] hover:from-[#00929A] hover:to-[#007A80] rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
              title="New Conversation"
            >
              <Plus className="w-4 h-4 text-white" />
              <div className="absolute -inset-1 bg-gradient-to-r from-[#00ACB5] to-[#00929A] rounded-xl blur opacity-25 group-hover:opacity-40 transition-opacity"></div>
            </button>
            <button
              onClick={onClose}
              className="p-2.5 hover:bg-gray-100/80 rounded-xl transition-all duration-200 lg:hidden"
            >
              <X className="w-4 h-4 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-4">
          <ChatHistory />
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200/50">
          <div className="text-center">
            <p className="text-xs text-gray-500">
              Powered by Castor
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;