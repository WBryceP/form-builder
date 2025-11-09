export interface Conversation {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ToolCall {
  span_id: string;
  trace_id: string;
  tool_name: string;
  input: string | null;
  output: string | null;
  started_at: string | null;
  ended_at: string | null;
  error: Record<string, unknown> | null;
}

export interface CreateConversationResponse {
  session_id: string;
  title: string;
  created_at: string;
}

export interface ListConversationsResponse {
  conversations: Conversation[];
  total_count: number;
}

export interface ConversationMessagesResponse {
  session_id: string;
  messages: Message[];
  total_count: number;
}

export interface ToolCallsResponse {
  session_id: string | null;
  trace_id: string;
  tool_calls: ToolCall[];
  total_count: number;
}

export interface ChatRequest {
  message: string;
  session_id: string;
}

export interface ChatResponse {
  response: string;
}

export interface DeleteConversationResponse {
  success: boolean;
  session_id: string;
}
