# Import of necessary parts of FastAPI
from dns.e164 import query
from fastapi import APIRouter, Depends, HTTPException, status, Response

# Import of or_ module as a filtering condition to avoid using '|'
from sqlalchemy import or_

# Import of SQLAlchemy Session (for type hints)
from sqlalchemy.orm import Session

from api.schemas import EmployeeUpdate, EmployeeCreate
# Import of SQLAlchemy ORM models
from database import models

# Import of Pydantic schemas
from api import schemas

# Import of database dependency
from database.database import get_db

# Import of EmployeeService
from services.employee_service import EmployeeService, get_employee_service

from uuid import UUID
from typing import List, Optional


# Creates APIRouter instance
employees_router = APIRouter(
    prefix="/employees",
    tags=["employees"],
)

@employees_router.post("/", response_model=schemas.Employee, status_code=status.HTTP_201_CREATED)
def create_employee(
        employee_data: EmployeeCreate,
        employee_service: EmployeeService = Depends(get_employee_service)
):
    """ Endpoint to create a new employee.

    Args:
        employee_data (schemas.EmployeeCreate): The Pydantic model containing the details
            for a new employee.
        employee_service (EmployeeService): The injected EmployeeService instance.

    Returns: db_employee: The newly created employee object incl. the automatically generated
        ID and timestamps.

    Raises:
        HTTPException: If the provided phone number or e-mail address is
            already in the database (HTTP 400 Bad Request).
    """

    try:
        db_employee = employee_service.create_employee(employee_data=employee_data)  # <-- Aufruf des Service
        return db_employee
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@employees_router.get("/{employee_id}", response_model=schemas.Employee, status_code=status.HTTP_200_OK)
def get_employee_by_id(
    employee_id: UUID,
    employee_service: EmployeeService = Depends(get_employee_service)
):
    """ Endpoint to get an employee by ID.

    Args:
        employee_id (UUID): A unique identifier in UUID format.
        employee_service (EmployeeService): The injected EmployeeService instance.

    Returns: db_employee: The newly created employee object incl. the automatically generated
        ID and timestamps.

    Raises: HTTPException: If the employee cannot be found by the passed ID (HTTP 404 Not Found)

    """

    db_employee = employee_service.get_employee_by_id(employee_id=employee_id)
    if not db_employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    return db_employee


@employees_router.get("/", response_model=List[schemas.Employee])
def get_employees(
        name_query: Optional[str] = None,
        employee_service: EmployeeService = Depends(get_employee_service)
):
    """ Endpoint to retrieve list of employees.
    case-insensitive, if name_query is provided, filters employees
    by name (case-insensitive, partial match).

    Args:
        name_query (Optional[str]): An optional string to filter employees by name.
        employee_service (EmployeeService): The injected EmployeeService instance.

    Returns: List[employee_schemas.Employee]: A list of all employees,
        if name_query provided: A list of all employees matching the name query.

    Raises: HTTPException: If the input data is invalid (422 Unprocessable Entity, Pydantic)
    """

    employees = employee_service.get_all_employees(name_query=name_query)

    return employees

@employees_router.patch("/{employee_id}", response_model=schemas.Employee, status_code=status.HTTP_200_OK)
def update_employee(
        employee_id: UUID,
        employee_update_data: EmployeeUpdate,
        employee_service: EmployeeService = Depends(get_employee_service)
):
    """ Endpoint to update at least one field of an existing employee.

    Args:
        employee_id (UUID): A unique identifier in UUID format.
        employee_update_data (EmployeeUpdate): An EmployeeUpdate object containing the updates.
        employee_service (EmployeeService): The injected EmployeeService instance.

    Returns: db_employee: The updated Employee object.

    Raises:
        HTTPException:
            - 404 Not found: If the ID searched after does not match with an
            employee from the database.
            - 400 Bad request: If there is a database error like unique constraint violation
            (for example same phone number or e-mail)
            - 422 Unprocessable Entity: If the input data is invalid (Pydantic)
    """

    try:
        db_employee = employee_service.update_employee(
            employee_id=employee_id,
            employee_update_data=employee_update_data
        )
        return db_employee

    except ValueError as e:

        if "Employee not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@employees_router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_by_id(
        employee_id: UUID,
        employee_service: EmployeeService = Depends(get_employee_service)
):
    """ Endpoint to delete an employee by id.

    Args:
        employee_id (UUID): A unique identifier in UUID format.
        employee_service (EmployeeService): The injected EmployeeService instance.

    Returns: Response(status_code=status.HTTP_204_NO_CONTENT): Returns a response without body.

    Raises:
        HTTPException: If the employee cannot be found by the passed ID (HTTP 404 Not Found)
    """

    try:
        employee_service.delete_employee(employee_id=employee_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ValueError as e:
        if "Employee not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
