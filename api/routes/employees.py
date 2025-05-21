# Import of necessary parts of FastAPI
from fastapi import APIRouter, Depends, HTTPException, status

# Import of or_ module as a filtering condition to avoid using '|'
from sqlalchemy import or_

# Import of SQLAlchemy Session (for type hints)
from sqlalchemy.orm import Session

# Import of SQLAlchemy ORM models
from database import models

# Import of Pydantic schemas
from api import schemas

# Import of database dependency
from database.database import get_db

import uuid
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

