"""
FastMCP Server implementation for Food & Nutrition Intelligence.
"""

import structlog
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP

from .tools.nutrition_tools import NutritionTools
from .tools.meal_planning_tools import MealPlanningTools
from .tools.dietary_analysis_tools import DietaryAnalysisTools
from .resources.nutrition_resources import NutritionResources
from .prompts.nutrition_prompts import NutritionPrompts
from .config import get_settings

logger = structlog.get_logger(__name__)


def create_server() -> FastMCP:
    """Create and configure the FastMCP server."""
    logger.info("Creating FastMCP nutrition server")
    
    # Initialize server
    mcp = FastMCP("Food & Nutrition Intelligence")
    
    # Initialize tool classes
    nutrition_tools = NutritionTools()
    meal_planning_tools = MealPlanningTools()
    dietary_analysis_tools = DietaryAnalysisTools()
    nutrition_resources = NutritionResources()
    nutrition_prompts = NutritionPrompts()
    
    # === NUTRITION TOOLS ===
    
    @mcp.tool()
    async def nutrition_get_food_data(
        food_name: str,
        portion_size: float = 100.0,
        include_detailed: bool = False
    ) -> str:
        """Get comprehensive nutrition data for a specific food item.
        
        Args:
            food_name: Name of the food to analyze
            portion_size: Portion size in grams (default: 100g)
            include_detailed: Include detailed nutrient breakdown
        """
        try:
            return await nutrition_tools.get_food_data(food_name, portion_size, include_detailed)
        except Exception as e:
            logger.error("Error getting food data", error=str(e), food_name=food_name)
            return f"Error retrieving nutrition data for {food_name}: {str(e)}"

    @mcp.tool()
    async def nutrition_search_foods(
        query: str,
        limit: int = 10
    ) -> str:
        """Search for foods in the nutrition database.
        
        Args:
            query: Search term for food items
            limit: Maximum number of results to return
        Returns:
            List of food items matching the query
        """
        try:
            return await nutrition_tools.search_foods(query, limit)
        except Exception as e:
            logger.error("Error searching foods", error=str(e), query=query)
            return f"Error searching for foods matching '{query}': {str(e)}"

    @mcp.tool()
    async def nutrition_analyze_recipe(
        ingredients: List[Dict[str, Any]],
        servings: int = 1
    ) -> str:
        """Analyze nutrition content of a recipe.
        
        Args:
            ingredients: List of ingredients with name, amount, and unit
            servings: Number of servings the recipe makes
        Returns:
            Nutrition analysis summary for the recipe
        """
        try:
            return await nutrition_tools.analyze_recipe(ingredients, servings)
        except Exception as e:
            logger.error("Error analyzing recipe", error=str(e))
            return f"Error analyzing recipe nutrition: {str(e)}"

    @mcp.tool()
    async def nutrition_compare_foods(
        foods: List[str],
        nutrient: str = "protein"
    ) -> str:
        """Compare nutrient content across multiple foods.
        
        Args:
            foods: List of food names to compare
            nutrient: Specific nutrient to compare (protein, calories, etc.)
        Returns:
            Comparison results for the specified nutrient
        """
        try:
            return await nutrition_tools.compare_foods(foods, nutrient)
        except Exception as e:
            logger.error("Error comparing foods", error=str(e))
            return f"Error comparing {nutrient} content: {str(e)}"

    # === MEAL PLANNING TOOLS ===

    @mcp.tool()
    async def meal_generate_plan(
        target_calories: int,
        dietary_restrictions: Optional[List[str]] = None,
        meals_per_day: int = 3,
        days: int = 1
    ) -> str:
        """Generate a meal plan based on nutritional requirements.
        
        Args:
            target_calories: Target daily calorie intake
            dietary_restrictions: List of dietary restrictions/preferences
            meals_per_day: Number of meals per day
            days: Number of days to plan for
        Returns:
            Generated meal plan as a string
        """
        try:
            return await meal_planning_tools.generate_meal_plan(
                target_calories, dietary_restrictions, meals_per_day, days
            )
        except Exception as e:
            logger.error("Error generating meal plan", error=str(e))
            return f"Error generating meal plan: {str(e)}"

    @mcp.tool()
    async def meal_calculate_nutrition(
        meal_items: List[Dict[str, Any]],
        meal_name: str = "Meal"
    ) -> str:
        """Calculate total nutrition for a meal.
        
        Args:
            meal_items: List of food items with amounts
            meal_name: Name of the meal
        Returns:
            Total nutrition information for the meal
        """
        try:
            return await meal_planning_tools.calculate_meal_nutrition(meal_items, meal_name)
        except Exception as e:
            logger.error("Error calculating meal nutrition", error=str(e))
            return f"Error calculating nutrition for {meal_name}: {str(e)}"

    @mcp.tool()
    async def meal_suggest_alternatives(
        current_foods: List[str],
        health_goal: str,
        max_alternatives: int = 5
    ) -> str:
        """Suggest healthier food alternatives.
        
        Args:
            current_foods: List of current food items
            health_goal: Health goal (weight_loss, muscle_gain, etc.)
            max_alternatives: Maximum number of alternatives per food
        Returns:
            Suggested alternatives for each food item
        """
        try:
            return await meal_planning_tools.suggest_alternatives(
                current_foods, health_goal, max_alternatives
            )
        except Exception as e:
            logger.error("Error suggesting alternatives", error=str(e))
            return f"Error suggesting food alternatives: {str(e)}"

    @mcp.tool()
    async def meal_balance_checker(
        meals: List[Dict[str, Any]],
        person_profile: Dict[str, Any]
    ) -> str:
        """Check nutritional balance of meals for a person.
        
        Args:
            meals: List of meals with food items
            person_profile: Person's profile (age, gender, activity level, etc.)
        Returns:
            Nutritional balance analysis for the meals
        """
        try:
            return await meal_planning_tools.check_meal_balance(meals, person_profile)
        except Exception as e:
            logger.error("Error checking meal balance", error=str(e))
            return f"Error analyzing meal balance: {str(e)}"

    # === DIETARY ANALYSIS TOOLS ===

    @mcp.tool()
    async def dietary_analyze_daily_intake(
        daily_meals: List[Dict[str, Any]],
        person_info: Dict[str, Any],
        analysis_focus: Optional[List[str]] = None
    ) -> str:
        """Analyze daily nutritional intake and provide recommendations.
        
        Args:
            daily_meals: List of meals consumed in a day
            person_info: Person's demographic and health information
            analysis_focus: Specific nutrients or aspects to focus on
        Returns:
            Analysis results and recommendations
        """
        try:
            return await dietary_analysis_tools.analyze_daily_intake(
                daily_meals, person_info, analysis_focus
            )
        except Exception as e:
            logger.error("Error analyzing daily intake", error=str(e))
            return f"Error analyzing daily intake: {str(e)}"

    @mcp.tool()
    async def dietary_check_compliance(
        food_log: List[Dict[str, Any]],
        dietary_guidelines: str,
        custom_restrictions: Optional[List[str]] = None
    ) -> str:
        """Check compliance with dietary guidelines and restrictions.
        
        Args:
            food_log: Food consumption log over multiple days
            dietary_guidelines: Type of dietary guidelines (mediterranean, keto, etc.)
            custom_restrictions: Additional custom dietary restrictions
        Returns:
            Compliance status and recommendations
        """
        try:
            return await dietary_analysis_tools.check_compliance(
                food_log, dietary_guidelines, custom_restrictions
            )
        except Exception as e:
            logger.error("Error checking compliance", error=str(e))
            return f"Error checking dietary compliance: {str(e)}"

    @mcp.tool()
    async def dietary_generate_report(
        analysis_period: Dict[str, Any],
        report_type: str = "comprehensive"
    ) -> str:
        """Generate comprehensive nutrition analysis report.
        
        Args:
            analysis_period: Time period and data for analysis
            report_type: Type of report (summary, comprehensive, trends)
        Returns:
            Nutrition analysis report
        """
        try:
            return await dietary_analysis_tools.generate_report(analysis_period, report_type)
        except Exception as e:
            logger.error("Error generating report", error=str(e))
            return f"Error generating nutrition report: {str(e)}"

    @mcp.tool()
    async def dietary_identify_patterns(
        eating_data: List[Dict[str, Any]],
        pattern_types: Optional[List[str]] = None
    ) -> str:
        """Identify eating patterns and trends in nutrition data.
        
        Args:
            eating_data: Historical eating and nutrition data
            pattern_types: Types of patterns to identify (timing, deficiencies, etc.)
        Returns:
            Identified patterns and insights
        """
        try:
            return await dietary_analysis_tools.identify_patterns(eating_data, pattern_types)
        except Exception as e:
            logger.error("Error identifying patterns", error=str(e))
            return f"Error identifying eating patterns: {str(e)}"

    # === RESOURCE ENDPOINTS ===

    @mcp.resource(uri="nutrition://usda/food-categories")
    async def usda_food_categories() -> str:
        """USDA food categories and classification system."""
        try:
            return await nutrition_resources.get_usda_food_categories()
        except Exception as e:
            logger.error("Error getting USDA categories", error=str(e))
            return f"Error retrieving USDA food categories: {str(e)}"

    @mcp.resource(uri="nutrition://guidelines/dietary")
    async def dietary_guidelines() -> str:
        """Current dietary guidelines and recommendations."""
        try:
            return await nutrition_resources.get_dietary_guidelines()
        except Exception as e:
            logger.error("Error getting dietary guidelines", error=str(e))
            return f"Error retrieving dietary guidelines: {str(e)}"

    @mcp.resource(uri="nutrition://safety/food")
    async def food_safety_info() -> str:
        """Food safety information and guidelines."""
        try:
            return await nutrition_resources.get_food_safety_info()
        except Exception as e:
            logger.error("Error getting food safety info", error=str(e))
            return f"Error retrieving food safety information: {str(e)}"

    @mcp.resource(uri="nutrition://allergens/database")
    async def allergen_database() -> str:
        """Common food allergens and intolerance information."""
        try:
            return await nutrition_resources.get_allergen_database()
        except Exception as e:
            logger.error("Error getting allergen database", error=str(e))
            return f"Error retrieving allergen information: {str(e)}"

    # === PROMPT TEMPLATES ===

    @mcp.prompt()
    async def analyze_meal_nutrition(
        meal_description: str,
        dietary_goals: str,
        health_conditions: str = "none"
    ) -> str:
        """Generate a detailed nutrition analysis prompt for a meal."""
        try:
            return await nutrition_prompts.analyze_meal_nutrition(
                meal_description, dietary_goals, health_conditions
            )
        except Exception as e:
            logger.error("Error generating meal analysis prompt", error=str(e))
            return f"Error generating meal analysis prompt: {str(e)}"

    @mcp.prompt()
    async def create_meal_plan(
        target_calories: int,
        dietary_preferences: str,
        meal_count: int = 3,
        duration_days: int = 7
    ) -> str:
        """Generate a meal planning prompt based on requirements."""
        try:
            return await nutrition_prompts.create_meal_plan(
                target_calories, dietary_preferences, meal_count, duration_days
            )
        except Exception as e:
            logger.error("Error generating meal plan prompt", error=str(e))
            return f"Error generating meal plan prompt: {str(e)}"

    @mcp.prompt()
    async def nutrition_education(
        topic: str,
        audience_level: str = "general",
        focus_areas: Optional[List[str]] = None
    ) -> str:
        """Generate nutrition education content prompt."""
        try:
            return await nutrition_prompts.nutrition_education(
                topic, audience_level, focus_areas or []
            )
        except Exception as e:
            logger.error("Error generating education prompt", error=str(e))
            return f"Error generating nutrition education prompt: {str(e)}"
    
    logger.info("FastMCP nutrition server created successfully")
    return mcp