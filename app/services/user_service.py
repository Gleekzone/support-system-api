from uuid import UUID
from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from db.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.cognito_service import CognitoService


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.cognito = CognitoService()


    def create_user(self, user_create: UserCreate, current_user: dict) -> UserRead:
        """Create a new user in the system."""
        # Check if the user is authorized to create users
        allowed_groups = ["admin", "manager"]
        user_groups = current_user.get("cognito:groups", [])
        if not any(g in allowed_groups for g in user_groups):
            raise HTTPException(status_code=403, detail="User not authorized")
        
        # Validations before creating the user
        if not user_create.email or "@" not in user_create.email:
            raise HTTPException(status_code=400, detail="Invalid email")
        if len(user_create.password) < 8:
            raise HTTPException(status_code=400, detail="Password too short")
        if not user_create.name:
            raise HTTPException(status_code=400, detail="Name is required")
        # Check if the user already exists
        try:
            self.cognito.admin_get_user(UserPoolId="tu_user_pool_id", Username=user_create.email)
            raise HTTPException(status_code=400, detail="User already exists")
        except self.cognito.exceptions.UserNotFoundException:
            cognito_sub = self.cognito.create_user(
                name=user_create.name,
                email=user_create.email,
                password=user_create.password
            )

            user = User(
                cognito_sub=cognito_sub,
                name=user_create.name,
                email=user_create.email,
                role=user_create.role
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return UserRead.model_validate(user)
    

    def get_user_by_email(self, email: str, current_user: dict) -> UserRead:
        """Retrieve a user by their email."""
        # Check if the user is authorized to view users
        allowed_groups = ["admin", "manager"]
        user_groups = current_user.get("cognito:groups", [])
        if not any(g in allowed_groups for g in user_groups):
            raise HTTPException(status_code=403, detail="User not authorized")
        
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserRead.model_validate(user)


    def list_users(self, current_user: dict) -> List[UserRead]:
        """List all users in the system."""
        # Check if the user is authorized to view users
        allowed_groups = ["admin", "manager"]
        user_groups = current_user.get("cognito:groups", [])
        if not any(g in allowed_groups for g in user_groups):
            raise HTTPException(status_code=403, detail="User not authorized")
        
        users = self.db.query(User).all()
        return [UserRead.model_validate(user) for user in users]


    def deactivate_user(self, user_id: UUID, current_user: dict) -> UserRead:
        """Deactivate a user in the system."""
        # Check if the user is authorized to deactivate users
        allowed_groups = ["admin", "manager"]
        user_groups = current_user.get("cognito:groups", [])
        if not any(g in allowed_groups for g in user_groups):
            raise HTTPException(status_code=403, detail="User not authorized")
        
        # Get the user from the database
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # deactivate in cognito
        self.cognito.deactivate_user(user.cognito_sub)
        # deactivate in db
        user.deactivated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return UserRead.model_validate(user)
