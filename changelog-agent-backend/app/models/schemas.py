from pydantic import BaseModel, Field
from typing import Optional, Annotated, Union, Literal, Any


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field(
        default="default",
        description="Session ID to maintain conversation context"
    )


class ChatResponse(BaseModel):
    response: str = Field(..., description="Agent's response")


class TraceResponse(BaseModel):
    session_id: str = Field(..., description="Session ID")
    trace_id: str = Field(..., description="Trace ID for viewing tool calls")
    trace_url: str = Field(..., description="URL to view the trace")


class ClarificationOutput(BaseModel):
    type: Literal["clarification"]
    clarification: str


class ChangelogOutput(BaseModel):
    type: Literal["changelog"]
    changes: dict[str, Any]


class AgentOutput(BaseModel):
    output: Union[ClarificationOutput, ChangelogOutput] = Field(discriminator="type")
