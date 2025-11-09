from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, TraceResponse, ToolCallsResponse, ToolCallData
from app.services.agent_service import AgentService

router = APIRouter()
agent_service = AgentService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
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
async def get_trace(session_id: str):
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
async def get_tool_calls_by_session(session_id: str):
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
async def get_tool_calls_by_trace(trace_id: str):
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
