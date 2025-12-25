# test_app.py
import pytest
import requests
import json
from unittest.mock import patch, Mock

# Define the base URL for the API as per spec
API_BASE_URL = "http://localhost:3000/api/v1"

# --- Helper functions for mocking responses ---
def mock_response(status_code, json_data=None, headers=None):
    mock = Mock()
    mock.status_code = status_code
    mock.json.return_value = json_data if json_data is not None else {}
    mock.headers = headers if headers is not None else {}
    mock.raise_for_status.side_effect = (
        requests.exceptions.HTTPError(f"HTTP Error: {status_code}")
        if status_code >= 400
        else None
    )
    return mock

# --- Pytest Fixtures (for shared setup) ---
@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer fake_jwt_token"}

# --- Test Cases for API Endpoints ---

@patch('requests.post')
def test_user_sign_up(mock_post):
    """
    Test user registration API endpoint.
    POST /api/v1/auth/sign_up
    """
    expected_user = {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User",
        "points": 0,
        "family_id": None,
    }
    expected_token = "mock_jwt_token_signup"
    mock_post.return_value = mock_response(
        201, {"user": expected_user, "token": expected_token}
    )

    data = {
        "user": {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "password_confirmation": "password123",
        }
    }
    response = requests.post(f"{API_BASE_URL}/auth/sign_up", json=data)

    # When `json=data` is used, requests automatically sets Content-Type header.
    # We should not explicitly add it to the headers dict in assert_called_once_with.
    mock_post.assert_called_once_with(
        f"{API_BASE_URL}/auth/sign_up",
        json=data,
        # headers={'Content-Type': 'application/json'} # Removed this line
    )
    assert response.status_code == 201
    assert response.json()["user"] == expected_user
    assert response.json()["token"] == expected_token

@patch('requests.post')
def test_user_sign_in(mock_post):
    """
    Test user login API endpoint.
    POST /api/v1/auth/sign_in
    """
    expected_user = {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User",
        "points": 100,
        "family_id": 10,
    }
    expected_token = "mock_jwt_token_signin"
    mock_post.return_value = mock_response(
        200, {"user": expected_user, "token": expected_token}
    )

    data = {"user": {"email": "test@example.com", "password": "password123"}}
    response = requests.post(f"{API_BASE_URL}/auth/sign_in", json=data)

    # When `json=data` is used, requests automatically sets Content-Type header.
    mock_post.assert_called_once_with(
        f"{API_BASE_URL}/auth/sign_in",
        json=data,
        # headers={'Content-Type': 'application/json'} # Removed this line
    )
    assert response.status_code == 200
    assert response.json()["user"] == expected_user
    assert response.json()["token"] == expected_token

@patch('requests.delete')
def test_user_sign_out(mock_delete, auth_headers):
    """
    Test user logout API endpoint.
    DELETE /api/v1/auth/sign_out
    """
    mock_delete.return_value = mock_response(204) # No Content

    response = requests.delete(f"{API_BASE_URL}/auth/sign_out", headers=auth_headers)

    # requests.delete without `json` or `data` does NOT automatically add Content-Type.
    mock_delete.assert_called_once_with(
        f"{API_BASE_URL}/auth/sign_out",
        headers=auth_headers # Removed explicit Content-Type
    )
    assert response.status_code == 204

@patch('requests.get')
def test_get_current_user(mock_get, auth_headers):
    """
    Test getting current user details.
    GET /api/v1/auth/me
    """
    expected_user = {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User",
        "points": 100,
        "family_id": 10,
    }
    mock_get.return_value = mock_response(200, expected_user)

    response = requests.get(f"{API_BASE_URL}/auth/me", headers=auth_headers)

    # requests.get does NOT automatically add Content-Type.
    mock_get.assert_called_once_with(
        f"{API_BASE_URL}/auth/me",
        headers=auth_headers # Removed explicit Content-Type
    )
    assert response.status_code == 200
    assert response.json() == expected_user

@patch('requests.post')
def test_create_family(mock_post, auth_headers):
    """
    Test creating a new family.
    POST /api/v1/families
    """
    expected_family = {
        "id": 1,
        "name": "Test Family",
        "join_code": "FAMILY123",
        "users": [],
    }
    mock_post.return_value = mock_response(201, expected_family)

    data = {"family": {"name": "Test Family"}}
    response = requests.post(f"{API_BASE_URL}/families", json=data, headers=auth_headers)

    # When `json=data` is used, requests automatically sets Content-Type.
    # The `headers` argument here should only contain the explicitly passed headers.
    mock_post.assert_called_once_with(
        f"{API_BASE_URL}/families",
        json=data,
        headers=auth_headers # Removed explicit Content-Type
    )
    assert response.status_code == 201
    assert response.json() == expected_family

