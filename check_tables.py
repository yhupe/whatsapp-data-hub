# Import environment variables
import os
from dotenv import load_dotenv
load_dotenv()

from database.database import get_engine
from sqlalchemy import inspect

engine = get_engine()
print(f"Connecting to engine at {engine.url}")

inspector = inspect(engine)
table_names = inspector.get_table_names()

print("Tables found in the database:", table_names)