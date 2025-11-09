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
    <div className="w-80 bg-gradient-to-b from-gray-50 to-gray-100 border-r border-gray-300 flex flex-col h-screen shadow-lg">
      <div className="p-6 border-b border-gray-300 bg-white">
        <h1 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
          <span className="text-3xl mr-2">🤖</span>
          Form Agent
        </h1>
        <button
          onClick={onCreateConversation}
          className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-4 py-3 rounded-lg font-semibold transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
        >
          <span className="text-lg mr-2">+</span> New Conversation
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-2">
        {conversations.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <div className="text-4xl mb-2">💬</div>
            <div className="text-sm">No conversations yet</div>
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.session_id}
              className={`relative mx-2 mb-2 rounded-lg ${
                currentConversationId === conv.session_id
                  ? 'bg-white shadow-md border-2 border-blue-500'
                  : 'bg-white hover:bg-gray-50 border border-gray-200 hover:border-gray-300'
              } transition-all group`}
            >
              <button
                onClick={() => onSelectConversation(conv.session_id)}
                className="w-full text-left px-4 py-3 pr-10"
              >
                <div className="font-semibold text-sm text-gray-900 truncate">
                  {conv.title}
                </div>
                <div className="text-xs text-gray-600 mt-1.5 flex items-center">
                  <span className="inline-flex items-center">
                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm3.293 1.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L7.586 10 5.293 7.707a1 1 0 010-1.414zM11 12a1 1 0 100 2h3a1 1 0 100-2h-3z"/>
                    </svg>
                    {conv.message_count}
                  </span>
                  <span className="mx-1.5">•</span>
                  <span>{new Date(conv.updated_at).toLocaleDateString()}</span>
                </div>
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm('Delete this conversation?')) {
                    onDeleteConversation(conv.session_id);
                  }
                }}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded text-xl w-8 h-8 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all"
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
