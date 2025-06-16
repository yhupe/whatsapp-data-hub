from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import os


DOCS_USERNAME = os.getenv("DOCS_USERNAME", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "supersecret")

# Initialize the HTTP basic security scheme
security = HTTPBasic()


# Dependency that checks the authentication
def get_current_docs_username(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Checks the HTTP basic authentication for access on the docs.
    """
    if credentials.username == DOCS_USERNAME and credentials.password == DOCS_PASSWORD:
        return credentials.username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Wrong username or password for the documentation",
        headers={"WWW-Authenticate": "Basic"},
    )


docs_router = APIRouter(
    tags=["docs"]
)


@docs_router.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(username: str = Depends(get_current_docs_username)):
    """
    Protected Swagger UI documentation.
    """

    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Hannes final project API - Swagger UI (protected)"
    )

@docs_router.get("/redoc", include_in_schema=False)
async def custom_redoc_html(username: str = Depends(get_current_docs_username)):
    """
    Protected ReDoc documentation.
    """

    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Hannes final project API - ReDoc (protected)"
    )

