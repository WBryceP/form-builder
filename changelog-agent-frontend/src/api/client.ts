import type {
  CreateConversationResponse,
  ListConversationsResponse,
  ConversationMessagesResponse,
  ToolCallsResponse,
  ChatRequest,
  ChatResponse,
  DeleteConversationResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = {
  async createConversation(): Promise<CreateConversationResponse> {
    const response = await fetch(`${API_BASE_URL}/conversations`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to create conversation');
    return response.json();
  },

  async listConversations(): Promise<ListConversationsResponse> {
    const response = await fetch(`${API_BASE_URL}/conversations`);
    if (!response.ok) throw new Error('Failed to list conversations');
    return response.json();
  },

  async getConversationMessages(sessionId: string): Promise<ConversationMessagesResponse> {
    const response = await fetch(`${API_BASE_URL}/conversations/${sessionId}/messages`);
    if (!response.ok) throw new Error('Failed to get conversation messages');
    return response.json();
  },

  async deleteConversation(sessionId: string): Promise<DeleteConversationResponse> {
    const response = await fetch(`${API_BASE_URL}/conversations/${sessionId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete conversation');
    return response.json();
  },

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error('Failed to send message');
    return response.json();
  },

  async getToolCalls(sessionId: string): Promise<ToolCallsResponse> {
    const response = await fetch(`${API_BASE_URL}/tool-calls/session/${sessionId}`);
    if (!response.ok) throw new Error('Failed to get tool calls');
    return response.json();
  },
};
