import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from functools import wraps

logger = logging.getLogger(__name__)


class NutritionCache:
    """Simple in-memory cache for nutrition data"""

    def __init__(self, ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl

    def _generate_key(self, data: Any) -> str:
        """Generate cache key from data"""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        return hashlib.md5(data_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry["expires"]:
                return entry["value"]
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set cache value with expiration"""
        self.cache[key] = {
            "value": value,
            "expires": datetime.now() + timedelta(seconds=self.ttl),
        }

    def clear(self) -> None:
        """Clear all cached data"""
        self.cache.clear()


# Global cache instance
nutrition_cache = NutritionCache()


def cached(ttl: Optional[int] = None):
    """Decorator for caching function results"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = nutrition_cache._generate_key(
                {"func": func.__name__, "args": args, "kwargs": kwargs}
            )

            # Try to get from cache
            cached_result = nutrition_cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for {func.__name__}")
                return cached_result

            # Call function and cache result
            result = await func(*args, **kwargs)
            nutrition_cache.set(cache_key, result)
            logger.info(f"Cache miss for {func.__name__}, result cached")

            return result

        return wrapper

    return decorator


def format_nutrition_data(nutrition_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format nutrition data for consistent output"""
    formatted = {
        "calories": nutrition_data.get("calories", 0),
        "macronutrients": {
            "protein": nutrition_data.get("protein", 0),
            "carbohydrates": nutrition_data.get("carbs", 0),
            "fat": nutrition_data.get("fat", 0),
            "fiber": nutrition_data.get("fiber", 0),
            "sugar": nutrition_data.get("sugar", 0),
        },
        "micronutrients": {
            "sodium": nutrition_data.get("sodium", 0),
            "potassium": nutrition_data.get("potassium", 0),
            "calcium": nutrition_data.get("calcium", 0),
            "iron": nutrition_data.get("iron", 0),
            "vitamin_c": nutrition_data.get("vitamin_c", 0),
            "vitamin_a": nutrition_data.get("vitamin_a", 0),
        },
    }
    return formatted


def calculate_bmi(weight_kg: float, height_m: float) -> Dict[str, Any]:
    """Calculate BMI and category"""
    bmi = weight_kg / (height_m**2)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return {"bmi": round(bmi, 2), "category": category, "healthy_range": "18.5 - 24.9"}


def calculate_daily_calories(
    weight_kg: float, height_cm: float, age: int, gender: str, activity_level: str
) -> Dict[str, Any]:
    """Calculate daily calorie needs using Mifflin-St Jeor Equation"""

    # Base Metabolic Rate (BMR)
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # Activity multipliers
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }

    multiplier = activity_multipliers.get(activity_level.lower(), 1.55)
    daily_calories = bmr * multiplier

    return {
        "bmr": round(bmr, 0),
        "daily_calories": round(daily_calories, 0),
        "activity_level": activity_level,
        "for_weight_loss": round(daily_calories - 500, 0),
        "for_weight_gain": round(daily_calories + 500, 0),
    }
