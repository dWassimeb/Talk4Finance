// frontend/src/components/Chat/Chat.js
import React from 'react';
import ChatInterface from './ChatInterface';
import Header from '../Layout/Header';

const Chat = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#F8FFFE] to-[#E6F7F8]">
      <Header />
      <ChatInterface />
    </div>
  );
};

export default Chat;