from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy import desc
from typing import Optional, Any

from database import models
from api.schemas import MessageLogCreate
from database.database import get_db
from fastapi import Depends


class MessageLogService:
    def __init__(self, db: Session):
        """
        Initializes the MessageLogService with a db-session.
        """

        self.db = db

    def create_message_log(
        self,
        message_log_data: MessageLogCreate
    ) -> models.WhatsappMessageLog:

        """
        Creates a new message log entry in the database.
        """

        db_message_log = models.WhatsappMessageLog(
            employee_id=message_log_data.employee_id,
            direction=message_log_data.direction,
            raw_message_content=message_log_data.raw_message_content,
            status=message_log_data.status
        )

        self.db.add(db_message_log)
        self.db.commit()
        self.db.refresh(db_message_log)
        return db_message_log


    def get_latest_message_log(self) -> Optional[models.WhatsappMessageLog]:
        """
        Retrieves the most recently added message log entry.
        """
        return (
            self.db.query(models.WhatsappMessageLog)
            .order_by(desc(models.WhatsappMessageLog.timestamp))
            .first()
        )

# Dependency for FastAPI-Router
# Function is used by FastAPI as dependency to inject a service instance
def get_message_log_service(db: Session = Depends(get_db)) -> MessageLogService:
    """
    Dependency that returns an instance of EmployeeService.
    """
    return MessageLogService(db)