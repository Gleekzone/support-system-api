import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum,  ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.dependencies.db import Base
from app.enums import enums


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    reporter_name = Column(String(100), nullable=False)
    reporter_email = Column(String(320), nullable=False)
    description = Column(String(500), nullable=False)
    status = Column(Enum(enums.TicketStatusEnum), default=enums.TicketStatusEnum.new, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                    onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)

    assigned_user = relationship('User', back_populates='tickets')
    comments = relationship('Comment', back_populates='tickets', cascade='all, delete-orphan')


class TicketImportJob(Base):
    __tablename__ = "ticket_import_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    s3_url = Column(String, nullable=False)
    status = Column(Enum(enums.JobStatusEnum), default=enums.JobStatusEnum.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                    onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    processed_at = Column(DateTime(timezone=True), default=None, nullable=True)
