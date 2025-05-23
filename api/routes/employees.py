# Import of necessary parts of FastAPI
from dns.e164 import query
from fastapi import APIRouter, Depends, HTTPException, status, Response

# Import of or_ module as a filtering condition to avoid using '|'
from sqlalchemy import or_

# Import of SQLAlchemy Session (for type hints)
from sqlalchemy.orm import Session

from api.schemas import EmployeeUpdate
# Import of SQLAlchemy ORM models
from database import models

# Import of Pydantic schemas
from api import schemas

# Import of database dependency
from database.database import get_db

from uuid import UUID
from typing import List, Optional


# Creates APIRouter instance
employees_router = APIRouter(
    prefix="/employees",
    tags=["employees"],
)

@employees_router.post("/", response_model=schemas.Employee, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db)
):
    """ Endpoint to create a new employee.

    Args:
        employee (schemas.EmployeeCreate): The Pydantic model containing the details
            for a new employee.
        db (Session = Depends(get_db)): The database session dependency.

    Returns: db_employee: The newly created employee object incl. the automatically generated
        ID and timestamps.

    Raises:
        HTTPException: If the provided phone number or e-mail address is
            already in the database (HTTP 400 Bad Request).
    """

    # Check whether an employee with the exact e-mail / phone number already exists
    db_employee = db.query(models.Employee).filter(
        or_(
            models.Employee.whatsapp_phone_number == employee.whatsapp_phone_number,
            models.Employee.email == employee.email
        )
    ).first()

    if db_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this phone number or email already exists."
        )

    db_employee = models.Employee(
        name=employee.name,
        whatsapp_phone_number=employee.whatsapp_phone_number,
        email=employee.email,
        role=employee.role
    )

    db.add(db_employee)

    db.commit()

    db.refresh(db_employee)

    return db_employee


@employees_router.get("/{employee_id}", response_model=schemas.Employee, status_code=status.HTTP_200_OK)
def get_employee_by_id(
    employee_id: UUID,
    db: Session = Depends(get_db)
):
    """ Endpoint to get an employee by ID.

    Args:
        employee_id (UUID): A unique identifier in UUID format.
        db (Session = Depends(get_db)): The database session dependency.

    Returns: db_employee: The newly created employee object incl. the automatically generated
        ID and timestamps.

    Raises: HTTPException: If the employee cannot be found by the passed ID (HTTP 404 Not Found)

    """

    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    return db_employee


@employees_router.get("/", response_model=List[schemas.Employee])
def get_employees(
        name_query: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """ Endpoint to retrieve list of employees.
    case-insensitive, if name_query is provided, filters employees
    by name (case-insensitive, partial match).

    Args:
        name_query (Optional[str]): An optional string to filter employees by name.
        db (Session = Depends(get_db)): The database session dependency.

    Returns: List[employee_schemas.Employee]: A list of all employees,
        if name_query provided: A list of all employees matching the name query.

    """

    # 'query' is set to query all instances in the Employee table
    query = db.query(models.Employee)

    # if optional 'name_query' is provided, query is set to all instances matching the filter
    if name_query:
        query = query.filter(models.Employee.name.ilike(f"%{name_query}%"))

    employees = query.all()

    return employees

@employees_router.patch("/{employee_id}", response_model=schemas.Employee, status_code=status.HTTP_200_OK)
def update_employee(
        employee_id: UUID,
        employee_update: EmployeeUpdate,
        db: Session = Depends(get_db)
):
    """ Endpoint to update at least one field of an existing employee.

    Args:
        employee_id (UUID): A unique identifier in UUID format.
        employee_update (EmployeeUpdate): An EmployeeUpdate object containing the updates.
        db (Session = Depends(get_db)): The database session dependency.

    Returns: db_employee: The updated Employee object.

    Raises:
        HTTPException:
            - 404 Not found: If the ID searched after does not match with an
            employee from the database.
            - 400 Bad request: If there is a database error like unique constraint violation
            (for example same phone number or e-mail)
            - 422 Unprocessable Entity: If the input data is invalid (Pydantic)


    """

    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()

    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Extracting updated fields from employee_update object.
    update_data = employee_update.model_dump(exclude_unset=True)

    # updated fields of the Employee object
    for key, value in update_data.items():
        # sets the attribute directly to the new value
        setattr(db_employee, key, value)

    try:
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee

    except Exception as e:
        db.rollback()

        # If the database throws an error, check if it has the 'orig' attribute from
        # the original database error exception and raise it. If not, show the SQLAlchemy error exception.
        error_detail = str(e.orig) if hasattr(e, 'orig') else str(e)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating employee: {error_detail}"
        )


@employees_router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_by_id(
        employee_id: UUID,
        db: Session = Depends(get_db)
):
    """ Endpoint to delete an employee by id.

    Args:
        employee_id (UUID): A unique identifier in UUID format.
        db (Session = Depends(get_db)): The database session dependency.

    Returns: Response(status_code=status.HTTP_204_NO_CONTENT): Returns a response without body.

    Raises:
        HTTPException: If the employee cannot be found by the passed ID (HTTP 404 Not Found)
    """

    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()

    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    db.delete(db_employee)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

