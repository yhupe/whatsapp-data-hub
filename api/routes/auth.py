# Import of necessary parts of FastAPI
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse

# Import of SQLAlchemy Session (for type hints)
from sqlalchemy.orm import Session

# Import of database dependency
from database.database import get_db

# Import of EmployeeService
from services.employee_service import EmployeeService, get_employee_service

from fastapi.templating import Jinja2Templates

from uuid import UUID

# Import of JWT decoding method
from utils.jwt_utils import decode_magic_link_token


templates = Jinja2Templates(directory="templates")


auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

@auth_router.get("/verify", response_class=HTMLResponse)
async def verify_magic_link(request: Request, token: str, db: Session = Depends(get_db)):
    """
    temporary endpoint to test success and failure pages
    """

    # Decoding and validating token
    decoded_token = decode_magic_link_token(token)
    employee_service = EmployeeService(db)

    try:
        # Extract employee_id and email address from decoded token
        employee_id = UUID(decoded_token.get("employee_id"))
        employee_email_from_token = decoded_token.get("email")

        # Find employee in database by ID
        employee = employee_service.get_employee_by_id(employee_id)

        # Extra checks:
        # does the employee exist?
        # Does the token email address match the database email address?

        if employee and str(employee.email).lower() == employee_email_from_token.lower():
            # If the above checks pass: check that the employee is not already authenticated
            # then setting 'is_authenticated = True'

            if not employee.is_authenticated:
                updated_employee = employee_service.set_employee_authenticated_status(employee_id, True)
                if updated_employee:
                    print(
                        f"Employee {employee_id} ({employee_email_from_token}) successfully authenticated.")

                    # return success HTML page
                    return templates.TemplateResponse("magic_link_success.html", {"request": request})

                else:
                    print(f"ERROR: is_authenticated status for Employee {employee_id} cannot be updated.")
            else:
                print(f"Employee {employee_id} is already authenticated. No update necessary.")

                # return success HTML page again
                return templates.TemplateResponse("magic_link_success.html", {"request": request})

        else:
            print(f"Token-Payload does not match MEmployee data or Employee was not found.")
            print(f"Employee ID from token: {employee_id}, Email from token: {employee_email_from_token}")
            print(
                f"Employee from DB: {employee.id if employee else 'None'}, Email from DB: {employee.email if employee else 'None'}")

    except ValueError as e:
        # Error if the UUID in the JWT is invalid
        print(f"ERROR: Invalid UUID in token payload: {e}")

    except Exception as e:
        print(f"ERROR: Unexpected error while token verification: {e}")

    else:
        print("Magic link token could not be decoded (invalid/expired/malformed).")

    # return failure HTML page
    return templates.TemplateResponse("magic_link_failure.html", {"request": request})
