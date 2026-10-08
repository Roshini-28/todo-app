"""Authentication API routes."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import UserCreate, UserLogin, UserResponse, TokenResponse
from services import user_service, auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.get("/users", response_model=list[UserResponse])
def get_all_users(current_user: dict = Depends(security)):
    """Get all users (for task assignment)."""
    from database.mongodb import get_db
    users = get_db()["users"].find()
    return [
        {
            "id": str(user["_id"]),
            "username": user["username"],
            "created_at": user["created_at"],
        }
        for user in users
    ]


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate):
    """Register a new user."""
    user, error = user_service.create_user(user_data.username, user_data.password)
    if error:
        raise HTTPException(status_code=409, detail=error)
    return user


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin):
    """Login and get access token."""
    user = user_service.authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = auth_service.create_access_token(user["id"], user["username"])
    return TokenResponse(access_token=token, user=user)


@router.get("/me", response_model=UserResponse)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current logged-in user."""
    token = credentials.credentials
    payload = auth_service.verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = user_service.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
