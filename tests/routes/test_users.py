import pytest
from unittest.mock import MagicMock, patch
from app.main import app
from app.dependencies.get_user import get_current_user
from app.services.cognito_service import CognitoService


@pytest.fixture
def user_payload():
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepassword"
    }


def test_create_user_endpoint_success(client, mock_current_user_manager, user_payload):
    app.dependency_overrides[get_current_user] = lambda: mock_current_user_manager
     # Create a mock for CognitoService
    mock_cognito = MagicMock()
    mock_cognito.create_user.return_value = {"Username": "user@example.com"}

    # Patch the CognitoService dependency
    with patch("app.services.user_service.CognitoService", return_value=mock_cognito):
        response = client.post("/users", json={"user_create": user_payload})
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"
    # Clear overrides after test
    app.dependency_overrides = {}


def test_create_user_endpoint_unauthorized(client, user_payload):
    app.dependency_overrides[get_current_user] = lambda: {"groups": ["support"]}
    response = client.post("/users", json={"user_create": user_payload})
    assert response.status_code == 403


def test_create_invalid_email_user(client, mock_current_user_manager, user_payload):
    user_payload["email"] = "invalid-email"
    app.dependency_overrides[get_current_user] = lambda: mock_current_user_manager
    response = client.post("/users", json={"user_create": user_payload})
    assert response.status_code == 422


def test_get_user_by_email(client, mock_current_user_manager, user_payload):
    app.dependency_overrides[get_current_user] = lambda: mock_current_user_manager
     # Create a mock for CognitoService
    mock_cognito = MagicMock()
    mock_cognito.create_user.return_value = {"Username": "user@example.com"}

    # Patch the CognitoService dependency
    with patch("app.services.user_service.CognitoService", return_value=mock_cognito):
        response = client.post("/users", json={"user_create": user_payload})
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"

        # Get the email of the created user
        user_email = response.json()["email"]
        response = client.get(f"/users/{user_email}")
        assert response.status_code == 200
        assert response.json()["email"] == user_email
    # Clear overrides after test
    app.dependency_overrides = {}


def test_get_user_by_email_unauthorized(client, user_payload):
    app.dependency_overrides[get_current_user] = lambda: {"groups": ["support"]}
    user_email = "test@example.com"
    response = client.get(f"/users/{user_email}")
    assert response.status_code == 403   
