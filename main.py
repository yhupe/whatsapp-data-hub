from fastapi import FastAPI

# Import of router
from api.routes import employees

app = FastAPI()

# linking the employees_router with main.py
app.include_router(employees.employees_router)

