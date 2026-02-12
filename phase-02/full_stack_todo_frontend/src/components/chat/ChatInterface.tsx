/**
 * ChatInterface component - main chat UI container
 * Manages chat state, message handling, and error display
 */

'use client';

import { useState, useEffect } from 'react';
import { sendChatMessage, getChatHistory, ChatMessage } from '@/lib/api/chat';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load conversation history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const history = await getChatHistory();
      setMessages(history.messages);
      setConversationId(history.conversation_id);
    } catch (err: any) {
      console.error('Failed to load chat history:', err);
      // Don't show error for missing history (new user)
      if (err.response?.status !== 404) {
        setError('Failed to load chat history');
      }
    }
  };

  const handleSendMessage = async (messageText: string) => {
    // Clear any previous errors
    setError(null);

    // Add user message to UI immediately
    const userMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: messageText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Set loading state
    setIsLoading(true);

    try {
      // Send message to API
      const response = await sendChatMessage({
        message: messageText,
        conversation_id: conversationId || undefined,
      });

      // Update conversation ID if new
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add agent response to messages
      const agentMessage: ChatMessage = {
        id: response.message_id,
        role: 'agent',
        content: response.response,
        created_at: new Date().toISOString(),
        tool_calls: response.tool_calls,
      };

      setMessages((prev) => {
        // Replace temp user message with real one and add agent response
        const withoutTemp = prev.filter((m) => m.id !== userMessage.id);
        return [
          ...withoutTemp,
          { ...userMessage, id: `user-${Date.now()}` },
          agentMessage,
        ];
      });
    } catch (err: any) {
      console.error('Failed to send message:', err);

      // Extract error message from API response
      const errorMessage = err.response?.data?.error?.message || 'Failed to send message. Please try again.';
      setError(errorMessage);

      // Remove the temporary user message on error
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  return (
    <div className="flex flex-col h-full bg-background-card rounded-xl border border-gray-800 shadow-lg">
      {/* Header */}
      <div className="border-b border-gray-800 p-4 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold text-gray-100">AI Todo Assistant</h2>
          <p className="text-sm text-gray-500">Ask me to help manage your tasks</p>
        </div>
        <button
          onClick={handleNewConversation}
          className="px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors"
        >
          New Conversation
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-4 mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl">
          <div className="flex items-start">
            <div className="ml-3 flex-1">
              <p className="text-sm text-red-400">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="ml-auto flex-shrink-0 text-red-400 hover:text-red-300"
            >
              <span className="sr-only">Dismiss</span>
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Messages */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Input */}
      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={isLoading}
        placeholder="Ask me to create, list, update, or delete tasks..."
      />
    </div>
  );
}
