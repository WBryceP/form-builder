import type { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div
        className={`max-w-3xl rounded-2xl px-5 py-4 shadow-md ${
          isUser
            ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white'
            : 'bg-white text-gray-900 border border-gray-200'
        }`}
      >
        <div className={`text-xs font-bold mb-2 flex items-center ${
          isUser ? 'text-blue-100' : 'text-gray-500'
        }`}>
          {isUser ? (
            <>
              <svg className="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
              You
            </>
          ) : (
            <>
              <svg className="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
                <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
              </svg>
              Agent
            </>
          )}
        </div>
        <div className="whitespace-pre-wrap break-words leading-relaxed">
          {message.content}
        </div>
        <div className={`text-xs mt-3 ${
          isUser ? 'text-blue-200' : 'text-gray-400'
        }`}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
