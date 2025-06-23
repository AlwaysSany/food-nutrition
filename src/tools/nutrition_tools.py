"""
Nutrition-related tools for retrieving food and nutrient data.
FastMCP compatible implementation.
"""

from typing import Any, List, Dict, Optional
import structlog
import json

from ..services.usda_service import USDAService
from ..utils.validators import validate_food_query, validate_nutrient_request
from ..utils.helpers import format_nutrition_data, handle_api_error

logger = structlog.get_logger(__name__)


class NutritionTools:
    """Tools for nutrition data retrieval and analysis."""
    
    def __init__(self):
        self.usda_service = USDAService()

    async def get_food_data(
        self, 
        food_name: str, 
        portion_size: float = 100, 
        include_detailed: bool = False
    ) -> str:
        """
        Retrieve detailed nutrition data for a specific food item.
        
        Args:
            food_name (str): Name of the food item to search for.
            portion_size (float): Portion size in grams (default is 100g).
            include_detailed (bool): Whether to include detailed nutrient breakdown.
        Returns:
            str: Formatted nutrition data or error message.
        """
        try:
            # Validate input
            validate_food_query(food_name)
            
            if portion_size <= 0:
                raise ValueError("Portion size must be greater than 0")
            
            # Search for food item in USDA database
            search_results = await self.usda_service.search_foods(food_name, limit=1)
            
            if not search_results:
                return f"No nutrition data found for '{food_name}'. Try a more specific or common food name."
            
            # Get detailed nutrition data for the first result
            food_id = search_results[0].get('fdcId')
            nutrition_data = await self.usda_service.get_food_details(food_id)
            
            if not nutrition_data:
                return f"Could not retrieve detailed nutrition data for '{food_name}'."
            
            # Format the nutrition data
            formatted_data = format_nutrition_data(
                nutrition_data, 
                portion_size, 
                include_detailed
            )
            
            logger.info("Successfully retrieved food data", food_name=food_name, portion_size=portion_size)
            return formatted_data
            
        except Exception as e:
            logger.error("Error getting food data", error=str(e), food_name=food_name)
            return handle_api_error(e, f"retrieving nutrition data for '{food_name}'")

    async def search_foods(self, query: str, limit: int = 10) -> str:
        """Search for foods in the USDA database based on a query string.
        Args:
            query (str): Search query for food items.
            limit (int): Maximum number of results to return (default is 10).
        Returns:
            str: Formatted search results or error message.
        """
        try:
            # Validate input
            validate_food_query(query)
            
            if limit <= 0 or limit > 50:
                limit = 10
            
            # Search USDA database
            results = await self.usda_service.search_foods(query, limit=limit)
            if not results:
                return f"No foods found matching '{query}'. Try different search terms."
            
            # Format search results
            formatted_results = self._format_search_results(results, query)
            
            logger.info("Food search completed", query=query, results_count=len(results))
            return formatted_results
            
        except Exception as e:
            logger.error("Error searching foods", error=str(e), query=query)
            return handle_api_error(e, f"searching for foods matching '{query}'")

    
    async def compare_foods(self, foods: List[str], nutrient: str = "protein") -> str:
        """Compare the nutrient content of multiple foods.
        Args:
            foods (List[str]): List of food names to compare.
            nutrient (str): Nutrient to compare (default is "protein").
        Returns:
            str: Formatted comparison results or error message.
        """
        try:
            if not foods or len(foods) < 2:
                return "Please provide at least 2 foods to compare."
            
            if len(foods) > 10:
                foods = foods[:10]  # Limit to 10 foods for performance
            
            # Validate nutrient parameter
            valid_nutrients = ["protein", "calories", "fat", "carbs", "fiber", "sugar", "sodium"]
            if nutrient.lower() not in valid_nutrients:
                nutrient = "protein"
            
            comparison_data = []
            
            # Get nutrition data for each food
            for food in foods:
                try:
                    search_results = await self.usda_service.search_foods(food, limit=1)
                    if search_results:
                        food_id = search_results[0].get('fdcId')
                        nutrition_data = await self.usda_service.get_food_details(food_id)
                        
                        if nutrition_data:
                            comparison_data.append({
                                'name': food,
                                'data': nutrition_data
                            })
                except Exception as e:
                    logger.warning("Could not get data for food", food=food, error=str(e))
                    continue
            
            if len(comparison_data) < 2:
                return f"Could not find sufficient nutrition data to compare {nutrient} content."
            
            # Format comparison results
            comparison = self._format_nutrient_comparison(comparison_data, nutrient)
            
            logger.info("Food comparison completed", foods=len(comparison_data), nutrient=nutrient)
            return comparison
            
        except Exception as e:
            logger.error("Error comparing foods", error=str(e))
            return handle_api_error(e, f"comparing {nutrient} content across foods")

    def _format_search_results(self, results: list[dict], query: str) -> str:
        """Format food search results."""
        formatted = f"# Search Results for '{query}'\n\n"
        
        for i, food in enumerate(results, 1):
            name = food.get('description', 'Unknown')
            brand = food.get('brandOwner', '')
            category = food.get('foodCategory', '')
            
            formatted += f"**{i}. {name}**\n"
            if brand:
                formatted += f"   Brand: {brand}\n"
            if category:
                formatted += f"   Category: {category}\n"
            formatted += "\n"
        
        return formatted

    def _format_nutrient_comparison(self, data: list[dict], nutrient_name: str) -> str:
        """Format nutrient comparison data."""
        formatted = f"# {nutrient_name.title()} Comparison (per 100g)\n\n"
        
        # Extract nutrient values and sort by amount
        nutrient_data = []
        for item in data:
            food_name = item['name']
            nutrition = item['data']
            
            # Extract the specific nutrient value
            nutrient_value = self._extract_nutrient_value(nutrition, nutrient_name)
            nutrient_data.append((food_name, nutrient_value))
        
        # Sort by nutrient value (highest first)
        nutrient_data.sort(key=lambda x: x[1] if x[1] is not None else 0, reverse=True)
        
        for food_name, value in nutrient_data:
            if value is not None:
                unit = self._get_nutrient_unit(nutrient_name)
                formatted += f"**{food_name}**: {value:.2f}{unit}\n"
            else:
                formatted += f"**{food_name}**: Data not available\n"
        
        return formatted

    def _format_recipe_analysis(self, nutrition_data: dict, servings: int, ingredients: list[dict]) -> str:
        """Format recipe nutrition analysis."""
        formatted = "# Recipe Nutrition Analysis\n\n"
        
        # Add ingredients list
        formatted += "## Ingredients:\n"
        for ingredient in ingredients:
            name = ingredient.get('name', '')
            amount = ingredient.get('amount', 0)
            unit = ingredient.get('unit', '')
            formatted += f"- {amount} {unit} {name}\n"
        
        formatted += f"\n**Servings**: {servings}\n\n"
        
        # Add nutrition information
        formatted += "## Nutrition Information:\n\n"
        
        # Extract key nutrients
        calories = nutrition_data.get('calories', 0)
        protein = nutrition_data.get('totalNutrients', {}).get('PROCNT', {}).get('quantity', 0)
        fat = nutrition_data.get('totalNutrients', {}).get('FAT', {}).get('quantity', 0)
        carbs = nutrition_data.get('totalNutrients', {}).get('CHOCDF', {}).get('quantity', 0)
        fiber = nutrition_data.get('totalNutrients', {}).get('FIBTG', {}).get('quantity', 0)
        
        formatted += f"**Per Serving:**\n"
        formatted += f"- Calories: {calories/servings:.0f}\n"
        formatted += f"- Protein: {protein/servings:.1f}g\n"
        formatted += f"- Fat: {fat/servings:.1f}g\n"
        formatted += f"- Carbohydrates: {carbs/servings:.1f}g\n"
        formatted += f"- Fiber: {fiber/servings:.1f}g\n"
        
        formatted += f"\n**Total Recipe:**\n"
        formatted += f"- Calories: {calories:.0f}\n"
        formatted += f"- Protein: {protein:.1f}g\n"
        formatted += f"- Fat: {fat:.1f}g\n"
        formatted += f"- Carbohydrates: {carbs:.1f}g\n"
        formatted += f"- Fiber: {fiber:.1f}g\n"
        
        return formatted

    def _extract_nutrient_value(self, nutrition_data: dict, nutrient_name: str) -> Optional[float]:
        """Extract specific nutrient value from nutrition data."""
        nutrient_map = {
            'protein': 'Protein',
            'calories': 'Energy',
            'fat': 'Total lipid (fat)',
            'carbs': 'Carbohydrate, by difference',
            'fiber': 'Fiber, total dietary',
            'sugar': 'Sugars, total including NLEA',
            'sodium': 'Sodium, Na'
        }
        
        target_nutrient = nutrient_map.get(nutrient_name.lower(), nutrient_name)
        
        nutrients = nutrition_data.get('foodNutrients', [])
        for nutrient in nutrients:
            if nutrient.get('nutrientName') == target_nutrient:
                return nutrient.get('value', 0)
        
        return None

    def _get_nutrient_unit(self, nutrient_name: str) -> str:
        """Get the unit for a specific nutrient."""
        unit_map = {
            'protein': 'g',
            'calories': ' kcal',
            'fat': 'g',
            'carbs': 'g',
            'fiber': 'g',
            'sugar': 'g',
            'sodium': 'mg'
        }
        
        return unit_map.get(nutrient_name.lower(), '')