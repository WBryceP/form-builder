from agents.tracing import TracingProcessor, Span, Trace, FunctionSpanData
from typing import Any, Optional
from collections import defaultdict
from datetime import datetime
import sqlite3
import json


class ToolCallProcessor(TracingProcessor):
    def __init__(self, sessions_db: Optional[str] = None):
        self.tool_calls_by_trace = defaultdict(list)
        self.sessions_db = sessions_db
        if self.sessions_db:
            self._init_tool_calls_table()
        
    def _init_tool_calls_table(self):
        with sqlite3.connect(self.sessions_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT NOT NULL,
                    span_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    input TEXT,
                    output TEXT,
                    started_at TEXT,
                    ended_at TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tool_calls_trace_id 
                ON tool_calls(trace_id)
            """)
            conn.commit()
    
    def _persist_tool_call(self, tool_call_data: dict):
        if not self.sessions_db:
            return
        
        try:
            with sqlite3.connect(self.sessions_db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tool_calls 
                    (trace_id, span_id, tool_name, input, output, started_at, ended_at, error, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tool_call_data["trace_id"],
                    tool_call_data["span_id"],
                    tool_call_data["tool_name"],
                    tool_call_data["input"],
                    tool_call_data["output"],
                    tool_call_data["started_at"],
                    tool_call_data["ended_at"],
                    tool_call_data["error"],
                    datetime.utcnow().isoformat() + "Z"
                ))
                conn.commit()
        except Exception:
            pass
    
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
            self._persist_tool_call(tool_call_data)
    
    def shutdown(self) -> None:
        pass
    
    def force_flush(self) -> None:
        pass
    
    def get_tool_calls(self, trace_id: str) -> list[dict[str, Any]]:
        if self.sessions_db:
            try:
                with sqlite3.connect(self.sessions_db) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT trace_id, span_id, tool_name, input, output, 
                               started_at, ended_at, error
                        FROM tool_calls
                        WHERE trace_id = ?
                        ORDER BY id ASC
                    """, (trace_id,))
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
            except Exception:
                pass
        
        return self.tool_calls_by_trace.get(trace_id, [])
    
    def clear_trace(self, trace_id: str) -> None:
        if trace_id in self.tool_calls_by_trace:
            del self.tool_calls_by_trace[trace_id]
        
        if self.sessions_db:
            try:
                with sqlite3.connect(self.sessions_db) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM tool_calls WHERE trace_id = ?", (trace_id,))
                    conn.commit()
            except Exception:
                pass
