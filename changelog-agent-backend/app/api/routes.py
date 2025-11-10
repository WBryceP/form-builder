from fastapi import APIRouter, HTTPException, Depends
from functools import lru_cache
from app.models.schemas import (
    ChatRequest, ChatResponse, TraceResponse, ToolCallsResponse, ToolCallData,
    CreateConversationResponse, ListConversationsResponse, ConversationMessagesResponse,
    DeleteConversationResponse, ConversationMetadata, Message
)
from app.services.agent_service import AgentService

router = APIRouter()


@lru_cache
def get_agent_service() -> AgentService:
    """Dependency injection for AgentService singleton."""
    return AgentService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Chat with the agent. Session ID maintains conversation context.
    """
    try:
        response = await agent_service.chat(
            user_message=request.message,
            session_id=request.session_id
        )
        
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/traces/{session_id}", response_model=TraceResponse)
async def get_trace(
    session_id: str,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Get the trace ID for a conversation session.
    Use the trace URL to view all tool calls for this conversation.
    """
    trace_id = agent_service.get_trace_id(session_id)
    
    if not trace_id:
        raise HTTPException(
            status_code=404,
            detail=f"No trace found for session_id: {session_id}"
        )
    
    return TraceResponse(
        session_id=session_id,
        trace_id=trace_id,
        trace_url=f"https://platform.openai.com/traces/trace?trace_id={trace_id}"
    )


@router.get("/tool-calls/session/{session_id}", response_model=ToolCallsResponse)
async def get_tool_calls_by_session(
    session_id: str,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Get all tool calls for a conversation session.
    This does not require OpenAI platform access.
    """
    trace_id = agent_service.get_trace_id(session_id)
    
    if not trace_id:
        raise HTTPException(
            status_code=404,
            detail=f"No trace found for session_id: {session_id}"
        )
    
    tool_calls_data = agent_service.get_tool_calls_by_session(session_id)
    tool_calls = [ToolCallData(**tc) for tc in tool_calls_data]
    
    return ToolCallsResponse(
        session_id=session_id,
        trace_id=trace_id,
        tool_calls=tool_calls,
        total_count=len(tool_calls)
    )


@router.get("/tool-calls/trace/{trace_id}", response_model=ToolCallsResponse)
async def get_tool_calls_by_trace(
    trace_id: str,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Get all tool calls for a specific trace ID.
    This does not require OpenAI platform access.
    """
    tool_calls_data = agent_service.get_tool_calls_by_trace(trace_id)
    
    if not tool_calls_data:
        raise HTTPException(
            status_code=404,
            detail=f"No tool calls found for trace_id: {trace_id}"
        )
    
    tool_calls = [ToolCallData(**tc) for tc in tool_calls_data]
    
    return ToolCallsResponse(
        session_id=None,
        trace_id=trace_id,
        tool_calls=tool_calls,
        total_count=len(tool_calls)
    )


@router.get("/conversations", response_model=ListConversationsResponse)
async def list_conversations(
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    List all conversations ordered by most recent activity.
    """
    try:
        conversations = agent_service.conversation_service.list_conversations()
        return ListConversationsResponse(
            conversations=[ConversationMetadata(**conv) for conv in conversations],
            total_count=len(conversations)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations", response_model=CreateConversationResponse)
async def create_conversation(
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Create a new conversation. Returns session_id for use in chat endpoint.
    """
    try:
        result = agent_service.conversation_service.create_conversation()
        return CreateConversationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{session_id}/messages", response_model=ConversationMessagesResponse)
async def get_conversation_messages(
    session_id: str,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Get all messages in a conversation.
    """
    conversation = agent_service.conversation_service.get_conversation(session_id)
    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation not found: {session_id}"
        )
    
    try:
        messages = agent_service.conversation_service.get_conversation_messages(session_id)
        return ConversationMessagesResponse(
            session_id=session_id,
            messages=[Message(**msg) for msg in messages],
            total_count=len(messages)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{session_id}", response_model=DeleteConversationResponse)
async def delete_conversation(
    session_id: str,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Delete a conversation and all associated data.
    """
    try:
        success = agent_service.conversation_service.delete_conversation(session_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation not found: {session_id}"
            )
        return DeleteConversationResponse(success=True, session_id=session_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
