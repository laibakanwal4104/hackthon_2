"""Chat API schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for chat endpoint.

    Attributes:
        message: User's message to the agent
        conversation_id: Optional conversation ID to continue existing conversation
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's message to the agent"
    )
    conversation_id: Optional[UUID] = Field(
        None,
        description="Optional conversation ID to continue existing conversation"
    )


class ToolCallInfo(BaseModel):
    """Information about a tool call made by the agent.

    Attributes:
        tool_name: Name of the MCP tool invoked
        input_params: Parameters passed to the tool
        output_result: Result returned by the tool
    """

    tool_name: str = Field(..., description="Name of the MCP tool invoked")
    input_params: Dict[str, Any] = Field(..., description="Parameters passed to the tool")
    output_result: Dict[str, Any] = Field(..., description="Result returned by the tool")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint.

    Attributes:
        response: Agent's response message
        conversation_id: Conversation identifier
        message_id: ID of the agent's message
        tool_calls: List of MCP tools invoked by the agent
    """

    response: str = Field(..., description="Agent's response message")
    conversation_id: UUID = Field(..., description="Conversation identifier")
    message_id: UUID = Field(..., description="ID of the agent's message")
    tool_calls: List[ToolCallInfo] = Field(
        default_factory=list,
        description="List of MCP tools invoked by the agent"
    )


class ErrorDetail(BaseModel):
    """Error detail information.

    Attributes:
        code: Error code
        message: Human-readable error message
        details: Additional error details (optional)
    """

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Error response schema.

    Attributes:
        error: Error detail object
    """

    error: ErrorDetail = Field(..., description="Error detail object")


class MessageItem(BaseModel):
    """Message item for chat history.

    Attributes:
        id: Message identifier
        role: Message role (user, agent, system)
        content: Message text content
        created_at: Message creation timestamp
        tool_calls: Tool calls associated with this message (agent messages only)
    """

    id: UUID = Field(..., description="Message identifier")
    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message text content")
    created_at: datetime = Field(..., description="Message creation timestamp")
    tool_calls: List[ToolCallInfo] = Field(
        default_factory=list,
        description="Tool calls associated with this message"
    )


class ChatHistoryResponse(BaseModel):
    """Response schema for chat history endpoint.

    Attributes:
        conversation_id: Conversation identifier
        messages: List of messages in chronological order
    """

    conversation_id: UUID = Field(..., description="Conversation identifier")
    messages: List[MessageItem] = Field(..., description="List of messages in chronological order")
