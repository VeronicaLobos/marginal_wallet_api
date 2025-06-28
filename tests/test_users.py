from fastapi.testclient import TestClient
from sqlmodel import Session
from schema.user import User, UserCreate
from auth.auth import get_password_hash

from tests.test_dependencies import (
    get_response_register_test_user,
    get_token_for_test_user,
    TEST_USER_DATA)

"""
Focus: User registration, login, profile retrieval, updates, password changes, deletion.
Next Key Tests:
test_update_name_email_success(): Valid update, HTTP 200.
test_update_name_email_unauthenticated(): HTTP 401.
test_update_password_success(): Valid old password, matching new passwords, HTTP 204.
test_update_password_incorrect_current_password(): HTTP 403.
test_update_password_new_passwords_mismatch(): HTTP 400.
test_delete_user_success(): Valid password, HTTP 204.
test_delete_user_incorrect_password(): HTTP 403.
test_dashboard_summary_initial(): Check dashboard for newly created user (0 balance, 0 categories/movements).
test_dashboard_summary_with_data(): (More integration-like, but still good here) Create user, categories, movements, then check dashboard totals.
"""

## Tests default route (no authentication required)

def test_home_route(client: TestClient):
    """
    * Tests the home route of the FastAPI application.
    * Should return a 200 status code and a greeting message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "greeting": "Welcome to the Marginal Wallet API!"
    }


## Tests user registration endpoints (no authentication required)
# Uses the `client` fixture to provide a non-authenticated client.
# Uses the `get_response_register_test_user` helper function
# to register a test user with predefined data,
# and the `get_token_for_test_user` helper function to get an access token.

def test_register_user_success(client: TestClient):
    """
    * Tests user registration with valid data.
    * Should return HTTP 201 and the created user data
    as per the UserPublic schema (name, email, id).

    Endpoint: POST /users/register
    """
    # Attempts to register the test user
    response = get_response_register_test_user(client)

    assert response.status_code == 201

    registered_user = response.json()
    assert registered_user["name"] == TEST_USER_DATA["name"]
    assert registered_user["email"] == TEST_USER_DATA["email"]
    assert "id" in registered_user


def test_register_user_duplicate_email(client: TestClient):
    """
    * Tests user registration with an already existing email.
    * Should return HTTP 400 Bad Request, and an error message.

    Endpoint: POST /users/register
    """
    # Registers the test user to ensure they exist in the database
    get_response_register_test_user(client)
    # Attempts to register the same user again
    response = client.post("/users/register", json=TEST_USER_DATA)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Username or email already exists"
    }


def test_get_access_token_at_login_success(client: TestClient):
    """
    * Tests user login with valid credentials.
    * Checks if the token is in the expected format: bearer token.
    * Should return HTTP 200 and a valid access token.

    Endpoint: POST /auth/token
    """
    # Registers the test user to ensure they exist in the database
    get_response_register_test_user(client)
    # Attempts to get the access token for the test user
    response = get_token_for_test_user(client)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_get_access_token_at_login_failure(client: TestClient):
    """
    * Tests user login with invalid credentials (UserPublic).
    * Should return HTTP 401 Unauthorized, and an error message.

    Endpoint: POST /auth/token
    """
    # Attempts to get the access token for a user that does not exist
    response = get_token_for_test_user(client)

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Incorrect username or password"
    }


## Testing user details retrieval endpoints (requires authentication)

# Uses the `auth_client` fixture to provide an authenticated client,
# the `client` fixture to provide a non-authenticated client,
# and the `test_auth_user` fixture to provide a pre-registered user.

def test_get_current_user_profile_authenticated_success(
        auth_client: TestClient,
        test_auth_user: User):
    """
    * Tests successful retrieval of the current user's details
    * Should return HTTP 200 and the user's profile data
    as per the UserPublic schema (name, email, id).

    Endpoint: GET /users/me
    """
    response = auth_client.get("/users/me")

    assert response.status_code == 200

    user_details = response.json()
    assert user_details["name"] == test_auth_user.name
    assert user_details["email"] == test_auth_user.email
    assert user_details["id"] == test_auth_user.id


def test_get_current_user_profile_unauthenticated_failure(client: TestClient):
    """
    * Tests retrieval of the current user's details without
     authentication.
    * Should return HTTP 401 Unauthorized, and an error message.

    Endpoint: GET /users/me
    """
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated"
    }
