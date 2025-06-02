// frontend/src/components/Layout/Sidebar.jsx
import React from 'react';
import { useChat } from '../../hooks/useChat';
import ChatHistory from '../Chat/ChatHistory';
import { Plus, X } from 'lucide-react';

const Sidebar = ({ isOpen, onClose, onNewChat }) => {
  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      } fixed lg:relative lg:translate-x-0 inset-y-0 left-0 z-50 w-80 bg-[#F9F9F9] border-r border-gray-200 transition-transform duration-300 ease-in-out flex flex-col`}>

        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Chat History</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={onNewChat}
              className="p-2 hover:bg-gray-200 rounded-lg transition duration-200"
              title="New Chat"
            >
              <Plus className="w-5 h-5 text-[#00ACB5]" />
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-200 rounded-lg transition duration-200 lg:hidden"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-4">
          <ChatHistory />
        </div>
      </div>
    </>
  );
};

export default Sidebar;