"""
Enhanced product discovery service with multiple e-commerce APIs
"""
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models.product import Product
from app.schemas.product import ProductCreate


class EcommerceAPIManager:
    """Manager for multiple e-commerce API integrations"""
    
    def __init__(self):
        self.apis = {
            'fakestore': self._fetch_fakestore_products,
            'amazon': self._fetch_amazon_products,
            'shopify': self._fetch_shopify_products,
            'ebay': self._fetch_ebay_products,
            'etsy': self._fetch_etsy_products,
        }
    
    async def discover_from_all_sources(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Discover products from all configured e-commerce sources"""
        all_products = []
        
        # Run all API calls concurrently
        tasks = []
        for api_name, api_func in self.apis.items():
            tasks.append(self._safe_api_call(api_name, api_func, limit // len(self.apis)))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_products.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"API call failed: {result}")
        
        # Remove duplicates and sort by relevance
        unique_products = self._deduplicate_products(all_products)
        return self._rank_products(unique_products)[:limit]
    
    async def _safe_api_call(self, api_name: str, api_func, limit: int) -> List[Dict[str, Any]]:
        """Safely call an API function with error handling"""
        try:
            logger.info(f"Fetching products from {api_name}")
            products = await api_func(limit)
            logger.info(f"Got {len(products)} products from {api_name}")
            return products
        except Exception as e:
            logger.error(f"Failed to fetch from {api_name}: {e}")
            return []
    
    async def _fetch_fakestore_products(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch products from FakeStore API (free, no auth required)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://fakestoreapi.com/products")
                response.raise_for_status()
                products_data = response.json()
                
                processed_products = []
                for product in products_data[:limit]:
                    processed_products.append({
                        "name": product.get("title", "Unknown Product"),
                        "description": product.get("description", "No description available"),
                        "price": f"${product.get('price', 0)}",
                        "url": f"https://fakestoreapi.com/products/{product.get('id', '')}",
                        "image_url": product.get("image", ""),
                        "category": product.get("category", "general"),
                        "rating": product.get("rating", {}).get("rate", 0),
                        "source": "fakestore",
                        "is_trending": True
                    })
                
                return processed_products
        except Exception as e:
            logger.error(f"FakeStore API error: {e}")
            return []
    
    async def _fetch_amazon_products(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch trending products from Amazon (requires API key)"""
        if not settings.AMAZON_API_KEY or settings.AMAZON_API_KEY == "your_amazon_api_key":
            return []
        
        try:
            # Using Amazon Product Advertising API or scraping service
            async with httpx.AsyncClient() as client:
                # Example endpoint - replace with actual Amazon API
                response = await client.get(
                    "https://webservices.amazon.com/paapi5/searchitems",
                    headers={"Authorization": f"Bearer {settings.AMAZON_API_KEY}"}
                )
                response.raise_for_status()
                data = response.json()
                
                # Process Amazon response format
                products = []
                for item in data.get("SearchResult", {}).get("Items", [])[:limit]:
                    products.append({
                        "name": item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "Unknown Product"),
                        "description": item.get("ItemInfo", {}).get("Features", {}).get("DisplayValues", [""])[0],
                        "price": item.get("Offers", {}).get("Listings", [{}])[0].get("Price", {}).get("DisplayAmount", "$0"),
                        "url": item.get("DetailPageURL", ""),
                        "image_url": item.get("Images", {}).get("Primary", {}).get("Large", {}).get("URL", ""),
                        "category": "amazon-product",
                        "rating": 4.5,  # Default rating
                        "source": "amazon",
                        "is_trending": True
                    })
                
                return products
        except Exception as e:
            logger.error(f"Amazon API error: {e}")
            return []
    
    async def _fetch_shopify_products(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch products from Shopify stores"""
        if not settings.SHOPIFY_API_KEY or settings.SHOPIFY_API_KEY == "your_shopify_api_key":
            return []
        
        try:
            # Example using Shopify Admin API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://{settings.SHOPIFY_STORE_URL}/admin/api/2023-10/products.json",
                    headers={"X-Shopify-Access-Token": settings.SHOPIFY_API_KEY}
                )
                response.raise_for_status()
                data = response.json()
                
                products = []
                for product in data.get("products", [])[:limit]:
                    # Get first variant for pricing
                    variant = product.get("variants", [{}])[0]
                    products.append({
                        "name": product.get("title", "Unknown Product"),
                        "description": product.get("body_html", "").strip() or "No description available",
                        "price": f"${variant.get('price', '0')}",
                        "url": f"https://{settings.SHOPIFY_STORE_URL}/products/{product.get('handle', '')}",
                        "image_url": product.get("images", [{}])[0].get("src", ""),
                        "category": product.get("product_type", "shopify-product"),
                        "rating": 4.0,
                        "source": "shopify",
                        "is_trending": True
                    })
                
                return products
        except Exception as e:
            logger.error(f"Shopify API error: {e}")
            return []
    
    async def _fetch_ebay_products(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch trending products from eBay"""
        if not settings.EBAY_API_KEY or settings.EBAY_API_KEY == "your_ebay_api_key":
            return []
        
        try:
            # Using eBay Browse API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.ebay.com/buy/browse/v1/item_summary/search",
                    headers={"Authorization": f"Bearer {settings.EBAY_API_KEY}"},
                    params={"q": "trending", "limit": limit}
                )
                response.raise_for_status()
                data = response.json()
                
                products = []
                for item in data.get("itemSummaries", [])[:limit]:
                    products.append({
                        "name": item.get("title", "Unknown Product"),
                        "description": item.get("shortDescription", "No description available"),
                        "price": item.get("price", {}).get("value", "$0"),
                        "url": item.get("itemWebUrl", ""),
                        "image_url": item.get("image", {}).get("imageUrl", ""),
                        "category": item.get("categories", [{}])[0].get("categoryName", "ebay-product"),
                        "rating": 4.2,
                        "source": "ebay",
                        "is_trending": True
                    })
                
                return products
        except Exception as e:
            logger.error(f"eBay API error: {e}")
            return []
    
    async def _fetch_etsy_products(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch trending products from Etsy"""
        if not settings.ETSY_API_KEY or settings.ETSY_API_KEY == "your_etsy_api_key":
            return []
        
        try:
            # Using Etsy Open API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://openapi.etsy.com/v3/application/listings/active",
                    headers={"x-api-key": settings.ETSY_API_KEY},
                    params={"limit": limit, "keywords": "trending"}
                )
                response.raise_for_status()
                data = response.json()
                
                products = []
                for listing in data.get("results", [])[:limit]:
                    products.append({
                        "name": listing.get("title", "Unknown Product"),
                        "description": listing.get("description", "No description available")[:200],
                        "price": f"${listing.get('price', {}).get('amount', 0) / 100}",  # Etsy prices in cents
                        "url": listing.get("url", ""),
                        "image_url": listing.get("images", [{}])[0].get("url_570xN", ""),
                        "category": "handmade",
                        "rating": 4.3,
                        "source": "etsy",
                        "is_trending": True
                    })
                
                return products
        except Exception as e:
            logger.error(f"Etsy API error: {e}")
            return []
    
    def _deduplicate_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate products based on name similarity"""
        seen_names = set()
        unique_products = []
        
        for product in products:
            name = product.get("name", "").lower().strip()
            # Simple deduplication - can be improved with fuzzy matching
            if name and name not in seen_names:
                seen_names.add(name)
                unique_products.append(product)
        
        return unique_products
    
    def _rank_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank products by trending score"""
        def calculate_score(product):
            score = 0
            # Rating factor
            score += product.get("rating", 0) * 10
            # Price factor (mid-range products often trend better)
            try:
                price = float(product.get("price", "$0").replace("$", ""))
                if 10 <= price <= 100:
                    score += 20
                elif 100 <= price <= 500:
                    score += 15
                else:
                    score += 5
            except:
                pass
            
            # Source diversity bonus
            source_bonus = {
                "amazon": 25,
                "shopify": 20,
                "ebay": 15,
                "etsy": 18,
                "fakestore": 10
            }
            score += source_bonus.get(product.get("source", ""), 0)
            
            return score
        
        return sorted(products, key=calculate_score, reverse=True)


# Enhanced discovery function
async def discover_enhanced_trending_products(db: Session, limit: int = 50) -> List[Product]:
    """
    Discover trending products from multiple e-commerce sources
    """
    api_manager = EcommerceAPIManager()
    
    try:
        logger.info("Starting enhanced product discovery from multiple sources")
        trending_products = await api_manager.discover_from_all_sources(limit)
        logger.info(f"Discovered {len(trending_products)} products from all sources")
    except Exception as e:
        logger.error(f"Enhanced product discovery failed: {e}")
        return []
    
    created_products = []
    
    for product_data in trending_products:
        try:
            # Check if product already exists
            existing_product = db.query(Product).filter(Product.url == product_data["url"]).first()
            
            if not existing_product:
                # Create new product
                from app.services.product_discovery import create_product
                product_create = ProductCreate(**product_data)
                created_product = create_product(db, product_create)
                created_products.append(created_product)
            else:
                # Update existing product trending status
                existing_product.is_trending = True
                db.commit()
                created_products.append(existing_product)
                
        except Exception as e:
            logger.error(f"Error processing product {product_data.get('name', 'Unknown')}: {e}")
            continue
    
    logger.info(f"Successfully processed {len(created_products)} products")
    return created_products