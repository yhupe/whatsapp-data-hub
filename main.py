from dotenv import load_dotenv

from api.routes.products import product_router

load_dotenv()

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

# Import of router
from api.routes import employees, message_logs, auth, products

app = FastAPI()

# linking the employees_router with main.py
app.include_router(employees.employees_router)

# linking the message_log_router with main.py
app.include_router(message_logs.message_log_router)

# linking the products_router with main.py
app.include_router(products.product_router)

# linking the auth_router with main.py
templates = Jinja2Templates(directory="templates")
app.include_router(auth.auth_router)

