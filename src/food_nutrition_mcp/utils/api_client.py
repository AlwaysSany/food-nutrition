import asyncio
import logging
from typing import Any, Dict, Optional
import httpx
from ..config.settings import settings

logger = logging.getLogger(__name__)


class APIClient:
    """Base API client with rate limiting and error handling"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = httpx.AsyncClient(timeout=30.0)
        self._rate_limit_lock = asyncio.Semaphore(settings.api_rate_limit)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with rate limiting"""

        async with self._rate_limit_lock:
            try:
                url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

                # Add API key to headers if available
                request_headers = headers or {}
                if self.api_key and "Authorization" not in request_headers:
                    request_headers["Authorization"] = f"Bearer {self.api_key}"

                response = await self.session.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    params=params,
                    json=json_data,
                )

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make GET request"""
        return await self._make_request("GET", endpoint, headers, params)

    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make POST request"""
        return await self._make_request("POST", endpoint, headers, json_data=json_data)


class NutritionixClient(APIClient):
    """Nutritionix API client"""

    def __init__(self):
        super().__init__(
            base_url="https://trackapi.nutritionix.com/v2",
            api_key=settings.nutritionix_api_key,
        )
        self.app_id = settings.nutritionix_app_id

    async def get_nutrition_data(self, food_query: str) -> Dict[str, Any]:
        """Get nutrition data for food item"""
        headers = {
            "x-app-id": self.app_id,
            "x-app-key": self.api_key,
            "Content-Type": "application/json",
        }

        data = {"query": food_query, "timezone": "US/Eastern"}

        return await self.post("natural/nutrients", json_data=data, headers=headers)


class EdamamClient(APIClient):
    """Edamam API client"""

    def __init__(self):
        super().__init__(
            base_url="https://api.edamam.com/api", api_key=settings.edamam_api_key
        )
        self.app_id = settings.edamam_app_id

    async def search_recipes(
        self, query: str, diet_type: Optional[str] = None, max_results: int = 10
    ) -> Dict[str, Any]:
        """Search for recipes"""
        params = {
            "type": "public",
            "q": query,
            "app_id": self.app_id,
            "app_key": self.api_key,
            "from": 0,
            "to": max_results,
        }

        if diet_type:
            params["diet"] = diet_type

        return await self.get("recipes/v2", params=params)


class USDAClient(APIClient):
    """USDA FoodData Central API client"""

    def __init__(self):
        super().__init__(
            base_url="https://api.nal.usda.gov/fdc/v1", api_key=settings.usda_api_key
        )

    async def search_foods(self, query: str, page_size: int = 10) -> Dict[str, Any]:
        """Search USDA food database"""
        params = {"query": query, "pageSize": page_size, "api_key": self.api_key}

        return await self.get("foods/search", params=params)


class SpoonacularClient(APIClient):
    """Spoonacular API client"""

    def __init__(self):
        super().__init__(
            base_url="https://api.spoonacular.com", api_key=settings.spoonacular_api_key
        )

    async def generate_meal_plan(
        self,
        target_calories: int,
        diet: Optional[str] = None,
        exclude: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate meal plan"""
        params = {
            "timeFrame": "day",
            "targetCalories": target_calories,
            "apiKey": self.api_key,
        }

        if diet:
            params["diet"] = diet
        if exclude:
            params["exclude"] = exclude

        return await self.get("mealplanner/generate", params=params)
