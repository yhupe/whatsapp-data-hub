from database.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
table_names = inspector.get_table_names()

print("Tables found in the database:", table_names)