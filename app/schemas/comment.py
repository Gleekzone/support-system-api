from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CommentCreate(BaseModel):
    ticket_id: UUID
    content: str
    user_id: UUID


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    ticket_id: UUID
    content: str
    created_at: datetime
