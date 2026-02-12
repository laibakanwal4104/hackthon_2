"""Chat API endpoints for AI agent interaction."""
import logging
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from src.api.dependencies.auth import get_current_user
from src.api.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    MessageItem,
    ErrorResponse,
    ErrorDetail,
    ToolCallInfo,
)
from src.models.user import User
from src.models.conversation import Conversation, ConversationStatus
from src.models.message import Message
from src.models.tool_invocation import ToolInvocation
from src.models.database import get_session
from src.services.agent_service import agent_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message to the AI agent",
    responses={
        200: {"description": "Agent response generated successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Unauthorized - missing or invalid JWT token"},
        500: {"description": "Internal server error (agent error, database error, etc.)"},
    },
)
async def send_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Send a message to the AI agent and receive a response.

    The agent can invoke MCP tools to perform todo operations. The endpoint is stateless
    and reconstructs conversation context from the database on each request.

    Args:
        request: Chat request with message and optional conversation_id
        current_user: Authenticated user from JWT token

    Returns:
        ChatResponse with agent's message, conversation_id, and tool calls

    Raises:
        HTTPException: 400 for invalid input, 401 for unauthorized, 500 for server errors
    """
    # Validate message content
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "Message cannot be empty",
                    "details": None
                }
            }
        )

    # Sanitize message content (basic XSS prevention)
    sanitized_message = request.message.strip()
    # Remove any HTML tags
    import re
    sanitized_message = re.sub(r'<[^>]+>', '', sanitized_message)

    if len(sanitized_message) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "Message exceeds maximum length of 2000 characters",
                    "details": f"Message length: {len(sanitized_message)}"
                }
            }
        )

    try:
        # Process message through agent service
        # Use user_id from TokenUser (which is the UUID)
        user_uuid = current_user.user_id if hasattr(current_user, 'user_id') else current_user.uuid

        agent_response, conversation_id, message_id, tool_calls = agent_service.process_message(
            user_id=user_uuid,
            message_content=sanitized_message,
            conversation_id=request.conversation_id
        )

        logger.info(
            f"Chat message processed for user {user_uuid}, "
            f"conversation {conversation_id}, message {message_id}, "
            f"tool_calls: {len(tool_calls)}"
        )

        # Convert tool calls to response format
        tool_calls_response = [
            ToolCallInfo(
                tool_name=tc["tool_name"],
                input_params=tc["input_params"],
                output_result=tc["output_result"]
            )
            for tc in tool_calls
        ]

        return ChatResponse(
            response=agent_response,
            conversation_id=conversation_id,
            message_id=message_id,
            tool_calls=tool_calls_response
        )

    except ValueError as e:
        # Handle validation errors
        logger.error(f"Validation error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_INPUT",
                    "message": str(e),
                    "details": None
                }
            }
        )

    except TimeoutError as e:
        # Handle timeout errors
        logger.error(f"Timeout error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "AGENT_ERROR",
                    "message": "Request timed out while processing message",
                    "details": "The AI agent took too long to respond. Please try again."
                }
            }
        )

    except Exception as e:
        # Handle all other errors
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to process message",
                    "details": str(e) if logger.level <= logging.DEBUG else None
                }
            }
        )


@router.get(
    "/history",
    response_model=ChatHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get chat history for a conversation",
    responses={
        200: {"description": "Conversation history retrieved successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Conversation not found"},
    },
)
async def get_chat_history(
    conversation_id: Optional[UUID] = Query(None, description="Specific conversation ID (optional, defaults to active conversation)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of messages to return"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Retrieve the full message history for the user's conversation.

    Returns messages in chronological order with optional pagination.

    Args:
        conversation_id: Optional specific conversation ID
        limit: Maximum number of messages to return (1-100, default 50)
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        ChatHistoryResponse with conversation_id and messages

    Raises:
        HTTPException: 401 for unauthorized, 404 for conversation not found
    """
    try:
        user_uuid = current_user.user_id if hasattr(current_user, 'user_id') else current_user.uuid

        # Get conversation
        if conversation_id:
            # Get specific conversation
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_uuid
            )
            conversation = session.exec(statement).first()
        else:
            # Get active conversation
            statement = select(Conversation).where(
                Conversation.user_id == user_uuid,
                Conversation.status == ConversationStatus.ACTIVE
            ).order_by(Conversation.updated_at.desc())
            conversation = session.exec(statement).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "No conversation found",
                        "details": None
                    }
                }
            )

        # Load messages with pagination
        statement = select(Message).where(
            Message.conversation_id == conversation.id
        ).order_by(Message.sequence_number).limit(limit)

        messages = session.exec(statement).all()

        # Load tool invocations for agent messages
        message_items = []
        for msg in messages:
            tool_calls = []

            if msg.role.value == "agent":
                # Load tool invocations for this message
                tool_statement = select(ToolInvocation).where(
                    ToolInvocation.message_id == msg.id
                )
                tool_invocations = session.exec(tool_statement).all()

                tool_calls = [
                    ToolCallInfo(
                        tool_name=ti.tool_name,
                        input_params=ti.input_params,
                        output_result=ti.output_result
                    )
                    for ti in tool_invocations
                ]

            message_items.append(
                MessageItem(
                    id=msg.id,
                    role=msg.role.value,
                    content=msg.content,
                    created_at=msg.created_at,
                    tool_calls=tool_calls
                )
            )

        logger.info(
            f"Retrieved {len(message_items)} messages for user {user_uuid}, "
            f"conversation {conversation.id}"
        )

        return ChatHistoryResponse(
            conversation_id=conversation.id,
            messages=message_items
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to retrieve chat history",
                    "details": str(e) if logger.level <= logging.DEBUG else None
                }
            }
        )
