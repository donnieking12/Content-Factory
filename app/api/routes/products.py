"""
Product API routes for the AI Content Factory application
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.services.product_discovery import get_product_by_id, get_products, create_product, update_product, delete_product, discover_trending_products

router = APIRouter()


@router.get("/test-api-connection")
def test_api_connection():
    """
    Test external API connection without database dependency
    """
    from app.services.product_discovery import discover_trending_products_from_api
    import asyncio
    
    try:
        raw_products = asyncio.run(discover_trending_products_from_api())
        return {
            "status": "success",
            "products_discovered": len(raw_products),
            "products": raw_products[:3],  # Return first 3 for testing
            "message": "External API connection working perfectly!"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"API connection failed: {str(e)}"
        }


@router.post("/discover-trending", status_code=status.HTTP_202_ACCEPTED)
def discover_trending_products_endpoint(db: Session = Depends(get_db)):
    """
    Discover trending products from external sources
    """
    # In a real implementation, we would trigger the Celery task:
    # from celery_worker import discover_products_task
    # task = discover_products_task.delay()
    # return {"task_id": task.id, "status": "started"}
    
    # For now, execute synchronously for demonstration
    try:
        discovered_products = discover_trending_products(db)
        return {
            "status": "completed",
            "products_discovered": len(discovered_products),
            "products": discovered_products
        }
    except Exception as e:
        # If database fails, still return the API data
        from app.services.product_discovery import discover_trending_products_from_api
        import asyncio
        
        raw_products = asyncio.run(discover_trending_products_from_api())
        return {
            "status": "completed_without_database", 
            "products_discovered": len(raw_products),
            "products": raw_products,
            "note": "Products fetched from API but not saved to database. Set up database to enable full functionality."
        }


@router.get("/", response_model=List[Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    products = get_products(db, skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = get_product_by_id(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_new_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = create_product(db=db, product=product)
    return db_product


@router.put("/{product_id}", response_model=Product)
def update_existing_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = update_product(db=db, product_id=product_id, product=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_product(product_id: int, db: Session = Depends(get_db)):
    success = delete_product(db=db, product_id=product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return None