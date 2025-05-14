# import of standard python libraries
import uuid
import datetime
from enum import Enum as PyEnum

# import of types and functions from SQLAlchemy
from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String
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
    """ Definition of ORM model class 'User' """

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

