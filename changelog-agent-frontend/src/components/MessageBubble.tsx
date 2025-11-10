import type { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const time = new Date(message.timestamp).toLocaleTimeString();

  return (
    <div className={`mb-4 flex ${isUser ? 'justify-end' : 'justify-start'} px-1 sm:px-2`}>
      <div className={`flex items-end gap-2 max-w-full ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div
          className={`w-8 h-8 rounded-full shadow-sm flex items-center justify-center text-xs font-semibold ${
            isUser
              ? "bg-gradient-to-br from-indigo-500 to-blue-600 text-white"
              : "bg-slate-200 text-slate-700"
          }`}
          aria-hidden="true"
        >
          {isUser ? 'You' : '🤖'}
        </div>

        {/* Bubble */}
        <div
          className={`max-w-2xl rounded-2xl px-4 py-3 shadow-md ring-1 ${
            isUser
              ? "bg-gradient-to-r from-indigo-600 to-blue-600 text-white ring-indigo-500/30"
              : "bg-white text-gray-900 ring-slate-200"
          }`}
        >
          <div
            className={`text-[11px] font-semibold mb-1 tracking-wide ${
              isUser ? "text-indigo-100" : "text-gray-500"
            }`}
          >
            {isUser ? 'You' : 'Agent'}
          </div>
          <div className="text-sm whitespace-pre-wrap break-words leading-relaxed">
            {message.content}
          </div>
          <div className={`mt-1 text-[11px] ${isUser ? 'text-indigo-200 text-right' : 'text-gray-400'}`}>{time}</div>
        </div>
      </div>
    </div>
  );
}