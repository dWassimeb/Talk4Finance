// frontend/src/components/Chat/ChatMessage.jsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Bot } from 'lucide-react';

const ChatMessage = ({ message, isUser, isTyping = false }) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex max-w-3xl ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? 'bg-[#00ACB5]' : 'bg-gray-600'
          }`}>
            {isUser ? (
              <User className="w-5 h-5 text-white" />
            ) : (
              <Bot className="w-5 h-5 text-white" />
            )}
          </div>
        </div>

        {/* Message Content */}
        <div className={`rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-[#00ACB5] text-white'
            : 'bg-[#FFFFFF] text-gray-800 border border-gray-200'
        }`}>
          {isTyping ? (
            <div className="flex items-center space-x-1">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          ) : isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code: ({node, inline, className, children, ...props}) => {
                    return inline ? (
                      <code className="bg-gray-100 px-1 py-0.5 rounded text-sm" {...props}>
                        {children}
                      </code>
                    ) : (
                      <pre className="bg-gray-100 p-3 rounded overflow-x-auto">
                        <code {...props}>{children}</code>
                      </pre>
                    );
                  },
                  table: ({children}) => (
                    <div className="overflow-x-auto">
                      <table className="min-w-full border border-gray-300">{children}</table>
                    </div>
                  ),
                  th: ({children}) => (
                    <th className="border border-gray-300 px-3 py-2 bg-gray-50 font-semibold text-left">
                      {children}
                    </th>
                  ),
                  td: ({children}) => (
                    <td className="border border-gray-300 px-3 py-2">{children}</td>
                  )
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}

          {/* Timestamp */}
          {message.created_at && (
            <div className={`text-xs mt-1 ${
              isUser ? 'text-teal-100' : 'text-gray-500'
            }`}>
              {new Date(message.created_at).toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;