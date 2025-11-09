from agents import Runner, SQLiteSession, trace, gen_trace_id
from app.agents.changelog_agent import form_agent
from app.models.schemas import ClarificationOutput, ChangelogOutput
import os
import json


class AgentService:
    def __init__(self):
        self.runner = Runner()
        # Store sessions in data directory
        self.sessions_db = os.getenv("SESSIONS_DB", "/app/data/sessions.db")
        # Map session_id to trace_id
        self.session_traces = {}
    
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
        
        with trace(f"Conversation {session_id}", trace_id=trace_id):
            result = await self.runner.run(
                starting_agent=form_agent,
                input=user_message,
                session=session,
                max_turns=25
            )
        
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
