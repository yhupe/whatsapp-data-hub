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


# Creates APIRouter instance
message_log_router = APIRouter(
    prefix="/message_log",
    tags=["message_log"],
)

@message_log_router.post("/", response_model=schemas.MessageLog, status_code=status.HTTP_201_CREATED)
def create_message_log(
    message_log: schemas.MessageLogCreate,
    db: Session = Depends(get_db),

):

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
