"""MCP tool schemas for OpenAI function calling."""

# Tool schema for creating a new todo task
CREATE_TODO_SCHEMA = {
    "type": "function",
    "function": {
        "name": "create_todo",
        "description": "Create a new todo task for the user",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the todo task"
                },
                "description": {
                    "type": "string",
                    "description": "Optional description of the task"
                }
            },
            "required": ["title"]
        }
    }
}

# Tool schema for listing todo tasks
LIST_TODOS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_todos",
        "description": "List the user's todo tasks with optional filtering",
        "parameters": {
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "enum": ["all", "completed", "pending"],
                    "description": "Filter tasks by status: 'all' (default), 'completed', or 'pending'"
                }
            },
            "required": []
        }
    }
}

# Tool schema for updating a todo task
UPDATE_TODO_SCHEMA = {
    "type": "function",
    "function": {
        "name": "update_todo",
        "description": "Update an existing todo task's title or description",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The ID of the task to update"
                },
                "title": {
                    "type": "string",
                    "description": "New title for the task (optional)"
                },
                "description": {
                    "type": "string",
                    "description": "New description for the task (optional)"
                }
            },
            "required": ["task_id"]
        }
    }
}

# Tool schema for deleting a todo task
DELETE_TODO_SCHEMA = {
    "type": "function",
    "function": {
        "name": "delete_todo",
        "description": "Delete a todo task permanently",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The ID of the task to delete"
                }
            },
            "required": ["task_id"]
        }
    }
}

# Tool schema for marking a todo task as complete or incomplete
MARK_TODO_COMPLETE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "mark_todo_complete",
        "description": "Mark a todo task as complete or incomplete",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The ID of the task to update"
                },
                "completed": {
                    "type": "boolean",
                    "description": "True to mark as complete, False to mark as incomplete"
                }
            },
            "required": ["task_id", "completed"]
        }
    }
}

# All tool schemas for registration with OpenAI
ALL_TOOLS = [
    CREATE_TODO_SCHEMA,
    LIST_TODOS_SCHEMA,
    UPDATE_TODO_SCHEMA,
    DELETE_TODO_SCHEMA,
    MARK_TODO_COMPLETE_SCHEMA,
]
