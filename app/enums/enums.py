from enum import Enum

class RoleEnum(str, Enum):
    support = "support"
    manager = "manager"
    admin = "admin"


class TicketStatusEnum(Enum):
    new = "new"
    triaging = "triaging"
    in_progress = "in_progress"
    in_review = "in_review"
    done = "done"
    closed = "closed"


class JobStatusEnum(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
