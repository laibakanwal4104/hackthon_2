"""Agent service for OpenAI Agents SDK integration."""
import logging
import json
from uuid import UUID
from typing import Dict, Any, List, Optional, Tuple, Union
from openai import OpenAI
from sqlmodel import Session, select

from src.config import settings
from src.agent.config import agent_config
from src.agent.prompts import get_system_prompt
from src.mcp import ALL_TOOLS, TOOL_REGISTRY
from src.models.conversation import Conversation, ConversationStatus
from src.models.message import Message, MessageRole
from src.models.tool_invocation import ToolInvocation, ToolInvocationStatus
from src.models.database import get_engine

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing AI agent interactions."""

    def __init__(self):
        """Initialize the agent service with OpenAI-compatible client (OpenRouter)."""
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
        self.system_prompt = get_system_prompt()

    def get_or_create_conversation(
        self, session: Session, user_id: Union[str, UUID], conversation_id: Optional[UUID] = None
    ) -> Conversation:
        """Get existing conversation or create a new one.

        Args:
            session: Database session
            user_id: User ID
            conversation_id: Optional conversation ID to retrieve

        Returns:
            Conversation object
        """
        user_id_str = str(user_id)

        if conversation_id:
            # Try to get specific conversation
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id_str
            )
            conversation = session.exec(statement).first()
            if conversation:
                return conversation

        # Get or create active conversation
        statement = select(Conversation).where(
            Conversation.user_id == user_id_str,
            Conversation.status == ConversationStatus.ACTIVE
        ).order_by(Conversation.updated_at.desc())

        conversation = session.exec(statement).first()

        if not conversation:
            # Create new conversation
            conversation = Conversation(
                user_id=str(user_id),
                status=ConversationStatus.ACTIVE
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            logger.info(f"Created new conversation {conversation.id} for user {user_id}")

        return conversation

    def load_conversation_history(
        self, session: Session, conversation_id: UUID
    ) -> List[Dict[str, str]]:
        """Load conversation history and format for OpenAI API.

        Args:
            session: Database session
            conversation_id: Conversation ID

        Returns:
            List of message dicts in OpenAI format
        """
        # Load messages ordered by sequence number
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.sequence_number)

        messages = session.exec(statement).all()

        # Format messages for OpenAI API
        formatted_messages = [{"role": "system", "content": self.system_prompt}]

        for msg in messages:
            role = "user" if msg.role == MessageRole.USER else "assistant"
            formatted_messages.append({
                "role": role,
                "content": msg.content
            })

        return formatted_messages

    def execute_tool(self, user_id: Union[str, UUID], tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool with comprehensive error handling.

        Args:
            user_id: User ID for authorization
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result with success status and error details if applicable
        """
        tool_func = TOOL_REGISTRY.get(tool_name)
        if not tool_func:
            logger.error(f"Tool {tool_name} not found in registry")
            return {
                "success": False,
                "error": f"Tool '{tool_name}' is not available. Please try a different action."
            }

        try:
            # All tools require user_id as first argument
            result = tool_func(user_id, **arguments)

            # Log tool execution
            if result.get('success'):
                logger.info(f"Successfully executed tool {tool_name} for user {user_id}")
            else:
                logger.warning(f"Tool {tool_name} returned error for user {user_id}: {result.get('error')}")

            return result

        except TypeError as e:
            # Handle argument mismatch errors
            logger.error(f"Invalid arguments for tool {tool_name}: {e}")
            return {
                "success": False,
                "error": f"Invalid parameters provided for {tool_name}. Please check your request and try again."
            }
        except Exception as e:
            # Handle all other errors
            logger.error(f"Unexpected error executing tool {tool_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"An error occurred while executing {tool_name}. Please try again or rephrase your request."
            }

    def process_message(
        self, user_id: Union[str, UUID], message_content: str, conversation_id: Optional[UUID] = None
    ) -> Tuple[str, UUID, UUID, List[Dict[str, Any]]]:
        """Process a user message and generate agent response.

        Args:
            user_id: User ID
            message_content: User's message
            conversation_id: Optional conversation ID

        Returns:
            Tuple of (agent_response, conversation_id, message_id, tool_calls)
        """
        with Session(get_engine()) as session:
            # Get or create conversation
            conversation = self.get_or_create_conversation(session, user_id, conversation_id)

            # Load conversation history
            messages = self.load_conversation_history(session, conversation.id)

            # Add user message to history
            messages.append({"role": "user", "content": message_content})

            # Get next sequence number
            statement = select(Message).where(
                Message.conversation_id == conversation.id
            ).order_by(Message.sequence_number.desc())
            last_message = session.exec(statement).first()
            next_sequence = (last_message.sequence_number + 1) if last_message else 0

            # Persist user message
            user_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=message_content,
                sequence_number=next_sequence
            )
            session.add(user_message)
            session.commit()
            session.refresh(user_message)

            # Call OpenAI API
            try:
                response = self.client.chat.completions.create(
                    model=agent_config.model,
                    messages=messages,
                    tools=ALL_TOOLS,
                    temperature=agent_config.temperature,
                    max_tokens=agent_config.max_tokens,
                    timeout=agent_config.timeout
                )

                assistant_message = response.choices[0].message

                # Handle tool calls if present
                if assistant_message.tool_calls:
                    # Execute tools and collect results
                    tool_results = []
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)

                        result = self.execute_tool(user_id, tool_name, arguments)
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "tool_name": tool_name,
                            "arguments": arguments,
                            "result": result
                        })

                    # Add assistant message with tool calls to history
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in assistant_message.tool_calls
                        ]
                    })

                    # Add tool results to history
                    for tr in tool_results:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tr["tool_call_id"],
                            "content": json.dumps(tr["result"])
                        })

                    # Call API again to get final response
                    response = self.client.chat.completions.create(
                        model=agent_config.model,
                        messages=messages,
                        temperature=agent_config.temperature,
                        max_tokens=agent_config.max_tokens,
                        timeout=agent_config.timeout
                    )

                    final_message = response.choices[0].message
                    agent_response = final_message.content or "I've completed the requested action."

                    # Persist agent message with tool invocations
                    agent_message = Message(
                        conversation_id=conversation.id,
                        role=MessageRole.AGENT,
                        content=agent_response,
                        sequence_number=next_sequence + 1
                    )
                    session.add(agent_message)
                    session.commit()
                    session.refresh(agent_message)

                    # Persist tool invocations
                    for tr in tool_results:
                        tool_invocation = ToolInvocation(
                            message_id=agent_message.id,
                            tool_name=tr["tool_name"],
                            input_params=tr["arguments"],
                            output_result=tr["result"],
                            status=ToolInvocationStatus.SUCCESS if tr["result"].get("success") else ToolInvocationStatus.ERROR
                        )
                        session.add(tool_invocation)

                    session.commit()

                else:
                    # No tool calls, just persist agent response
                    agent_response = assistant_message.content or "I'm here to help!"

                    agent_message = Message(
                        conversation_id=conversation.id,
                        role=MessageRole.AGENT,
                        content=agent_response,
                        sequence_number=next_sequence + 1
                    )
                    session.add(agent_message)
                    session.commit()
                    session.refresh(agent_message)

                    # No tool results for this branch
                    tool_results = []

                # Update conversation timestamp
                from datetime import datetime
                conversation.updated_at = datetime.utcnow()
                session.add(conversation)
                session.commit()

                logger.info(f"Processed message for user {user_id}, conversation {conversation.id}")

                # Return tool invocation information
                tool_calls_info = [
                    {
                        "tool_name": tr["tool_name"],
                        "input_params": tr["arguments"],
                        "output_result": tr["result"]
                    }
                    for tr in tool_results
                ]

                return agent_response, conversation.id, agent_message.id, tool_calls_info

            except Exception as e:
                logger.error(f"Error calling OpenAI API: {e}")
                raise


# Singleton instance
agent_service = AgentService()
