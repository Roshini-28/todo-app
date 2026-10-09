"""Task service - handles all task-related database operations."""
from datetime import datetime
from typing import Optional
from bson import ObjectId
from bson.errors import InvalidId
from database.mongodb import get_tasks_collection, get_pages_collection, get_db


def get_users_by_ids(user_ids):
    """Get multiple users by their IDs for task assignment."""
    if not user_ids:
        return []
    try:
        obj_ids = [ObjectId(uid) for uid in user_ids]
        users = get_db()["users"].find({"_id": {"$in": obj_ids}})
        return [{"id": str(u["_id"]), "username": u["username"]} for u in users]
    except (InvalidId, TypeError):
        return []


def serialize_task(task):
    """Convert a MongoDB task document to a JSON-serializable dict."""
    assigned_to = task.get("assigned_to", [])
    if not isinstance(assigned_to, list):
        assigned_to = [assigned_to] if assigned_to else []

    users = get_users_by_ids(assigned_to)
    assigned_to_usernames = [u["username"] for u in users]

    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task.get("description", ""),
        "page": task["page"],
        "status": task["status"],
        "priority": task.get("priority", "Medium"),
        "order": task.get("order", 0),
        "assigned_to": assigned_to,
        "assigned_to_usernames": assigned_to_usernames,
        "created_at": task["created_at"],
        "updated_at": task["updated_at"],
    }


def get_all_tasks(page=None, status=None, search=None):
    """Get tasks with optional filtering."""
    collection = get_tasks_collection()
    query = {}

    if page:
        query["page"] = page
    if status:
        query["status"] = status
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]

    tasks = collection.find(query).sort([("order", 1), ("created_at", -1)])
    return [serialize_task(task) for task in tasks]


def get_task_by_id(task_id):
    """Get a single task by its ID."""
    try:
        obj_id = ObjectId(task_id)
    except (InvalidId, TypeError):
        return None

    collection = get_tasks_collection()
    task = collection.find_one({"_id": obj_id})
    if task:
        return serialize_task(task)
    return None


def create_task(title, description, page, priority="Medium", assigned_to=None):
    """Create a new task."""
    collection = get_tasks_collection()
    now = datetime.utcnow()

    # Get the highest order value for this page
    last_task = collection.find_one(
        {"page": page},
        sort=[("order", -1)]
    )
    next_order = (last_task.get("order", 0) + 1) if last_task else 1

    task = {
        "title": title,
        "description": description or "",
        "page": page,
        "status": "Pending",
        "priority": priority,
        "order": next_order,
        "assigned_to": assigned_to or [],
        "created_at": now,
        "updated_at": now,
    }

    result = collection.insert_one(task)
    task["_id"] = result.inserted_id
    return serialize_task(task)


def update_task(task_id, title=None, description=None, page=None, priority=None, assigned_to=None):
    """Update an existing task."""
    try:
        obj_id = ObjectId(task_id)
    except (InvalidId, TypeError):
        return None

    collection = get_tasks_collection()
    now = datetime.utcnow()

    update_fields = {"updated_at": now}
    if title is not None:
        update_fields["title"] = title
    if description is not None:
        update_fields["description"] = description
    if page is not None:
        update_fields["page"] = page
    if priority is not None:
        update_fields["priority"] = priority
    if assigned_to is not None:
        update_fields["assigned_to"] = assigned_to

    result = collection.find_one_and_update(
        {"_id": obj_id},
        {"$set": update_fields},
        return_document=True,
    )

    if result:
        return serialize_task(result)
    return None


def update_task_order(task_ids):
    """Update the order of multiple tasks.

    Args:
        task_ids: List of task ID strings in the desired order.

    Returns:
        dict: {'success': bool, 'updated': int, 'errors': list}
    """
    collection = get_tasks_collection()
    now = datetime.utcnow()
    errors = []
    updated = 0

    for index, task_id in enumerate(task_ids):
        try:
            obj_id = ObjectId(task_id)
        except (InvalidId, TypeError):
            errors.append(f"Invalid task ID: {task_id}")
            continue

        result = collection.update_one(
            {"_id": obj_id},
            {"$set": {"order": index + 1, "updated_at": now}}
        )

        if result.matched_count == 0:
            errors.append(f"Task not found: {task_id}")
        else:
            updated += 1

    return {
        "success": len(errors) == 0,
        "updated": updated,
        "errors": errors,
    }


def complete_task(task_id):
    """Mark a task as completed."""
    try:
        obj_id = ObjectId(task_id)
    except (InvalidId, TypeError):
        return None

    collection = get_tasks_collection()
    result = collection.find_one_and_update(
        {"_id": obj_id},
        {"$set": {"status": "Completed", "updated_at": datetime.utcnow()}},
        return_document=True,
    )

    if result:
        return serialize_task(result)
    return None


def uncomplete_task(task_id):
    """Mark a task as pending (uncomplete)."""
    try:
        obj_id = ObjectId(task_id)
    except (InvalidId, TypeError):
        return None

    collection = get_tasks_collection()
    result = collection.find_one_and_update(
        {"_id": obj_id},
        {"$set": {"status": "Pending", "updated_at": datetime.utcnow()}},
        return_document=True,
    )

    if result:
        return serialize_task(result)
    return None


def delete_task(task_id):
    """Delete a single task."""
    try:
        obj_id = ObjectId(task_id)
    except (InvalidId, TypeError):
        return False

    collection = get_tasks_collection()
    result = collection.delete_one({"_id": obj_id})
    return result.deleted_count > 0


def clear_completed_tasks(page=None):
    """Delete all completed tasks, optionally filtered by page."""
    collection = get_tasks_collection()
    query = {"status": "Completed"}

    if page:
        query["page"] = page

    result = collection.delete_many(query)
    return result.deleted_count
