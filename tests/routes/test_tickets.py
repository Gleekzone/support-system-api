import pytest
from uuid import UUID
from app.schemas.ticket import TicketRead
from common.enums import TicketStatusEnum
from unittest.mock import patch
from app.dependencies.get_user import get_current_user
from app.main import app


@pytest.fixture
def ticket_payload(support_user, request):
    """Returns a reusable base payload for creating tickets."""
    desc = getattr(request, "param", "Test ticket")

    return {
        "reporter_name": "Alice",
        "reporter_email": "alice@example.com",
        "description": desc
    }


def test_create_ticket_as_customer(client, ticket_payload):
    response = client.post("/tickets/", json=ticket_payload)
    assert response.status_code == 200

    ticket = TicketRead.model_validate(response.json()).model_dump()

    assert ticket["reporter_name"] == "Alice"
    assert ticket["status"] == TicketStatusEnum.new
    assert "id" in ticket


def test_create_ticket_as_admin(client, admin_user, ticket_payload):
    response = client.post("/tickets/", json=ticket_payload, headers={
        "user_id": str(admin_user.id),
        "user_groups": "admin"
    })
    assert response.status_code == 200
    ticket = TicketRead.model_validate(response.json()).model_dump()
    assert ticket["reporter_name"] == "Alice"


def test_create_ticket_as_support(client, support_user, ticket_payload):
    response = client.post("/tickets/", json=ticket_payload, headers={
        "user_id": str(support_user.id),
        "user_groups": "support"
    })
    assert response.status_code == 200
    ticket = TicketRead.model_validate(response.json()).model_dump()
    assert ticket["reporter_name"] == "Alice"


@pytest.mark.parametrize("ticket_payload", [""], indirect=True)
def test_create_ticket_empty_description(client, ticket_payload):
    response = client.post("/tickets", json=ticket_payload)
    assert response.status_code == 422


def test_create_ticket_invalid_email(client, ticket_payload):
    ticket_payload["reporter_email"] = "invalid-email"
    response = client.post("/tickets", json=ticket_payload)
    assert response.status_code == 422


def test_create_ticket_missing_fields(client):
    response = client.post("/tickets", json={})
    assert response.status_code == 422

# Test cases for retrieving tickets

def test_get_ticket(client, ticket_payload):
    # First, create a ticket
    response = client.post("/tickets/", json=ticket_payload)
    assert response.status_code == 200
    ticket = TicketRead.model_validate(response.json())

    # Now retrieve the ticket by ID
    response = client.get(f"/tickets/{ticket.id}")
    assert response.status_code == 200

    retrieved_ticket = TicketRead.model_validate(response.json())
    assert retrieved_ticket.reporter_name == "Alice"
    assert retrieved_ticket.status == TicketStatusEnum.new
    assert retrieved_ticket.reporter_email == "alice@example.com"


def test_get_nonexistent_ticket(client):
    # Attempt to retrieve a ticket that does not exist
    response = client.get("/tickets/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket not found"}


def test_list_tickets(client, ticket_payload, mock_current_user_admin):
    
    app.dependency_overrides[get_current_user] = lambda: mock_current_user_admin
    # Create a couple of tickets
    response = client.post("/tickets/", json=ticket_payload)
    assert response.status_code == 200

    payload2 = {
        "reporter_name": "Bob",
        "reporter_email": "bob@example.com",
        "description": "Ticket 2"
    }
    response = client.post("/tickets/", json=payload2)
    assert response.status_code == 200

    # Now list all tickets
    response = client.get("/tickets/")
    assert response.status_code == 200

    tickets = response.json()
    assert isinstance(tickets, list)
    assert len(tickets) >= 2  # At least two tickets should be returned
    for ticket in tickets:
        assert "id" in ticket
        assert "reporter_name" in ticket
        assert "status" in ticket
    app.dependency_overrides = {}


def test_list_tickets_as_guest_forbidden(client, mock_current_user_guest):
    app.dependency_overrides[get_current_user] = lambda: mock_current_user_guest

    response = client.get("/tickets/")
    assert response.status_code == 403

    app.dependency_overrides = {}


def test_list_tickets_unauthenticated(client, mock_current_user_unauthenticated):
    # Replace the dependency with a mock that raises an exception
    app.dependency_overrides[get_current_user] = mock_current_user_unauthenticated

    response = client.get("/tickets/")  
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

    # clear the overrides to avoid affecting other tests
    app.dependency_overrides = {}


def test_cannot_update_unassigned_ticket(client, ticket_payload, mock_current_user_support):
    # Replace the dependency with a mock that raises an exception
    app.dependency_overrides[get_current_user] = lambda: mock_current_user_support

     # First, create a ticket
    response = client.post("/tickets/", json=ticket_payload)
    assert response.status_code == 200
    ticket = TicketRead.model_validate(response.json())
    assert ticket.status == TicketStatusEnum.new
    # Now retrieve the ticket by ID
    response = client.patch(f"/tickets/{ticket.id}/status", json={"status": {"status": "in_progress"}})
    assert response.status_code == 403  # Forbidden
    assert response.json()["detail"] == "Ticket not assigned to any user"

    # clear the overrides to avoid affecting other tests
    app.dependency_overrides = {}


def test_update_ticket_status_as_support(client, ticket_payload, mock_current_user_support, mock_current_user_manager):
    # Step 1: Create a ticket
    app.dependency_overrides[get_current_user] = lambda: mock_current_user_support
    response = client.post("/tickets/", json=ticket_payload)
    ticket = TicketRead.model_validate(response.json())

    # Step 2: Assign the ticket to the support user as a manager
    app.dependency_overrides[get_current_user] = lambda: mock_current_user_manager
    assigned_user_id = 'd6baa7e0-32f1-4881-a790-8a9d4564d099'
    response = client.patch(f"/tickets/{ticket.id}/assign", json={"assigned_to_id": {"assigned_to_id": assigned_user_id}})
    ticket = TicketRead.model_validate(response.json())

    assert response.status_code == 200
    assert ticket.assigned_to_id == UUID("d6baa7e0-32f1-4881-a790-8a9d4564d099")

    # Step 3: Assign the ticket to the support user as a support agent
    app.dependency_overrides[get_current_user] = lambda: mock_current_user_support
    response = client.patch(f"/tickets/{ticket.id}/assign", json={"assigned_to_id": {"assigned_to_id": assigned_user_id}})
    assert response.status_code == 403

    app.dependency_overrides = {}


@pytest.mark.asyncio
@pytest.mark.skip(reason="Skipping async test temporarily")
@patch("app.services.ticket_service.aioboto3.Session.client")
def test_create_bulk_ticket_job(mock_s3_client, client, mock_current_user_manager, ticket_payload):
    app.dependency_overrides[get_current_user] = lambda: mock_current_user_manager

    ticket_payload = [
    {"reporter_name": "Alice", "reporter_email": "alice@example.com", "description": "Ticket 1"},
    {"reporter_name": "Bob", "reporter_email": "bob@example.com", "description": "Ticket 2"}]

    response = client.post("/tickets/bulk", json={"tickets_create": ticket_payload})
    assert response.status_code == 200

    # Clear overrides after test
    app.dependency_overrides = {}
