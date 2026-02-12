"""MCP tools module for todo operations."""
from src.mcp.schemas import (
    CREATE_TODO_SCHEMA,
    LIST_TODOS_SCHEMA,
    UPDATE_TODO_SCHEMA,
    DELETE_TODO_SCHEMA,
    MARK_TODO_COMPLETE_SCHEMA,
    ALL_TOOLS,
)
from src.mcp.tools import (
    create_todo,
    list_todos,
    update_todo,
    delete_todo,
    mark_todo_complete,
)

# Tool registry mapping tool names to functions
TOOL_REGISTRY = {
    "create_todo": create_todo,
    "list_todos": list_todos,
    "update_todo": update_todo,
    "delete_todo": delete_todo,
    "mark_todo_complete": mark_todo_complete,
}

__all__ = [
    "CREATE_TODO_SCHEMA",
    "LIST_TODOS_SCHEMA",
    "UPDATE_TODO_SCHEMA",
    "DELETE_TODO_SCHEMA",
    "MARK_TODO_COMPLETE_SCHEMA",
    "ALL_TOOLS",
    "create_todo",
    "list_todos",
    "update_todo",
    "delete_todo",
    "mark_todo_complete",
    "TOOL_REGISTRY",
]
