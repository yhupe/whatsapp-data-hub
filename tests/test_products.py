from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from database import models
import pytest
import uuid
import datetime
from decimal import Decimal


def test_create_product_success(client: TestClient, db_session_for_test: Session):
    """
    Tests the successful creation of a new Product via POST /products/.
    Verifies HTTP status, response data, and database entry.
    """

    product_data_1 = {
        "name": "Test Product A",
        "description": "Description for Test Product A",
        "price": 19.99,
        "stock_quantity": 100,
        "is_active": True,
        "length": 20.0,
        "height": 10.0,
        "width": 5.0,
        "weight": 2.5,
        "image_url": "http://example.com/image_a.jpg",
        "notes": "Internal note A"
    }

    response = client.post("/products/", json=product_data_1)

    assert response.status_code == 201, f"Expected status 201, got {response.status_code}. Response: {response.json()}"
    response_data = response.json()

    assert "id" in response_data
    assert isinstance(uuid.UUID(response_data["id"]), uuid.UUID)
    assert response_data["name"] == product_data_1["name"]
    assert response_data["description"] == product_data_1["description"]
    assert float(response_data["price"]) == product_data_1["price"]
    assert response_data["stock_quantity"] == product_data_1["stock_quantity"]
    assert response_data["is_active"] == product_data_1["is_active"]
    assert float(response_data["length"]) == product_data_1["length"]
    assert "created_at" in response_data
    assert "updated_at" in response_data

    # Verify that product is in database
    db_product = db_session_for_test.query(models.Product).filter(
        models.Product.id == uuid.UUID(response_data["id"])
    ).first()

    assert db_product is not None, "Product was not found in the database."
    assert db_product.name == product_data_1["name"]
    assert db_product.description == product_data_1["description"]
    assert float(db_product.price) == product_data_1["price"]
    assert db_product.stock_quantity == product_data_1["stock_quantity"]
    assert db_product.is_active == product_data_1["is_active"]


def test_create_product_duplicate_name(client: TestClient):
    """
    Tests that creating a product with an existing name fails (assuming unique constraint).
    """

    product_data_1 = {
        "name": "Test Product A",
        "description": "Description for Test Product A",
        "price": 19.99,
        "stock_quantity": 100,
        "is_active": True,
        "length": 20.0,
        "height": 10.0,
        "width": 5.0,
        "weight": 2.5,
        "image_url": "http://example.com/image_a.jpg",
        "notes": "Internal note A"
    }

    product_data_2 = {
        "name": "Test Product B",
        "description": "Description for Test Product B",
        "price": 29.99,
        "stock_quantity": 50,
        "is_active": True,
        "length": 25.0,
        "height": 12.0,
        "width": 6.0,
        "weight": 3.0,
        "image_url": "http://example.com/image_b.jpg",
        "notes": "Internal note B"
    }


    # Create first product successfully
    response_1 = client.post("/products/", json=product_data_1)
    assert response_1.status_code == 201

    # Try to create another product with the same name but different other data
    duplicate_name_data = product_data_2
    duplicate_name_data["name"] = product_data_1["name"] # Duplicate name
    response_2 = client.post("/products/", json=duplicate_name_data)

    assert response_2.status_code == 400, f"Expected 400 for duplicate name, got {response_2.status_code}. Response: {response_2.json()}"
    assert "detail" in response_2.json()
    assert "name already exists" in response_2.json()["detail"]


def test_create_product_invalid_data(client: TestClient):
    """
    Tests that creating a product with missing required data (e.g., 'price') returns 422.
    FastAPI/Pydantic should automatically return HTTP 422 Unprocessable Entity.
    """

    invalid_product_data = {
        "name": "Invalid Product",
        "description": "Missing price and stock_quantity",
        # "price" is missing
        # "stock_quantity" is missing
    }
    response = client.post("/products/", json=invalid_product_data)

    assert response.status_code == 422, f"Expected status 422, got {response.status_code}. Response: {response.json()}"
    assert "detail" in response.json()
    assert any("price" in error["loc"] for error in response.json()["detail"])
    assert any("stock_quantity" in error["loc"] for error in response.json()["detail"])


def test_get_all_products_empty_db(client: TestClient):
    """
    Tests that retrieving all products from an empty database returns 404 (as per your endpoint's logic).
    """

    response = client.get("/products/all")
    assert response.status_code == 404, f"Expected status 404, got {response.status_code}. Response: {response.json()}"
    assert response.json()["detail"] == "No products found"


