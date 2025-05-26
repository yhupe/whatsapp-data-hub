from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, Any

from database import models
from database.database import get_db
from api.schemas import MessageLogCreate, MessageLog
from api.schemas import Employee
from services.message_log_service import MessageLogService, get_message_log_service
from services.employee_service import EmployeeService, get_employee_service

from fastapi import Depends


class MessageProcessingService:
    def __init__(self, db: Session,
                 message_log_service: MessageLogService,
                 employee_service: EmployeeService):
        """
        Initializes the MessageProcessingService with a db-session
        and dependencies to other services.
        """

        self.db = db
        self.message_log_service = message_log_service
        self.employee_service = employee_service


    async def process_inbound_message(
        self,
        employee_id: Optional[UUID],
        whatsapp_customer_phone_number: str,
        raw_message_content: str
    ) -> MessageLog:
        """
        Processes an inbound message.
        Saves message to MessageLog Table.
        """

        # Saving message to database
        message_log_data = MessageLogCreate(
            employee_id=employee_id,
            whatsapp_customer_phone_number=whatsapp_customer_phone_number,
            direction=models.MessageDirection.inbound,
            raw_message_content=raw_message_content,
            status=models.MessageStatus.received
        )
        db_message_log = self.message_log_service.create_message_log(message_log_data=message_log_data)

        print(f"Inbound message logged (ID: {db_message_log.id}): '{raw_message_content}'")

        return db_message_log

# Dependency for FastAPI-Router or Bot
def get_message_processing_service(
    db: Session = Depends(get_db),
    message_log_service: MessageLogService = Depends(get_message_log_service),
    employee_service: EmployeeService = Depends(get_employee_service)
) -> MessageProcessingService:
    """
    Dependency that returns an instance of MessageProcessingService.
    """
    return MessageProcessingService(db=db,
                                    message_log_service=message_log_service,
                                    employee_service=employee_service)