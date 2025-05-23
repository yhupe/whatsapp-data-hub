from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
import uuid


def test_create_message_log_success(client: TestClient, db_session_for_test: Session):

    test_employee_1 = {
        "name": "Test User 1",
        "whatsapp_phone_number": "+491111111111",
        "email": "test_1@example.com",
        "role": "general_user"
    }

    # Create test employee 1 to have a valid uuid
    response_employee = client.post("/employees/", json=test_employee_1)
    assert response_employee.status_code == 201
    response_employee_data = response_employee.json()

    # Everything is correct
    test_data_1 = {
        "employee_id" : f"{response_employee_data['id']}",
        "direction" : "inbound",
        "raw_message_content" : "Test Message to check the message logs!",
        "status" : "received"
    }

    # Sends post request to endpoint
    response_1 = client.post("/message_log/", json=test_data_1)

    # Check HTTP status code
    assert response_1.status_code == 201, f"Expected status 201, got {response_1.status_code}. Response: {response_1.json()}"

    response_data_1 = response_1.json()

    # Check whether the ID is a valid UUID
    assert "id" in response_data_1
    assert isinstance(uuid.UUID(response_data_1["id"]), uuid.UUID)

    assert response_data_1["employee_id"] == test_data_1["employee_id"]
    assert response_data_1["direction"] == test_data_1["direction"]
    assert response_data_1["raw_message_content"] == test_data_1["raw_message_content"]
    assert response_data_1["status"] == test_data_1["status"]
    assert "timestamp" in response_data_1

    # Check that the employee is in the Employee database
    from database import models

    employee_id_from_response = uuid.UUID(response_data_1["employee_id"])

    db_employee = db_session_for_test.query(models.Employee).filter(
        models.Employee.id == employee_id_from_response
    ).first()

    assert db_employee is not None, "Employee was not found in the database."
    assert db_employee.id == employee_id_from_response

    # Check that 'test_data_2' throws an error

    # 'status' is missing (Enum)
    test_data_2 = {
        "employee_id" : f"{response_employee_data['id']}",
        "direction" : "inbound",
        "raw_message_content" : "Test Message to check the message logs!",
        "status" : ""
    }

    response_2 = client.post("/message_log/", json=test_data_2)

    assert response_2.status_code == 422, f"Expected status 201, got {response_2.status_code}. Response: {response_2.json()}"



