"""Page service - handles all page-related database operations."""
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from database.mongodb import get_pages_collection, get_tasks_collection, get_db


def get_user_by_id(user_id):
    """Get a user by ID."""
    try:
        obj_id = ObjectId(user_id)
        user = get_db()["users"].find_one({"_id": obj_id})
        if user:
            return {"id": str(user["_id"]), "username": user["username"]}
    except (InvalidId, TypeError):
        pass
    return None


def get_users_by_ids(user_ids):
    """Get multiple users by their IDs."""
    if not user_ids:
        return []
    try:
        obj_ids = [ObjectId(uid) for uid in user_ids]
        users = get_db()["users"].find({"_id": {"$in": obj_ids}})
        return [{"id": str(u["_id"]), "username": u["username"]} for u in users]
    except (InvalidId, TypeError):
        return []


def serialize_page(page):
    """Convert a MongoDB page document to a JSON-serializable dict."""
    created_by = page.get("created_by")
    created_by_username = None
    if created_by:
        user = get_user_by_id(created_by)
        if user:
            created_by_username = user["username"]

    shared_with = page.get("shared_with", [])
    if not isinstance(shared_with, list):
        shared_with = [shared_with] if shared_with else []

    shared_users = get_users_by_ids(shared_with)
    shared_with_usernames = [u["username"] for u in shared_users]

    return {
        "id": str(page["_id"]),
        "name": page["name"],
        "created_by": created_by,
        "created_by_username": created_by_username,
        "shared_with": shared_with,
        "shared_with_usernames": shared_with_usernames,
        "created_at": page["created_at"],
    }


def get_all_pages(current_user_id):
    """Get all pages: created by user OR shared with user."""
    collection = get_pages_collection()
    query = {
        "$or": [
            {"created_by": current_user_id},
            {"shared_with": current_user_id},
        ]
    }
    pages = collection.find(query).sort("created_at", 1)
    return [serialize_page(page) for page in pages]


def get_my_pages(current_user_id):
    """Get pages created by the current user."""
    collection = get_pages_collection()
    pages = collection.find({"created_by": current_user_id}).sort("created_at", 1)
    return [serialize_page(page) for page in pages]


def get_shared_pages(current_user_id):
    """Get pages shared with the current user."""
    collection = get_pages_collection()
    pages = collection.find({"shared_with": current_user_id}).sort("created_at", 1)
    return [serialize_page(page) for page in pages]


def get_page_by_name(name):
    """Get a page by its name (case-insensitive)."""
    collection = get_pages_collection()
    page = collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
    if page:
        return serialize_page(page)
    return None


def create_page(name, current_user_id, shared_with=None):
    """Create a new page. Returns (page, error_message)."""
    collection = get_pages_collection()

    # Check for duplicate (case-insensitive)
    existing = collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
    if existing:
        return None, "Page already exists!"

    page = {
        "name": name,
        "created_by": current_user_id,
        "shared_with": shared_with or [],
        "created_at": datetime.utcnow(),
    }

    result = collection.insert_one(page)
    page["_id"] = result.inserted_id
    return serialize_page(page), None


def update_page(page_id, name=None, shared_with=None):
    """Update a page. Returns (page, error_message)."""
    try:
        obj_id = ObjectId(page_id)
    except (InvalidId, TypeError):
        return None, "Invalid page ID"

    collection = get_pages_collection()
    page = collection.find_one({"_id": obj_id})
    if not page:
        return None, "Page not found"

    update_fields = {}
    if name is not None:
        update_fields["name"] = name
    if shared_with is not None:
        update_fields["shared_with"] = shared_with

    result = collection.find_one_and_update(
        {"_id": obj_id},
        {"$set": update_fields},
        return_document=True,
    )

    if result:
        return serialize_page(result), None
    return None, "Update failed"


def delete_page(page_id, current_user_id):
    """Delete a page. Only creator can delete. Returns (success, message)."""
    try:
        obj_id = ObjectId(page_id)
    except (InvalidId, TypeError):
        return False, "Invalid page ID"

    pages_collection = get_pages_collection()
    tasks_collection = get_tasks_collection()

    # Find the page
    page = pages_collection.find_one({"_id": obj_id})
    if not page:
        return False, "Page not found"

    # Only creator can delete
    if page.get("created_by") != current_user_id:
        return False, "Only the creator can delete this page"

    page_name = page["name"]

    # Reassign tasks from this page to "Uncategorized"
    tasks_collection.update_many(
        {"page": page_name},
        {"$set": {"page": "Uncategorized", "updated_at": datetime.utcnow()}},
    )

    # Delete the page
    pages_collection.delete_one({"_id": obj_id})
    return True, f"Page '{page_name}' deleted. Tasks moved to 'Uncategorized'."
