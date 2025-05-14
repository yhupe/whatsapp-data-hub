# import of standard python libraries
import uuid
import datetime
from enum import Enum as PyEnum

# import of types and functions from SQLAlchemy
from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
)

# import of postgreSQL specific types from SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, JSONB

# import of relationship function to define relationships between models
from sqlalchemy.orm import relationship

# import of Base class from which all ORM models will inherit
from .database import Base


class UserRole(PyEnum):
    """Class to define user role Enums according to DBMS scheme"""
    admin = "admin"
    general_user = "general_user"

class MessageDirection(PyEnum):
    """Class to define message direction Enums according to DBMS scheme.
    Can be either incoming (inbound) or outgoing (outbound) message.
    """

    inbound = "inbound"
    outbound = "outbound"

class MessageStatus(PyEnum):
    """Class to define status of whatsapp message Enums according to DBMS scheme"""

    received = "received"
    processed = "processed"
    sent = "sent"
    error = "error"


class User(Base):
    """ Definition of ORM model class/ table 'User' """

    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4())
    name = Column(String)
    whatsapp_phone_number = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False)
    magic_link_token = Column(String, index=True)
    magic_link_expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc),
                        onupdate=datetime.datetime.now(datetime.timezone.utc))

    # Definition of relationship to other models
    partners = relationship("Partner", back_populates="main_contact_user")
    message_logs = relationship("WhatsappMessageLog", back_populates="user")


class Partner(Base):
    """ Definition of ORM model class/ table 'Partner' """

    __tablename__ = "partners"

    partner_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    contact_person = Column(String)
    email = Column(String)
    phone_number = Column(String)
    address_street = Column(String)
    address_city = Column(String)
    address_zip_code = Column(String)
    address_country = Column(String)
    notes = Column(Text)
    main_contact_user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))

    # Definition of relationship to other models
    main_contact_user = relationship("User", back_populates="partners")


class Product(Base):
    """ Definition of ORM model class/ table 'Product' """

    __tablename__ = "products"

    product_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
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


class WhatsappMessageLog(Base):
    """ Definition of ORM model class/ table 'WhatsappMessageLog' """

    __tablename__ = "whatsapp_message_logs"

    message_log_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True, nullable=True)
    direction = Column(Enum(MessageDirection), nullable=False)
    raw_message_content = Column(Text, nullable=False)
    ai_interpreted_command = Column(JSONB)
    system_response_content = Column(Text)
    status = Column(Enum(MessageStatus), nullable=False)
    error_message = Column(Text)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc), index=True)

    # Definition of relationship to other models
    user = relationship("User", back_populates="message_logs")