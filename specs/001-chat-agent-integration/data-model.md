# Data Model: AI Chat Agent & Integration

**Feature**: 001-chat-agent-integration
**Date**: 2026-02-07
**Phase**: Phase 1 - Design

## Overview

This document defines the database schema for conversation persistence, including three new entities: Conversation, Message, and ToolInvocation. These entities enable stateless chat execution with full traceability of agent interactions.

## Entity Relationship Diagram

```
User (existing)
  ↓ 1:N
Conversation
  ↓ 1:N
Message
  ↓ 1:N
ToolInvocation
```

## Entities

### 1. Conversation

Represents a chat session between a user and the AI agent.

**Table Name**: `conversation`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique conversation identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → User.uuid, INDEX | Owner of the conversation |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | Conversation status (active, archived) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When conversation was created |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last message timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for user's conversation lookup)
- INDEX on `(user_id, status)` (for active conversation queries)
- INDEX on `created_at` (for sorting)

**Relationships**:
- Many-to-one with User (user_id → User.uuid)
- One-to-many with Message

**Validation Rules**:
- `user_id` must reference existing User
- `status` must be one of: 'active', 'archived'
- `updated_at` must be >= `created_at`

**Business Rules**:
- Each user can have multiple conversations
- Typically one active conversation per user at a time
- Conversations can be archived but not deleted (audit trail)
- `updated_at` is updated whenever a new message is added

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

