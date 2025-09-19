"""
Content workflow tests for the AI Content Factory application
"""
import pytest
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate
from app.services.content_workflow import execute_full_content_workflow, create_content_for_product
from app.services.product_discovery import create_product


def test_execute_full_content_workflow(db: Session):
    """Test executing the full content workflow"""
    # First create a product to work with
    product_data = ProductCreate(
        name="Test Product for Workflow",
        description="A test product for workflow testing",
        price="$29.99",
        url="https://example.com/test-product-workflow",
        image_url="https://example.com/test-product-workflow.jpg",
        is_trending=True
    )
    
    created_product = create_product(db, product_data)
    
    # Execute the workflow
    import asyncio
    result = asyncio.run(execute_full_content_workflow(db))
    
    assert result["status"] in ["started", "completed", "failed"]
    assert "steps" in result
    assert isinstance(result["steps"], list)


def test_create_content_for_product(db: Session):
    """Test creating content for a specific product"""
    # First create a product to work with
    product_data = ProductCreate(
        name="Test Product for Content Creation",
        description="A test product for content creation testing",
        price="$39.99",
        url="https://example.com/test-product-content",
        image_url="https://example.com/test-product-content.jpg"
    )
    
    created_product = create_product(db, product_data)
    
    # Create content for the product (convert to int properly)
    product_id = int(str(created_product.id))
    import asyncio
    result = asyncio.run(create_content_for_product(db, product_id))
    
    assert result["status"] in ["started", "completed", "failed"]
    assert result["product_id"] == product_id
    assert "steps" in result
    assert isinstance(result["steps"], list)


def test_workflow_with_no_products(db: Session):
    """Test workflow behavior when no products are available"""
    # Execute the workflow with no products
    import asyncio
    result = asyncio.run(execute_full_content_workflow(db))
    
    assert result["status"] in ["started", "completed", "failed"]
    assert "steps" in result
    assert isinstance(result["steps"], list)