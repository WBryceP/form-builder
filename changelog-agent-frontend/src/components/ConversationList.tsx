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
    <aside className="w-72 sm:w-80 shrink-0 border-r border-slate-200 flex flex-col h-full shadow-sm bg-gradient-to-b from-indigo-50 to-blue-50">
      <div className="p-4 border-b border-slate-200 bg-white/90 backdrop-blur">
        <h1 className="text-xl font-bold text-gray-900 mb-1">
          Echelon Take-home
        </h1>
        <p className="text-xs text-slate-600 mb-3">Manage your chats</p>
        <button
          onClick={onCreateConversation}
          className="w-full px-4 py-2.5 text-sm rounded-lg font-semibold shadow-sm text-white bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
        >
          <span className="text-base mr-2">＋</span> New Conversation
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-2 px-2">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <div className="text-5xl mb-3 leading-none">💬</div>
            <div className="text-sm">No conversations yet</div>
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = currentConversationId === conv.session_id;
            return (
              <div
                key={conv.session_id}
                className={`relative mb-2 rounded-xl transition group ${
                  isActive
                    ? "bg-white shadow-md ring-1 ring-indigo-600/60"
                    : "bg-white/90 hover:bg-white shadow-sm ring-1 ring-slate-200"
                }`}
              >
                {isActive && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl bg-gradient-to-b from-indigo-600 to-blue-600" />
                )}

                <button
                  onClick={() => onSelectConversation(conv.session_id)}
                  className="w-full text-left px-4 py-3 pr-10"
                >
                  <div className="font-semibold text-sm text-gray-900 truncate">
                    {conv.title}
                  </div>
                  <div className="text-xs text-gray-600 mt-1.5 flex items-center gap-1">
                    <span className="inline-flex items-center gap-1">
                      <svg
                        className="w-3.5 h-3.5 flex-shrink-0"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm3.293 1.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L7.586 10 5.293 7.707a1 1 0 010-1.414zM11 12a1 1 0 100 2h3a1 1 0 100-2h-3z" />
                      </svg>
                      {conv.message_count}
                    </span>
                    <span>•</span>
                    <span>{new Date(conv.updated_at).toLocaleDateString()}</span>
                  </div>
                </button>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm("Delete this conversation?")) {
                      onDeleteConversation(conv.session_id);
                    }
                  }}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full w-7 h-7 flex items-center justify-center text-lg opacity-0 group-hover:opacity-100 transition"
                  title="Delete conversation"
                  aria-label="Delete conversation"
                >
                  ×
                </button>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
}
