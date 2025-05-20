from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
import uuid

def test_create_employee_success(client: TestClient, db_session_test: Session):
    """
    Tests the successful creation of new Employee with the POST /employees/ endpoint.
    `client` and `db_session_test` are being provided by pytest as fixtures.
    """

    employee_data = {
        "name": "Test Employee",
        "whatsapp_phone_number": "+12345678901",
        "email": "test.employee@example.com",
        "role": "admin"
    }

    # Sends post request to endpoint
    response = client.post("/employees/", json=employee_data)

    # Check HTTP statuscode
    assert response.status_code == 201, f"Expected status 201, got {response.status_code}. Response: {response.json()}"

    # Check response body (returned data)
    response_data = response.json()
    assert "id" in response_data
    # Check whether the ID is a valid UUID
    assert isinstance(uuid.UUID(response_data["id"]), uuid.UUID)

    assert response_data["name"] == employee_data["name"]
    assert response_data["whatsapp_phone_number"] == employee_data["whatsapp_phone_number"]
    assert response_data["email"] == employee_data["email"]
    assert response_data["role"] == employee_data["role"]
    assert "created_at" in response_data
    assert "updated_at" in response_data
    assert response_data["magic_link_token"] is None
    assert response_data["magic_link_expires_at"] is None


    # Check whether the employee even is inside the database
    from database import models

    employee_id_from_response = uuid.UUID(response_data["id"])

    db_employee = db_session_test.query(models.Employee).filter(
        models.Employee.id == employee_id_from_response
    ).first()

    assert db_employee is not None, "Employee was not found in the database."
    assert db_employee.id == employee_id_from_response
    assert db_employee.name == employee_data["name"]
    assert db_employee.email == employee_data["email"]
    assert db_employee.whatsapp_phone_number == employee_data["whatsapp_phone_number"]
    assert db_employee.role.value == employee_data["role"]


def test_create_employee_duplicate_email_or_phone(client: TestClient, db_session_test: Session):
    """ Tests that creating employee with existing email or phone number fails."""

    # First employee to be created successful
    employee_data_1 = {
        "name": "Duplicate Test User 1",
        "whatsapp_phone_number": "+491111111111",
        "email": "duplicate.test1@example.com",
        "role": "admin"
    }

    response_1 = client.post("/employees/", json=employee_data_1)

    assert response_1.status_code == 201

    # Try to create another employee with same e-mail, should fail
    employee_data_2 = {
        "name": "Duplicate Test User 2",
        "whatsapp_phone_number": "+492222222222",
        "email": "duplicate.test1@example.com", # same e-mail
        "role": "general_user"
    }
    response_2 = client.post("/employees/", json=employee_data_2)
    # Expect HTTP 400 Bad Request as API endpoint should handle it like that
    assert response_2.status_code == 400, f"Expected status 400 for duplicate email, got {response_2.status_code}. Response: {response_2.json()}"
    assert "detail" in response_2.json()
    assert "already exists" in response_2.json()["detail"]

    # Try to create another employee with same phone number, should fail
    employee_data_3 = {
        "name": "Duplicate Test User 3",
        "whatsapp_phone_number": "+491111111111", # same phone number
        "email": "duplicate.test3@example.com",
        "role": "general_user"
    }
    response_3 = client.post("/employees/", json=employee_data_3)
    # Expect HTTP 400 Bad Request as API endpoint should handle it like that
    assert response_3.status_code == 400, f"Expected status 400 for duplicate phone, got {response_3.status_code}. Response: {response_3.json()}"
    assert "detail" in response_3.json()
    assert "already exists" in response_3.json()["detail"]


def test_create_employee_invalid_data(client: TestClient):
    """
    Tests that try creating a new employee with missing data where it is required
    ends up in an error.
    FastAPI/Pydantic should automatically return HTTP 422 Unprocessable Entity.
    """
    invalid_employee_data = {
        "name": "Invalid User",
        # "whatsapp_phone_number" is missing
        "email": "invalid.user@example.com",
        "role": "general_user"
    }

    response = client.post("/employees/", json=invalid_employee_data)

    # Expecting HTTP 422 Unprocessable Entity for pydantic validation error
    assert response.status_code == 422, f"Expected status 422, got {response.status_code}. Response: {response.json()}"
    assert "detail" in response.json()
    assert any("whatsapp_phone_number" in error["loc"] for error in response.json()["detail"])