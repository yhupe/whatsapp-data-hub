# Import of engine and Base from database.py
from database.database import engine, Base

# import of all ORM models -> hint for SQLAlchemy what classes inherit from Base
# and therefore are tables
from database.models import Employee, Partner, Product, WhatsappMessageLog

print("Dropping database tables...")

# Drops all tables
Base.metadata.drop_all(bind=engine)

print("Database tables dropped successfully!")