# import of engine and base from database.py
from database.database import engine, Base

# import of all ORM models -> hint for SQLAlchemy what classes inherit from Base
# and therefore are tables
from database.models import Employee, Partner, Product, WhatsappMessageLog

print("Creating database tables...")

# Creates all tables that inheriting from base and creates them
# in the database that is connected to the engine
# checkfirst=True avoids errors in case that tables exist already
Base.metadata.create_all(bind=engine, checkfirst=True)

print("Database tables created successfully!")