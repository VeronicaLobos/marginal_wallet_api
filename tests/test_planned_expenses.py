"""
Tests for Planned Expenses API Endpoints

This module contains tests for the Planned Expenses API endpoints.
It includes tests for creating, listing, retrieving,
updating, and deleting planned expenses (complete CRUD operations).
"""

from fastapi.testclient import TestClient

from schema.enums import CurrencyType, FrequencyType
from schema.user import User

PLANNED_EXPENSE_DATA = {
    "aprox_date": "2025-07-01",
    "value": 500.0,
    "currency": CurrencyType.usd.value,
    "frequency": FrequencyType.monthly.value,
    "description": "Rent"
}

UPDATED_PLANNED_EXPENSE_DATA = {
    "value": 450.0
}


def test_create_planned_expense_success(
        auth_client: TestClient,
        test_auth_user: User):
    """
    Test creating a planned expense successfully.
    * Creates a planned expense with valid data, as per the
    PlannedExpenseCreate schema.
    * Should return response status code 201 (Created),
    and the created planned expense data as per the
    PlannedExpensePublic schema.
    * Cheks that the response data matches the input data.

    Endpoint: POST /planned_expenses/
    """
    response = auth_client.post("/planned_expenses/",
                            json=PLANNED_EXPENSE_DATA
    )

    assert response.status_code == 201

    response_data = response.json()
    assert response_data["aprox_date"] == PLANNED_EXPENSE_DATA["aprox_date"]
    assert response_data["value"] == PLANNED_EXPENSE_DATA["value"]
    assert response_data["currency"] == PLANNED_EXPENSE_DATA["currency"]
    assert response_data["frequency"] == PLANNED_EXPENSE_DATA["frequency"]
    assert response_data["description"] == PLANNED_EXPENSE_DATA["description"]
    assert response_data["user_id"] == test_auth_user.id
    assert response_data["id"] is not None


def test_list_planned_expenses(
        auth_client: TestClient,
        test_auth_user: User):
    """
    Test listing planned expenses for the authenticated user.
    * Creates a planned expense and then lists all planned expenses.
    * Should return response status code 200 (OK).
    * Checks that the response data contains the created planned
    expense and that there is one planned expense in the list.

    Endpoint: GET /planned_expenses/
    """
    auth_client.post("/planned_expenses/",
                    json=PLANNED_EXPENSE_DATA
    )

    response = auth_client.get("/planned_expenses/list")
    assert response.status_code == 200

    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 1


def test_get_planned_expense(
        auth_client: TestClient,
        test_auth_user: User):
    """
    Tests retrieving a planned expense by its ID.
    * Creates a planned expense and then retrieves it by ID.
    * Should return response status code 200 (OK),
    and the planned expense data as per the PlannedExpensePublic schema.
    """
    auth_client.post("/planned_expenses/",
                     json=PLANNED_EXPENSE_DATA
                     )
    response = auth_client.get("/planned_expenses/1")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["aprox_date"] == PLANNED_EXPENSE_DATA["aprox_date"]


def test_update_planned_expense(
        auth_client: TestClient,
        test_auth_user: User):
    """
    Tests updating a planned expense successfully.
    * Creates a planned expense and then updates it with new data,
    as per the PlannedExpenseUpdate schema.
    * Should return response status code 200 (OK), and the updated
    planned expense data as per the PlannedExpensePublic schema.
    * Checks that the response data matches the updated data.

    Endpoint: PATCH /planned_expenses/{planned_expense_id}
    """
    auth_client.post("/planned_expenses/",
                     json=PLANNED_EXPENSE_DATA
                     )

    response = auth_client.patch("/planned_expenses/1",
                                 json=UPDATED_PLANNED_EXPENSE_DATA
                                 )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["value"] == UPDATED_PLANNED_EXPENSE_DATA["value"]


def test_delete_planned_expense(
        auth_client: TestClient,
        test_auth_user: User):
    """
    Tests deleting a planned expense successfully.
    * Creates a planned expense and then deletes it.
    * Should return response status code 204 (No Content).
    * Checks that the planned expense is no longer listed.

    Endpoint: DELETE /planned_expenses/{planned_expense_id}
    """
    auth_client.post("/planned_expenses/",
                     json=PLANNED_EXPENSE_DATA
                     )

    response = auth_client.delete("/planned_expenses/1")
    assert response.status_code == 204

    # Verify that the planned expense is deleted
    response = auth_client.get("/planned_expenses/list")
    assert response.status_code == 200
    assert len(response.json()) == 0
