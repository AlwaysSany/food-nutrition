"""
Data models for Food & Nutrition Intelligence MCP Server.
"""

from .nutrition_models import (
    FoodItem,
    NutrientInfo,
    NutritionData,
    MealPlan,
    DietaryProfile,
    RecipeData,
    FoodSearchResult,
    NutrientComparison
)

__all__ = [
    "FoodItem",
    "NutrientInfo", 
    "NutritionData",
    "MealPlan",
    "DietaryProfile",
    "RecipeData",
    "FoodSearchResult",
    "NutrientComparison"
]
