// frontend/src/components/Layout/Header.jsx
import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Menu, Bot, LogOut, User } from 'lucide-react'; // Changed Database to Bot

const Header = ({ onMenuClick, user }) => {
  const { logout } = useAuth();

  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <button
            onClick={onMenuClick}
            className="p-2 hover:bg-gray-100 rounded-lg transition duration-200 lg:hidden"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center space-x-2">
            <Bot className="w-6 h-6 text-[#00ACB5]" /> {/* Changed icon and color */}
            <h1 className="text-xl font-semibold text-gray-900">FinSight</h1>
            <span className="text-sm text-gray-500">- Your Personal PowerBI Agent</span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <User className="w-4 h-4" />
            <span>{user?.username}</span>
          </div>
          <button
            onClick={logout}
            className="flex items-center space-x-1 px-3 py-2 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition duration-200"
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;