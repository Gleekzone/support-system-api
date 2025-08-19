from uuid import UUID
import uuid
from typing import List, Optional
import json, aioboto3
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from common.models.ticket import Ticket, TicketImportJob
from app.schemas.ticket import TicketCreate, TicketUpdateStatus, TicketAssignUser, TicketRead
from common.config  import S3_BUCKET_NAME, SQS_QUEUE_URL
from app.dependencies.auth import check_user_roles


class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.s3_session = aioboto3.Session()
    
    def create_ticket(self, ticket_create: TicketCreate) -> TicketRead:
        """Create a new ticket."""
        ticket = Ticket(**ticket_create.model_dump())
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return TicketRead.model_validate(ticket)
    
    def get_ticket(self, ticket_id: UUID) -> TicketRead:
        """Retrieve a ticket by its ID."""
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        return TicketRead.model_validate(ticket)
    
    def update_ticket(self, current_user: dict, ticket_id: UUID, status: TicketUpdateStatus) -> TicketRead:
        """Update the status of a ticket."""
        allowed_groups = ["support", "manager"]
        check_user_roles(current_user, allowed_groups)
        ticket = self.get_ticket(ticket_id)

        # Check if the ticket is assigned to a user
        if ticket.assigned_to_id is None:
            raise HTTPException(
                status_code=403,
                detail="Ticket not assigned to any user"
            )
        
        # Ensure the user is assigned to the ticket before updating
        user_id = current_user["sub"]
        if ticket.assigned_to_id != user_id:
            raise HTTPException(status_code=403, detail="User not assigned to this ticket")

        # Update the ticket status
        ticket.status = status.status

        self.db.commit()
        self.db.refresh(ticket)
        return TicketRead.model_validate(ticket)
    
    def assign_ticket(self, current_user: dict, ticket_id: UUID, assigned_to_id: TicketAssignUser) -> TicketRead:
        """Assign a ticket to a user."""
        # Check if the user is authorized to assign tickets
        allowed_groups = ["admin", "manager"]
        check_user_roles(current_user, allowed_groups)
        
        ticket = self.get_ticket(ticket_id)
        ticket.assigned_to_id = assigned_to_id.assigned_to_id
        self.db.commit()
        self.db.refresh(ticket)
        return TicketRead.model_validate(ticket)
    
    def list_tickets(self, current_user: dict, assigned_to_id: Optional[UUID] = None, status: Optional[str] = None) -> List[TicketRead]:
        """List tickets with optional filters for assigned user and status."""
        # Check if the user is authorized to view tickets
        allowed_groups = ["admin", "support", "manager"]
        check_user_roles(current_user, allowed_groups)

        query = self.db.query(Ticket)
        # Apply filters if provided
        if assigned_to_id:
            query = query.filter(Ticket.assigned_to_id == assigned_to_id)
        if status:
            query = query.filter(Ticket.status == status)
        tickets = query.all()
        return [TicketRead.model_validate(ticket) for ticket in tickets]

    async def create_bulk_ticket_job(self, current_user: dict, tickets_json: List[TicketCreate]) -> dict:
        """Create multiple tickets in bulk."""
        # Validate if the user is authorized to create bulk tickets
        allowed_groups = ["manager"]
        check_user_roles(current_user, allowed_groups)
        try:
            job = TicketImportJob(
            created_by=current_user["sub"],
            s3_url="",
            status="PENDING"
            )
            self.db.add(job)
            await self.db.commit()
            await self.db.refresh(job)

            # Upload tickets to S3
            s3_key = f"tickets/{uuid.uuid4()}.json"
            s3_url = f"s3://{S3_BUCKET_NAME}/{s3_key}"
            async with self.s3_session.client('s3') as s3_client:
                await s3_client.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=s3_key,
                    Body=json.dumps([ticket.dict() for ticket in tickets_json]),
                    ContentType="application/json"
                )
            # Update the job with the S3 URL
            job.s3_url = s3_url
            await self.db.commit()

            # Send a message to SQS to process the job
            async with self.s3_session.client('sqs') as sqs:
                await sqs.send_message(
                    QueueUrl=SQS_QUEUE_URL,
                    MessageBody=json.dumps({
                    "job_id": job.id,
                    "s3_url": s3_url
                    }))
            return {"job_id": job.id, "status": "queued", "s3_url": s3_url}
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating bulk ticket job: {str(e)}"
            )
