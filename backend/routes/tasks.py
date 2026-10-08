"""Task API routes."""
from fastapi import APIRouter, HTTPException, Query, Depends
from models.task import TaskCreate, TaskUpdate, TaskResponse, TaskReorder
from services import task_service
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=list[TaskResponse])
def get_tasks(
    page: str = Query(default=None, description="Filter by page name"),
    status: str = Query(default=None, description="Filter by status (Pending/Completed)"),
    search: str = Query(default=None, description="Search in title and description"),
    current_user: dict = Depends(get_current_user),
):
    """Get all tasks with optional filtering by page, status, and search."""
    tasks = task_service.get_all_tasks(page=page, status=status, search=search)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, current_user: dict = Depends(get_current_user)):
    """Get a single task by ID."""
    task = task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)):
    """Create a new task."""
    created = task_service.create_task(
        title=task.title,
        description=task.description,
        page=task.page,
        priority=task.priority,
        assigned_to=task.assigned_to,
    )
    return created


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, task: TaskUpdate, current_user: dict = Depends(get_current_user)):
    """Update an existing task."""
    updated = task_service.update_task(
        task_id=task_id,
        title=task.title,
        description=task.description,
        page=task.page,
        priority=task.priority,
        assigned_to=task.assigned_to,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    """Mark a task as completed."""
    task = task_service.complete_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/uncomplete", response_model=TaskResponse)
def uncomplete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    """Mark a task as pending (uncomplete)."""
    task = task_service.uncomplete_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a single task."""
    deleted = task_service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


@router.delete("/completed/clear")
def clear_completed_tasks(page: str = Query(default=None), current_user: dict = Depends(get_current_user)):
    """Delete all completed tasks, optionally filtered by page."""
    count = task_service.clear_completed_tasks(page=page)
    return {"message": f"Cleared {count} completed task(s)"}


@router.put("/reorder")
def reorder_tasks(reorder_data: TaskReorder, current_user: dict = Depends(get_current_user)):
    """Update the order of tasks (for drag and drop)."""
    task_service.update_task_order(reorder_data.task_ids)
    return {"message": "Tasks reordered successfully"}
