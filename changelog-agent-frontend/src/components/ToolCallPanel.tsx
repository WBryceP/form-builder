import { useState } from 'react';
import type { ToolCall } from '../types';

interface ToolCallPanelProps {
  toolCalls: ToolCall[];
}

export function ToolCallPanel({ toolCalls }: ToolCallPanelProps) {
  const [isOpen, setIsOpen] = useState(true);
  const [expandedCalls, setExpandedCalls] = useState<Set<string>>(new Set());

  const toggleCallExpanded = (spanId: string) => {
    const newSet = new Set(expandedCalls);
    if (newSet.has(spanId)) {
      newSet.delete(spanId);
    } else {
      newSet.add(spanId);
    }
    setExpandedCalls(newSet);
  };

  if (toolCalls.length === 0) {
    return null;
  }

  return (
    <div className="border-t-2 border-gray-300 bg-gradient-to-b from-gray-50 to-gray-100">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-100 transition-colors group"
      >
        <div className="flex items-center">
          <svg className="w-5 h-5 mr-2 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
          </svg>
          <span className="font-bold text-gray-800 text-lg">
            Tool Calls
          </span>
          <span className="ml-2 px-2.5 py-0.5 bg-blue-600 text-white text-xs font-semibold rounded-full">
            {toolCalls.length}
          </span>
        </div>
        <span className="text-gray-600 group-hover:text-gray-800 transition-colors">{isOpen ? '▼' : '▶'}</span>
      </button>

      {isOpen && (
        <div className="px-6 pb-6 max-h-96 overflow-y-auto space-y-3">
          {toolCalls.map((call) => (
            <div key={call.span_id} className="bg-white rounded-xl border-2 border-gray-200 shadow-sm hover:shadow-md transition-shadow">
              <button
                onClick={() => toggleCallExpanded(call.span_id)}
                className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors flex items-center justify-between rounded-t-xl"
              >
                <div className="flex-1 flex items-center">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                    <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M13 7H7v6h6V7z" />
                      <path fillRule="evenodd" d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2zM5 5h10v10H5V5z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <span className="font-bold text-sm text-gray-900 block">
                      {call.tool_name}
                    </span>
                    {call.started_at && (
                      <span className="text-xs text-gray-500">
                        {new Date(call.started_at).toLocaleTimeString()}
                      </span>
                    )}
                  </div>
                </div>
                <div className="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center text-gray-600 font-bold text-sm">
                  {expandedCalls.has(call.span_id) ? '−' : '+'}
                </div>
              </button>

              {expandedCalls.has(call.span_id) && (
                <div className="px-4 pb-4 text-xs space-y-3 border-t border-gray-100">
                  {call.input && (
                    <div className="mt-3">
                      <div className="font-bold text-gray-700 mb-2 flex items-center">
                        <svg className="w-4 h-4 mr-1.5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
                        </svg>
                        Input
                      </div>
                      <pre className="bg-gradient-to-br from-gray-50 to-gray-100 p-3 rounded-lg overflow-x-auto text-gray-800 border border-gray-200">
                        {call.input}
                      </pre>
                    </div>
                  )}
                  {call.output && (
                    <div>
                      <div className="font-bold text-gray-700 mb-2 flex items-center">
                        <svg className="w-4 h-4 mr-1.5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
                        </svg>
                        Output
                      </div>
                      <pre className="bg-gradient-to-br from-gray-50 to-gray-100 p-3 rounded-lg overflow-x-auto text-gray-800 border border-gray-200">
                        {call.output}
                      </pre>
                    </div>
                  )}
                  {call.error && (
                    <div>
                      <div className="font-bold text-red-700 mb-2 flex items-center">
                        <svg className="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        Error
                      </div>
                      <pre className="bg-gradient-to-br from-red-50 to-red-100 p-3 rounded-lg overflow-x-auto text-red-800 border border-red-200">
                        {JSON.stringify(call.error, null, 2)}
                      </pre>
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
