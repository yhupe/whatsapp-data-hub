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
    message_log: schemas.MessageLogCreate,
    db: Session = Depends(get_db)
):
    """ Endpoint to create message logs.

    Args:
        message_log (schemas.MessageLogCreate): The Pydantic model containing the details
            for a new message log.
        db (Session = Depends(get_db)): The database session dependency.

    Returns: db_message_log: The newly created message_log object incl. the automatically generated
        ID and timestamp.

    Raises:
        HTTPException: If the input data is invalid (422 Unprocessable Entity, Pydantic)

    """

    db_message_log = models.WhatsappMessageLog(
        employee_id=message_log.employee_id,
        direction=message_log.direction,
        raw_message_content=message_log.raw_message_content,
        status=message_log.status
    )

    db.add(db_message_log)

    db.commit()

    db.refresh(db_message_log)

    return db_message_log


@message_log_router.get("/last", response_model=schemas.MessageLog, status_code=status.HTTP_200_OK)
def get_latest_message_log(
    #message_log: schemas.MessageLog,
    db: Session = Depends(get_db)
):
    """ Endpoint to get message logs and print them as logs to the console.

        Args:
            message_log (schemas.MessageLog): The Pydantic model containing the details
                for a new message log.
            db (Session = Depends(get_db)): The database session dependency.

        Returns: db_message_log:

        Raises:
            HTTPException:
                - 404 Not Found : If no message log was found
                - 422 Unprocessable Entity, Pydantic: If the input data is invalid
        """

    # Querying the latest added message to the table by sorting in descending order by timestamp
    db_message_log = (db.query(models.WhatsappMessageLog)
                      .order_by(desc(models.WhatsappMessageLog.timestamp))
                      .first()
                      )

    if not db_message_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No message logs found."
        )

    # extracting Employee.name from employee_id in message_log
    db_employee = db.query(models.Employee).filter(models.Employee.id == db_message_log.employee_id).first()

    # Logging new message status to the console
    print(f"Message log: from/to: '{db_employee.name}', "
          f"Status={db_message_log.status.value}, "
          f"Direction={db_message_log.direction.value}, "
          f"Content='{db_message_log.raw_message_content}'")

    return db_message_log