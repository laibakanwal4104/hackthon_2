"""User database model for authentication."""
from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """User entity for authentication.

    Attributes:
        id: Auto-increment integer primary key
        uuid: Unique user identifier (UUID stored as string)
        email: User's email address (unique, indexed)
        hashed_password: Bcrypt hashed password
        is_active: Whether the user account is active
        created_at: Timestamp of account creation
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid4()), unique=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
