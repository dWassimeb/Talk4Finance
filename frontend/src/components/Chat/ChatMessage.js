// frontend/src/components/Chat/ChatMessage.jsx
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Bot, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';

const ChatMessage = ({ message, isUser, isTyping = false }) => {
  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} group`}>
      <div className={`flex max-w-4xl w-full ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-4' : 'mr-4'}`}>
          <div className={`w-10 h-10 rounded-2xl flex items-center justify-center ${
            isUser
              ? 'bg-gradient-to-br from-[#00ACB5] to-[#00929A]'
              : 'bg-gradient-to-br from-[#00ACB5] to-[#00929A]'
          }`}>
            {isUser ? (
              <User className="w-5 h-5 text-white" />
            ) : (
              <Bot className="w-5 h-5 text-white" />
            )}
          </div>
        </div>

        {/* Message Content */}
        <div className="flex-1 min-w-0">
          <div className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-gradient-to-r from-[#00ACB5] to-[#00929A] text-white ml-auto max-w-2xl'
              : 'bg-white border border-gray-200/50 shadow-sm text-gray-800 mr-auto'
          }`}>
            {isTyping ? (
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
                </div>
                <span className="text-sm text-gray-500">AI is thinking...</span>
              </div>
            ) : isUser ? (
              <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
            ) : (
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code: ({node, inline, className, children, ...props}) => {
                      return inline ? (
                        <code className="bg-gray-100 px-2 py-1 rounded-lg text-sm font-mono" {...props}>
                          {children}
                        </code>
                      ) : (
                        <pre className="bg-gray-50 p-4 rounded-xl overflow-x-auto border border-gray-200 my-4">
                          <code className="text-sm font-mono" {...props}>{children}</code>
                        </pre>
                      );
                    },
                    table: ({children}) => (
                      <div className="overflow-x-auto my-4">
                        <table className="min-w-full border-collapse border border-gray-300 rounded-lg overflow-hidden">{children}</table>
                      </div>
                    ),
                    th: ({children}) => (
                      <th className="border border-gray-300 px-4 py-3 bg-gray-50 font-semibold text-left text-sm">
                        {children}
                      </th>
                    ),
                    td: ({children}) => (
                      <td className="border border-gray-300 px-4 py-3 text-sm">{children}</td>
                    ),
                    p: ({children}) => (
                      <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>
                    ),
                    ul: ({children}) => (
                      <ul className="mb-3 pl-4 space-y-1">{children}</ul>
                    ),
                    ol: ({children}) => (
                      <ol className="mb-3 pl-4 space-y-1">{children}</ol>
                    ),
                    li: ({children}) => (
                      <li className="text-sm">{children}</li>
                    ),
                    h1: ({children}) => (
                      <h1 className="text-xl font-bold mb-3 text-gray-900">{children}</h1>
                    ),
                    h2: ({children}) => (
                      <h2 className="text-lg font-semibold mb-2 text-gray-900">{children}</h2>
                    ),
                    h3: ({children}) => (
                      <h3 className="text-base font-semibold mb-2 text-gray-900">{children}</h3>
                    ),
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            )}

            {/* Timestamp */}
            {message.created_at && (
              <div className={`text-xs mt-2 ${
                isUser ? 'text-white/70' : 'text-gray-500'
              }`}>
                {new Date(message.created_at).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            )}
          </div>

          {/* Message Actions */}
          {!isUser && !isTyping && (
            <div className="flex items-center space-x-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <button
                onClick={handleCopy}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200 text-gray-500 hover:text-gray-700"
                title="Copy message"
              >
                <Copy className="w-4 h-4" />
              </button>
              <button
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200 text-gray-500 hover:text-green-600"
                title="Good response"
              >
                <ThumbsUp className="w-4 h-4" />
              </button>
              <button
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200 text-gray-500 hover:text-red-600"
                title="Poor response"
              >
                <ThumbsDown className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;