def test_get_all_products_multiple_exist(client: TestClient):
    """
    Tests that retrieving all products returns all existing products.
    """

    product_data_1 = {
        "name": "Test Product A",
        "description": "Description for Test Product A",
        "price": 19.99,
        "stock_quantity": 100,
        "is_active": True,
        "length": 20.0,
        "height": 10.0,
        "width": 5.0,
        "weight": 2.5,
        "image_url": "http://example.com/image_a.jpg",
        "notes": "Internal note A"
    }

    product_data_2 = {
        "name": "Test Product B",
        "description": "Description for Test Product B",
        "price": 29.99,
        "stock_quantity": 50,
        "is_active": True,
        "length": 25.0,
        "height": 12.0,
        "width": 6.0,
        "weight": 3.0,
        "image_url": "http://example.com/image_b.jpg",
        "notes": "Internal note B"
    }

    product_data_3 = {
        "name": "Another Product C",
        "description": "Just another product for testing.",
        "price": 5.00,
        "stock_quantity": 200,
        "is_active": False,  # inactive product
        "length": 10.0,
        "height": 5.0,
        "width": 2.0,
        "weight": 1.0,
        "image_url": None,  # optional field being None
        "notes": None
    }


    # create Product 1
    res1 = client.post("/products/", json=product_data_1)

    # create Product 2
    res2 = client.post("/products/", json=product_data_2)

    # create Product 3
    res3 = client.post("/products/", json=product_data_3)

    response = client.get("/products/all")
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.json()}"
    products_list = response.json()
    assert len(products_list) == 3, f"Expected 3 products, got {len(products_list)}"

    returned_names = {product["name"] for product in products_list}

    expected_names = {
        product_data_1["name"],
        product_data_2["name"],
        product_data_3["name"]
    }

    assert returned_names == expected_names


def test_get_product_by_id_success(client: TestClient):
    """
    Tests retrieving a product by its ID successfully.
    """

    product_data_1 = {
        "name": "Test Product A",
        "description": "Description for Test Product A",
        "price": 19.99,
        "stock_quantity": 100,
        "is_active": True,
        "length": 20.0,
        "height": 10.0,
        "width": 5.0,
        "weight": 2.5,
        "image_url": "http://example.com/image_a.jpg",
        "notes": "Internal note A"
    }

    # create Product 1
    res_create = client.post("/products/", json=product_data_1)

    created_product = res_create.json()
    product_id = created_product["id"]

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.json()}"
    retrieved_product = response.json()

    assert retrieved_product["id"] == product_id
    assert retrieved_product["name"] == created_product["name"]
    assert float(retrieved_product["price"]) == float(created_product["price"])
    assert retrieved_product["stock_quantity"] == created_product["stock_quantity"]


def test_get_product_by_id_not_found(client: TestClient):
    """
    Tests retrieving a non-existent product by ID returns 404.
    """

    non_existent_id = uuid.uuid4() # A random UUID that should not exist
    response = client.get(f"/products/{non_existent_id}")
    assert response.status_code == 404, f"Expected status 404, got {response.status_code}. Response: {response.json()}"
    assert response.json()["detail"] == "Product not found"


def test_get_product_by_id_invalid_uuid(client: TestClient):
    """
    Tests that requesting with an invalid UUID format returns 422 (Pydantic validation).
    """

    invalid_uuid = "not-a-valid-uuid"
    response = client.get(f"/products/{invalid_uuid}")
    assert response.status_code == 422, f"Expected status 422, got {response.status_code}. Response: {response.json()}"
    assert "Input should be a valid UUID" in response.json()["detail"][0]["msg"]


