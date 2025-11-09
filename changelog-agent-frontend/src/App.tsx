import { useState, useEffect } from 'react';
import { ConversationList } from './components/ConversationList';
import { ChatInterface } from './components/ChatInterface';
import { api } from './api/client';
import type { Conversation, Message, ToolCall } from './types';

function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (currentConversationId) {
      loadConversationData(currentConversationId);
    }
  }, [currentConversationId]);

  const loadConversations = async () => {
    try {
      const data = await api.listConversations();
      setConversations(data.conversations);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const loadConversationData = async (sessionId: string) => {
    try {
      const [messagesData, toolCallsData] = await Promise.all([
        api.getConversationMessages(sessionId),
        api.getToolCalls(sessionId).catch(() => ({ tool_calls: [], total_count: 0, trace_id: '', session_id: sessionId })),
      ]);
      setMessages(messagesData.messages);
      setToolCalls(toolCallsData.tool_calls);
    } catch (error) {
      console.error('Failed to load conversation data:', error);
      setMessages([]);
      setToolCalls([]);
    }
  };

  const handleCreateConversation = async () => {
    try {
      const newConv = await api.createConversation();
      await loadConversations();
      setCurrentConversationId(newConv.session_id);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleSelectConversation = (sessionId: string) => {
    setCurrentConversationId(sessionId);
  };

  const handleDeleteConversation = async (sessionId: string) => {
    try {
      await api.deleteConversation(sessionId);
      if (currentConversationId === sessionId) {
        setCurrentConversationId(null);
        setMessages([]);
        setToolCalls([]);
      }
      await loadConversations();
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!currentConversationId) return;

    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await api.sendMessage({
        message,
        session_id: currentConversationId,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      await loadConversations();
      
      const toolCallsData = await api.getToolCalls(currentConversationId).catch(() => ({ 
        tool_calls: [], 
        total_count: 0, 
        trace_id: '', 
        session_id: currentConversationId 
      }));
      setToolCalls(toolCallsData.tool_calls);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Error: Failed to send message. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      <ConversationList
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onCreateConversation={handleCreateConversation}
        onDeleteConversation={handleDeleteConversation}
      />
      {currentConversationId ? (
        <ChatInterface
          messages={messages}
          toolCalls={toolCalls}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      ) : (
        <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-gray-50 via-blue-50 to-gray-50">
          <div className="text-center text-gray-600 max-w-md">
            <div className="text-8xl mb-8 animate-pulse">🤖</div>
            <div className="text-3xl font-bold mb-4 text-gray-800">Form Builder Agent</div>
            <div className="text-base text-gray-600 mb-8 leading-relaxed">
              Create a new conversation or select an existing one to start chatting with the agent.
            </div>
            <div className="bg-white rounded-xl p-6 shadow-lg border-2 border-gray-200">
              <div className="text-sm text-gray-500 mb-3 font-semibold">Quick Tips:</div>
              <div className="text-xs text-left space-y-2 text-gray-700">
                <div className="flex items-start">
                  <span className="text-blue-600 mr-2">•</span>
                  <span>Click "+ New Conversation" to start</span>
                </div>
                <div className="flex items-start">
                  <span className="text-blue-600 mr-2">•</span>
                  <span>Ask about forms, fields, or database changes</span>
                </div>
                <div className="flex items-start">
                  <span className="text-blue-600 mr-2">•</span>
                  <span>View tool calls to see what the agent did</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
