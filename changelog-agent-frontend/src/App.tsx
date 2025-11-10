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
    <div className="h-screen w-full flex bg-gradient-to-br from-slate-50 via-white to-slate-50 text-gray-900">
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
        <main className="flex-1 min-w-0 flex flex-col min-h-0">
          <div className="flex-1 flex items-center justify-center text-gray-600">
            <div className="text-center max-w-md px-4">
              <div className="mb-6">
                <div className="mx-auto w-16 h-16 rounded-2xl bg-white/80 backdrop-blur-md ring-1 ring-slate-200 flex items-center justify-center text-3xl">
                  💬
                </div>
              </div>
              <div className="text-2xl font-semibold text-gray-800 mb-2">
                Start a conversation
              </div>
              <p className="text-sm leading-relaxed text-gray-600">
                Ask about forms, fields, or database changes.
                <br />The agent will help you generate structured changelogs.
              </p>
            </div>
          </div>
        </main>
      )}
    </div>
  );
}

export default App;
