from agents.tracing import TracingProcessor, Span, Trace, FunctionSpanData
from typing import Any
from collections import defaultdict
from datetime import datetime


class ToolCallProcessor(TracingProcessor):
    def __init__(self):
        self.tool_calls_by_trace = defaultdict(list)
        
    def on_trace_start(self, trace: Trace) -> None:
        pass
    
    def on_trace_end(self, trace: Trace) -> None:
        pass
    
    def on_span_start(self, span: Span[Any]) -> None:
        pass
    
    def on_span_end(self, span: Span[Any]) -> None:
        if isinstance(span.span_data, FunctionSpanData):
            tool_call_data = {
                "span_id": span.span_id,
                "trace_id": span.trace_id,
                "tool_name": span.span_data.name,
                "input": span.span_data.input,
                "output": str(span.span_data.output) if span.span_data.output else None,
                "started_at": span.started_at,
                "ended_at": span.ended_at,
                "error": span.error if span.error else None,
            }
            self.tool_calls_by_trace[span.trace_id].append(tool_call_data)
    
    def shutdown(self) -> None:
        pass
    
    def force_flush(self) -> None:
        pass
    
    def get_tool_calls(self, trace_id: str) -> list[dict[str, Any]]:
        return self.tool_calls_by_trace.get(trace_id, [])
    
    def clear_trace(self, trace_id: str) -> None:
        if trace_id in self.tool_calls_by_trace:
            del self.tool_calls_by_trace[trace_id]
