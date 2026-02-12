"""ToolInvocation database model for MCP tool calls."""
from datetime import datetime
from typing import Dict, Any
from uuid import UUID, uuid4
from enum import Enum
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class ToolInvocationStatus(str, Enum):
    """Tool invocation status enumeration."""
    SUCCESS = "success"
    ERROR = "error"


class ToolInvocation(SQLModel, table=True):
    """Tool invocation entity representing an MCP tool call.

    Attributes:
        id: Unique invocation identifier (UUID)
        message_id: Agent message that triggered tool (foreign key to Message.id)
        tool_name: Name of MCP tool invoked
        input_params: Tool input parameters (JSON)
        output_result: Tool execution result (JSON)
        status: Execution status (success, error)
        executed_at: Timestamp of tool execution
    """

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
        sa_column=Column(JSON, nullable=False),
        description="Tool input parameters (JSON)"
    )
    output_result: Dict[str, Any] = Field(
        sa_column=Column(JSON, nullable=False),
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

    def __repr__(self) -> str:
        return f"<ToolInvocation id={self.id} tool_name={self.tool_name} status={self.status}>"
