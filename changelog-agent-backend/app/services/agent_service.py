from agents import Runner, SQLiteSession, trace, gen_trace_id
from agents.tracing import add_trace_processor
from app.agents.changelog_agent import form_agent
from app.agents.context import FormContext
from app.tracing.tool_call_processor import ToolCallProcessor
from app.services.conversation_service import ConversationService
import os
import json


class AgentService:
    def __init__(self):
        self.sessions_db = os.getenv("SESSIONS_DB", "/app/data/sessions.db")
        self.db_path = os.getenv("DATABASE_PATH", "/app/data/forms.sqlite")
        self.session_traces = {}
        
        self.tool_call_processor = ToolCallProcessor(self.sessions_db)
        add_trace_processor(self.tool_call_processor)
        
        self.conversation_service = ConversationService(self.sessions_db)
    
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
        
        trace_id = self.conversation_service.get_trace_id(session_id)
        if not trace_id:
            trace_id = gen_trace_id()
            self.session_traces[session_id] = trace_id
        
        existing_conv = self.conversation_service.get_conversation(session_id)
        if not existing_conv:
            title = user_message[:50] if len(user_message) <= 50 else user_message[:47] + "..."
            self.conversation_service.ensure_conversation_exists(session_id, title)
            self.conversation_service.set_trace_id(session_id, trace_id)
        else:
            self.conversation_service.update_conversation_metadata(session_id)
            if not self.conversation_service.get_trace_id(session_id):
                self.conversation_service.set_trace_id(session_id, trace_id)
        
        context = FormContext(db_path=self.db_path)
        
        with trace(f"Conversation {session_id}", trace_id=trace_id):
            result = await Runner.run(
                starting_agent=form_agent,
                input=user_message,
                session=session,
                context=context,
                max_turns=25
            )
        
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
        trace_id = self.conversation_service.get_trace_id(session_id)
        if trace_id:
            self.session_traces[session_id] = trace_id
        return trace_id or self.session_traces.get(session_id)
    
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
