from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from db.db import get_db
from app.dependencies.get_user import get_current_user
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_user(user_create: UserCreate,
                db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    """Create a new user."""
    user_service = UserService(db)
    return user_service.create_user(user_create, current_user)


@router.get("/{email}", response_model=UserRead)
def get_user_by_email(email: str,
                      db: Session = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    """Retrieve a user by their email."""
    user_service = UserService(db)
    return user_service.get_user_by_email(email, current_user)


@router.patch("/{user_id}", response_model=UserRead)
def deactivate_user(user: str,
                    db: Session = Depends(get_db),
                    user_id: str = Path(..., description="ID del usuario a desactivar"),
                    current_user: dict = Depends(get_current_user)):
    """Deactivate a user by their ID."""
    user_service = UserService(db)
    return user_service.deactivate_user(user_id, current_user)


@router.get("/", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db),
               current_user: dict = Depends(get_current_user)):
    """List all users."""
    user_service = UserService(db)
    return user_service.list_users(current_user)
