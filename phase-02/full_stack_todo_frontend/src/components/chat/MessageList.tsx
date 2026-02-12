/**
 * MessageList component for displaying chat messages
 * Shows messages with role-based styling and loading indicators
 */

'use client';

import { useEffect, useRef } from 'react';
import { ChatMessage } from '@/lib/api/chat';

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
}

export default function MessageList({ messages, isLoading = false }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 && !isLoading && (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <p className="text-lg font-medium">Start a conversation</p>
            <p className="text-sm mt-2">Ask me to help you manage your todos!</p>
          </div>
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[70%] rounded-lg px-4 py-2 ${
              message.role === 'user'
                ? 'bg-primary-500 text-white'
                : message.role === 'agent'
                ? 'bg-gray-800 text-gray-100'
                : 'bg-yellow-900/30 text-yellow-200'
            }`}
          >
            <div className="whitespace-pre-wrap break-words">{message.content}</div>

            {/* Tool call indicators */}
            {message.tool_calls && message.tool_calls.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-600">
                <div className="text-xs font-semibold mb-2 opacity-75">
                  Actions performed:
                </div>
                <div className="space-y-1">
                  {message.tool_calls.map((tc, idx) => (
                    <div key={idx} className="text-xs opacity-75 bg-gray-700/50 rounded px-2 py-1">
                      <span className="font-medium">
                        {tc.tool_name === 'create_todo' && '➕ Created task'}
                        {tc.tool_name === 'list_todos' && '📋 Listed tasks'}
                        {tc.tool_name === 'update_todo' && '✏️ Updated task'}
                        {tc.tool_name === 'delete_todo' && '🗑️ Deleted task'}
                        {tc.tool_name === 'mark_todo_complete' && '✅ Marked task'}
                      </span>
                      {tc.output_result?.success === false && (
                        <span className="ml-1 text-red-600">❌ Failed</span>
                      )}
                      {tc.output_result?.success === true && (
                        <span className="ml-1 text-green-600">✓</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="text-xs mt-1 opacity-75">
              {new Date(message.created_at).toLocaleTimeString()}
            </div>
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-800 text-gray-100 rounded-lg px-4 py-2">
            <div className="flex items-center space-x-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
              <span className="text-sm">Agent is thinking...</span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
