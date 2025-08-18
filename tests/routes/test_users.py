import pytest
from app.main import app
from unittest.mock import MagicMock
from app.dependencies.get_user import get_current_user

mock_cognito = MagicMock()

class UserNotFoundException(Exception):
    pass

mock_cognito.exceptions.UserNotFoundException = UserNotFoundException
mock_cognito.admin_get_user.side_effect = UserNotFoundException()

def test_create_user_endpoint_success(client, mock_current_user_manager):
    app.dependency_overrides[get_current_user] = lambda: mock_current_user_manager
    response = client.post("/users", json={"user_create": {
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepassword"
    }})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    # Clear overrides after test
    app.dependency_overrides = {}
