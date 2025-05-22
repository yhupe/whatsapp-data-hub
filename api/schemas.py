import uuid
import datetime
from typing import Optional
from enum import Enum as PyEnum

# Import BaseModel and ConfigDict for pydantic v2+
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

# IMport of Enums from SQLAlchemy models
from database.models import UserRole, MessageDirection, MessageStatus


class EmployeeBase(BaseModel):
    """ Pydantic model for Employee.
    Common field for create and read requests.
    """

    name: str = Field(min_length=1, max_length=255)
    whatsapp_phone_number: str = Field(pattern=r"^\+\d{10,15}$")
    email: EmailStr
    role: UserRole


class EmployeeCreate(EmployeeBase):
    """ Pydantic model for creating an Employee.
    But id, created_at, updated_at, magic_link_token etc. will be
    created by the server automatically and are not part of create request.
    Optionally for later.
    """

    pass


class EmployeeUpdate(EmployeeBase):
    """ Pydantic model for updating an Employee.
    All fields are optional because you don't want to update everything at the same time
    """

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    whatsapp_phone_number: Optional[str] = Field(None, pattern=r"^\+\d{10,15}$")
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None

    @model_validator(mode='after')
    def check_at_least_one_field(self):
        """ Validation that at least one field is being updated.
        model_dump(exclude_none=True) returns all fields that are not 'None'.

        Raises: ValueError: If no field is given (or not 'None') to update

        Returns: self: The current instance of EmployeeUpdate object that's being validated
        """

        # check that at least one field is not 'None'
        if not any(self.model_dump(exclude_none=True).values()):
            raise ValueError(
                "At least one field (name, whatsapp_phone_number, email, role) must be provided for update.")
        return self


class Employee(EmployeeBase):
    """ Model (inheriting from EmployeeBase) for the response of the API.
    Typically containing all fields that are relevant for the client, including
    server-generated fields.
    """

    id: uuid.UUID
    magic_link_token: Optional[str] = None
    magic_link_expires_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # Config allows Pydantic to load data from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)



class WhatsappMessageLogBase(BaseModel):
    """ Pydantic model for WhatsappMessageLog. """

    employee_id: Optional[uuid.UUID] = None
    whatsapp_customer_phone_number: str = Field(pattern=r"^\+\d{10,15}$")
    direction: MessageDirection
    raw_message_content: str
    status: MessageStatus


class WhatsappMessageLogCreate(WhatsappMessageLogBase):
    """ Pydantic model for creating a WhatsappMessageLog entry.
    Fields like id, timestamp, AI interpretation, and system response
    are created by the server automatically
    and are not part of the create request.
    """

    pass


class WhatsappMessageLog(WhatsappMessageLogBase):
    """ Model (inheriting from WhatsappMessageLogBase) for the response of the API.
    Typically containing all fields that are relevant for the client, including
    server-generated fields and fields added during processing.
    """

    id: uuid.UUID
    ai_interpreted_command: Optional[str] = None
    system_response_content: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime.datetime

    # Config allows Pydantic to load data from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)