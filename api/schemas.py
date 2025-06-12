import uuid
import datetime
from typing import Optional, Any
from decimal import Decimal
from enum import Enum as PyEnum

# Import BaseModel and ConfigDict for pydantic v2+
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from sqlalchemy import Boolean

# IMport of Enums from SQLAlchemy models
from database.models import UserRole, MessageDirection, MessageStatus


class EmployeeBase(BaseModel):
    """ Pydantic model for Employee.
    Common field for create and read requests.
    """

    name: str = Field(min_length=1, max_length=255)
    phone_number: str = Field(pattern=r"^\+\d{10,15}$")
    telegram_id : Optional[int] = None
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
    phone_number: Optional[str] = Field(None, pattern=r"^\+\d{10,15}$")
    telegram_id: Optional[int] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_authenticated: Optional[bool] = None

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
                "At least one field (name, phone_number, email, role) must be provided for update.")
        return self


class Employee(EmployeeBase):
    """ Model (inheriting from EmployeeBase) for the response of the API.
    Typically containing all fields that are relevant for the client, including
    server-generated fields.
    """

    id: uuid.UUID
    magic_link_token: Optional[str] = None
    magic_link_expires_at: Optional[datetime.datetime] = None
    is_authenticated: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # Config allows Pydantic to load data from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)



class MessageLogBase(BaseModel):
    """ Pydantic model for MessageLog. """

    employee_id: Optional[uuid.UUID] = None
    phone_number: str
    direction: MessageDirection
    raw_message_content: str
    status: MessageStatus


class MessageLogCreate(MessageLogBase):
    """ Pydantic model for creating a MessageLog entry.
    Fields like id, timestamp, AI interpretation, and system response
    are created by the server automatically
    and are not part of the create request.
    """
    system_response_content: Optional[str] = None
    ai_interpreted_command: Optional[Any] = None


class MessageLogUpdate(BaseModel):
    """ Pydantic model for updating a message log.
        All fields are optional because you don't want
        to update everything at the same time.
        """

    system_response_content: Optional[str] = None
    ai_interpreted_command: Optional[Any] = None
    direction: Optional[MessageDirection] = None
    error_message: Optional[str] = None
    status: Optional[MessageStatus] = None


class MessageLog(MessageLogBase):
    """
    Model (inheriting from MessageLogBase) for the response of the API.
    Typically containing all fields that are relevant for the client, including
    server-generated fields and fields added during processing.
    """

    id: uuid.UUID
    raw_message_content : str
    ai_interpreted_command: Optional[str] = None
    system_response_content: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime.datetime

    # Config allows Pydantic to load data from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    """ Pydantic model for Products. """

    name : str = Field(min_length=1, max_length=255)
    description : Optional[str] = Field(None)
    length : Optional[Decimal] = Field(None)
    height : Optional[Decimal] = Field(None)
    width : Optional[Decimal] = Field(None)
    weight : Optional[Decimal] = Field(None)
    image_url : Optional[str] = Field(None)
    price : Decimal = Field(gt=0)
    stock_quantity : int = Field(0, ge=0)
    is_active : bool = Field(True)
    notes : Optional[str] = Field(None)


class ProductCreate(ProductBase):
    """
    Pydantic model for creating a Product entry.
    Fields like id and timestamps
    are created by the server automatically
    and are not part of the create request.
    """

    pass


class ProductUpdate(BaseModel):
    """
    Pydantic model for updating a message log.
    All fields are optional because you don't want
    to update everything at the same time.
    """

    name : Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    length: Optional[Decimal] = None
    height: Optional[Decimal] = None
    width: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    image_url: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    notes: Optional[str] = None

    model_config = ConfigDict(extra='ignore')

    @model_validator(mode='after')
    def check_at_least_one_field(self):
        """ Validation that at least one field is being updated.
        model_dump(exclude_none=True) returns all fields that are not 'None'.

        Raises: ValueError: If no field is given (or not 'None') to update

        Returns: self: The current instance of ProductUpdate object that's being validated
        """

        # check that at least one field is not 'None'
        if not any(self.model_dump(exclude_none=True).values()):
            raise ValueError(
                "At least one field (name, description, size, price etc.) must be provided for update.")
        return self




class Product(ProductBase):
    """
    Model (inheriting from ProductBase) for the response of the API.
    Typically containing all fields that are relevant for the client, including
    server-generated fields and fields added during processing.
    """

    id : uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # Config allows Pydantic to load data from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)