def test_get_product_by_name_success(client: TestClient):
    """
    Tests retrieving products by name (case-insensitive, partial match).
    This test relies on FastAPI's routing order to correctly map to the {product_name} path.
    """

    product_data_1 = {
        "name": "Test Product A",
        "description": "Description for Test Product A",
        "price": 19.99,
        "stock_quantity": 100,
        "is_active": True,
        "length": 20.0,
        "height": 10.0,
        "width": 5.0,
        "weight": 2.5,
        "image_url": "http://example.com/image_a.jpg",
        "notes": "Internal note A"
    }

    product_data_2 = {
        "name": "Test Product B",
        "description": "Description for Test Product B",
        "price": 29.99,
        "stock_quantity": 50,
        "is_active": True,
        "length": 25.0,
        "height": 12.0,
        "width": 6.0,
        "weight": 3.0,
        "image_url": "http://example.com/image_b.jpg",
        "notes": "Internal note B"
    }

    product_data_3 = {
        "name": "Another Product C",
        "description": "Just another product for testing.",
        "price": 5.00,
        "stock_quantity": 200,
        "is_active": False,  # inactive product
        "length": 10.0,
        "height": 5.0,
        "width": 2.0,
        "weight": 1.0,
        "image_url": None,  # optional field being None
        "notes": None
    }

    # create Product 1
    client.post("/products/", json=product_data_1)

    # create Product 2
    client.post("/products/", json=product_data_2)

    # create Product 3
    client.post("/products/", json=product_data_3)


    # Search for "test" (should find "Test Product A", "Test Product B" and NOT "Another Product 3")
    response = client.get("/products/search", params={"name_query": "test"})
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.json()}"

    products_list = response.json()
    assert len(products_list) == 2, f"Expected 2 products, got {len(products_list)}"

    returned_names = {p["name"] for p in products_list}
    assert product_data_1["name"] in returned_names
    assert product_data_2["name"] in returned_names


def test_get_product_by_name_not_found(client: TestClient):
    """
    Tests retrieving products by a non-existent name returns 404.
    """
    product_data_1 = {
        "name": "Test Product A",
        "description": "Description for Test Product A",
        "price": 19.99,
        "stock_quantity": 100,
        "is_active": True,
        "length": 20.0,
        "height": 10.0,
        "width": 5.0,
        "weight": 2.5,
        "image_url": "http://example.com/image_a.jpg",
        "notes": "Internal note A"
    }

    # creating one product but not the one searched for
    client.post("/products/", json=product_data_1)

    # searching for NonExistentProduct, expecting 404 Not found Error
    response = client.get("/products/search", params={"name_query": "NonExistentProduct"})

    assert response.status_code == 404, f"Expected status 404, got {response.status_code}. Response: {response.json()}"
    assert response.json()["detail"] == "No products found with this name"


def test_update_product_success(client: TestClient):
    """
    Tests that an existing product can be successfully updated with partial data.
    """

    product_data_1 = {
        "name": "Test Product A",
        "description": "Description for Test Product A",
        "price": 19.99,
        "stock_quantity": 100,
        "is_active": True,
        "length": 20.0,
        "height": 10.0,
        "width": 5.0,
        "weight": 2.5,
        "image_url": "http://example.com/image_a.jpg",
        "notes": "Internal note A"
    }

    # creating one product but not the one searched for
    res_create = client.post("/products/", json=product_data_1)

    created_product = res_create.json()
    product_id = created_product["id"]

    update_data = {
        "name": "Updated Product Name",
        "price": 99.99,
        "description": "Updated description too!"
    }
    response = client.patch(f"/products/{product_id}", json=update_data)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.json()}"
    updated_product = response.json()

    assert updated_product["id"] == product_id
    assert updated_product["name"] == update_data["name"]
    assert float(updated_product["price"]) == update_data["price"]
    assert updated_product["description"] == update_data["description"]

    # Check that unchanged fields remain unchanged
    assert updated_product["stock_quantity"] == created_product["stock_quantity"]
    assert float(updated_product["length"]) == float(created_product["length"])


def test_update_product_not_found(client: TestClient):
    """
    Tests that updating a non-existent product returns 404.
    """

    non_existent_id = uuid.uuid4()
    update_data = {"name": "Non Existent Update"}
    response = client.patch(f"/products/{non_existent_id}", json=update_data)
    assert response.status_code == 404, f"Expected status 404, got {response.status_code}. Response: {response.json()}"
    assert response.json()["detail"] == "Product not found"


def test_update_product_invalid_data(client: TestClient):
    """
    Tests that updating a product with invalid data (e.g., negative price) returns 422.
    """

    product_data_1 = {
        "name": "Test Product A",
        "description": "Description for Test Product A",
        "price": 19.99,
        "stock_quantity": 100,
        "is_active": True,
        "length": 20.0,
        "height": 10.0,
        "width": 5.0,
        "weight": 2.5,
        "image_url": "http://example.com/image_a.jpg",
        "notes": "Internal note A"
    }

    # creating one product but not the one searched for
    res_create = client.post("/products/", json=product_data_1)

    created_product = res_create.json()
    product_id = created_product["id"]

    invalid_update_data = {"price": -5.00} # Price must be > 0
    response = client.patch(f"/products/{product_id}", json=invalid_update_data)
    assert response.status_code == 422, f"Expected status 422, got {response.status_code}. Response: {response.json()}"
    assert "should be greater than 0" in response.json()["detail"][0]["msg"]


