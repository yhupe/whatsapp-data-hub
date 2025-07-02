import uuid
import datetime
from typing import Optional, Any
from decimal import Decimal
from enum import Enum as PyEnum

# Import BaseModel and ConfigDict for pydantic v2+
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from pydantic.v1 import UUID4
from sqlalchemy import Boolean

# IMport of Enums from SQLAlchemy models
from database.models import UserRole, MessageDirection, MessageStatus


class EmployeeBase(BaseModel):
    """ Pydantic model for Employee.
    Common field for create and read requests.
    """

    name: str = Field(min_length=1, max_length=255, examples=["Employee Dummy"], description="Mandatory: here goes the employee full name.")
    phone_number: str = Field(pattern=r"^\+\d{10,15}$", examples=["+4917641208453"], description="Mandatory: here goes the employees phone number.")
    username: Optional[str] = Field(None, min_length=1, max_length=255, examples=["dummy321"], description="Optional: here goes the employees username.")
    hashed_password: Optional[str] = Field(None, min_length=8, max_length=255, examples=["find a strong password!"], description="Optional: here goes the employees personal password.")
    email: EmailStr = Field(examples=["dummy@example.com"], description="Mandatory: here goes the employees email address.")
    role: UserRole = Field(examples=["general_user", "admin"], description="Mandatory: here goes the employees role.")


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

    name: Optional[str] = Field(Field("Optional, str"), min_length=1, max_length=255)
    phone_number: Optional[str] = Field(Field("Optional, str"), pattern=r"^\+\d{10,15}$")
    username: Optional[str] = Field("Optional, str")
    hashed_password: Optional[str] = Field("Optional, str")
    email: Optional[EmailStr] = Field("Optional, EmailStr")
    role: Optional[UserRole] = Field("Optional, 'general_user' or 'admin'")
    is_authenticated: Optional[bool] = Field("Optional, true or false")

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
    ai_interpreted_command: Optional[str] = None


class MessageLogUpdate(BaseModel):
    """ Pydantic model for updating a message log.
        All fields are optional because you don't want
        to update everything at the same time.
        """

    system_response_content: Optional[str] = None
    ai_interpreted_command: Optional[str] = None
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
    ai_interpreted_command: Optional[str] = None
    system_response_content: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime.datetime

    # Config allows Pydantic to load data from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    """ Pydantic model for Products. """

    name : str = Field(min_length=1, max_length=255, examples=["Product A"], description="Mandatory: here goes the product name.")
    description : Optional[str] = Field(None, examples=["This is a very nice product!"], description="Optional: here goes an text to describe the product.")
    product_manager_id: Optional[uuid.UUID] = Field(None, examples=["7ed60d8d-ef12-4cd2-910f-05cd423bf21c"], description="UUID of the employee assigned as product manager.")
    length : Optional[Decimal] = Field(None, examples=["20.00"], description="Optional: length of the product in cm.")
    height : Optional[Decimal] = Field(None, examples=["10.00"], description="Optional: height of the product in cm.")
    width : Optional[Decimal] = Field(None, examples=["5.50"], description="Optional: width of the product in cm.")
    weight : Optional[Decimal] = Field(None, examples=["2.50"], description="Optional: weight of the product in kg.")
    image_url : Optional[str] = Field(None, examples=["www.here-goes-the-link.com"], description="Optional: URL to a picture of the product.")
    price : Decimal = Field(gt=0, examples=["20.00"], description="Mandatory: price of the product in €.")
    stock_quantity : int = Field(ge=0, examples=["20.00"], description="Mandatory: stock quantity of the product.")
    is_active : bool = Field(True, examples=["true", "false"], description="Mandatory: true if actively selling, false if not actively selling or qty < 1.")
    notes : Optional[str] = Field(None, examples=["An internal note about the product :)"], description="Optional: here goes an internal note about the product.")


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

    name : Optional[str] = Field("Optional, str", min_length=1, max_length=255)
    description: Optional[str] = Field("Optional, str")
    product_manager_id: Optional[uuid.UUID] = Field("Optional, uuid")
    length: Optional[Decimal] = Field("Optional, decimal")
    height: Optional[Decimal] = Field("Optional, decimal")
    width: Optional[Decimal] = Field("Optional, decimal")
    weight: Optional[Decimal] = Field("Optional, decimal")
    image_url: Optional[str] = Field("Optional, str")
    price: Optional[Decimal] = Field("Optional, decimal, > 0", gt=0)
    stock_quantity: Optional[int] = Field("Optional, int, >= 0", ge=0)
    is_active: Optional[bool] = Field("Optional, true or false")
    notes: Optional[str] = Field("Optional, str")

    model_config = ConfigDict(extra='ignore')

    @model_validator(mode='after')
    def check_at_least_one_field(self):
        """ Validation that at least one field is being updated.
        model_dump(exclude_none=True) returns all fields that are not 'None'.

        Raises: ValueError: If no field is given (or not 'None') to update

        Returns: self: The current instance of ProductUpdate object that's being validated
        """

        # check that at least one field is not 'None'
        if not self.model_fields_set:
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
    product_manager: Optional[EmployeeBase] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # Config allows Pydantic to load data from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)