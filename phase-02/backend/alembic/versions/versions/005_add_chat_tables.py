"""Create chat tables migration.

Revision ID: 005
Revises: 004
Create Date: 2026-02-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime
from uuid import uuid4

# revision identifiers
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create conversation, message, and tool_invocation tables."""

    # Create conversation table
    op.create_table(
        "conversation",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid4),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column("updated_at", sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.PrimaryKeyConstraint("id", name="pk_conversation"),
        sa.ForeignKeyConstraint(["user_id"], ["user.uuid"], name="fk_conversation_user_id"),
    )
    op.create_index("ix_conversation_user_id", "conversation", ["user_id"])
    op.create_index("ix_conversation_user_id_status", "conversation", ["user_id", "status"])
    op.create_index("ix_conversation_created_at", "conversation", ["created_at"])

    # Create message table
    op.create_table(
        "message",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid4),
        sa.Column("conversation_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.PrimaryKeyConstraint("id", name="pk_message"),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversation.id"], name="fk_message_conversation_id"),
        sa.UniqueConstraint("conversation_id", "sequence_number", name="uq_message_conversation_sequence"),
    )
    op.create_index("ix_message_conversation_id", "message", ["conversation_id"])
    op.create_index("ix_message_created_at", "message", ["created_at"])

    # Create tool_invocation table
    op.create_table(
        "tool_invocation",
        sa.Column("id", sa.UUID(), nullable=False, default=uuid4),
        sa.Column("message_id", sa.UUID(), nullable=False),
        sa.Column("tool_name", sa.String(100), nullable=False),
        sa.Column("input_params", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("output_result", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("executed_at", sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.PrimaryKeyConstraint("id", name="pk_tool_invocation"),
        sa.ForeignKeyConstraint(["message_id"], ["message.id"], name="fk_tool_invocation_message_id"),
    )
    op.create_index("ix_tool_invocation_message_id", "tool_invocation", ["message_id"])
    op.create_index("ix_tool_invocation_tool_name", "tool_invocation", ["tool_name"])
    op.create_index("ix_tool_invocation_status", "tool_invocation", ["status"])
    op.create_index("ix_tool_invocation_executed_at", "tool_invocation", ["executed_at"])


def downgrade() -> None:
    """Drop chat tables."""
    # Drop in reverse order due to foreign key constraints
    op.drop_index("ix_tool_invocation_executed_at", table_name="tool_invocation")
    op.drop_index("ix_tool_invocation_status", table_name="tool_invocation")
    op.drop_index("ix_tool_invocation_tool_name", table_name="tool_invocation")
    op.drop_index("ix_tool_invocation_message_id", table_name="tool_invocation")
    op.drop_table("tool_invocation")

    op.drop_index("ix_message_created_at", table_name="message")
    op.drop_index("ix_message_conversation_id", table_name="message")
    op.drop_table("message")

    op.drop_index("ix_conversation_created_at", table_name="conversation")
    op.drop_index("ix_conversation_user_id_status", table_name="conversation")
    op.drop_index("ix_conversation_user_id", table_name="conversation")
    op.drop_table("conversation")
