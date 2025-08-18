from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from common.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentRead


class CommentService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_comment(self, comment_create: CommentCreate) -> CommentRead:
        """Create a new comment for a ticket."""
        comment = Comment(**comment_create.model_dump())
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return CommentRead.model_validate(comment)
    
    def get_comment(self, ticket_id: UUID) -> CommentRead:
        """Retrieve a comment by ticket ID."""
        comment = self.db.query(Comment).filter(Comment.ticket_id == ticket_id).first()
        if not comment:
            raise ValueError('Ticket not found')
        return CommentRead.model_validate(comment)

    def get_comments_by_ticket(self, ticket_id: UUID) -> List[CommentRead]:
        """Retrieve all comments for a specific ticket."""
        comments = self.db.query(Comment).filter(Comment.ticket_id == ticket_id).all()
        return [CommentRead.model_validate(comment) for comment in comments]
