import type { Conversation } from '../types';

interface ConversationListProps {
  conversations: Conversation[];
  currentConversationId: string | null;
  onSelectConversation: (sessionId: string) => void;
  onCreateConversation: () => void;
  onDeleteConversation: (sessionId: string) => void;
}

export function ConversationList({
  conversations,
  currentConversationId,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
}: ConversationListProps) {
  return (
    <div className="w-64 bg-gray-100 border-r border-gray-200 flex flex-col h-screen">
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-lg font-bold text-gray-900 mb-3">Form Agent</h1>
        <button
          onClick={onCreateConversation}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-medium transition-colors"
        >
          + New Conversation
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500 text-sm">
            No conversations yet
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.session_id}
              className={`border-b border-gray-200 ${
                currentConversationId === conv.session_id
                  ? 'bg-white'
                  : 'bg-gray-100 hover:bg-gray-50'
              } transition-colors`}
            >
              <button
                onClick={() => onSelectConversation(conv.session_id)}
                className="w-full text-left px-4 py-3"
              >
                <div className="font-medium text-sm text-gray-900 truncate">
                  {conv.title}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {conv.message_count} message{conv.message_count !== 1 ? 's' : ''}
                  {' • '}
                  {new Date(conv.updated_at).toLocaleDateString()}
                </div>
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm('Delete this conversation?')) {
                    onDeleteConversation(conv.session_id);
                  }
                }}
                className="absolute right-2 top-3 text-gray-400 hover:text-red-600 text-xs px-2 py-1"
                title="Delete conversation"
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
