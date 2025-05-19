import uuid
import datetime
from typing import Optional
from enum import Enum as PyEnum

# Import BaseModel and ConfigDict for pydantic v2+
from pydantic import BaseModel, ConfigDict

# IMport of Enums from SQLAlchemy models
from database.models import UserRole, MessageDirection, MessageStatus


class EmployeeBase(BaseModel):
    """ Pydantic model for Employee.
    Common field for create and read requests.
    """

    name: str
    whatsapp_phone_number: str
    email: str
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

    name: Optional[str] = None
    whatsapp_phone_number: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None


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