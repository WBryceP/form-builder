from pydantic import BaseModel, Field
from typing import Optional, Union, Literal, Any


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
    type: Literal["clarification"] = "clarification"
    clarification: str = Field(..., description="Question or clarification request for the user")


class ChangelogOutput(BaseModel):
    type: Literal["changelog"] = "changelog"
    changes: dict[str, Any] = Field(
        ...,
        description="Database changes keyed by table name"
    )


class AgentOutputWrapper(BaseModel):
    """Wrapper for agent output that can be either clarification or changelog."""
    response: Union[ClarificationOutput, ChangelogOutput] = Field(
        ...,
        discriminator="type",
        description="Either a clarification request or a changelog"
    )


AgentOutput = Union[ClarificationOutput, ChangelogOutput]


class ToolCallData(BaseModel):
    span_id: str = Field(..., description="Unique span ID")
    trace_id: str = Field(..., description="Trace ID this tool call belongs to")
    tool_name: str = Field(..., description="Name of the tool that was called")
    input: Optional[str] = Field(None, description="Input arguments to the tool")
    output: Optional[str] = Field(None, description="Output returned by the tool")
    started_at: Optional[str] = Field(None, description="Timestamp when tool call started")
    ended_at: Optional[str] = Field(None, description="Timestamp when tool call ended")
    error: Optional[dict[str, Any]] = Field(None, description="Error information if tool call failed")


class ToolCallsResponse(BaseModel):
    session_id: Optional[str] = Field(None, description="Session ID if queried by session")
    trace_id: str = Field(..., description="Trace ID")
    tool_calls: list[ToolCallData] = Field(..., description="List of tool calls in this trace")
    total_count: int = Field(..., description="Total number of tool calls")


class ConversationMetadata(BaseModel):
    session_id: str = Field(..., description="Unique session/conversation ID")
    title: str = Field(..., description="Conversation title")
    created_at: str = Field(..., description="ISO timestamp when conversation was created")
    updated_at: str = Field(..., description="ISO timestamp when conversation was last updated")
    message_count: int = Field(default=0, description="Number of messages in conversation")


class CreateConversationResponse(BaseModel):
    session_id: str = Field(..., description="Unique session/conversation ID")
    title: str = Field(..., description="Conversation title")
    created_at: str = Field(..., description="ISO timestamp when conversation was created")


class ListConversationsResponse(BaseModel):
    conversations: list[ConversationMetadata] = Field(..., description="List of all conversations")
    total_count: int = Field(..., description="Total number of conversations")


class Message(BaseModel):
    role: Literal["user", "assistant"] = Field(..., description="Message sender role")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="ISO timestamp when message was sent")


class ConversationMessagesResponse(BaseModel):
    session_id: str = Field(..., description="Session/conversation ID")
    messages: list[Message] = Field(..., description="List of messages in conversation")
    total_count: int = Field(..., description="Total number of messages")


class DeleteConversationResponse(BaseModel):
    success: bool = Field(..., description="Whether deletion was successful")
    session_id: str = Field(..., description="Deleted session ID")
