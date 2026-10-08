"""FastAPI main application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.mongodb import mongodb
from routes import tasks, pages, ai, auth
from app.api.routes import ai as ai_chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup: connect to MongoDB
    try:
        mongodb.connect()
    except Exception as e:
        print(f"[WARNING] Could not connect to MongoDB: {e}")
        print("   The application will start but database operations will fail.")
        print("   Please check your MONGO_CONNECTION_STRING in .env")
    yield
    # Shutdown: close MongoDB connection
    mongodb.close()


app = FastAPI(
    title="Todo App API",
    description="A full-stack Todo List application with AI-powered task suggestions",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration - allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(pages.router)
app.include_router(ai.router)
app.include_router(ai_chat.router)


@app.get("/")
def root():
    """Root endpoint - API info."""
    return {
        "message": "Todo App API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "tasks": "/tasks",
            "pages": "/pages",
            "ai": "/ai",
        },
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
