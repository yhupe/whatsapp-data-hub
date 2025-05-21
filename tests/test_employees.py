from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
import uuid

def test_create_employee_success(client: TestClient, db_session_for_test: Session):
    """
    Tests the successful creation of new Employee with the POST /employees/ endpoint.
    `client` and `db_session_for_test` are being provided by pytest as fixtures.
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

    db_employee = db_session_for_test.query(models.Employee).filter(
        models.Employee.id == employee_id_from_response
    ).first()

    assert db_employee is not None, "Employee was not found in the database."
    assert db_employee.id == employee_id_from_response
    assert db_employee.name == employee_data["name"]
    assert db_employee.email == employee_data["email"]
    assert db_employee.whatsapp_phone_number == employee_data["whatsapp_phone_number"]
    assert db_employee.role.value == employee_data["role"]


def test_create_employee_duplicate_email_or_phone(client: TestClient, db_session_for_test: Session):
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


def test_get_employees_empty_db(client: TestClient):
    """
    Test that retrieving employees from an empty database returns an empty list.
    """

    response = client.get("/employees/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_all_employees(client: TestClient):
    """
    Test that retrieving all employees returns all existing employees.
    """

    # Create some employees
    employee_data_1 = {
        "name": "Alice Test",
        "whatsapp_phone_number": "+4917612345678",
        "email": "alice.test@example.com",
        "role": "admin"
    }
    employee_data_2 = {
        "name": "Bob Test",
        "whatsapp_phone_number": "+4917687654321",
        "email": "bob.test@example.com",
        "role": "admin"
    }
    employee_data_3 = {
        "name": "Charlie Test",
        "whatsapp_phone_number": "+4917611223344",
        "email": "charlie.test@example.com",
        "role": "general_user"
    }

    # Post requests to create the test employees
    response_1 = client.post("/employees/", json=employee_data_1)
    assert response_1.status_code == 201
    created_employee_1 = response_1.json()

    response_2 = client.post("/employees/", json=employee_data_2)
    assert response_2.status_code == 201
    created_employee_2 = response_2.json()

    response_3 = client.post("/employees/", json=employee_data_3)
    assert response_3.status_code == 201
    created_employee_3 = response_3.json

    # query all test employees
    response = client.get("/employees")

    # actual testing
    assert response.status_code == 200

    employees_list = response.json()

    # testing that all three employees are returned
    assert len(employees_list) == 3

    # comparing names in sets (mutable order)
    returned_names = {employee["name"] for employee in employees_list}
    expected_names = {
        employee_data_1["name"],
        employee_data_2["name"],
        employee_data_3["name"]
    }
    assert returned_names == expected_names


def test_search_employee_by_full_name(client: TestClient):
    """
    Test that searching for a full name of an existing employee returns only that employee.
    """

    # Create employee to search for
    employee_data_to_find = {
        "name": "Diana Search",
        "whatsapp_phone_number": "+4917699887766",
        "email": "diana.search@example.com",
        "role": "admin"
    }
    # Create employee that should not be found
    another_employee_data = {
        "name": "Eve Other",
        "whatsapp_phone_number": "+4917611335577",
        "email": "eve.other@example.com",
        "role": "admin"
    }

    response_created_1 = client.post("/employees/", json=employee_data_to_find)
    assert response_created_1.status_code == 201
    created_employee_to_find = response_created_1.json()

    response_created_2 = client.post("/employees/", json=another_employee_data)
    assert response_created_2.status_code == 201

    # Get request to filter for the full name
    response = client.get(f"/employees/?name_query={employee_data_to_find['name']}")

    assert response.status_code == 200
    employees_list = response.json()

    # expecting only one employee
    assert len(employees_list) == 1
    found_employee = employees_list[0]

    # check that it is the right employee
    assert found_employee["name"] == employee_data_to_find["name"]
    assert found_employee["role"] == employee_data_to_find["role"]
    assert found_employee["id"] == created_employee_to_find["id"]


def test_search_employee_partial_and_case_insensitive(client: TestClient):
    """
    Test that searching for a partial name (case-insensitive) returns all matching employees.
    """

    # Creating different employees with different writing of the names
    employee_data_1 = {
        "name": "Frank Tester",
        "whatsapp_phone_number": "+4915111111111",
        "email": "frank.tester@example.com",
        "role": "admin"
    }
    employee_data_2 = {
        "name": "gertrud testmann",
        "whatsapp_phone_number": "+4915122222222",
        "email": "gertrud.t@example.com",
        "role": "admin"
    }
    employee_data_3 = {
        "name": "Heidi Smith",
        "whatsapp_phone_number": "+4915133333333",
        "email": "heidi.s@example.com",
        "role": "general_user"
    }
    employee_data_4 = {
        "name": "IGOR TEST",
        "whatsapp_phone_number": "+4915144444444",
        "email": "igor.t@example.com",
        "role": "general_user"
    }

    client.post("/employees/", json=employee_data_1)
    client.post("/employees/", json=employee_data_2)
    client.post("/employees/", json=employee_data_3)
    client.post("/employees/", json=employee_data_4)

    search_query = "test"
    response = client.get(f"/employees/?name_query={search_query}")

    assert response.status_code == 200
    employees_list = response.json()

    assert len(employees_list) == 3

    returned_names = {employee["name"] for employee in employees_list}
    expected_names = {
        employee_data_1["name"],
        employee_data_2["name"],
        employee_data_4["name"]
    }
    assert returned_names == expected_names