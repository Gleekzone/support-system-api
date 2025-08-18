from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from db.db import get_db
from app.dependencies.get_user import get_current_user
from app.services.comment_service import CommentService
from app.schemas.comment import CommentCreate, CommentRead

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=CommentRead)
def create_comment(comment_create: CommentCreate,
                   db: Session = Depends(get_db),
                   current_user: dict = Depends(get_current_user)):
    """Create a new comment."""
    comment_service = CommentService(db)
    return comment_service.create_comment(comment_create)


@router.get("/ticket/{ticket_id}", response_model=list[CommentRead])
def list_comments_for_ticket(ticket_id: str,
                             db: Session = Depends(get_db),
                             current_user: dict = Depends(get_current_user)):
    """List all comments for a specific ticket."""
    comment_service = CommentService(db)
    return comment_service.list_comments_for_ticket(ticket_id)
