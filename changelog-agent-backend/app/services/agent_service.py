from agents import Runner, SQLiteSession, trace, gen_trace_id
from agents.tracing import add_trace_processor
from app.agents.changelog_agent import form_agent
from app.agents.context import FormContext
from app.tracing.tool_call_processor import ToolCallProcessor
import os
import json


class AgentService:
    def __init__(self):
        # Store sessions in data directory
        self.sessions_db = os.getenv("SESSIONS_DB", "/app/data/sessions.db")
        self.db_path = os.getenv("DATABASE_PATH", "/app/data/forms.sqlite")
        # Map session_id to trace_id
        self.session_traces = {}
        
        # Add our custom tool call processor
        self.tool_call_processor = ToolCallProcessor()
        add_trace_processor(self.tool_call_processor)
    
    async def chat(
        self,
        user_message: str,
        session_id: str = "default"
    ) -> str:
        """
        Send a message to the agent and get a response.
        
        Args:
            user_message: The user's input message
            session_id: Unique identifier for the conversation session
            
        Returns:
            JSON string containing either clarification or changelog output
        """
        session = SQLiteSession(session_id, self.sessions_db)
        
        if session_id not in self.session_traces:
            self.session_traces[session_id] = gen_trace_id()
        
        trace_id = self.session_traces[session_id]
        
        # Create context with database path
        context = FormContext(db_path=self.db_path)
        
        with trace(f"Conversation {session_id}", trace_id=trace_id):
            result = await Runner.run(
                starting_agent=form_agent,
                input=user_message,
                session=session,
                context=context,
                max_turns=25
            )
        
        # Convert structured output to JSON string
        if hasattr(result.final_output, 'model_dump'):
            return json.dumps(result.final_output.model_dump())
        return result.final_output
    
    def get_trace_id(self, session_id: str) -> str | None:
        """
        Get the trace_id for a given session.
        
        Args:
            session_id: Unique identifier for the conversation session
            
        Returns:
            The trace_id if it exists, None otherwise
        """
        return self.session_traces.get(session_id)
    
    def get_tool_calls_by_session(self, session_id: str) -> list[dict]:
        """
        Get all tool calls for a given session.
        
        Args:
            session_id: Unique identifier for the conversation session
            
        Returns:
            List of tool call data
        """
        trace_id = self.session_traces.get(session_id)
        if not trace_id:
            return []
        return self.tool_call_processor.get_tool_calls(trace_id)
    
    def get_tool_calls_by_trace(self, trace_id: str) -> list[dict]:
        """
        Get all tool calls for a given trace_id.
        
        Args:
            trace_id: Trace ID
            
        Returns:
            List of tool call data
        """
        return self.tool_call_processor.get_tool_calls(trace_id)
