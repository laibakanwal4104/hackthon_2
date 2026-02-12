"""MCP tools for todo operations."""
import logging
from uuid import UUID
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from datetime import datetime

from src.models.task import Task
from src.models.database import get_engine

logger = logging.getLogger(__name__)


def create_todo(user_id: UUID, title: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Create a new todo task.

    Args:
        user_id: UUID of the user creating the task
        title: Title of the task
        description: Optional description of the task

    Returns:
        Dict with success status, task_id, and message
    """
    try:
        with Session(get_engine()) as session:
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                is_completed=False
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            logger.info(f"Created todo task {task.id} for user {user_id}")
            return {
                "success": True,
                "task_id": str(task.id),
                "message": f"Created todo: {title}"
            }
    except Exception as e:
        logger.error(f"Error creating todo for user {user_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def list_todos(user_id: UUID, filter: str = "all") -> Dict[str, Any]:
    """List user's todo tasks with optional filtering.

    Args:
        user_id: UUID of the user
        filter: Filter by status - 'all', 'completed', or 'pending'

    Returns:
        Dict with success status, tasks list, and count
    """
    try:
        with Session(get_engine()) as session:
            # Base query filtered by user
            statement = select(Task).where(Task.user_id == user_id)

            # Apply status filter
            if filter == "completed":
                statement = statement.where(Task.is_completed == True)
            elif filter == "pending":
                statement = statement.where(Task.is_completed == False)

            # Order by creation date (newest first)
            statement = statement.order_by(Task.created_at.desc())

            tasks = session.exec(statement).all()

            # Format tasks for response
            tasks_list = [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "is_completed": task.is_completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ]

            logger.info(f"Listed {len(tasks_list)} tasks for user {user_id} with filter '{filter}'")
            return {
                "success": True,
                "tasks": tasks_list,
                "count": len(tasks_list),
                "filter": filter
            }
    except Exception as e:
        logger.error(f"Error listing todos for user {user_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def update_todo(user_id: UUID, task_id: str, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """Update an existing todo task.

    Args:
        user_id: UUID of the user (for authorization)
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Dict with success status and message
    """
    try:
        task_uuid = UUID(task_id)

        with Session(get_engine()) as session:
            # Find task and verify ownership
            statement = select(Task).where(Task.id == task_uuid, Task.user_id == user_id)
            task = session.exec(statement).first()

            if not task:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found or you don't have permission to update it"
                }

            # Update fields if provided
            updated_fields = []
            if title is not None:
                task.title = title
                updated_fields.append("title")
            if description is not None:
                task.description = description
                updated_fields.append("description")

            if not updated_fields:
                return {
                    "success": False,
                    "error": "No fields provided to update"
                }

            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()

            logger.info(f"Updated task {task_id} for user {user_id}: {', '.join(updated_fields)}")
            return {
                "success": True,
                "message": f"Updated task: {', '.join(updated_fields)}",
                "task_id": task_id
            }
    except ValueError:
        return {
            "success": False,
            "error": f"Invalid task ID format: {task_id}"
        }
    except Exception as e:
        logger.error(f"Error updating task {task_id} for user {user_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def delete_todo(user_id: UUID, task_id: str) -> Dict[str, Any]:
    """Delete a todo task.

    Args:
        user_id: UUID of the user (for authorization)
        task_id: ID of the task to delete

    Returns:
        Dict with success status and message
    """
    try:
        task_uuid = UUID(task_id)

        with Session(get_engine()) as session:
            # Find task and verify ownership
            statement = select(Task).where(Task.id == task_uuid, Task.user_id == user_id)
            task = session.exec(statement).first()

            if not task:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found or you don't have permission to delete it"
                }

            task_title = task.title
            session.delete(task)
            session.commit()

            logger.info(f"Deleted task {task_id} for user {user_id}")
            return {
                "success": True,
                "message": f"Deleted task: {task_title}",
                "task_id": task_id
            }
    except ValueError:
        return {
            "success": False,
            "error": f"Invalid task ID format: {task_id}"
        }
    except Exception as e:
        logger.error(f"Error deleting task {task_id} for user {user_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def mark_todo_complete(user_id: UUID, task_id: str, completed: bool) -> Dict[str, Any]:
    """Mark a todo task as complete or incomplete.

    Args:
        user_id: UUID of the user (for authorization)
        task_id: ID of the task to update
        completed: True to mark complete, False to mark incomplete

    Returns:
        Dict with success status and message
    """
    try:
        task_uuid = UUID(task_id)

        with Session(get_engine()) as session:
            # Find task and verify ownership
            statement = select(Task).where(Task.id == task_uuid, Task.user_id == user_id)
            task = session.exec(statement).first()

            if not task:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found or you don't have permission to update it"
                }

            task.is_completed = completed
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()

            status = "complete" if completed else "incomplete"
            logger.info(f"Marked task {task_id} as {status} for user {user_id}")
            return {
                "success": True,
                "message": f"Marked task as {status}: {task.title}",
                "task_id": task_id,
                "is_completed": completed
            }
    except ValueError:
        return {
            "success": False,
            "error": f"Invalid task ID format: {task_id}"
        }
    except Exception as e:
        logger.error(f"Error marking task {task_id} complete for user {user_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }
