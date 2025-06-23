"""
USDA FoodData Central API service for nutrition data retrieval.
"""

import asyncio
from typing import Optional, List, Dict, Any
import httpx
import structlog
from ..config import get_settings
from ..utils.helpers import handle_rate_limiting, cache_response

logger = structlog.get_logger(__name__)


class USDAService:
    """Service for interacting with USDA FoodData Central API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.USDA_BASE_URL
        self.api_key = self.settings.USDA_API_KEY
        self.client: Optional[httpx.AsyncClient] = None
        self._cache: Dict[str, Any] = {}
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            timeout=self.settings.REQUEST_TIMEOUT,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if not self.client:
            self.client = httpx.AsyncClient(
                timeout=self.settings.REQUEST_TIMEOUT,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            )
        return self.client
    
    @handle_rate_limiting
    @cache_response(ttl=3600)
    async def search_foods(self, query: str, limit: int = 10, food_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for foods in the USDA database."""

        if not self.api_key:
            raise ValueError("USDA API key not configured")
        
        client = await self._get_client()
        
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": min(limit, 200),  # USDA API limit
        }
        logger.debug("Preparing USDA search parameters", params=params) 
        if food_category:
            # Map common categories to USDA categories
            category_mapping = {
                "fruits": "Fruits and Fruit Juices",
                "vegetables": "Vegetables and Vegetable Products",
                "grains": "Cereal Grains and Pasta",
                "protein": "Poultry Products,Beef Products,Finfish and Shellfish Products",
                "dairy": "Dairy and Egg Products",
                "fats": "Fats and Oils"
            }
            
            if food_category.lower() in category_mapping:
                params["brandOwner"] = category_mapping[food_category.lower()]
        
        try:
            logger.info("Searching USDA foods", query=query, limit=limit, category=food_category)
            
            response = await client.get(f"{self.base_url}/foods/search", params=params)

            response.raise_for_status()
            
            data = response.json()
            foods = data.get("foods", [])
            
            # Process and standardize the response
            processed_foods = []
            for food in foods[:limit]:
                processed_food = {
                    "fdcId": food.get("fdcId"),
                    "description": food.get("description", ""),
                    "foodCategory": food.get("foodCategory", ""),
                    "dataType": food.get("dataType", ""),
                    "brandOwner": food.get("brandOwner", ""),
                    "ingredients": food.get("ingredients", ""),
                    "servingSize": food.get("servingSize"),
                    "servingSizeUnit": food.get("servingSizeUnit", "")
                }
                processed_foods.append(processed_food)
            
            logger.info("USDA search completed", results=len(processed_foods))
            return processed_foods
            
        except httpx.HTTPStatusError as e:

            logger.error("USDA API HTTP error", status=e.response.status_code, error=str(e))
            if e.response.status_code == 429:
                raise ValueError("Rate limit exceeded. Please try again later.")
            elif e.response.status_code == 401:
                raise ValueError("Invalid USDA API key")
            else:
                raise ValueError(f"USDA API error: {e.response.status_code}")
        except Exception as e:
            logger.error("USDA search failed", error=str(e))
            raise ValueError(f"Failed to search USDA database: {str(e)}")
    
    @handle_rate_limiting
    @cache_response(ttl=3600)
    async def get_food_details(self, food_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed nutrition information for a specific food."""
        if not self.api_key:
            raise ValueError("USDA API key not configured")
        
        try:
            # First search for the food
            search_results = await self.search_foods(food_name, limit=1)
            
            if not search_results:
                logger.warning("No USDA results found", food=food_name)
                return None
            
            fdc_id = search_results[0]["fdcId"]
            return await self.get_food_by_id(fdc_id)
            
        except Exception as e:
            logger.error("Failed to get food details", food=food_name, error=str(e))
            return None
    
    @handle_rate_limiting
    @cache_response(ttl=3600)
    async def get_food_by_id(self, fdc_id: int) -> Optional[Dict[str, Any]]:
        """Get food details by FDC ID."""
        if not self.api_key:
            raise ValueError("USDA API key not configured")
        
        client = await self._get_client()
        
        params = {
            "api_key": self.api_key,
            "nutrients": [203, 204, 205, 208, 291, 269, 301, 303, 307, 401]  # Key nutrients
        }
        
        try:
            logger.info("Getting USDA food by ID", fdc_id=fdc_id)
            
            response = await client.get(f"{self.base_url}/food/{fdc_id}", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Process nutrition data
            processed_data = {
                "fdcId": data.get("fdcId"),
                "description": data.get("description", ""),
                "foodCategory": data.get("foodCategory", ""),
                "dataType": data.get("dataType", ""),
                "nutrients": {},
                "portions": []
            }
            
            # Extract nutrients
            food_nutrients = data.get("foodNutrients", [])
            for nutrient in food_nutrients:
                nutrient_info = nutrient.get("nutrient", {})
                nutrient_id = nutrient_info.get("id")
                nutrient_name = nutrient_info.get("name", "")
                amount = nutrient.get("amount", 0)
                unit = nutrient_info.get("unitName", "")
                
                if nutrient_id:
                    processed_data["nutrients"][nutrient_id] = {
                        "name": nutrient_name,
                        "amount": amount,
                        "unit": unit
                    }
            
            # Extract portion information
            food_portions = data.get("foodPortions", [])
            for portion in food_portions:
                portion_info = {
                    "modifier": portion.get("modifier", ""),
                    "gramWeight": portion.get("gramWeight", 0),
                    "amount": portion.get("amount", 1),
                    "measureUnit": portion.get("measureUnit", {}).get("name", "")
                }
                processed_data["portions"].append(portion_info)
            
            return processed_data
            
        except httpx.HTTPStatusError as e:
            logger.error("USDA API HTTP error for food ID", fdc_id=fdc_id, status=e.response.status_code)
            return None
        except Exception as e:
            logger.error("Failed to get food by ID", fdc_id=fdc_id, error=str(e))
            return None
    
    async def get_nutrient_comparison(self, nutrient_name: str, food_list: List[str], sort_by_content: bool = True) -> List[Dict[str, Any]]:
        """Compare nutrient content across multiple foods."""
        comparison_results = []
        
        # Nutrient ID mapping for common nutrients
        nutrient_mapping = {
            "protein": 203,
            "fat": 204,
            "carbohydrates": 205,
            "carbs": 205,
            "calories": 208,
            "energy": 208,
            "fiber": 291,
            "sugar": 269,
            "calcium": 301,
            "iron": 303,
            "sodium": 307,
            "vitamin c": 401,
            "vitamin_c": 401
        }
        
        target_nutrient_id = nutrient_mapping.get(nutrient_name.lower())
        
        for food_name in food_list:
            try:
                food_data = await self.get_food_details(food_name)
                
                if food_data and "nutrients" in food_data:
                    nutrients = food_data["nutrients"]
                    nutrient_content = 0
                    nutrient_unit = "g"
                    
                    # Look for the specific nutrient
                    if target_nutrient_id and target_nutrient_id in nutrients:
                        nutrient_info = nutrients[target_nutrient_id]
                        nutrient_content = nutrient_info["amount"]
                        nutrient_unit = nutrient_info["unit"]
                    else:
                        # Search by name if ID not found
                        for nutrient_id, nutrient_info in nutrients.items():
                            if nutrient_name.lower() in nutrient_info["name"].lower():
                                nutrient_content = nutrient_info["amount"]
                                nutrient_unit = nutrient_info["unit"]
                                break
                    
                    comparison_results.append({
                        "food_name": food_name,
                        "nutrient_content": nutrient_content,
                        "unit": nutrient_unit,
                        "food_description": food_data.get("description", food_name)
                    })
                else:
                    # Add entry with zero content if food not found
                    comparison_results.append({
                        "food_name": food_name,
                        "nutrient_content": 0,
                        "unit": "g",
                        "food_description": food_name,
                        "note": "Food not found in database"
                    })
                    
            except Exception as e:
                logger.warning("Failed to get nutrient data for food", food=food_name, error=str(e))
                comparison_results.append({
                    "food_name": food_name,
                    "nutrient_content": 0,
                    "unit": "g",
                    "food_description": food_name,
                    "note": f"Error retrieving data: {str(e)}"
                })
        
        # Sort by nutrient content if requested
        if sort_by_content:
            comparison_results.sort(key=lambda x: x["nutrient_content"], reverse=True)
        
        logger.info("Nutrient comparison completed", 
                   nutrient=nutrient_name, 
                   foods=len(comparison_results))
        
        return comparison_results
    
    async def get_food_categories(self) -> List[Dict[str, Any]]:
        """Get list of all food categories from USDA."""
        if not self.api_key:
            raise ValueError("USDA API key not configured")
        
        # Return predefined categories since USDA doesn't have a dedicated endpoint
        categories = [
            {"id": 1, "name": "Dairy and Egg Products"},
            {"id": 2, "name": "Spices and Herbs"},
            {"id": 3, "name": "Baby Foods"},
            {"id": 4, "name": "Fats and Oils"},
            {"id": 5, "name": "Poultry Products"},
            {"id": 6, "name": "Soups, Sauces, and Gravies"},
            {"id": 7, "name": "Sausages and Luncheon Meats"},
            {"id": 8, "name": "Breakfast Cereals"},
            {"id": 9, "name": "Fruits and Fruit Juices"},
            {"id": 10, "name": "Pork Products"},
            {"id": 11, "name": "Vegetables and Vegetable Products"},
            {"id": 12, "name": "Nut and Seed Products"},
            {"id": 13, "name": "Beef Products"},
            {"id": 14, "name": "Beverages"},
            {"id": 15, "name": "Finfish and Shellfish Products"},
            {"id": 16, "name": "Legumes and Legume Products"},
            {"id": 17, "name": "Lamb, Veal, and Game Products"},
            {"id": 18, "name": "Baked Products"},
            {"id": 19, "name": "Sweets"},
            {"id": 20, "name": "Cereal Grains and Pasta"},
            {"id": 21, "name": "Fast Foods"},
            {"id": 22, "name": "Meals, Entrees, and Side Dishes"},
            {"id": 23, "name": "Snacks"},
            {"id": 25, "name": "Alcoholic Beverages"}
        ]
        
        return categories
    
    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
