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
    <div className="border-t border-gray-200 bg-gray-50">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-100 transition-colors"
      >
        <span className="font-semibold text-gray-700">
          Tool Calls ({toolCalls.length})
        </span>
        <span className="text-gray-500">{isOpen ? '▼' : '▶'}</span>
      </button>

      {isOpen && (
        <div className="px-4 pb-4 max-h-96 overflow-y-auto">
          {toolCalls.map((call) => (
            <div key={call.span_id} className="mb-2 bg-white rounded border border-gray-200">
              <button
                onClick={() => toggleCallExpanded(call.span_id)}
                className="w-full px-3 py-2 text-left hover:bg-gray-50 transition-colors flex items-center justify-between"
              >
                <div className="flex-1">
                  <span className="font-medium text-sm text-gray-900">
                    {call.tool_name}
                  </span>
                  {call.started_at && (
                    <span className="ml-2 text-xs text-gray-500">
                      {new Date(call.started_at).toLocaleTimeString()}
                    </span>
                  )}
                </div>
                <span className="text-gray-400 text-xs">
                  {expandedCalls.has(call.span_id) ? '−' : '+'}
                </span>
              </button>

              {expandedCalls.has(call.span_id) && (
                <div className="px-3 pb-3 text-xs space-y-2">
                  {call.input && (
                    <div>
                      <div className="font-semibold text-gray-700 mb-1">Input:</div>
                      <pre className="bg-gray-50 p-2 rounded overflow-x-auto text-gray-800">
                        {call.input}
                      </pre>
                    </div>
                  )}
                  {call.output && (
                    <div>
                      <div className="font-semibold text-gray-700 mb-1">Output:</div>
                      <pre className="bg-gray-50 p-2 rounded overflow-x-auto text-gray-800">
                        {call.output}
                      </pre>
                    </div>
                  )}
                  {call.error && (
                    <div>
                      <div className="font-semibold text-red-700 mb-1">Error:</div>
                      <pre className="bg-red-50 p-2 rounded overflow-x-auto text-red-800">
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
