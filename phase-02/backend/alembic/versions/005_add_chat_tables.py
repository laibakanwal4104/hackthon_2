"""Add chat tables

Revision ID: 005
Revises: 004
Create Date: 2026-02-07 07:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from datetime import datetime
from uuid import uuid4

# revision identifiers
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Create conversation table
    op.create_table('conversation',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_user_id'), 'conversation', ['user_id'])
    op.create_index(op.f('ix_conversation_created_at'), 'conversation', ['created_at'])

    # Create message table
    op.create_table('message',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('conversation_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),  # 'user' or 'agent'
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_conversation_id'), 'message', ['conversation_id'])
    op.create_index(op.f('ix_message_sequence_number'), 'message', ['sequence_number'])
    op.create_index(op.f('ix_message_created_at'), 'message', ['created_at'])

    # Create tool_invocation table
    op.create_table('tool_invocation',
        sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('message_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column('tool_name', sa.String(), nullable=False),
        sa.Column('input_params', sa.JSON(), nullable=True),
        sa.Column('output_result', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),  # 'success' or 'error'
        sa.Column('executed_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['message_id'], ['message.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tool_invocation_message_id'), 'tool_invocation', ['message_id'])
    op.create_index(op.f('ix_tool_invocation_tool_name'), 'tool_invocation', ['tool_name'])
    op.create_index(op.f('ix_tool_invocation_executed_at'), 'tool_invocation', ['executed_at'])


def downgrade():
    # Drop tool_invocation table
    op.drop_index(op.f('ix_tool_invocation_executed_at'), table_name='tool_invocation')
    op.drop_index(op.f('ix_tool_invocation_tool_name'), table_name='tool_invocation')
    op.drop_index(op.f('ix_tool_invocation_message_id'), table_name='tool_invocation')
    op.drop_table('tool_invocation')

    # Drop message table
    op.drop_index(op.f('ix_message_created_at'), table_name='message')
    op.drop_index(op.f('ix_message_sequence_number'), table_name='message')
    op.drop_index(op.f('ix_message_conversation_id'), table_name='message')
    op.drop_table('message')

    # Drop conversation table
    op.drop_index(op.f('ix_conversation_created_at'), table_name='conversation')
    op.drop_index(op.f('ix_conversation_user_id'), table_name='conversation')
    op.drop_table('conversation')