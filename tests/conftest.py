"""
This module sets up fixtures for testing a FastAPI application.
It provides a test database session, a FastAPI TestClient,
and a pre-registered authenticated user for tests that require
authentication.
Fixtures are the dependency injection mechanism in pytest,
allowing tests to share setup code and resources.

Fixtures in this module include:
* session: A SQLModel Session for database operations during tests.
* client: A FastAPI TestClient that uses the test database session.
* test_auth_user: A pre-registered user in the test database,
  used for authentication in tests.
* auth_client: A TestClient that is authenticated with a test user.
"""

import sys
import os

# Set a test-specific database URL environment variable BEFORE importing the app.
# This ensures that when the application is imported, its database engine
# is created using this test database, not the one from the .env file.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

# Ensure the project root is in the path for imports

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, project_root)

from main import app

# Actual dependency functions to override
from config.database import get_session as get_session_dependency
from auth.auth import get_current_active_user as get_current_active_user_dependency
from auth.rate_limit import limiter

# Auth functions and models
from auth.auth import get_password_hash
from schema.user import User, UserCreate

# Rate limiting setup
from slowapi import Limiter
from slowapi.util import get_ipaddr
from slowapi.middleware import SlowAPIMiddleware

# Database setup for testing
sqlite_file_name = "test.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
test_engine = create_engine(sqlite_url, echo=False)

AUTHENTICATED_USER = {
    "name": "jdoe_test",
    "email": "jdoe_test@gmail.com",
    "password": "admin123supersecure",
}


@pytest.fixture(name="session", scope="function")
def session_fixture():
    """
    Setup and teardown for the test database session.
    Creates a test database session for the entire test session.

    For each test that uses this fixture, a clean in-memory SQLite database
    is created, tables are initialized, and then dropped after the test.
    This ensures test isolation and a predictable state.
    """
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="client", scope="function")
def client_fixture(session: Session):
    """
    Provides a FastAPI TestClient with its database session overridden
    to use the test session fixture. This allows API requests in tests
    to interact with the in-memory test database.

    The session is cleared after each test to ensure no state is carried over.
    """
    app.dependency_overrides[get_session_dependency] = lambda: session

    # original_limiter_enabled = limiter.enabled

    # limiter.enabled = False

    with TestClient(app) as client:
        yield client

    # limiter.enabled = original_limiter_enabled

    app.dependency_overrides.clear()


@pytest.fixture(name="test_auth_user", scope="function")
def test_auth_user_fixture(session: Session):
    """
    Creates and provides a pre-registered, authenticated test user for tests
    that require authentication.
    """
    user_create_data = UserCreate(
        name=AUTHENTICATED_USER["name"],
        email=AUTHENTICATED_USER["email"],
        password=AUTHENTICATED_USER["password"],
    )
    hashed_password = get_password_hash(user_create_data.password)

    test_user_db = User(
        name=user_create_data.name,
        email=user_create_data.email,
        password=hashed_password,
    )

    session.add(test_user_db)
    session.commit()
    session.refresh(test_user_db)
    return test_user_db


@pytest.fixture(name="auth_client", scope="function")
def auth_client_fixture(client: TestClient, test_auth_user: User):
    """
    Provides a TestClient that is authenticated with the test user.

    It overrides the get_current_active_user dependency to return
    the predefined test_auth_user, bypassing actual JWT creation/validation
    for unit tests.

    This client will be used in tests that require authentication.
    """
    app.dependency_overrides[get_current_active_user_dependency] = (
        lambda: test_auth_user
    )
    yield client
    app.dependency_overrides.clear()
