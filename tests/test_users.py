from fastapi.testclient import TestClient
from schema.user import User

TEST_AUTH_USER_PLAIN_PASSWORD = "admin123supersecure"

TEST_USER_DATA = {
    "name": "jdoe_test",
    "email": "jdoe_test@gmail.com",
    "password": TEST_AUTH_USER_PLAIN_PASSWORD
}

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
    response = client.post("/users/register", json=TEST_USER_DATA)
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
    client.post("/users/register", json=TEST_USER_DATA)
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
    client.post("/users/register", json=TEST_USER_DATA)
    # Attempts to get the access token for the test user
    response = client.post("/auth/token", data={
        "username": TEST_USER_DATA["email"],
        "password": TEST_USER_DATA["password"]
    })

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
    response = client.post("/auth/token", data={
        "username": TEST_USER_DATA["email"],
        "password": TEST_USER_DATA["password"]
    })

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Incorrect username or password"
    }


## Testing user details retrieval endpoints (requires authentication)

# Uses the `auth_client` fixture to provide an authenticated client,
# the `client` fixture to provide a non-authenticated client,
# and the `test_auth_user` fixture to provide a pre-registered user.

def test_get_current_user_profile_success(
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


def test_get_current_user_profile_failure(client: TestClient):
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


def test_update_name_email_success(
        auth_client: TestClient,
        test_auth_user: User):
    """
    * Tests successful update of the user's name and email.
    * Should return HTTP 200 and the updated user data
    as per the UserPublic schema (name, email, id).

    Endpoint: PATCH /users/me/update_details
    """
    updated_details = {
        "name": TEST_USER_DATA["name"],
        "email": TEST_USER_DATA["email"]
    }

    response = auth_client.patch("/users/me/update_details",
                                 json=updated_details)

    assert response.status_code == 200

    updated_details = response.json()
    assert updated_details["name"] == TEST_USER_DATA["name"]
    assert updated_details["email"] == TEST_USER_DATA["email"]
    assert updated_details["id"] == test_auth_user.id


def test_update_name_email_failure(client: TestClient):
    """
    * Tests update of the user's name and email without authentication.
    * Should return HTTP 401 Unauthorized, and an error message.

    Endpoint: PUT /users/me/update_details
    """
    updated_details = {
        "name": TEST_USER_DATA["name"],
        "email": TEST_USER_DATA["email"]
    }

    response = client.patch("/users/me/update_details",
                            json=updated_details)

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated"
    }


def test_update_password_success(
        auth_client: TestClient,
        test_auth_user: User,
        client: TestClient):
    """
    * Tests successful update of the user's password.
    * Requires the current password from the fixture test_auth_user,
    and a new password, as per the UserPasswordUpdate schema.
    * Should return HTTP 204 No Content indicating success.
    * After updating the password, attempts to log in with the old
    password should fail with HTTP 401 Unauthorized, and an error
    message.

    Endpoint: PUT /users/me/update_password
    """
    current_password = TEST_AUTH_USER_PLAIN_PASSWORD
    new_password = TEST_AUTH_USER_PLAIN_PASSWORD + "_new"
    updated_password_data = {
        "current_password": current_password,
        "new_password": new_password,
        "confirm_new_password": new_password
    }

    response = auth_client.patch("/users/me/update_password",
                                 json=updated_password_data)

    assert response.status_code == 204

    response = client.post("/auth/token", data={
        "username": test_auth_user.email,
        "password": test_auth_user.password
    })
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Incorrect username or password"
    }



def test_update_password_incorrect_current_password(
        auth_client: TestClient,
        test_auth_user: User):
    """
    * Tests update of the user's password with an incorrect
    current password.
    * Should return HTTP 403 Forbidden, and an error message.

    Endpoint: PUT /users/me/update_password
    """
    incorrect_current_password = TEST_AUTH_USER_PLAIN_PASSWORD + "_wrong"
    new_password = TEST_AUTH_USER_PLAIN_PASSWORD + "_new"
    updated_password_data = {
        "current_password": incorrect_current_password,
        "new_password": new_password,
        "confirm_new_password": new_password
    }

    response = auth_client.patch("/users/me/update_password",
                                 json=updated_password_data)

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Incorrect current password."
    }


def test_update_password_new_passwords_mismatch(
        auth_client: TestClient,
        test_auth_user: User):
    """
    * Tests update of the user's password with mismatched
    new passwords.
    * Should return HTTP 400 Bad Request, and an error message.

    Endpoint: PUT /users/me/update_password
    """
    current_password = TEST_AUTH_USER_PLAIN_PASSWORD
    new_password = TEST_AUTH_USER_PLAIN_PASSWORD + "_new"
    updated_password_data = {
        "current_password": current_password,
        "new_password": new_password,
        "confirm_new_password": new_password + "_mismatch"
    }

    response = auth_client.patch("/users/me/update_password",
                                 json=updated_password_data)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "New passwords do not match."
    }


def test_delete_user_success(
        auth_client: TestClient,
        test_auth_user: User,
        client: TestClient):
    """
    * Tests successful deletion of the user's account.
    * Requires the current password from the fixture
    test_auth_user, (as per the UserDeleteConfirmation schema),
    sent via a custom header.
    * Should return HTTP 204 No Content indicating success.
    * After deletion, attempts to log in with the same credentials
    should fail with HTTP 401 Unauthorized, and an error message.

    Endpoint: DELETE /users/me
    """
    delete_headers = {"X-Confirm-Password": TEST_AUTH_USER_PLAIN_PASSWORD}
    response = auth_client.delete("/users/me", headers=delete_headers)
    assert response.status_code == 204

    response = client.post("/auth/token", data={
        "username": test_auth_user.name,
        "password": test_auth_user.password
    })
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Incorrect username or password"
    }


def test_delete_user_failure(client: TestClient):
    """
    * Tests deletion of the user's account without authentication.
    * Should return HTTP 401 Unauthorized, and an error message.

    Endpoint: DELETE /users/me
    """
    delete_headers = {"X-Confirm-Password": TEST_AUTH_USER_PLAIN_PASSWORD}
    response = client.delete("/users/me", headers=delete_headers)

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated"
    }


def test_dashboard_summary_initial(
        auth_client: TestClient,
        test_auth_user: User):
    """
    * Tests the initial dashboard summary for a newly created user.
    * Should return HTTP 200 and a dashboard summary with 0 balance,
    0 categories, and 0 movements, as per the UserDashboard schema.

    Endpoint: GET /users/me/dashboard/
    """
    response = auth_client.get("/users/me/dashboard/")

    assert response.status_code == 200

    dashboard_summary = response.json()
    assert dashboard_summary["balance"] == 0.0
    assert dashboard_summary["num_categories"] == 0
    assert dashboard_summary["num_movements"] == 0


def test_minijobs_balance_initial(
        auth_client: TestClient,
        test_auth_user: User
):
    """
    * Tests the initial minijobs balance summary for a
    newly created user.
    * Should return HTTP 200 and a minijobs balance summary
    with 0.0 balance, "556€" max earnings, current month and
    year, as per the MinijobsBalanceSummary schema.

    Endpoint: GET /users/me/minijobs_balance/
    """
    response = auth_client.get("/users/me/minijobs_balance/")

    assert response.status_code == 200

    minijobs_balance = response.json()
    assert minijobs_balance["minijobs_balance"] == 0.0
    assert minijobs_balance["max_earnings"] == "556€"
    assert "current_month" in minijobs_balance
    assert "current_year" in minijobs_balance
