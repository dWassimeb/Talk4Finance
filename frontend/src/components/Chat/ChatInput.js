// frontend/src/components/Chat/ChatInput.jsx
import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Mic } from 'lucide-react';

const ChatInput = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleTextareaChange = (e) => {
    setMessage(e.target.value);

    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  return (
    <div className="p-6">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
        <div className="relative bg-white rounded-2xl border border-gray-200/50 shadow-lg hover:shadow-xl transition-all duration-200 focus-within:ring-2 focus-within:ring-[#00ACB5]/20 focus-within:border-[#00ACB5]/50">
          <div className="flex items-end space-x-3 p-4">
            {/* Attachment Button */}
            <button
              type="button"
              className="p-2.5 text-gray-400 hover:text-[#00ACB5] hover:bg-[#00ACB5]/10 rounded-xl transition-all duration-200"
              title="Attach file"
            >
              <Paperclip className="w-5 h-5" />
            </button>

            {/* Textarea */}
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={handleTextareaChange}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about Docaposte financial performance, trends, or any data insights..."
                className="w-full resize-none border-0 bg-transparent focus:ring-0 focus:outline-none placeholder-gray-400 text-gray-900"
                rows="1"
                style={{ maxHeight: '120px' }}
                disabled={disabled}
              />
            </div>

            {/* Voice Input Button */}
            <button
              type="button"
              className="p-2.5 text-gray-400 hover:text-[#00ACB5] hover:bg-[#00ACB5]/10 rounded-xl transition-all duration-200"
              title="Voice input"
            >
              <Mic className="w-5 h-5" />
            </button>

            {/* Send Button */}
            <button
              type="submit"
              disabled={!message.trim() || disabled}
              className="relative group p-2.5 bg-gradient-to-r from-[#00ACB5] to-[#00929A] hover:from-[#00929A] hover:to-[#007A80] disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed text-white rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl disabled:shadow-none"
            >
              <Send className="w-5 h-5" />
              {!disabled && message.trim() && (
                <div className="absolute -inset-1 bg-gradient-to-r from-[#00ACB5] to-[#00929A] rounded-xl blur opacity-25 group-hover:opacity-40 transition-opacity"></div>
              )}
            </button>
          </div>

          {/* Suggestions Bar */}
          {!message && (
            <div className="px-4 pb-3">
              <div className="flex items-center space-x-2 text-xs">
                <span className="text-gray-400">Quick prompts:</span>
                <button
                  type="button"
                  onClick={() => setMessage("Show me Q4 2024 revenue by business unit")}
                  className="px-3 py-1 bg-gray-50 hover:bg-[#00ACB5]/10 text-gray-600 hover:text-[#00ACB5] rounded-full transition-all duration-200"
                >
                  Q4 Revenue
                </button>
                <button
                  type="button"
                  onClick={() => setMessage("Compare actual vs budget for this year")}
                  className="px-3 py-1 bg-gray-50 hover:bg-[#00ACB5]/10 text-gray-600 hover:text-[#00ACB5] rounded-full transition-all duration-200"
                >
                  Budget Analysis
                </button>
                <button
                  type="button"
                  onClick={() => setMessage("Top 5 clients by revenue")}
                  className="px-3 py-1 bg-gray-50 hover:bg-[#00ACB5]/10 text-gray-600 hover:text-[#00ACB5] rounded-full transition-all duration-200"
                >
                  Top Clients
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer Text */}
        <div className="text-center mt-3">
          <p className="text-xs text-gray-500">
            Talk4Finance can make mistakes. Please verify important information.
          </p>
        </div>
      </form>
    </div>
  );
};

export default ChatInput;