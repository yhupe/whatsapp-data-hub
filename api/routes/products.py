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
    """ **Endpoint to create a new product.**

    **"name": mandatory**\n
    **"description": optional**\n
    **"product_manager_id": optional**\n
    **"length": optional**\n
    **"height": optional**\n
    **"width": optional**\n
    **"weight": optional**\n
    **"image_url": optional**\n
    **"price": mandatory**\n
    **"stock_quantity": mandatory**\n
    **"is_active": optional (automatically handled based on 'stock_quantity')**\n
    **"notes": optional**\n

    **Args:**\n
        product_data (schemas.ProductCreate): The Pydantic model containing the details for a new product.\n
        product_service (ProductService): The injected ProductService instance.

    **Returns:**\n
        db_product: The newly created product object incl. the automatically generated ID and timestamps.

    **Raises:**\n
        HTTPException:\n
        - HTTP 400 Bad Request: If the provided product name is already in the database.\n
        - 422 Unprocessable Entity, Pydantic: If the input data is invalid.
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
    """ **Endpoint to get all products.**

    **Args:**\n
        product_service (ProductService): The injected ProductService instance.

    **Returns:**\n
        db_product: The list of all product objects.

    **Raises:**\n
        HTTPException:\n
            - HTTP 404 Not Found:If the product cannot be found by the passed name.

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
    """ **Endpoint to search products by name using a query parameter.**

    **Args:**\n
        name_query (str): The search term for the product name.\n
        product_service (ProductService): The injected ProductService instance.

    **Returns:**\n
        db_product: A list of product objects matching the search term.

    **Raises:**\n
        HTTPException:\n
            - HTTP 404 Not Found: If no products are found for the given search term.

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
    """ **Endpoint to get a product by ID.**

    **Args:**\n
        product_id (UUID): A unique identifier in UUID format.\n
        product_service (ProductService): The injected ProductService instance.

    **Returns:**\n
        db_product: The product object searched for.

    **Raises:**\n
        HTTPException:\n
            - HTTP 404 Not Found: If the product cannot be found by the passed ID.

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
    """ **Endpoint to update at least one field of an existing product.**

    **Please ensure to send at least one field to be updated.** \n
    **Also only execute used fields as otherwise the examples are going to be updated.**

    **"name": optional**\n
    **"description": optional**\n
    **"product_manager_id": optional**\n
    **"length": optional**\n
    **"height": optional**\n
    **"width": optional**\n
    **"weight": optional**\n
    **"image_url": optional**\n
    **"price": optional**\n
    **"stock_quantity": optional**\n
    **"is_active": optional**\n
    **"notes": optional**\n

    **Args:**\n
        product_id (UUID): A unique identifier in UUID format.\n
        product_update_data (ProductUpdate): An ProductUpdate object containing the updates.\n
        product_service (ProductService): The injected ProductService instance.

    **Returns:**\n
        db_product: The updated Product object.

    **Raises:**\n
        HTTPException:\n
            - HTTP 404 Not found: If the ID searched after does not match with a product from the database.\n
            - HTTP 400 Bad request: If there is a database error like unique constraint violation.\n
            - HTTP 422 Unprocessable Entity, Pydantic: If the input data is invalid.
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
    """ **Endpoint to delete a product by id.**

    **Args:**\n
        product_id (UUID): A unique identifier in UUID format.\n
        product_service (ProductService): The injected ProductService instance.

    **Returns:**\n
        Response(status_code=status.HTTP_204_NO_CONTENT): Returns a response without body.

    **Raises:**\n
        HTTPException:\n
            - HTTP 404 Not Found: If the product cannot be found by the passed ID.
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
