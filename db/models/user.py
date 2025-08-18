from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.db import Base
from app.schemas.user import RoleEnum


class User(Base):
    """Model for users in the system."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    cognito_sub = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    deactivated_at = Column(DateTime(timezone=True), default=None, nullable=True)

    tickets = relationship("Ticket", back_populates="assigned_user")
