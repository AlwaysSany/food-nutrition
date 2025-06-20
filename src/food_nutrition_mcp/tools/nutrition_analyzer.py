import logging
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from ..utils.api_client import NutritionixClient, USDAClient
from ..utils.validators import NutritionQuery
from ..utils.helpers import cached, format_nutrition_data
from ..config.settings import settings

logger = logging.getLogger(__name__)

class NutritionAnalyzer:
    """Tool for analyzing nutrition content of foods"""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self.nutritionix_client = NutritionixClient()
        self.usda_client = USDAClient()
        self._register_tools()
    
    def _register_tools(self):
        """Register MCP tools"""
        
        @self.mcp.tool()
        async def analyze_nutrition(
            food_item: str,
            quantity: str = "1 serving",
            use_usda: bool = False
        ) -> str:
            """
            Analyze the nutritional content of food items including calories, macronutrients, and micronutrients.
            
            Args:
                food_item: Name of the food item to analyze
                quantity: Quantity of the food item (e.g., '1 cup', '100g', '1 medium apple')
                use_usda: Whether to use USDA database as primary source
            
            Returns:
                Formatted nutrition analysis
            """
            
            result = await self.analyze_food_nutrition(food_item, quantity, use_usda)
            
            if "error" in result:
                return f"❌ Error: {result['error']}"
            
            # Format response
            response = f"🍎 **Nutrition Analysis for {result['food_item']} ({result['quantity']})**\n\n"
            response += f"**Calories:** {result['calories']:.1f} kcal\n\n"
            
            response += "**Macronutrients:**\n"
            macros = result['macronutrients']
            response += f"• Protein: {macros['protein']:.1f}g\n"
            response += f"• Carbohydrates: {macros['carbohydrates']:.1f}g\n"
            response += f"• Fat: {macros['fat']:.1f}g\n"
            response += f"• Fiber: {macros['fiber']:.1f}g\n"
            response += f"• Sugar: {macros['sugar']:.1f}g\n\n"
            
            response += "**Micronutrients:**\n"
            micros = result['micronutrients']
            response += f"• Sodium: {micros['sodium']:.1f}mg\n"
            response += f"• Potassium: {micros['potassium']:.1f}mg\n"
            response += f"• Calcium: {micros['calcium']:.1f}mg\n"
            response += f"• Iron: {micros['iron']:.1f}mg\n"
            response += f"• Vitamin C: {micros['vitamin_c']:.1f}mg\n"
            response += f"• Vitamin A: {micros['vitamin_a']:.1f}mcg\n\n"
            
            response += f"**Data Source:** {result['source']}"
            
            return response

        @self.mcp.tool()
        async def compare_foods(
            food_items: List[str],
            quantity: str = "100g"
        ) -> str:
            """
            Compare nutritional content between multiple food items.
            
            Args:
                food_items: List of food items to compare (max 5 items)
                quantity: Quantity for comparison (same for all items)
            
            Returns:
                Comparative nutrition analysis
            """
            
            if len(food_items) > 5:
                return "❌ Error: Maximum 5 food items can be compared at once"
            
            if len(food_items) < 2:
                return "❌ Error: At least 2 food items are required for comparison"
            
            results = []
            for food_item in food_items:
                result = await self.analyze_food_nutrition(food_item, quantity, False)
                if "error" not in result:
                    results.append(result)
            
            if not results:
                return "❌ Error: Could not analyze any of the provided food items"
            
            # Format comparison
            response = f"📊 **Nutrition Comparison ({quantity} each)**\n\n"
            
            # Calories comparison
            response += "**Calories (kcal):**\n"
            for result in results:
                response += f"• {result['food_item']}: {result['calories']:.1f}\n"
            
            response += "\n**Protein (g):**\n"
            for result in results:
                response += f"• {result['food_item']}: {result['macronutrients']['protein']:.1f}\n"
            
            response += "\n**Carbohydrates (g):**\n"
            for result in results:
                response += f"• {result['food_item']}: {result['macronutrients']['carbohydrates']:.1f}\n"
            
            response += "\n**Fat (g):**\n"
            for result in results:
                response += f"• {result['food_item']}: {result['macronutrients']['fat']:.1f}\n"
            
            # Find highest values
            highest_calories = max(results, key=lambda x: x['calories'])
            highest_protein = max(results, key=lambda x: x['macronutrients']['protein'])
            
            response += f"\n**Summary:**\n"
            response += f"• Highest calories: {highest_calories['food_item']} ({highest_calories['calories']:.1f} kcal)\n"
            response += f"• Highest protein: {highest_protein['food_item']} ({highest_protein['macronutrients']['protein']:.1f}g)\n"
            
            return response
    
    @cached(ttl=3600)
    async def analyze_food_nutrition(self, food_item: str, quantity: str = "1 serving",
                                   use_usda: bool = False) -> Dict[str, Any]:
        """Analyze nutrition content of a food item"""
        
        try:
            # Validate input
            query = NutritionQuery(food_item=food_item, quantity=quantity)
            
            # Construct search query
            search_query = f"{quantity} {food_item}" if quantity != "1 serving" else food_item
            
            nutrition_data = {}
            
            if use_usda and settings.usda_api_key:
                nutrition_data = await self._get_usda_nutrition(search_query)
            
            # Fallback to Nutritionix if USDA fails or not requested
            if not nutrition_data and settings.nutritionix_api_key:
                nutrition_data = await self._get_nutritionix_nutrition(search_query)
            
            if not nutrition_data:
                return {
                    "error": "Unable to find nutrition data for the specified food item",
                    "food_item": food_item,
                    "quantity": quantity
                }
            
            # Format and return results
            formatted_data = format_nutrition_data(nutrition_data)
            formatted_data.update({
                "food_item": food_item,
                "quantity": quantity,
                "source": nutrition_data.get("source", "unknown")
            })
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error analyzing nutrition for {food_item}: {e}")
            return {
                "error": f"Failed to analyze nutrition: {str(e)}",
                "food_item": food_item,
                "quantity": quantity
            }
    
    async def _get_nutritionix_nutrition(self, query: str) -> Dict[str, Any]:
        """Get nutrition data from Nutritionix API"""
        try:
            async with self.nutritionix_client as client:
                response = await client.get_nutrition_data(query)
                
                if response.get('foods') and len(response['foods']) > 0:
                    food_data = response['foods'][0]
                    
                    return {
                        "calories": food_data.get('nf_calories', 0),
                        "protein": food_data.get('nf_protein', 0),
                        "carbs": food_data.get('nf_total_carbohydrate', 0),
                        "fat": food_data.get('nf_total_fat', 0),
                        "fiber": food_data.get('nf_dietary_fiber', 0),
                        "sugar": food_data.get('nf_sugars', 0),
                        "sodium": food_data.get('nf_sodium', 0),
                        "potassium": food_data.get('nf_potassium', 0),
                        "source": "Nutritionix"
                    }
                    
        except Exception as e:
            logger.error(f"Nutritionix API error: {e}")
            
        return {}
    
    async def _get_usda_nutrition(self, query: str) -> Dict[str, Any]:
        """Get nutrition data from USDA API"""
        try:
            async with self.usda_client as client:
                search_response = await client.search_foods(query, page_size=5)
                
                if search_response.get('foods') and len(search_response['foods']) > 0:
                    # Get the first food item
                    food_item = search_response['foods'][0]
                    fdc_id = food_item.get('fdcId')
                    
                    if fdc_id:
                        details = await client.get_food_details(str(fdc_id))
                        return self._parse_usda_nutrition(details)
                        
        except Exception as e:
            logger.error(f"USDA API error: {e}")
            
        return {}
    
    def _parse_usda_nutrition(self, food_details: Dict[str, Any]) -> Dict[str, Any]:
        """Parse USDA nutrition data"""
        try:
            nutrients = food_details.get('foodNutrients', [])
            nutrition_data = {
                "calories": nutrients.get('calories', 0),
                "protein": nutrients.get('protein', 0),
                "carbs": nutrients.get('carbohydrate', 0),
                "fat": nutrients.get('fat', 0),
                "fiber": nutrients.get('fiber', 0),
                "sugar": nutrients.get('sugar', 0),
                "sodium": nutrients.get('sodium', 0),
                "potassium": nutrients.get('potassium', 0),
                "source": "USDA"
            }
            return nutrition_data
        except Exception as e:
            logger.error(f"Error parsing USDA nutrition data: {e}")
            return {}