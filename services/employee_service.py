from sqlalchemy.orm import Session
from sqlalchemy import or_
from uuid import UUID
from typing import List, Optional

from database import models
from api.schemas import EmployeeCreate, EmployeeUpdate
from database.database import get_db
from fastapi import Depends, HTTPException

class EmployeeService:
    def __init__(self, db: Session):
        """
        Initializes the EmployeeService with a db-session.
        """
        self.db = db

    def create_employee(
        self,
        employee_data: EmployeeCreate
    ) -> models.Employee:
        """
        Creates a new employee in the database.
        Includes checking for existing phone number or email.
        """

        # Check whether an employee with the exact e-mail / phone number already exists
        db_employee = self.db.query(models.Employee).filter(
            or_(
                models.Employee.whatsapp_phone_number == employee_data.whatsapp_phone_number,
                models.Employee.email == employee_data.email
            )
        ).first()

        if db_employee:
            raise ValueError("Employee with this phone number or email already exists.")

        new_employee = models.Employee(
            name=employee_data.name,
            whatsapp_phone_number=employee_data.whatsapp_phone_number,
            email=employee_data.email,
            role=employee_data.role
        )

        self.db.add(new_employee)
        self.db.commit()
        self.db.refresh(new_employee)
        return new_employee

    def get_employee_by_id(self, employee_id: UUID) -> Optional[models.Employee]:
        """
        Retrieves an employee by ID.
        """

        return self.db.query(models.Employee).filter(models.Employee.id == employee_id).first()

    def get_all_employees(self, name_query: Optional[str] = None) -> List[models.Employee]:
        """
        Retrieves a list of employees, optionally filtered by name.
        """
        query = self.db.query(models.Employee)

        if name_query:
            query = query.filter(models.Employee.name.ilike(f"%{name_query}%"))

        employees = query.all()
        return employees

    def update_employee(
        self,
        employee_id: UUID,
        employee_update_data: EmployeeUpdate
    ) -> Optional[models.Employee]:
        """
        Updates an existing employee's fields.
        Handles unique constraint violations.
        """

        db_employee = self.get_employee_by_id(employee_id)

        if not db_employee:
            raise ValueError("Employee not found.")

        update_data = employee_update_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_employee, key, value)

        try:
            self.db.add(db_employee)
            self.db.commit()
            self.db.refresh(db_employee)
            return db_employee

        except Exception as e:
            self.db.rollback()
            error_detail = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise ValueError(f"Database error updating employee: {error_detail}")

    def delete_employee(self, employee_id: UUID) -> bool:
        """
        Deletes an employee by ID.
        Returns True if deleted, False if not found.
        """

        db_employee = self.get_employee_by_id(employee_id)

        if not db_employee:
            raise ValueError("Employee not found.")

        self.db.delete(db_employee)
        self.db.commit()
        return True


# Dependency for FastAPI-Router
# Function is used by FastAPI as dependency to inject a service instance
def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    """
    Dependency that returns an instance of EmployeeService
    """

    return EmployeeService(db)