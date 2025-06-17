# import of standard python libraries
import uuid
import datetime
from enum import Enum as PyEnum

# import of types and functions from SQLAlchemy
from sqlalchemy import (
    Boolean, BigInteger, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
)

# import of postgreSQL specific types from SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, JSONB

# import of relationship function to define relationships between models
from sqlalchemy.orm import relationship

# import of Base class from which all ORM models will inherit
from .database import Base


class UserRole(PyEnum):
    """ Class to define user role Enums according to DBMS scheme"""
    admin = "admin"
    general_user = "general_user"

class MessageDirection(PyEnum):
    """ Class to define message direction Enums according to DBMS scheme.
    Can be either incoming (inbound) or outgoing (outbound) message.
    """

    inbound = "inbound"
    outbound = "outbound"

class MessageStatus(PyEnum):
    """ Class to define status of message Enums according to DBMS scheme"""

    received = "received"
    processed = "processed"
    sent = "sent"
    error = "error"


class Employee(Base):
    """ Definition of ORM model class/ table 'Employee' """

    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    username = Column(String)
    hashed_password = Column(String)
    phone_number = Column(String, unique=True, nullable=False, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False)
    is_authenticated = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc),
                        onupdate=datetime.datetime.now(datetime.timezone.utc))

    # Definition of relationship to other models
    managed_products = relationship("Product", back_populates="product_manager")
    message_logs = relationship("MessageLog", back_populates="employee")


class Product(Base):
    """ Definition of ORM model class/ table 'Product' """

    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    product_manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    description = Column(Text)
    length = Column(Numeric(10, 2))
    height = Column(Numeric(10, 2))
    width = Column(Numeric(10, 2))
    weight = Column(Numeric(10, 2))
    image_url = Column(String)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))

    # Definition of relationship to other models
    product_manager = relationship("Employee", back_populates="managed_products")

class MessageLog(Base):
    """ Definition of ORM model class/ table 'MessageLog' """

    __tablename__ = "message_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    phone_number = Column(String, nullable=False, index=True)
    direction = Column(Enum(MessageDirection), nullable=False)
    raw_message_content = Column(Text, nullable=False)
    ai_interpreted_command = Column(JSONB)
    system_response_content = Column(String, nullable=True)
    status = Column(Enum(MessageStatus), nullable=False)
    error_message = Column(Text)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc), index=True)

    # Definition of relationship to other models
    employee = relationship("Employee", back_populates="message_logs")