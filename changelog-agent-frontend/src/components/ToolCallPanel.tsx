import { useState } from 'react';
import type { ToolCall } from '../types';

interface ToolCallPanelProps {
  toolCalls: ToolCall[];
}

export function ToolCallPanel({ toolCalls }: ToolCallPanelProps) {
  const [isOpen, setIsOpen] = useState(true);
  const [expandedCalls, setExpandedCalls] = useState<Set<string>>(new Set());

  const toggle = (spanId: string) => {
    const copy = new Set(expandedCalls);
    if (copy.has(spanId)) copy.delete(spanId);
    else copy.add(spanId);
    setExpandedCalls(copy);
  };

  if (toolCalls.length === 0) return null;

  return (
    <div className="border-t border-slate-200 bg-slate-50/70">
      <button
        onClick={() => setIsOpen((o) => !o)}
        aria-expanded={isOpen}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-100 transition group"
      >
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
          </svg>
          <span className="font-semibold text-gray-800 text-sm">Tool Calls</span>
          <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full bg-slate-100 text-slate-700">{toolCalls.length}</span>
        </div>
        <span className="text-sm text-gray-600 group-hover:text-gray-800 transition">{isOpen ? "▼" : "▶"}</span>
      </button>

      {isOpen && (
        <div className="px-4 pb-4 max-h-80 overflow-y-auto space-y-2">
          {toolCalls.map((call) => (
            <div key={call.span_id} className="bg-white/80 backdrop-blur-md ring-1 ring-slate-200 rounded-xl">
              <button
                onClick={() => toggle(call.span_id)}
                className="w-full px-3 py-2.5 text-left hover:bg-slate-50 transition flex items-center justify-between rounded-t-xl"
              >
                <div className="flex-1 flex items-center gap-2.5 min-w-0">
                  <div className="w-7 h-7 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <svg className="w-3.5 h-3.5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M13 7H7v6h6V7z" />
                      <path fillRule="evenodd" d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2zM5 5h10v10H5V5z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="min-w-0">
                    <span className="font-semibold text-sm text-gray-900 block truncate">{call.tool_name}</span>
                    {call.started_at && (
                      <span className="text-xs text-gray-500">
                        {new Date(call.started_at).toLocaleTimeString()}
                      </span>
                    )}
                  </div>
                </div>
                <div className="w-6 h-6 bg-slate-100 rounded-full flex items-center justify-center text-gray-600 font-semibold text-sm flex-shrink-0">
                  {expandedCalls.has(call.span_id) ? "−" : "+"}
                </div>
              </button>

              {expandedCalls.has(call.span_id) && (
                <div className="px-3 pb-3 text-xs space-y-2.5 border-t border-slate-100">
                  {call.input && (
                    <div className="mt-2.5">
                      <div className="font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
                        <svg className="w-3.5 h-3.5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
                        </svg>
                        Input
                      </div>
                      <pre className="bg-slate-50 p-2.5 rounded-xl overflow-x-auto text-slate-800 ring-1 ring-slate-200 max-w-full text-xs">{call.input}</pre>
                    </div>
                  )}
                  {call.output && (
                    <div>
                      <div className="font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
                        <svg className="w-3.5 h-3.5 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
                        </svg>
                        Output
                      </div>
                      <pre className="bg-slate-50 p-2.5 rounded-xl overflow-x-auto text-slate-800 ring-1 ring-slate-200 max-w-full text-xs">{call.output}</pre>
                    </div>
                  )}
                  {call.error && (
                    <div>
                      <div className="font-semibold text-red-700 mb-1.5 flex items-center gap-1.5">
                        <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        Error
                      </div>
                      <pre className="bg-red-50 p-2.5 rounded-xl overflow-x-auto text-red-800 ring-1 ring-red-200 max-w-full text-xs">{JSON.stringify(call.error, null, 2)}</pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
