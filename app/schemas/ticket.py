from pydantic import BaseModel, Field, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from app.schemas.comment import CommentRead
from app.enums.enums import TicketStatusEnum


class TicketCreate(BaseModel):
    reporter_name: str = Field(..., min_length=1, max_length=100)
    reporter_email: EmailStr
    description: str = Field(..., min_length=1, max_length=500)


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reporter_name: str
    reporter_email: EmailStr
    description: str
    status: TicketStatusEnum
    created_at: datetime
    updated_at: datetime
    assigned_to_id: Optional[UUID] = None
    comments: List[CommentRead] = Field(default_factory=list)


class TicketUpdateStatus(BaseModel):
    status: TicketStatusEnum


class TicketAssignUser(BaseModel):
    assigned_to_id: UUID


class TicketBulkResponse(BaseModel):
    msg: str
    job_id: UUID
    s3_url: str
