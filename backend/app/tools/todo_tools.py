"""Todo tools for the AI agent.

These tools allow the AI to perform Todo operations.
The AI calls these tools instead of directly accessing MongoDB.
"""
from typing import Optional
from services import task_service, page_service


def create_todo(title: str, description: str = "", page: str = "Default", priority: str = "Medium") -> dict:
    """Create a new todo item.

    Args:
        title: Task title (required)
        description: Task description (optional)
        page: Page/project name (default: "Default")
        priority: Task priority - Low, Medium, High (default: "Medium")

    Returns:
        dict: Created task details
    """
    task = task_service.create_task(
        title=title,
        description=description,
        page=page,
        priority=priority,
    )
    return {
        "success": True,
        "message": f"Task '{title}' created successfully",
        "task": task,
    }


def list_todos(status: Optional[str] = None, page: Optional[str] = None, search: Optional[str] = None) -> dict:
    """List todo items with optional filtering.

    Args:
        status: Filter by status - "Pending" or "Completed"
        page: Filter by page name
        search: Search in title and description

    Returns:
        dict: List of tasks
    """
    tasks = task_service.get_all_tasks(page=page, status=status, search=search)
    return {
        "success": True,
        "count": len(tasks),
        "tasks": tasks,
    }


def get_todo(task_id: str) -> dict:
    """Get a single todo item by ID.

    Args:
        task_id: The task ID

    Returns:
        dict: Task details
    """
    task = task_service.get_task_by_id(task_id)
    if not task:
        return {
            "success": False,
            "message": f"Task with ID '{task_id}' not found",
        }
    return {
        "success": True,
        "task": task,
    }


def update_todo(task_id: str, title: Optional[str] = None, description: Optional[str] = None,
                 page: Optional[str] = None, priority: Optional[str] = None) -> dict:
    """Update an existing todo item.

    Args:
        task_id: The task ID
        title: New title (optional)
        description: New description (optional)
        page: New page name (optional)
        priority: New priority - Low, Medium, High (optional)

    Returns:
        dict: Updated task details
    """
    task = task_service.update_task(
        task_id=task_id,
        title=title,
        description=description,
        page=page,
        priority=priority,
    )
    if not task:
        return {
            "success": False,
            "message": f"Task with ID '{task_id}' not found",
        }
    return {
        "success": True,
        "message": f"Task updated successfully",
        "task": task,
    }


def complete_todo(task_id: str) -> dict:
    """Mark a todo item as completed.

    Args:
        task_id: The task ID

    Returns:
        dict: Updated task details
    """
    task = task_service.complete_task(task_id)
    if not task:
        return {
            "success": False,
            "message": f"Task with ID '{task_id}' not found",
        }
    return {
        "success": True,
        "message": f"Task '{task['title']}' marked as completed",
        "task": task,
    }


def uncomplete_todo(task_id: str) -> dict:
    """Mark a todo item as pending (not completed).

    Args:
        task_id: The task ID

    Returns:
        dict: Updated task details
    """
    task = task_service.uncomplete_task(task_id)
    if not task:
        return {
            "success": False,
            "message": f"Task with ID '{task_id}' not found",
        }
    return {
        "success": True,
        "message": f"Task '{task['title']}' marked as pending",
        "task": task,
    }


def delete_todo(task_id: str) -> dict:
    """Delete a todo item.

    Args:
        task_id: The task ID

    Returns:
        dict: Deletion result
    """
    success = task_service.delete_task(task_id)
    if not success:
        return {
            "success": False,
            "message": f"Task with ID '{task_id}' not found",
        }
    return {
        "success": True,
        "message": "Task deleted successfully",
    }


def summarize_todos(status: Optional[str] = None) -> dict:
    """Get a summary of todo items.

    Args:
        status: Filter by status - "Pending" or "Completed"

    Returns:
        dict: Summary of tasks
    """
    tasks = task_service.get_all_tasks(status=status)

    if not tasks:
        return {
            "success": True,
            "message": "No tasks found",
            "summary": {
                "total": 0,
                "pending": 0,
                "completed": 0,
            },
        }

    pending = [t for t in tasks if t["status"] == "Pending"]
    completed = [t for t in tasks if t["status"] == "Completed"]

    # Group by priority
    high_priority = [t for t in pending if t.get("priority") == "High"]
    medium_priority = [t for t in pending if t.get("priority") == "Medium"]
    low_priority = [t for t in pending if t.get("priority") == "Low"]

    summary_text = f"You have {len(tasks)} total tasks: {len(pending)} pending, {len(completed)} completed."

    if high_priority:
        summary_text += f"\n\nHigh priority tasks ({len(high_priority)}):"
        for task in high_priority:
            summary_text += f"\n- {task['title']}"

    if medium_priority:
        summary_text += f"\n\nMedium priority tasks ({len(medium_priority)}):"
        for task in medium_priority:
            summary_text += f"\n- {task['title']}"

    if low_priority:
        summary_text += f"\n\nLow priority tasks ({len(low_priority)}):"
        for task in low_priority:
            summary_text += f"\n- {task['title']}"

    return {
        "success": True,
        "message": summary_text,
        "summary": {
            "total": len(tasks),
            "pending": len(pending),
            "completed": len(completed),
            "high_priority": len(high_priority),
            "medium_priority": len(medium_priority),
            "low_priority": len(low_priority),
        },
    }


# Export all tools for the agent
TODO_TOOLS = [
    create_todo,
    list_todos,
    get_todo,
    update_todo,
    complete_todo,
    uncomplete_todo,
    delete_todo,
    summarize_todos,
]
