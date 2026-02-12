"""Conversation database model for chat sessions."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum
from sqlmodel import SQLModel, Field


class ConversationStatus(str, Enum):
    """Conversation status enumeration."""
    ACTIVE = "active"
    ARCHIVED = "archived"


class Conversation(SQLModel, table=True):
    """Conversation entity representing a chat session.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Owner of the conversation (foreign key to User.uuid)
        status: Conversation status (active, archived)
        created_at: Timestamp of conversation creation
        updated_at: Last message timestamp
    """

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier"
    )
    user_id: str = Field(
        nullable=False,
        foreign_key="user.uuid",
        index=True,
        max_length=255,
        description="Owner of the conversation"
    )
    status: ConversationStatus = Field(
        default=ConversationStatus.ACTIVE,
        nullable=False,
        description="Conversation status"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp"
    )

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} user_id={self.user_id} status={self.status}>"
