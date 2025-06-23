"""
Meal planning tools for generating meal plans and calculating nutrition.
FastMCP compatible implementation.
"""

from typing import List, Dict, Any, Optional
import structlog

from ..services.usda_service import USDAService
from ..config import get_settings

logger = structlog.get_logger(__name__)


class MealPlanningTools:
    """Tools for meal planning and nutrition calculation."""
    
    def __init__(self):
        self.usda_service = USDAService()
        self.settings = get_settings()

    async def generate_meal_plan(
        self,
        target_calories: int,
        dietary_restrictions: Optional[List[str]] = None,
        meals_per_day: int = 3,
        days: int = 1
    ) -> str:
        """Generate a balanced meal plan based on target calories and dietary restrictions.
        Args:
        target_calories (int): Daily calorie target for the meal plan.
        dietary_restrictions (Optional[List[str]]): List of dietary restrictions (e.g., 'vegetarian', 'vegan').
        meals_per_day (int): Number of meals to include per day.
        days (int): Number of days to plan meals for.
        Returns:
            str: Formatted meal plan with food items and nutritional information.
        """
        try:
            if target_calories <= 0:
                return "Target calories must be greater than 0."
            
            if meals_per_day <= 0:
                meals_per_day = 3
            
            if days <= 0:
                days = 1
            
            dietary_restrictions = dietary_restrictions or []
            
            # Create meal plan structure
            meal_plan = await self._create_balanced_meal_plan(
                target_calories=target_calories,
                dietary_restrictions=dietary_restrictions,
                meals_per_day=meals_per_day,
                days=days
            )
            
            # Format the meal plan
            formatted_plan = self._format_meal_plan(meal_plan, target_calories, days)
            
            logger.info("Meal plan generated successfully", 
                       calories=target_calories, days=days, meals_per_day=meals_per_day)
            return formatted_plan
            
        except Exception as e:
            logger.error("Error generating meal plan", error=str(e))
            return f"Error generating meal plan: {str(e)}"

    async def calculate_meal_nutrition(
        self,
        meal_items: List[Dict[str, Any]],
        meal_name: str = "Meal"
    ) -> str:
        """Calculate total nutrition for a complete meal."""
        try:
            if not meal_items:
                return "No meal items provided for nutrition calculation."
            
            # Calculate nutrition for all items in the meal
            total_nutrition = await self._calculate_simple_meal_nutrition(meal_items)
            
            # Format the nutrition data
            formatted_nutrition = self._format_meal_nutrition(
                total_nutrition, meal_name, meal_items
            )
            
            logger.info("Meal nutrition calculated", meal_name=meal_name, items=len(meal_items))
            return formatted_nutrition
            
        except Exception as e:
            logger.error("Error calculating meal nutrition", error=str(e), meal_name=meal_name)
            return f"Error calculating nutrition for {meal_name}: {str(e)}"

    async def suggest_alternatives(
        self,
        current_foods: List[str],
        health_goal: str,
        max_alternatives: int = 5
    ) -> str:
        """Suggest healthier food alternatives based on a health goal.
        Args:
        current_foods (List[str]): List of current food items.
        health_goal (str): Health goal to guide suggestions (e.g., 'weight_loss', 'muscle_gain').
        max_alternatives (int): Maximum number of alternatives to suggest.
        Returns:
            str: Formatted list of healthier food alternatives.
        """
        try:
            if not current_foods:
                return "No foods provided for alternative suggestions."
            
            if max_alternatives <= 0:
                max_alternatives = 5
            
            # Find healthy alternatives
            alternatives = await self._find_healthy_alternatives(
                current_foods, health_goal, max_alternatives
            )
            
            # Format the alternatives
            formatted_alternatives = self._format_food_alternatives(alternatives, health_goal)
            
            logger.info("Food alternatives suggested", 
                       foods=len(current_foods), goal=health_goal)
            return formatted_alternatives
            
        except Exception as e:
            logger.error("Error suggesting alternatives", error=str(e))
            return f"Error suggesting food alternatives: {str(e)}"

    async def check_meal_balance(
        self,
        meals: List[Dict[str, Any]],
        person_profile: Dict[str, Any]
    ) -> str:
        """Check the nutritional balance of provided meals against a person's profile.
        Args:
        meals (List[Dict[str, Any]]): List of meals to analyze.
          person_profile (Dict[str, Any]): Person's nutritional profile.
        Returns:
          str: Formatted analysis of meal balance.
        """
        try:
            if not meals:
                return "No meals provided for balance analysis."
            
            if not person_profile:
                return "Person profile is required for meal balance analysis."
            
            # Analyze meal balance
            balance_analysis = await self._analyze_meal_balance(meals, person_profile)
            
            # Format the analysis
            formatted_analysis = self._format_balance_analysis(balance_analysis)
            
            logger.info("Meal balance analyzed", meals=len(meals))
            return formatted_analysis
            
        except Exception as e:
            logger.error("Error checking meal balance", error=str(e))
            return f"Error analyzing meal balance: {str(e)}"

    async def _create_balanced_meal_plan(self, **kwargs) -> dict:
        """Create a balanced meal plan (simplified implementation)."""
        target_calories = kwargs.get('target_calories', 2000)
        dietary_restrictions = kwargs.get('dietary_restrictions', [])
        meals_per_day = kwargs.get('meals_per_day', 3)
        days = kwargs.get('days', 1)
        
        # Distribute calories across meals
        calories_per_meal = target_calories // meals_per_day
        
        meal_plan = {}
        
        for day in range(1, days + 1):
            day_meals = []
            
            for meal_num in range(meals_per_day):
                if meal_num == 0:
                    meal_type = "breakfast"
                elif meal_num == 1:
                    meal_type = "lunch"
                elif meal_num == 2:
                    meal_type = "dinner"
                else:
                    meal_type = f"snack_{meal_num - 2}"
                
                # Get foods for this meal type
                meal_foods = await self._get_foods_for_meal_type(
                    meal_type, calories_per_meal, dietary_restrictions
                )
                
                day_meals.append({
                    'type': meal_type,
                    'target_calories': calories_per_meal,
                    'foods': meal_foods
                })
            
            meal_plan[f'day_{day}'] = day_meals
        
        return meal_plan

    async def _get_foods_for_meal_type(self, meal_type: str, target_calories: int, restrictions: list) -> list:
        """Get appropriate foods for a meal type."""
        # Simplified food suggestions based on meal type
        food_suggestions = {
            'breakfast': [
                {'name': 'Oatmeal with berries', 'calories': 300, 'protein': 10},
                {'name': 'Greek yogurt with nuts', 'calories': 250, 'protein': 20},
                {'name': 'Whole grain toast with avocado', 'calories': 280, 'protein': 8}
            ],
            'lunch': [
                {'name': 'Grilled chicken salad', 'calories': 400, 'protein': 35},
                {'name': 'Quinoa bowl with vegetables', 'calories': 380, 'protein': 15},
                {'name': 'Turkey and hummus wrap', 'calories': 420, 'protein': 25}
            ],
            'dinner': [
                {'name': 'Baked salmon with vegetables', 'calories': 450, 'protein': 40},
                {'name': 'Lean beef stir-fry', 'calories': 480, 'protein': 35},
                {'name': 'Vegetarian lentil curry', 'calories': 400, 'protein': 18}
            ]
        }
        
        # Filter based on dietary restrictions
        available_foods = food_suggestions.get(meal_type, food_suggestions['lunch'])
        
        # Simple filtering logic
        if 'vegetarian' in restrictions:
            available_foods = [f for f in available_foods if 'chicken' not in f['name'].lower() 
                             and 'beef' not in f['name'].lower() and 'salmon' not in f['name'].lower()]
        
        if 'vegan' in restrictions:
            available_foods = [f for f in available_foods if 'yogurt' not in f['name'].lower() 
                             and 'chicken' not in f['name'].lower() and 'beef' not in f['name'].lower()]
        
        return available_foods[:2] if available_foods else [{'name': 'Mixed vegetables', 'calories': 200, 'protein': 5}]

    async def _find_healthy_alternatives(self, foods: list, health_goal: str, max_alternatives: int) -> dict:
        """Find healthy alternatives based on health goal."""
        alternatives = {}
        
        # Define healthy alternatives based on goals
        goal_alternatives = {
            'weight_loss': {
                'white rice': ['brown rice', 'quinoa', 'cauliflower rice'],
                'white bread': ['whole grain bread', 'ezekiel bread', 'lettuce wraps'],
                'pasta': ['zucchini noodles', 'shirataki noodles', 'whole wheat pasta'],
                'potato chips': ['baked sweet potato chips', 'air-popped popcorn', 'kale chips']
            },
            'muscle_gain': {
                'cereal': ['protein oatmeal', 'greek yogurt with granola', 'protein smoothie'],
                'snacks': ['protein bars', 'nuts and seeds', 'cottage cheese'],
                'drinks': ['protein shakes', 'milk', 'chocolate milk']
            },
            'heart_health': {
                'butter': ['olive oil', 'avocado', 'nuts'],
                'red meat': ['salmon', 'chicken breast', 'legumes'],
                'fried foods': ['grilled foods', 'baked foods', 'steamed foods']
            }
        }
        
        relevant_alternatives = goal_alternatives.get(health_goal.lower(), goal_alternatives['weight_loss'])
        
        for food in foods:
            food_alternatives = []
            
            # Check for direct matches
            if food.lower() in relevant_alternatives:
                food_alternatives = relevant_alternatives[food.lower()][:max_alternatives]
            else:
                # Check for partial matches
                for key, alts in relevant_alternatives.items():
                    if key in food.lower() or food.lower() in key:
                        food_alternatives = alts[:max_alternatives]
                        break
            
            if not food_alternatives:
                # Generic healthy alternatives
                food_alternatives = ['fresh vegetables', 'lean protein', 'whole grains'][:max_alternatives]
            
            alternatives[food] = food_alternatives
        
        return alternatives

    async def _analyze_meal_balance(self, meals: list, person_profile: dict) -> dict:
        """Analyze nutritional balance of meals."""
        # Get nutrition recommendations based on profile
        recommendations = self._get_nutrition_recommendations(person_profile)
        
        # Calculate total nutrition from all meals
        total_nutrition = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
        
        for meal in meals:
            foods = meal.get('foods', [])
            for food in foods:
                total_nutrition['calories'] += food.get('calories', 0)
                total_nutrition['protein'] += food.get('protein', 0)
                total_nutrition['carbs'] += food.get('carbs', 0)
                total_nutrition['fat'] += food.get('fat', 0)
        
        # Calculate balance score
        balance_score = self._calculate_balance_score(total_nutrition, recommendations)
        
        return {
            'total_nutrition': total_nutrition,
            'recommendations': recommendations,
            'balance_score': balance_score,
            'analysis': self._get_balance_analysis(total_nutrition, recommendations)
        }

    async def _calculate_simple_meal_nutrition(self, foods: list) -> dict:
        """Calculate basic nutrition for a meal (simplified)."""
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0
        }
        
        for food_item in foods:
            # Extract nutrition info if available
            total_nutrition['calories'] += food_item.get('calories', 0)
            total_nutrition['protein'] += food_item.get('protein', 0)
            total_nutrition['carbs'] += food_item.get('carbs', 0)
            total_nutrition['fat'] += food_item.get('fat', 0)
            total_nutrition['fiber'] += food_item.get('fiber', 0)
        
        return total_nutrition

    def _get_nutrition_recommendations(self, profile: dict) -> dict:
        """Get nutrition recommendations based on profile."""
        age = profile.get('age', 30)
        gender = profile.get('gender', 'unknown')
        activity_level = profile.get('activity_level', 'moderate')
        weight = profile.get('weight', 70)
        
        # Base calorie calculation (simplified)
        if gender.lower() == 'male':
            base_calories = 2000 + (age * 5) + (weight * 12)
        else:
            base_calories = 1800 + (age * 4) + (weight * 10)
        
        # Adjust for activity level
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        multiplier = activity_multipliers.get(activity_level.lower(), 1.55)
        recommended_calories = int(base_calories * multiplier)
        
        return {
            'calories': recommended_calories,
            'protein': weight * 1.2,  # 1.2g per kg body weight
            'carbs': recommended_calories * 0.45 / 4,  # 45% of calories
            'fat': recommended_calories * 0.25 / 9  # 25% of calories
        }

    def _calculate_balance_score(self, actual: dict, recommended: dict) -> float:
        """Calculate a balance score (0-100)."""
        scores = []
        
        for nutrient in ['calories', 'protein', 'carbs', 'fat']:
            actual_val = actual.get(nutrient, 0)
            recommended_val = recommended.get(nutrient, 1)
            
            if recommended_val == 0:
                continue
            
            ratio = actual_val / recommended_val
            
            # Score based on how close to 1.0 the ratio is
            if 0.8 <= ratio <= 1.2:
                score = 100
            elif 0.6 <= ratio <= 1.4:
                score = 80
            elif 0.4 <= ratio <= 1.6:
                score = 60
            else:
                score = 40
            
            scores.append(score)
        
        return sum(scores) / len(scores) if scores else 0

    def _get_balance_analysis(self, actual: dict, recommended: dict) -> dict:
        """Get detailed balance analysis."""
        analysis = {}
        
        for nutrient in ['calories', 'protein', 'carbs', 'fat']:
            actual_val = actual.get(nutrient, 0)
            recommended_val = recommended.get(nutrient, 1)
            
            ratio = actual_val / recommended_val if recommended_val > 0 else 0
            
            if ratio < 0.8:
                status = "below target"
            elif ratio > 1.2:
                status = "above target"
            else:
                status = "on target"
            
            analysis[nutrient] = {
                'actual': actual_val,
                'recommended': recommended_val,
                'ratio': ratio,
                'status': status
            }
        
        return analysis

    def _format_meal_plan(self, meal_plan: dict, target_calories: int, days: int) -> str:
        """Format meal plan for display."""
        formatted = f"# {days}-Day Meal Plan ({target_calories} calories/day)\n\n"
        
        for day_key, meals in meal_plan.items():
            day_num = day_key.split('_')[1]
            formatted += f"## Day {day_num}\n\n"
            
            for meal in meals:
                meal_type = meal['type'].replace('_', ' ').title()
                target_cals = meal['target_calories']
                foods = meal['foods']
                
                formatted += f"### {meal_type} (Target: {target_cals} calories)\n"
                
                for food in foods:
                    name = food['name']
                    calories = food.get('calories', 0)
                    protein = food.get('protein', 0)
                    formatted += f"- {name} ({calories} cal, {protein}g protein)\n"
                
                formatted += "\n"
        
        formatted += "## Tips:\n"
        formatted += "- Adjust portion sizes to meet your exact calorie needs\n"
        formatted += "- Stay hydrated with 8-10 glasses of water daily\n"
        formatted += "- Include a variety of colorful vegetables\n"
        formatted += "- Consider meal prep for convenience\n"
        
        return formatted

    def _format_meal_nutrition(self, nutrition_data: dict, meal_name: str, meal_items: list) -> str:
        """Format meal nutrition data."""
        formatted = f"# Nutrition Analysis: {meal_name}\n\n"
        
        formatted += "## Ingredients:\n"
        for item in meal_items:
            name = item.get('name', 'Unknown item')
            amount = item.get('amount', '')
            unit = item.get('unit', '')
            formatted += f"- {amount} {unit} {name}\n"
        
        formatted += "\n## Nutritional Information:\n"
        formatted += f"- **Calories**: {nutrition_data.get('calories', 0):.0f}\n"
        formatted += f"- **Protein**: {nutrition_data.get('protein', 0):.1f}g\n"
        formatted += f"- **Carbohydrates**: {nutrition_data.get('carbs', 0):.1f}g\n"
        formatted += f"- **Fat**: {nutrition_data.get('fat', 0):.1f}g\n"
        formatted += f"- **Fiber**: {nutrition_data.get('fiber', 0):.1f}g\n"
        
        return formatted

    def _format_food_alternatives(self, alternatives: dict, health_goal: str) -> str:
        """Format food alternatives."""
        formatted = f"# Healthier Food Alternatives for {health_goal.replace('_', ' ').title()}\n\n"
        
        for original_food, alternative_list in alternatives.items():
            formatted += f"## Instead of {original_food}:\n"
            for i, alternative in enumerate(alternative_list, 1):
                formatted += f"{i}. {alternative}\n"
            formatted += "\n"
        
        formatted += "## Benefits:\n"
        if health_goal.lower() == 'weight_loss':
            formatted += "- Lower calories and refined carbs\n"
            formatted += "- Higher fiber and nutrients\n"
            formatted += "- Better satiety and blood sugar control\n"
        elif health_goal.lower() == 'muscle_gain':
            formatted += "- Higher protein content\n"
            formatted += "- Better amino acid profiles\n"
            formatted += "- Enhanced recovery and growth\n"
        else:
            formatted += "- Improved overall nutrition\n"
            formatted += "- Better long-term health outcomes\n"
        
        return formatted

    def _format_balance_analysis(self, analysis: dict) -> str:
        """Format meal balance analysis."""
        formatted = "# Meal Balance Analysis\n\n"
        
        balance_score = analysis.get('balance_score', 0)
        formatted += f"**Overall Balance Score**: {balance_score:.1f}/100\n\n"
        
        if balance_score >= 80:
            formatted += "✅ Excellent nutritional balance!\n\n"
        elif balance_score >= 60:
            formatted += "⚠️ Good balance with room for improvement\n\n"
        else:
            formatted += "❌ Poor balance - significant adjustments needed\n\n"
        
        formatted += "## Detailed Analysis:\n"
        
        nutrient_analysis = analysis.get('analysis', {})
        for nutrient, data in nutrient_analysis.items():
            actual = data['actual']
            recommended = data['recommended']
            status = data['status']
            
            formatted += f"- **{nutrient.title()}**: {actual:.1f} (recommended: {recommended:.1f}) - {status}\n"
        
        formatted += "\n## Recommendations:\n"
        for nutrient, data in nutrient_analysis.items():
            if data['status'] == 'below target':
                formatted += f"- Increase {nutrient} intake\n"
            elif data['status'] == 'above target':
                formatted += f"- Reduce {nutrient} intake\n"
        
        return formatted