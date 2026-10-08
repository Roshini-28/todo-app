"""User service - handles all user-related database operations."""
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
import bcrypt
from database.mongodb import get_db


def get_users_collection():
    """Get the users collection."""
    return get_db()["users"]


def serialize_user(user):
    """Convert a MongoDB user document to a JSON-serializable dict."""
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "created_at": user["created_at"],
    }


def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, hashed):
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def get_user_by_username(username):
    """Get a user by username."""
    collection = get_users_collection()
    user = collection.find_one({"username": username})
    if user:
        return serialize_user(user)
    return None


def get_user_by_id(user_id):
    """Get a user by ID."""
    try:
        obj_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        return None

    collection = get_users_collection()
    user = collection.find_one({"_id": obj_id})
    if user:
        return serialize_user(user)
    return None


def create_user(username, password):
    """Create a new user. Returns (user, error_message)."""
    collection = get_users_collection()

    # Check if username already exists
    existing = collection.find_one({"username": username})
    if existing:
        return None, "Username already exists"

    # Hash password
    hashed = hash_password(password)

    user = {
        "username": username,
        "password": hashed,
        "created_at": datetime.utcnow(),
    }

    result = collection.insert_one(user)
    user["_id"] = result.inserted_id
    return serialize_user(user), None


def authenticate_user(username, password):
    """Authenticate a user. Returns user dict if successful, None otherwise."""
    collection = get_users_collection()
    user = collection.find_one({"username": username})

    if not user:
        return None

    if verify_password(password, user["password"]):
        return serialize_user(user)

    return None
