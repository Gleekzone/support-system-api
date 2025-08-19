from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from common.enums import RoleEnum


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: RoleEnum = RoleEnum.support


class UserCreate(UserBase):
    password: str # Temporal for cognito user creation


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    deactivated_at: Optional[datetime] = None