class Conversation(SQLModel, table=True):
    """Conversation entity representing a chat session."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier"
    )
    user_id: UUID = Field(
        nullable=False,
        foreign_key="user.uuid",
        index=True,
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
```

### 2. Message

Represents a single message in a conversation (user or agent).

**Table Name**: `message`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique message identifier |
| conversation_id | UUID | NOT NULL, FOREIGN KEY → Conversation.id, INDEX | Parent conversation |
| role | VARCHAR(20) | NOT NULL | Message role (user, agent, system) |
| content | TEXT | NOT NULL | Message text content |
| sequence_number | INTEGER | NOT NULL | Message order in conversation |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When message was created |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `conversation_id` (for conversation message lookup)
- UNIQUE INDEX on `(conversation_id, sequence_number)` (ensure ordering)
- INDEX on `created_at` (for sorting)

**Relationships**:
- Many-to-one with Conversation (conversation_id → Conversation.id)
- One-to-many with ToolInvocation

**Validation Rules**:
- `conversation_id` must reference existing Conversation
- `role` must be one of: 'user', 'agent', 'system'
- `content` must not be empty (min length 1)
- `sequence_number` must be unique per conversation
- `sequence_number` must be >= 0

**Business Rules**:
- Messages are immutable once created (no updates)
- Sequence numbers start at 0 for each conversation
- System messages (if used) contain agent instructions
- User messages contain user input
- Agent messages contain agent responses
- Messages are never deleted (audit trail)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"

class Message(SQLModel, table=True):
    """Message entity representing a single message in a conversation."""

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

    class Config:
        # Ensure unique sequence per conversation
        table_args = (
            UniqueConstraint('conversation_id', 'sequence_number'),
        )
```

### 3. ToolInvocation

Represents an agent's invocation of an MCP tool.

**Table Name**: `tool_invocation`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique invocation identifier |
| message_id | UUID | NOT NULL, FOREIGN KEY → Message.id, INDEX | Agent message that triggered tool |
| tool_name | VARCHAR(100) | NOT NULL | Name of MCP tool invoked |
| input_params | JSONB | NOT NULL | Tool input parameters (JSON) |
| output_result | JSONB | NOT NULL | Tool execution result (JSON) |
| status | VARCHAR(20) | NOT NULL | Execution status (success, error) |
| executed_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When tool was executed |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `message_id` (for message's tool calls)
- INDEX on `tool_name` (for analytics)
- INDEX on `executed_at` (for sorting)
- INDEX on `status` (for error tracking)

**Relationships**:
- Many-to-one with Message (message_id → Message.id)

**Validation Rules**:
- `message_id` must reference existing Message with role='agent'
- `tool_name` must be one of: 'create_todo', 'list_todos', 'update_todo', 'delete_todo', 'mark_todo_complete'
- `input_params` must be valid JSON
- `output_result` must be valid JSON
- `status` must be one of: 'success', 'error'

**Business Rules**:
- Tool invocations are immutable once created
- Multiple tool invocations can be associated with one agent message
- Tool invocations are never deleted (audit trail)
- Used for debugging, analytics, and traceability

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from enum import Enum

class ToolInvocationStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"

class ToolInvocation(SQLModel, table=True):
    """Tool invocation entity representing an MCP tool call."""

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique invocation identifier"
    )
    message_id: UUID = Field(
        nullable=False,
        foreign_key="message.id",
        index=True,
        description="Agent message that triggered tool"
    )
    tool_name: str = Field(
        nullable=False,
        max_length=100,
        index=True,
        description="Name of MCP tool invoked"
    )
    input_params: Dict[str, Any] = Field(
        sa_column=Column(JSON),
        nullable=False,
        description="Tool input parameters (JSON)"
    )
    output_result: Dict[str, Any] = Field(
        sa_column=Column(JSON),
        nullable=False,
        description="Tool execution result (JSON)"
    )
    status: ToolInvocationStatus = Field(
        nullable=False,
        index=True,
        description="Execution status"
    )
    executed_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Execution timestamp"
    )
```

## Database Migration

**Migration File**: `alembic/versions/005_add_chat_tables.py`

**Operations**:
1. Create `conversation` table with indexes
2. Create `message` table with indexes and unique constraint
3. Create `tool_invocation` table with indexes
4. Add foreign key constraints

**Rollback**:
1. Drop `tool_invocation` table
2. Drop `message` table
3. Drop `conversation` table

## Data Access Patterns

### Common Queries

**Get or Create Active Conversation**:
```python
conversation = session.query(Conversation).filter_by(
    user_id=user_id,
    status=ConversationStatus.ACTIVE
).first()

if not conversation:
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
```

**Load Conversation History**:
```python
messages = session.query(Message).filter_by(
    conversation_id=conversation_id
).order_by(Message.sequence_number).all()
```

**Create Message with Tool Invocations**:
```python
# Create agent message
message = Message(
    conversation_id=conversation_id,
    role=MessageRole.AGENT,
    content=agent_response,
    sequence_number=next_sequence
)
session.add(message)
session.flush()  # Get message.id

# Create tool invocations
for tool_call in tool_calls:
    invocation = ToolInvocation(
        message_id=message.id,
        tool_name=tool_call.name,
        input_params=tool_call.params,
        output_result=tool_call.result,
        status=ToolInvocationStatus.SUCCESS
    )
    session.add(invocation)

session.commit()
```

## Storage Estimates

**Assumptions**:
- 50 users
- 10 conversations per user (average)
- 20 messages per conversation (average)
- 0.5 tool invocations per agent message (average)

**Calculations**:
- Conversations: 50 × 10 = 500 rows (~50 KB)
- Messages: 500 × 20 = 10,000 rows (~5 MB with text content)
- Tool Invocations: 10,000 × 0.5 × 0.5 = 2,500 rows (~1 MB with JSON)

**Total**: ~6 MB for hackathon demo scale

## Performance Considerations

- Indexes on foreign keys ensure fast joins
- Unique constraint on (conversation_id, sequence_number) prevents race conditions
- JSONB type for tool parameters enables efficient querying
- Conversation.updated_at indexed for "recent conversations" queries
- Consider partitioning by created_at for long-term scaling

## Security & Privacy

- User isolation enforced at query level (always filter by user_id)
- No cross-user data access possible
- Audit trail preserved (no deletions)
- Sensitive data in tool parameters should be sanitized before storage
- Consider encryption at rest for conversation content
