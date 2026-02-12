/**
 * Chat page - AI Todo Assistant
 * Provides natural language interface for managing todos
 */

'use client';

import ChatInterface from '@/components/chat/ChatInterface';

export default function ChatPage() {
  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-100">AI Todo Assistant</h2>
        <p className="text-gray-400 text-sm mt-1">
          Chat with your AI assistant to manage your tasks naturally
        </p>
      </div>

      <div className="h-[calc(100vh-250px)]">
        <ChatInterface />
      </div>
    </div>
  );
}
