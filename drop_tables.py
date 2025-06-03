# Import environment variables
import os
from dotenv import load_dotenv
load_dotenv()

# Import of engine and Base from database.py
from database.database import get_engine, Base

# import of all ORM models -> hint for SQLAlchemy what classes inherit from Base
# and therefore are tables
from database.models import Employee, Partner, Product, MessageLog

engine = get_engine()
print(f"Connecting to engine at {engine.url}")

print("Dropping database tables...")

# Drops all tables
Base.metadata.drop_all(bind=engine)

print("Database tables dropped successfully!")