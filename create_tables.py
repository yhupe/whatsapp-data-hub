# Import environment variables
import os
from dotenv import load_dotenv
load_dotenv()


# import of engine and base from database.py
from database.database import get_engine, Base

# import of all ORM models -> hint for SQLAlchemy what classes inherit from Base
# and therefore are tables
from database.models import Employee, Product, MessageLog

engine = get_engine()
print(f"Connecting to engine at {engine.url}")

print("Creating database tables...")

# Creates all tables that inheriting from base and creates them
# in the database that is connected to the engine
# checkfirst=True avoids errors in case that tables exist already
Base.metadata.create_all(bind=engine, checkfirst=True)

print("Database tables created successfully!")