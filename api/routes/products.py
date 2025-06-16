# Import of necessary parts of FastAPI
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query

# Import of or_ module as a filtering condition to avoid using '|'
from sqlalchemy import or_

# Import of SQLAlchemy Session (for type hints)
from sqlalchemy.orm import Session

from api.schemas import ProductUpdate, ProductCreate
# Import of SQLAlchemy ORM models
from database import models

# Import of Pydantic schemas
from api import schemas

# Import of database dependency
from database.database import get_db

# Import of ProductService
from services.products_service import ProductService, get_product_service

from uuid import UUID
from typing import List, Optional


# Creates APIRouter instance
product_router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@product_router.post("/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(
        product_data: ProductCreate,
        product_service: ProductService = Depends(get_product_service)
):
    """ Endpoint to create a new product.

        Args:
            product_data (schemas.ProductCreate): The Pydantic model containing the details
                for a new product.
            product_service (ProductService): The injected ProductService instance.

        Returns: db_product: The newly created product object incl. the automatically generated
            ID and timestamps.

        Raises:
            HTTPException: If the provided product name is
                already in the database (HTTP 400 Bad Request).
        """

    try:
        db_product = product_service.create_product(product_data=product_data)  # calling the service
        return db_product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@product_router.get("/all", response_model=List[schemas.Product], status_code=status.HTTP_200_OK)
def get_all_products(
    product_service: ProductService = Depends(get_product_service)
):
    """ Endpoint to get all products.

    Args:
        product_service (ProductService): The injected ProductService instance.

    Returns: db_product: The list of all product objects.

    Raises: HTTPException: If the product cannot be found by the passed name (HTTP 404 Not Found)

    """

    db_product = product_service.get_all_products()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")

    return db_product


@product_router.get("/search", response_model=List[schemas.Product], status_code=status.HTTP_200_OK)
def search_products_by_name(
    name_query: str = Query(..., min_length=1, description="Search term for product name (case-insensitive, partial match)"),
    product_service: ProductService = Depends(get_product_service)
):
    """ Endpoint to search products by name using a query parameter.

    Args:
        name_query (str): The search term for the product name.
        product_service (ProductService): The injected ProductService instance.

    Returns: db_product: A list of product objects matching the search term.

    Raises: HTTPException: If no products are found for the given search term (HTTP 404 Not Found)

    """

    db_products = product_service.get_all_products(name_query=name_query)
    if not db_products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found with this name")

    return db_products


@product_router.get("/{product_id}", response_model=schemas.Product, status_code=status.HTTP_200_OK)
def get_product_by_id(
    product_id: UUID,
    product_service: ProductService = Depends(get_product_service)
):
    """ Endpoint to get a product by ID.

    Args:
        product_id (UUID): A unique identifier in UUID format.
        product_service (ProductService): The injected ProductService instance.

    Returns: db_product: The product object searched for.

    Raises: HTTPException: If the product cannot be found by the passed ID (HTTP 404 Not Found)

    """

    db_product = product_service.get_product_by_id(product_id=product_id)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return db_product


@product_router.patch("/{product_id}", response_model=schemas.Product, status_code=status.HTTP_200_OK)
def update_product(
        product_id: UUID,
        product_update_data: ProductUpdate,
        product_service: ProductService = Depends(get_product_service)
):
    """ Endpoint to update at least one field of an existing product.

    Args:
        product_id (UUID): A unique identifier in UUID format.
        product_update_data (ProductUpdate): An ProductUpdate object containing the updates.
        product_service (ProductService): The injected ProductService instance.

    Returns: db_product: The updated Product object.

    Raises:
        HTTPException:
            - 404 Not found: If the ID searched after does not match with a
            product from the database.
            - 400 Bad request: If there is a database error like unique constraint violation
            - 422 Unprocessable Entity: If the input data is invalid (Pydantic)
    """

    try:
        db_product = product_service.update_product(
            product_id=product_id,
            product_update_data=product_update_data
        )
        return db_product

    except ValueError as e:

        if "Product not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@product_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_by_id(
        product_id: UUID,
        product_service: ProductService = Depends(get_product_service)
):
    """ Endpoint to delete a product by id.

    Args:
        product_id (UUID): A unique identifier in UUID format.
        product_service (ProductService): The injected ProductService instance.

    Returns: Response(status_code=status.HTTP_204_NO_CONTENT): Returns a response without body.

    Raises:
        HTTPException: If the product cannot be found by the passed ID (HTTP 404 Not Found)
    """

    try:
        product_service.delete_product(product_id=product_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ValueError as e:
        if "Product not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
