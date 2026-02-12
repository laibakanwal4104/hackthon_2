"""Message database model for conversation messages."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum
from sqlmodel import SQLModel, Field


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class Message(SQLModel, table=True):
    """Message entity representing a single message in a conversation.

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Parent conversation (foreign key to Conversation.id)
        role: Message role (user, agent, system)
        content: Message text content
        sequence_number: Message order in conversation
        created_at: Timestamp of message creation
    """

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier"
    )
    conversation_id: UUID = Field(
        nullable=False,
        foreign_key="conversation.id",
        index=True,
        description="Parent conversation"
    )
    role: MessageRole = Field(
        nullable=False,
        description="Message role (user, agent, system)"
    )
    content: str = Field(
        nullable=False,
        min_length=1,
        description="Message text content"
    )
    sequence_number: int = Field(
        nullable=False,
        ge=0,
        description="Message order in conversation"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp"
    )

    def __repr__(self) -> str:
        return f"<Message id={self.id} conversation_id={self.conversation_id} role={self.role}>"
