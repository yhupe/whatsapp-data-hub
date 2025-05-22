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


def test_update_employee_success(client: TestClient, db_session_for_test: Session):
    """
    Test that an employee can be successfully updated with partial data.
    """

    employee_data = {
        "name": "Original Name",
        "whatsapp_phone_number": "+4912345678900",
        "email": "original@example.com",
        "role": "general_user"
    }
    response = client.post("/employees/", json=employee_data)
    assert response.status_code == 201
    created_employee = response.json()
    employee_id = created_employee["id"]

    # updated name and email address
    update_data = {
        "name": "Updated Name",
        "email": "updated@example.com"
    }

    # patch request
    response = client.patch(f"/employees/{employee_id}", json=update_data)

    assert response.status_code == 200
    updated_employee = response.json()

    # check for correct id and that updated name and email address are correct
    assert updated_employee["id"] == employee_id
    assert updated_employee["name"] == "Updated Name"
    assert updated_employee["email"] == "updated@example.com"

    # Check that unchanged fields are really unchanged
    assert updated_employee["whatsapp_phone_number"] == employee_data["whatsapp_phone_number"]
    assert updated_employee["role"] == employee_data["role"]

    # Get request to check that the updates are saved to the database correctly
    get_response = client.get(f"/employees/{employee_id}")
    assert get_response.status_code == 200
    fetched_employee = get_response.json()
    assert fetched_employee["name"] == "Updated Name"
    assert fetched_employee["email"] == "updated@example.com"


def test_update_employee_not_found(client: TestClient, db_session_for_test: Session):
    """
    Test that attempting to update a non-existent employee returns 404 Not Found.
    """

    # An uuid that definitely does not exist
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    update_data = {"name": "Non Existent Update"}

    # Try to patch an employee with non-existent id
    response = client.patch(f"/employees/{non_existent_id}", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


def test_update_employee_invalid_data(client: TestClient, db_session_for_test: Session):
    """
    Test that updating an employee with invalid data (wrong email format)
    returns 422 Unprocessable Entity due to Pydantic validation.
    """

    # Create employee
    employee_data = {
        "name": "Valid User",
        "whatsapp_phone_number": "+4998765432100",
        "email": "valid@example.com",
        "role": "general_user"
    }
    response = client.post("/employees/", json=employee_data)
    assert response.status_code == 201
    created_employee = response.json()
    employee_id = created_employee["id"]

    # Try to update an invalid email address format
    invalid_update_data = {"email": "invalid-email-format"}
    response = client.patch(f"/employees/{employee_id}", json=invalid_update_data)

    # expecting pydantic validation error
    assert response.status_code == 422
    assert "value is not a valid email address" in response.json()["detail"][0]["msg"]


def test_update_employee_duplicate_email(client: TestClient, db_session_for_test: Session):
    """
    Test that updating an employee with an email or phone number that already exists
    for another employee returns 400 Bad Request (unique constraint violation).
    """

    employee_1_data = {
        "name": "Employee One",
        "whatsapp_phone_number": "+4911111111111",
        "email": "alpha@example.com",
        "role": "admin"
    }
    employee_2_data = {
        "name": "Employee 3",
        "whatsapp_phone_number": "+4922222222222",
        "email": "beta@example.com",
        "role": "general_user"
    }

    response_1 = client.post("/employees/", json=employee_1_data)
    assert response_1.status_code == 201
    created_employee_1 = response_1.json()
    employee_1_id = created_employee_1["id"]

    response_2 = client.post("/employees/", json=employee_2_data)
    assert response_2.status_code == 201
    created_employee_2 = response_2.json()

    # Case 1: duplicate email address
    duplicate_email_update = {"email": "beta@example.com"}
    response = client.patch(f"/employees/{employee_1_id}", json=duplicate_email_update)
    assert response.status_code == 400
    assert "duplicate key value violates unique constraint" in response.json()["detail"]
    assert "ix_employees_email" in response.json()["detail"]


def test_update_employee_duplicate_phone_number(client: TestClient, db_session_for_test: Session):
    """
    Test that updating an employee with a phone number that already exists for another employee
    returns 400 Bad Request.
    """
    # Zwei Mitarbeiter erstellen
    employee_1_data = {
        "name": "Employee Three",
        "whatsapp_phone_number": "+4933333333333",
        "email": "gamma@example.com",
        "role": "admin"
    }
    employee_2_data = {
        "name": "Employee Four",
        "whatsapp_phone_number": "+4944444444444",
        "email": "delta@example.com",
        "role": "general_user"
    }

    response_1 = client.post("/employees/", json=employee_1_data)
    assert response_1.status_code == 201
    created_employee_1 = response_1.json()
    employee_1_id = created_employee_1["id"]

    response_2 = client.post("/employees/", json=employee_2_data)
    assert response_2.status_code == 201
    created_employee_2 = response_2.json()

    # Case 2: duplicate phone number
    duplicate_phone_update = {"whatsapp_phone_number": "+4944444444444"}
    response = client.patch(f"/employees/{employee_1_id}", json=duplicate_phone_update)
    assert response.status_code == 400
    assert "duplicate key value violates unique constraint" in response.json()["detail"]
    assert "ix_employees_whatsapp_phone_number" in response.json()["detail"]


def test_update_employee_no_data_provided(client: TestClient, db_session_for_test: Session):
    """
    Test that attempting to update an employee by sending an empty JSON body
    returns 422 (at_least_one_field check in the Pydantic model).
    """

    employee_data = {
        "name": "Test User",
        "whatsapp_phone_number": "+4912341234123",
        "email": "test@example.com",
        "role": "admin"
    }
    response = client.post("/employees/", json=employee_data)
    assert response.status_code == 201
    created_employee = response.json()
    employee_id = created_employee["id"]

    # Empty update object
    empty_update_data = {}
    response = client.patch(f"/employees/{employee_id}", json=empty_update_data)
    assert response.status_code == 422

    # Check that a more specific error note is thrown by the pydantic @model_validator
    assert "At least one field (name, whatsapp_phone_number, email, role) must be provided for update." in response.json()["detail"][0]["msg"]


def test_delete_employee_success(client: TestClient, db_session_for_test: Session):
    """
    Test that an employee can be deleted.
    """

    employee_data = {
        "name": "Employee to Delete",
        "whatsapp_phone_number": "+4998765432100",
        "email": "delete_me@example.com",
        "role": "general_user"
    }
    response_create = client.post("/employees/", json=employee_data)
    assert response_create.status_code == 201
    created_employee = response_create.json()
    employee_id = created_employee["id"]

    # Delete request
    response_delete = client.delete(f"/employees/{employee_id}")


    assert response_delete.status_code == 204
    # checks that the body is empty
    assert not response_delete.content

    # Check that the employee really is deleted and returns 404 as expected
    response_get = client.get(f"/employees/{employee_id}")
    assert response_get.status_code == 404
    assert response_get.json() == {"detail": "Employee not found"}


def test_delete_employee_not_found(client: TestClient, db_session_for_test: Session):
    """
    Test that deleting a non-existent employee returns 404 Not Found.
    """

    # generating a non-existing uuid
    non_existent_id = str(uuid.UUID(int=0))

    # delete request
    response = client.delete(f"/employees/{non_existent_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Employee not found"}