@patch('requests.post')
def test_join_family(mock_post, auth_headers):
    """
    Test joining an existing family.
    POST /api/v1/families/join
    """
    expected_family = {
        "id": 1,
        "name": "Test Family",
        "join_code": "FAMILY123",
        "users": [{"id": 1, "name": "Test User", "email": "test@example.com", "points": 100}],
    }
    mock_post.return_value = mock_response(200, expected_family)

    data = {"join_code": "FAMILY123"}
    response = requests.post(f"{API_BASE_URL}/families/join", json=data, headers=auth_headers)

    # When `json=data` is used, requests automatically sets Content-Type.
    mock_post.assert_called_once_with(
        f"{API_BASE_URL}/families/join",
        json=data,
        headers=auth_headers # Removed explicit Content-Type
    )
    assert response.status_code == 200
    assert response.json() == expected_family

@patch('requests.get')
def test_get_my_family(mock_get, auth_headers):
    """
    Test getting details of the current user's family.
    GET /api/v1/families/my_family
    """
    expected_family = {
        "id": 1,
        "name": "Test Family",
        "join_code": "FAMILY123",
        "users": [
            {"id": 1, "name": "Test User", "email": "test@example.com", "points": 100},
            {"id": 2, "name": "Member 2", "email": "member2@example.com", "points": 50},
        ],
    }
    mock_get.return_value = mock_response(200, expected_family)

    response = requests.get(f"{API_BASE_URL}/families/my_family", headers=auth_headers)

    # requests.get does NOT automatically add Content-Type.
    mock_get.assert_called_once_with(
        f"{API_BASE_URL}/families/my_family",
        headers=auth_headers # Removed explicit Content-Type
    )
    assert response.status_code == 200
    assert response.json() == expected_family

@patch('requests.post')
def test_create_chore(mock_post, auth_headers):
    """
    Test creating a new chore.
    POST /api/v1/chores
    """
    expected_chore = {
        "id": 1,
        "name": "Wash Dishes",
        "description": "Wash all dishes in the sink",
        "points": 10,
        "frequency": "daily",
        "assigned_to_user_id": None,
        "last_completed_at": None,
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T10:00:00Z",
        "family_id": 1,
    }
    mock_post.return_value = mock_response(201, expected_chore)

    data = {
        "chore": {
            "name": "Wash Dishes",
            "description": "Wash all dishes in the sink",
            "points": 10,
            "frequency": "daily",
        }
    }
    response = requests.post(f"{API_BASE_URL}/chores", json=data, headers=auth_headers)

    # When `json=data` is used, requests automatically sets Content-Type.
    mock_post.assert_called_once_with(
        f"{API_BASE_URL}/chores",
        json=data,
        headers=auth_headers # Removed explicit Content-Type
    )
    assert response.status_code == 201
    assert response.json() == expected_chore

@patch('requests.put')
def test_update_chore(mock_put, auth_headers):
    """
    Test updating an existing chore.
    PUT /api/v1/chores/:id
    """
    chore_id = 1
    updated_chore = {
        "id": chore_id,
        "name": "Wash Dishes (Evening)",
        "description": "Wash all dishes in the sink after dinner",
        "points": 12,
        "frequency": "daily",
        "assigned_to_user_id": None,
        "last_completed_at": None,
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T11:00:00Z",
        "family_id": 1,
    }
    mock_put.return_value = mock_response(200, updated_chore)

    data = {
        "chore": {
            "name": "Wash Dishes (Evening)",
            "description": "Wash all dishes in the sink after dinner",
            "points": 12,
        }
    }
    response = requests.put(f"{API_BASE_URL}/chores/{chore_id}", json=data, headers=auth_headers)

    # When `json=data` is used, requests automatically sets Content-Type.
    mock_put.assert_called_once_with(
        f"{API_BASE_URL}/chores/{chore_id}",
        json=data,
        headers=auth_headers # Removed explicit Content-Type
    )
    assert response.status_code == 200
    assert response.json() == updated_chore

@patch('requests.delete')
def test_delete_chore(mock_delete, auth_headers):
    """
    Test deleting a chore.
    DELETE /api/v1/chores/:id
    """
    chore_id = 1
    mock_delete.return_value = mock_response(204)

    response = requests.delete(f"{API_BASE_URL}/chores/{chore_id}", headers=auth_headers)

    # requests.delete without `json` or `data` does NOT automatically add Content-Type.
    mock_delete.assert_called_once_with(
        f"{API_BASE_URL}/chores/{chore_id}",
        headers=auth_headers # Removed explicit Content-Type
    )
    assert response.status_code == 204

