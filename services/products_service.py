from sqlalchemy.orm import Session
from sqlalchemy import or_
from uuid import UUID
from typing import List, Optional

from database import models
from api.schemas import ProductCreate, ProductUpdate
from database.database import get_db
from fastapi import Depends, HTTPException


class ProductService:
    def __init__(self, db: Session):
        """
        Initializes the ProductService with a db-session.
        """
        self.db = db


    def create_product(
        self,
        product_data: ProductCreate
    ) -> models.Product:
        """
        Creates a new product in the database.
        """

        # Check whether an employee with the exact name already exists
        db_product = self.db.query(models.Product).filter(
            or_(
                models.Product.name == product_data.name,
            )
        ).first()

        if db_product:
            raise ValueError("Product with this exact name already exists.")

        new_product = models.Product(
            name=product_data.name,
            description=product_data.description,
            length=product_data.length,
            height=product_data.height,
            width=product_data.width,
            weight=product_data.weight,
            image_url=product_data.image_url,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity,
            is_active=product_data.is_active,
            notes=product_data.notes
        )

        self.db.add(new_product)
        self.db.commit()
        self.db.refresh(new_product)
        return new_product


    def get_product_by_id(self, product_id: UUID) -> Optional[models.Product]:
        """
        Retrieves a product by ID.
        """

        return self.db.query(models.Product).filter(models.Product.id == product_id).first()


    def get_all_products(self, name_query: Optional[str] = None) -> List[models.Product]:
        """
        Retrieves a list of products, optionally filtered by name.
        """

        query = self.db.query(models.Product)

        if name_query:
            query = query.filter(models.Product.name.ilike(f"%{name_query}%"))

        products = query.all()
        return products


    def update_product(
        self,
        product_id: UUID,
        product_update_data: ProductUpdate
    ) -> Optional[models.Product]:
        """
        Updates an existing product's fields.
        Handles unique constraint violations.
        """

        db_product = self.get_product_by_id(product_id)

        if not db_product:
            raise ValueError("Product not found")

        update_data = product_update_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_product, key, value)

        try:
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            return db_product

        except Exception as e:
            self.db.rollback()
            error_detail = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise ValueError(f"Database error updating product: {error_detail}")


    def delete_product(self, product_id: UUID) -> bool:
        """
        Deletes an employee by ID.
        Returns True if deleted, False if not found.
        """

        db_product = self.get_product_by_id(product_id)

        if not db_product:
            raise ValueError("Product not found")

        self.db.delete(db_product)
        self.db.commit()
        return True

# Dependency for FastAPI-Router
# Function is used by FastAPI as dependency to inject a service instance
def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """
    Dependency that returns an instance of EmployeeService
    """

    return ProductService(db)