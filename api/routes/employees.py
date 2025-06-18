# Import of necessary parts of FastAPI
from dns.e164 import query
from fastapi import APIRouter, Depends, HTTPException, status, Response

# Import of or_ module as a filtering condition to avoid using '|'
from sqlalchemy import or_

# Import of SQLAlchemy Session (for type hints)
from sqlalchemy.orm import Session

from api.schemas import EmployeeUpdate, EmployeeCreate, Employee
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
    """ **Endpoint to create a new employee.**

    **Please only send used fields in the request as otherwise examples are executed and saved.**

    **"name": mandatory**\n
    **"phone_number": mandatory**\n
    **"username": optional**\n
    **"hashed_password": optional**\n
    **"email": mandatory**\n
    **"role": mandatory**\n

    **Args:**\n
        employee_data (schemas.EmployeeCreate): The Pydantic model containing the details
            for a new employee.\n
        employee_service (EmployeeService): The injected EmployeeService instance.

    **Returns:**\n
        db_employee: The newly created employee object (incl. the automatically generated
        ID and timestamps).

    **Raises:**\n
        HTTPException: \n
            - HTTP 400 Bad Request: If the provided phone number or e-mail address is already in the database.\n
            - HTTP 422 Unprocessable Entity, Pydantic: If the input data is invalid.
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
    """ **Endpoint to get an employee by ID.**

    **Args:**\n
        employee_id (UUID): A unique identifier in UUID format.\n
        employee_service (EmployeeService): The injected EmployeeService instance.

    **Returns:**\n
        db_employee: The newly created employee object incl. the automatically generated ID and timestamps.

    **Raises:**\n
        HTTPException:\n
           - HTTP 404 Not Found: If the employee cannot be found by the passed ID

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
    """ **Endpoint to retrieve list of employees.**
    **Case-insensitive, if name_query is provided, filters employees by name (case-insensitive, partial match).**

    **Args:**\n
        name_query (Optional[str]): An optional string to filter employees by name.\n
        employee_service (EmployeeService): The injected EmployeeService instance.

    **Returns:**
        List[employee_schemas.Employee]: A list of all employees,\n
        if name_query provided: A list of all employees matching the name query.

    **Raises:**
       HTTPException: - 422 Unprocessable Entity, Pydantic: If the input data is invalid.

    """

    employees = employee_service.get_all_employees(name_query=name_query)

    return employees

@employees_router.patch("/{employee_id}", response_model=schemas.Employee, status_code=status.HTTP_200_OK)
def update_employee(
        employee_id: UUID,
        employee_update_data: EmployeeUpdate,
        employee_service: EmployeeService = Depends(get_employee_service)
):
    """ **Endpoint to update at least one field of an existing employee.**

    **Please ensure to send at least one field to be updated.** \n
    **Also only execute used fields as otherwise the examples are going to be updated.**

    **"name": optional**\n
    **"phone_number": optional**\n
    **"username": optional**\n
    **"hashed_password": optional**\n
    **"email": optional**\n
    **"role": optional**\n
    **"is_authenticated": optional**\n

    **Args:**\n
        employee_id (UUID): A unique identifier in UUID format.\n
        employee_update_data (EmployeeUpdate): An EmployeeUpdate object containing the updates.\n
        employee_service (EmployeeService): The injected EmployeeService instance.

    **Returns:**\n
        db_employee: The updated Employee object.

    **Raises:**\n
        HTTPException:\n
            - 404 Not found: If the ID searched after does not match with an
            employee from the database.\n
            - 400 Bad request: If there is a database error like unique constraint violation
            (for example same phone number or e-mail)\n
            - 422 Unprocessable Entity, Pydantic: If the input data is invalid.

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
    """ **Endpoint to delete an employee by id.**

    **Args:**\n
        employee_id (UUID): A unique identifier in UUID format.\n
        employee_service (EmployeeService): The injected EmployeeService instance.

    **Returns:**\n
        Response(status_code=status.HTTP_204_NO_CONTENT): Returns a response without body.

    **Raises:**\n
        HTTPException:\n
            - HTTP 404 Not Found: If the employee cannot be found by the passed ID.
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
