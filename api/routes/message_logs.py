# Import of necessary parts of FastAPI
from dns.e164 import query
from fastapi import APIRouter, Depends, HTTPException, status, Response

# Import of SQLAlchemy Session (for type hints)
from sqlalchemy.orm import Session

# Import of SQLAlchemy ORM models
from database import models

# Import of Pydantic schemas
from api import schemas

# Import of database dependency
from database.database import get_db

# Import of MessageLogService
from services.message_log_service import MessageLogService, get_message_log_service

from uuid import UUID
from typing import List, Optional
from sqlalchemy import desc


# Creates APIRouter instance
message_log_router = APIRouter(
    prefix="/message_log",
    tags=["message_log"],
)

@message_log_router.post("/", response_model=schemas.MessageLog, status_code=status.HTTP_201_CREATED)
def create_message_log(
        message_log_data: schemas.MessageLogCreate,
        message_log_service: MessageLogService = Depends(get_message_log_service)
):
    """ Endpoint to create message logs.

    Args:
        message_log_data (MessageLogCreate): The Pydantic model containing the details
            for a new message log.
        message_log_service (MessageLogService): The injected message log service instance.

    Returns: db_message_log: The newly created message_log object incl. the automatically generated
        ID and timestamp.

    Raises:
        HTTPException: If the input data is invalid (422 Unprocessable Entity, Pydantic)

    """

    if message_log_data.employee_id:
        db_employee = message_log_service.db.query(models.Employee).filter(
            models.Employee.id == message_log_data.employee_id).first()
        if not db_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID {message_log_data.employee_id} not found."
            )

    db_message_log = message_log_service.create_message_log(message_log_data=message_log_data)  # <-- Aufruf des Service

    return db_message_log


@message_log_router.get("/last", response_model=schemas.MessageLog, status_code=status.HTTP_200_OK)
def get_latest_message_log(
    message_log_service: MessageLogService = Depends(get_message_log_service)
):
    """ Endpoint to get message logs and print them as logs to the console.

        Args:
            message_log_service (MessageLogService): The injected message log service instance.

        Returns: db_message_log:

        Raises:
            HTTPException:
                - 404 Not Found : If no message log was found
                - 422 Unprocessable Entity, Pydantic: If the input data is invalid
        """

    db_message_log = message_log_service.get_latest_message_log()

    if not db_message_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No message logs found."
        )

    db_employee = None
    if db_message_log.employee_id:
        db_employee = message_log_service.db.query(models.Employee).filter(
            models.Employee.id == db_message_log.employee_id).first()

    employee_name = db_employee.name if db_employee else "N/A (Employee not found)"

    # Logging new message status to the console
    print(f"Message log: from/to: '{employee_name}', "
          f"Status={db_message_log.status.value}, "
          f"Direction={db_message_log.direction.value}, "
          f"Content='{db_message_log.raw_message_content}'")

    return db_message_log