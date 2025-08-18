from typing import Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query
from db.db import get_db
from app.dependencies.get_user import get_current_user
from app.services.ticket_service import TicketService
from app.schemas.ticket import TicketCreate, TicketRead, TicketUpdateStatus, TicketAssignUser, TicketBulkResponse

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/", response_model=TicketRead)
def create_ticket(ticket_create: TicketCreate, db: Session = Depends(get_db)):
    """Create a new ticket."""
    ticket_service = TicketService(db)
    return ticket_service.create_ticket(ticket_create)


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Retrieve a ticket by its ID."""
    ticket_service = TicketService(db)
    return ticket_service.get_ticket(ticket_id)


@router.get("/", response_model=list[TicketRead])
def list_tickets(assigned_to_id: Optional[str] = Query(None, description="Filter by assigned user ID"),
                 status: Optional[str] = Query(None, description="Filter by ticket status"),
                 db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    """List all tickets."""
    ticket_service = TicketService(db)
    return ticket_service.list_tickets(current_user, assigned_to_id, status)


@router.patch("/{ticket_id}/status", response_model=TicketRead)
def update_ticket_status(ticket_id: str, status: TicketUpdateStatus,
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    """Update the status of a ticket."""
    ticket_service = TicketService(db)
    return ticket_service.update_ticket(current_user, ticket_id, status)


@router.patch("/{ticket_id}/assign", response_model=TicketRead)
def assing_ticket(ticket_id: str, assigned_to_id: TicketAssignUser,
                  db: Session = Depends(get_db),
                  current_user: dict = Depends(get_current_user)):
    """Assign a ticket to a user."""
    ticket_service = TicketService(db)
    return ticket_service.assign_ticket(current_user, ticket_id, assigned_to_id)


@router.post("/bulk", response_model=TicketBulkResponse)
def bulk_create_tickets(tickets_create: list[TicketCreate],
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    """Bulk create tickets."""
    ticket_service = TicketService(db)
    return ticket_service.create_bulk_ticket_job(current_user, tickets_create)
