# tests/conftest.py
import pytest
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from app.main import app
from app.enums.enums import RoleEnum
from db.db import get_db
from db.models.user import User
from app.enums.enums import TicketStatusEnum


@pytest.fixture
def client(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_db_session(monkeypatch):
    session = MagicMock()
    tickets_store = []

    def add_ticket(ticket):
        if not getattr(ticket, "id", None):
            ticket.id = uuid4()
        ticket.created_at = datetime.now(timezone.utc)
        ticket.updated_at = datetime.now(timezone.utc)
        if not getattr(ticket, "status", None):
            ticket.status = TicketStatusEnum.new
        tickets_store.append(ticket)

    session.add.side_effect = add_ticket
    session.commit.return_value = None
    session.refresh.side_effect = lambda ticket: None
    session.query.return_value.all.side_effect = lambda: tickets_store.copy()
    session.query.return_value.filter.return_value.first.side_effect = lambda *args, **kwargs: tickets_store[0] if tickets_store else None
    session._tickets_store = tickets_store

    # Patch get_db para usar esta sesión mock
    monkeypatch.setattr("app.dependencies.db.get_db", lambda: session)

    yield session


# Fixtures for different user roles
@pytest.fixture
def customer_user():
    """Returns a user with a 'user' role."""
    return User(
        id=uuid4(),
        name="John Doe",
        email="john@example.com",
        role=RoleEnum.user
    )

@pytest.fixture
def support_user():
    """Returns a user with a 'support' role."""
    return User(
        id=uuid4(),
        name="Support Agent",
        email="support@example.com",
        role=RoleEnum.support
    )

@pytest.fixture
def manager_user():
    """Returns a user with a 'manager' role."""
    return User(
        id=uuid4(),
        name="Manager",
        email="manager@example.com",
        role=RoleEnum.manager
    )

@pytest.fixture
def admin_user():
    """Returns a user with an 'admin' role."""
    return User(
        id=uuid4(),
        name="Admin",
        email="admin@example.com",
        role=RoleEnum.admin
    )

@pytest.fixture
def mock_current_user_admin():
    return {"username": "admin_user", "cognito:groups": ["admin"]}

@pytest.fixture
def mock_current_user_support():
    return {"sub": "test-support-456", "username": "support_user", "cognito:groups": ["support"]}

@pytest.fixture
def mock_current_user_manager():
    return {"sub": "test-manager-345", "username": "manager_user", "cognito:groups": ["manager"]}

@pytest.fixture
def mock_current_user_guest():
    return {"username": "guest_user", "cognito:groups": ["guest"]}

@pytest.fixture
def mock_current_user_unauthenticated():
    def _mock():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return _mock
