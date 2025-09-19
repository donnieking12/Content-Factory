"""
Product discovery service for the AI Content Factory application
"""
import httpx
import asyncio
from typing import List, Optional, Dict, Any, cast
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    try:
        return db.query(Product).filter(Product.id == product_id).first()
    except Exception as e:
        logger.error(f"Error retrieving product with ID {product_id}: {e}", exc_info=True)
        return None


def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    try:
        return db.query(Product).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error retrieving products: {e}", exc_info=True)
        return []


def create_product(db: Session, product: ProductCreate) -> Product:
    try:
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Created new product with ID {db_product.id}")
        return db_product
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating product: {e}", exc_info=True)
        raise


def update_product(db: Session, product_id: int, product: ProductUpdate) -> Optional[Product]:
    try:
        db_product = get_product_by_id(db, product_id)
        if db_product:
            update_data = product.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_product, key, value)
            db.commit()
            db.refresh(db_product)
            logger.info(f"Updated product with ID {product_id}")
        return db_product
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating product with ID {product_id}: {e}", exc_info=True)
        return None


def delete_product(db: Session, product_id: int) -> bool:
    try:
        db_product = get_product_by_id(db, product_id)
        if db_product:
            db.delete(db_product)
            db.commit()
            logger.info(f"Deleted product with ID {product_id}")
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting product with ID {product_id}: {e}", exc_info=True)
        return False


async def discover_trending_products_from_api() -> List[Dict[str, Any]]:
    """
    Discover trending products from external APIs
    Using FakeStoreAPI as an example (free, no authentication required)
    """
    trending_products = []
    
    try:
        logger.info("Starting product discovery from external APIs")
        async with httpx.AsyncClient() as client:
            # Get all products from FakeStoreAPI
            logger.debug("Fetching products from FakeStoreAPI")
            response = await client.get("https://fakestoreapi.com/products")
            response.raise_for_status()
            products_data = response.json()
            
            logger.info(f"Retrieved {len(products_data)} products from FakeStoreAPI")
            
            # Process products and mark them as trending
            for product in products_data:
                # Convert price to string format
                price_str = f"${product.get('price', 0)}"
                
                trending_product = {
                    "name": product.get("title", "Unknown Product"),
                    "description": product.get("description", "No description available"),
                    "price": price_str,
                    "url": f"https://fakestoreapi.com/products/{product.get('id', '')}",
                    "image_url": product.get("image", ""),
                    "is_trending": True
                }
                trending_products.append(trending_product)
                
                # Limit to 10 products for demo purposes
                if len(trending_products) >= 10:
                    break
            
            logger.info(f"Processed {len(trending_products)} trending products")
    except httpx.HTTPError as e:
        logger.error(f"HTTP error occurred while fetching products: {e}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"Error discovering products: {e}", exc_info=True)
        return []
    
    return trending_products


def discover_trending_products(db: Session) -> List[Product]:
    """
    Discover trending products and save them to the database
    """
    # Use asyncio to run the async function synchronously
    import asyncio
    
    try:
        logger.info("Starting trending product discovery")
        # Run the async function
        trending_products = asyncio.run(discover_trending_products_from_api())
        logger.info(f"Discovered {len(trending_products)} trending products from APIs")
    except Exception as e:
        logger.error(f"Error running async product discovery: {e}", exc_info=True)
        trending_products = []
    
    created_products = []
    
    for product_data in trending_products:
        try:
            # Check if product already exists
            existing_product = db.query(Product).filter(Product.url == product_data["url"]).first()
            
            if not existing_product:
                # Create new product
                product_create = ProductCreate(**product_data)
                created_product = create_product(db, product_create)
                created_products.append(created_product)
            else:
                # Update existing product if it's trending
                update_data = ProductUpdate(is_trending=True)
                # Get the product ID and convert to int to satisfy type checker
                product_id = int(str(existing_product.id))
                updated_product = update_product(db, product_id, update_data)
                if updated_product:
                    created_products.append(updated_product)
        except Exception as e:
            logger.error(f"Error processing product {product_data.get('name', 'Unknown')}: {e}", exc_info=True)
            continue
    
    logger.info(f"Successfully processed {len(created_products)} products")
    return created_products


def analyze_product_trend_score(product: Product) -> float:
    """
    Analyze a product and assign a trend score based on various factors
    This is a placeholder implementation
    """
    # In a real implementation, this would analyze:
    # - Social media mentions
    # - Sales velocity
    # - Search volume
    # - Price competitiveness
    # - Product ratings
    
    # For now, return a simple score
    base_score = 50.0
    
    # Adjust based on product attributes
    # Use getattr to safely access the attribute value
    is_trending = getattr(product, 'is_trending', False)
    if is_trending is True:
        base_score += 30.0
        
    # Add some randomness for demonstration
    import random
    base_score += random.uniform(0, 20)
    
    return min(base_score, 100.0)
