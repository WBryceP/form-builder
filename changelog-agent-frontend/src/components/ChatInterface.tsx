import { useState, useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { ToolCallPanel } from './ToolCallPanel';
import type { Message, ToolCall } from '../types';

interface ChatInterfaceProps {
  messages: Message[];
  toolCalls: ToolCall[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export function ChatInterface({ messages, toolCalls, onSendMessage, isLoading }: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <main className="flex-1 min-w-0 flex flex-col min-h-0">
      <div className="flex-1 overflow-y-auto px-4 md:px-6 lg:px-8 py-6">
        <div className="max-w-4xl mx-auto w-full min-h-full">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center text-gray-600">
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
          ) : (
            <>
              {messages.map((message, index) => (
                <MessageBubble key={index} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      <div className="max-w-4xl mx-auto w-full">
        <ToolCallPanel toolCalls={toolCalls} />
      </div>

      <div className="border-t border-slate-200 px-4 py-4 bg-white/80 backdrop-blur shadow-sm">
        <form onSubmit={handleSubmit} className="flex gap-3 md:gap-4 max-w-4xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message…"
            disabled={isLoading}
            className="flex-1 rounded-xl px-4 py-3 text-sm md:text-[15px] text-gray-900 placeholder-gray-400 border border-slate-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-slate-50 disabled:text-gray-400 transition"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-5 md:px-6 py-3 text-sm md:text-[15px] disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-semibold shadow-sm text-white bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
          >
            Send
          </button>
        </form>
        <div className="max-w-4xl mx-auto mt-2">
          <p className="text-[11px] text-slate-500">
            Press <kbd className="px-1 py-0.5 rounded border border-slate-300 bg-slate-50">Enter</kbd> to send •
            <span className="hidden sm:inline"> Shift+Enter for newline</span>
          </p>
        </div>
      </div>
    </main>
  );
}
