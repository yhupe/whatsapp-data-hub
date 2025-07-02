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
                models.Employee.phone_number == employee_data.phone_number,
                models.Employee.email == employee_data.email
            )
        ).first()

        if db_employee:
            raise ValueError("Employee with this phone number or email already exists.")

        new_employee = models.Employee(
            name=employee_data.name,
            username=employee_data.username,
            hashed_password=employee_data.hashed_password,
            phone_number=employee_data.phone_number,
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

    def get_employee_by_telegram_id(self, telegram_id: int) -> Optional[models.Employee]:
        """
        Retrieves an employee by Telegram ID.
        """

        return self.db.query(models.Employee).filter(models.Employee.telegram_id == telegram_id).first()

    def get_employee_by_phone_number(self, phone_number: str) -> Optional[models.Employee]:
        """
        Retrieves an employee by  phone number.
        """

        return self.db.query(models.Employee).filter(models.Employee.phone_number == phone_number).first()

    def update_employee_telegram_details(self, employee_id: UUID, telegram_id: Optional[int] = None) -> Optional[models.Employee]:
        """
        Updates specific telegram related details (telegram_id) of an existing employee.
        """

        db_employee = self.db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        if db_employee:
            changed = False
            if telegram_id is not None and db_employee.telegram_id != telegram_id:
                db_employee.telegram_id = telegram_id
                changed = True


            if changed:
                try:
                    self.db.commit()
                    self.db.refresh(db_employee)
                    print(f"Employee ({employee_id}) telegram ID has been updated.")
                    return db_employee
                except Exception as e:
                    self.db.rollback()
                    print(f"ERROR: Error while updating telegram ID for employee {employee_id}: {e}")
                    raise
            else:
                return db_employee
        return None

    def set_employee_authenticated_status(self, employee_id: UUID, status: bool) -> Optional[models.Employee]:
        """
        Sets authentification status of an employee.
        """

        db_employee = self.db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        if db_employee:
            db_employee.is_authenticated = status
            try:
                self.db.commit()
                self.db.refresh(db_employee)
                print(f"Employee ({employee_id}) authentification status now set to 'is_authenticated = {status}'.")
                return db_employee
            except Exception as e:
                self.db.rollback()
                print(f"ERROR: Error while setting authentification status for employee {employee_id}: {e}")
                raise
        return None


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
            raise ValueError("Employee not found")

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
            raise ValueError("Employee not found")

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