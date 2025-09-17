"""
Product tests for the AI Content Factory application
"""
import pytest
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate
from app.services.product_discovery import create_product, get_product_by_id


def test_create_product(db: Session):
    """Test creating a product"""
    product_data = ProductCreate(
        name="Test Product",
        description="A test product",
        price="$19.99",
        url="https://example.com/test-product",
        image_url="https://example.com/test-product.jpg",
        is_trending=True
    )
    
    product = create_product(db, product_data)
    
    assert product.name == "Test Product"
    assert product.description == "A test product"
    assert product.price == "$19.99"
    assert product.url == "https://example.com/test-product"
    assert product.is_trending is True


def test_get_product_by_id(db: Session):
    """Test retrieving a product by ID"""
    # First create a product
    product_data = ProductCreate(
        name="Test Product 2",
        description="Another test product",
        price="$29.99",
        url="https://example.com/test-product-2",
        image_url="https://example.com/test-product-2.jpg"
    )
    
    created_product = create_product(db, product_data)
    
    # Then retrieve it
    retrieved_product = get_product_by_id(db, created_product.id)
    
    assert retrieved_product is not None
    assert retrieved_product.id == created_product.id
    assert retrieved_product.name == "Test Product 2"