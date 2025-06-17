from sqlalchemy.orm import Session
from sqlalchemy import or_
from uuid import UUID
from typing import List, Optional
import datetime

from database import models
from api.schemas import ProductCreate, ProductUpdate
from database.database import get_db
from services.employee_service import EmployeeService, get_employee_service
from fastapi import Depends, HTTPException


class ProductService:
    def __init__(self, db: Session, employee_service: EmployeeService):
        """
        Initializes the ProductService with a db-session.
        """

        self.db = db
        self.employee_service = employee_service

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

    def create_product(
        self,
        product_data: ProductCreate
    ) -> models.Product:
        """
        Creates a new product in the database.
        """

        # Check whether an employee with the exact name already exists
        db_product = self.db.query(models.Product).filter(
            models.Product.name == product_data.name
        ).first()

        if db_product:
            raise ValueError("Product with this exact name already exists.")

        product_manager_instance = None
        if product_data.product_manager_id:
            product_manager_instance = self.employee_service.get_employee_by_id(product_data.product_manager_id)
            if not product_manager_instance:
                raise ValueError(f"Product manager with ID '{product_data.product_manager_id}' not found.")

        new_product = models.Product(
            name=product_data.name,
            description=product_data.description,
            product_manager=product_manager_instance,
            length=product_data.length,
            height=product_data.height,
            width=product_data.width,
            weight=product_data.weight,
            image_url=product_data.image_url,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity,
            notes=product_data.notes
        )

        # Logic for is_active status based on stock_quantity
        if new_product.stock_quantity == 0:
            new_product.is_active = False
            print(f"Product '{new_product.name}' automatically deactivated: stock_quantity has reached 0")
        elif new_product.stock_quantity > 0:
            if not new_product.is_active:
                new_product.is_active = True
                print(f"Product '{new_product.name}' automatically activated: stock_quantity > 0")

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

        # Check only if the name is part of update request
        if product_update_data.name is not None and product_update_data.name != db_product.name:
            # Exact request for the new name
            existing_product_with_new_name = self.db.query(models.Product).filter(
                models.Product.name == product_update_data.name
            ).first()

            # Check if the new name exists already and its not the product we want to update:
            if existing_product_with_new_name and existing_product_with_new_name.id != product_id:
                raise ValueError(f"Product with name '{product_update_data.name}' already exists for another product.")

        # Update data
        update_data = product_update_data.model_dump(exclude_unset=True)

        # Logic to update the product manager ID with update payload
        if 'product_manager_id' in update_data:
            if update_data['product_manager_id'] is not None:
                # injected method to get employee by id
                product_manager_instance = self.employee_service.get_employee_by_id(update_data['product_manager'])

                if not product_manager_instance:
                    raise ValueError(
                        f"Product manager with ID '{update_data['product_manager']}' not found for update.")

                db_product.product_manager = product_manager_instance
            # If product manager explicitly is None:
            else:
                db_product.product_manager_id = None
            update_data.pop('product_manager')

        # Update all fields with new values in update_data
        for key, value in update_data.items():
            setattr(db_product, key, value)

        # if the stock_quantity was part of the update data and is now 0 --> is_active status becomes 'false'
        if db_product.stock_quantity == 0:
            db_product.is_active = False
            print(
                f"Product '{db_product.name}' automatically deactivated: stock_quantity has reached 0")

        elif db_product.stock_quantity > 0:
            if not db_product.is_active:
                db_product.is_active = True
                print(
                    f"Product '{db_product.name}' automatically activated: stock_quantity > 0")

        db_product.updated_at = datetime.datetime.now(datetime.timezone.utc)

        try:
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            return db_product

        except Exception as e:
            self.db.rollback()
            error_detail = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise ValueError(f"Database error updating product: {error_detail}")


# Dependency for FastAPI-Router
# Function is used by FastAPI as dependency to inject a service instance
def get_product_service(
    db: Session = Depends(get_db),
    employee_service: EmployeeService = Depends(get_employee_service)
) -> ProductService:
    """
    Dependency that returns an instance of ProductService
    """

    return ProductService(db, employee_service)