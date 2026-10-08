"""MongoDB database connection and operations."""
import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv

load_dotenv()


class MongoDB:
    """Handles MongoDB connection and provides database access."""

    def __init__(self):
        self.client = None
        self.db = None
        self.connection_string = os.getenv("MONGO_CONNECTION_STRING")
        self.database_name = os.getenv("DATABASE_NAME", "todo_db")

        if not self.connection_string:
            raise ValueError(
                "MONGO_CONNECTION_STRING environment variable is not set. "
                "Please check your .env file."
            )

    def connect(self):
        """Establish connection to MongoDB Atlas."""
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            # Verify connection
            self.client.admin.command("ping")
            self.db = self.client[self.database_name]
            print(f"[OK] Connected to MongoDB Atlas - Database: {self.database_name}")
            return self.db
        except ConnectionFailure:
            raise ConnectionError(
                "[ERROR] Could not connect to MongoDB Atlas. "
                "Please check your connection string and network."
            )
        except Exception as e:
            raise ConnectionError(f"[ERROR] MongoDB connection error: {str(e)}")

    def get_collection(self, collection_name):
        """Get a MongoDB collection."""
        if self.db is None:
            self.connect()
        return self.db[collection_name]

    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            print("[INFO] MongoDB connection closed")


# Singleton instance
mongodb = MongoDB()


def get_db():
    """Get database instance, connecting if necessary."""
    if mongodb.db is None:
        mongodb.connect()
    return mongodb.db


def get_tasks_collection():
    """Get the tasks collection."""
    return get_db()["tasks"]


def get_pages_collection():
    """Get the pages collection."""
    return get_db()["pages"]