@patch('requests.post')
def test_assign_chore(mock_post, auth_headers):
    """
    Test assigning a chore to a user.
    POST /api/v1/chores/:id/assign
    """
    chore_id = 2
    assigned_user_id = 1
    assigned_chore = {
        "id": chore_id,
        "name": "Take out trash",
        "description": "Empty all trash bins",
        "points": 5,
        "frequency": "weekly",
        "assigned_to_user_id": assigned_user_id,
        "last_completed_at": None,
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T10:30:00Z",
        "family_id": 1,
    }
    mock_post.return_value = mock_response(200, assigned_chore)

    data = {"user_id": assigned_user_id}
    response = requests.post(f"{API_BASE_URL}/chores/{chore_id}/assign", json=data, headers=auth_headers)

    # When `json=data` is used, requests automatically sets Content-Type.
    mock_post.assert_called_once_with(
        f"{API_BASE_URL}/chores/{chore_id}/assign",
        json=data,
        headers=auth_headers # Removed explicit Content-Type
    )
    assert response.status_code == 200
    assert response.json() == assigned_chore

@patch('requests.post')
def test_mark_chore_as_complete(mock_post, auth_headers):
    """
    Test marking a chore as completed.
    POST /api/v1/chores/:id/complete
    """
    chore_id = 2
    expected_completion = {
        "id": 1,
        "chore_id": chore_id,
        "user_id": 1,
        "completed_at": "2023-10-27T12:00:00Z",
    }
    mock_post.return_value = mock_response(201, expected_completion)

    response = requests.post(f"{API_BASE_URL}/chores/{chore_id}/complete", headers=auth_headers)

    # The actual call does NOT pass `json={}` and requests.post without `json` or `data`
    # does NOT automatically add Content-Type.
    mock_post.assert_called_once_with(
        f"{API_BASE_URL}/chores/{chore_id}/complete",
        headers=auth_headers # Removed `json={}` and explicit Content-Type
    )
    assert response.status_code == 201
    assert response.json() == expected_completion

@patch('requests.get')
def test_list_all_chores_for_family(mock_get, auth_headers):
    """
    Test listing all chores for the current user's family.
    GET /api/v1/chores
    """
    expected_chores = [
        {
            "id": 1,
            "name": "Wash Dishes",
            "description": "Wash all dishes in the sink",
            "points": 10,
            "frequency": "daily",
            "assigned_to_user_id": 1,
            "last_completed_at": None,
            "created_at": "2023-10-27T10:00:00Z",
            "updated_at": "2023-10-27T10:00:00Z",
            "family_id": 1,
        },
        {
            "id": 2,
            "name": "Take out trash",
            "description": "Empty all trash bins",
            "points": 5,
            "frequency": "weekly",
            "assigned_to_user_id": None,
            "last_completed_at": None,
            "created_at": "2023-10-27T10:00:00Z",
            "updated_at": "2023-10-27T10:30:00Z",
            "family_id": 1,
        },
    ]
    mock_get.return_value = mock_response(200, expected_chores)

    response = requests.get(f"{API_BASE_URL}/chores", headers=auth_headers)

    # requests.get does NOT automatically add Content-Type.
    mock_get.assert_called_once_with(
        f"{API_BASE_URL}/chores",
        headers=auth_headers # Removed explicit Content-Type
    )
    assert response.status_code == 200
    assert response.json() == expected_chores

@patch('requests.get')
def test_list_all_completions(mock_get, auth_headers):
    """
    Test listing all chore completions for the family.
    GET /api/v1/completions
    """
    expected_completions = [
        {"id": 1, "chore_id": 1, "user_id": 1, "completed_at": "2023-10-27T12:00:00Z"},
        {"id": 2, "chore_id": 2, "user_id": 2, "completed_at": "2023-10-26T18:00:00Z"},
    ]
    mock_get.return_value = mock_response(200, expected_completions)

    response = requests.get(f"{API_BASE_URL}/completions", headers=auth_headers)

    # requests.get does NOT automatically add Content-Type.
    mock_get.assert_called_once_with(
        f"{API_BASE_URL}/completions",
        headers=auth_headers # Removed explicit Content-Type
    )
    assert response.status_code == 200
    assert response.json() == expected_completions