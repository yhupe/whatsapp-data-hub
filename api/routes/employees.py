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
    """ Endpoint to create a new employee """

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
