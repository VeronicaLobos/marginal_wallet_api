TEST_USER_DATA = {
    "name": "jdoe_test",
    "email": "jdoe_test@gmail.com",
    "password": "123supersecurefortesting"
}

def get_response_register_test_user(client):
    """
    Helper function to register a test user.
    """
    response = client.post("/users/register", json=TEST_USER_DATA)

    return response


def get_token_for_test_user(client):
    """
    Helper function to get an access token for the test user.
    """
    response = client.post("/auth/token", data={
        "username": TEST_USER_DATA["email"],
        "password": TEST_USER_DATA["password"]
    })

    return response