def test_update_product_duplicate_name(client: TestClient):
    """
    Tests that updating a product with a name that already exists for another product returns 400.
    (Assumes unique constraint on name)
    """

    product_data_1 = {
        "name": "Test Product A",
        "description": "Description for Test Product A",
        "price": 19.99,
        "stock_quantity": 100,
        "is_active": True,
        "length": 20.0,
        "height": 10.0,
        "width": 5.0,
        "weight": 2.5,
        "image_url": "http://example.com/image_a.jpg",
        "notes": "Internal note A"
    }

    product_data_2 = {
        "name": "Test Product B",
        "description": "Description for Test Product B",
        "price": 29.99,
        "stock_quantity": 50,
        "is_active": True,
        "length": 25.0,
        "height": 12.0,
        "width": 6.0,
        "weight": 3.0,
        "image_url": "http://example.com/image_b.jpg",
        "notes": "Internal note B"
    }

    # create Product 1
    response_1 = client.post("/products/", json=product_data_1)

    # create Product 2
    response_2 = client.post("/products/", json=product_data_2)

    assert response_1.status_code == 201
    created_product_1 = response_1.json()
    product_1_id = created_product_1["id"]

    assert response_2.status_code == 201

    # Try to update product 1's name to product 2's name (which already exists)
    duplicate_name_update = {"name": product_data_2["name"]}
    response = client.patch(f"/products/{product_1_id}", json=duplicate_name_update)
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}. Response: {response.json()}"
    assert "already exists" in response.json()["detail"]


def test_update_product_no_data_provided(client: TestClient):
    """
    Tests that attempting to update a product by sending an empty JSON body
    returns 422 due to the @model_validator in ProductUpdate.
    """

    product_data_1 = {
        "name": "Test Product A",
        "description": "Description for Test Product A",
        "price": 19.99,
        "stock_quantity": 100,
        "is_active": True,
        "length": 20.0,
        "height": 10.0,
        "width": 5.0,
        "weight": 2.5,
        "image_url": "http://example.com/image_a.jpg",
        "notes": "Internal note A"
    }

    # creating one product
    res_create = client.post("/products/", json=product_data_1)

    created_product = res_create.json()
    product_id = created_product["id"]

    empty_update_data = {}
    response = client.patch(f"/products/{product_id}", json=empty_update_data)

    assert response.status_code == 422, f"Expected status 422, got {response.status_code}. Response: {response.json()}"

    # This specific error message comes from your @model_validator in ProductUpdate
    assert "At least one field (name, description, size, price etc.) must be provided for update." in response.json()["detail"][0]["msg"]


def test_delete_product_success(client: TestClient, db_session_for_test: Session):
    """
    Tests that a product can be successfully deleted.
    """

    product_data_1 = {
        "name": "Test Product A",
        "description": "Description for Test Product A",
        "price": 19.99,
        "stock_quantity": 100,
        "is_active": True,
        "length": 20.0,
        "height": 10.0,
        "width": 5.0,
        "weight": 2.5,
        "image_url": "http://example.com/image_a.jpg",
        "notes": "Internal note A"
    }

    # creating one product but not the one searched for
    res_create = client.post("/products/", json=product_data_1)

    created_product = res_create.json()
    product_id = created_product["id"]

    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 204, f"Expected status 204, got {response.status_code}. Response: {response.json()}"
    assert not response.content # 204 No Content should have an empty body

    # Verify in database that the product no longer exists
    db_product = db_session_for_test.query(models.Product).filter(
        models.Product.id == uuid.UUID(product_id)
    ).first()
    assert db_product is None, "Product was found in the database after deletion."

    # Try to get the product again, should return 404
    response_get = client.get(f"/products/{product_id}")
    assert response_get.status_code == 404, f"Expected status 404, got {response_get.status_code}. Response: {response_get.json()}"
    assert response_get.json()["detail"] == "Product not found"


def test_delete_product_not_found(client: TestClient):
    """
    Tests that deleting a non-existent product returns 404.
    """

    non_existent_id = uuid.uuid4() # A random UUID that should not exist
    response = client.delete(f"/products/{non_existent_id}")
    assert response.status_code == 404, f"Expected status 404, got {response.status_code}. Response: {response.json()}"
    assert response.json()["detail"] == "Product not found"
