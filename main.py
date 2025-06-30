from dotenv import load_dotenv

from api.routes.products import product_router

# --- DEBUGGING PRINTS START ---
print("DEBUG: main.py script started.")
# --- DEBUGGING PRINTS END ---

# --- DEBUGGING PRINTS START ---
print("DEBUG: Before load_dotenv().")
# --- DEBUGGING PRINTS END ---

load_dotenv()

# --- DEBUGGING PRINTS START ---
print("DEBUG: After load_dotenv().")
# --- DEBUGGING PRINTS END ---

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

# --- DEBUGGING PRINTS START ---
print("DEBUG: Before router imports.")
# --- DEBUGGING PRINTS END ---

# Import of router
from api.routes import employees, message_logs, auth, products, docs

# --- DEBUGGING PRINTS START ---
print("DEBUG: After router imports.")
# --- DEBUGGING PRINTS END ---

# --- DEBUGGING PRINTS START ---
print("DEBUG: Before FastAPI app instantiation.")
# --- DEBUGGING PRINTS END ---

app = FastAPI(
    docs_url=None,
    redoc_url=None
)

# --- DEBUGGING PRINTS START ---
print("DEBUG: After FastAPI app instantiation.")
# --- DEBUGGING PRINTS END ---

# --- DEBUGGING PRINTS START ---
print("DEBUG: Before router inclusions.")
# --- DEBUGGING PRINTS END ---

# linking the employees_router with main.py
app.include_router(employees.employees_router)

# linking the message_log_router with main.py
#app.include_router(message_logs.message_log_router)

# linking the products_router with main.py
app.include_router(products.product_router)

# linking the auth_router with main.py
templates = Jinja2Templates(directory="templates")
app.include_router(auth.auth_router)

# linking the docs_router with main.py
app.include_router(docs.docs_router)

# --- DEBUGGING PRINTS START ---
print("DEBUG: After all router inclusions.")
print("DEBUG: main.py script finished successfully. App ready for Uvicorn.")
# --- DEBUGGING PRINTS END ---