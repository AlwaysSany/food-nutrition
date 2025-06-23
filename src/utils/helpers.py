"""
Helper functions for data formatting, API handling, and common utilities.
"""

import asyncio
import functools
import time
from typing import Any, Dict, List, Optional, Callable
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger(__name__)


def format_nutrition_data(nutrition_data: Dict[str, Any], portion_size: float = 100, include_detailed: bool = True) -> str:
    """Format nutrition data into human-readable text."""
    if not nutrition_data:
        return "No nutrition data available."
    
    output = []
    
    # Header with food name if available
    food_name = nutrition_data.get("description", "Food Item")
    output.append(f"🥗 **{food_name}** (per {portion_size}g)")
    output.append("")
    
    # Basic nutrition facts
    output.append("**Basic Nutrition:**")
    
    # Handle different data sources (USDA vs Edamam)
    if "calories" in nutrition_data:
        # Edamam format
        calories = nutrition_data.get("calories", 0)
        output.append(f"• **Calories**: {calories:.0f} kcal")
        
        nutrients = nutrition_data.get("totalNutrients", {})
        
        # Macronutrients
        if "PROCNT" in nutrients:
            protein = nutrients["PROCNT"]["quantity"]
            output.append(f"• **Protein**: {protein:.1f}g")
        
        if "FAT" in nutrients:
            fat = nutrients["FAT"]["quantity"]
            output.append(f"• **Fat**: {fat:.1f}g")
        
        if "CHOCDF" in nutrients:
            carbs = nutrients["CHOCDF"]["quantity"]
            output.append(f"• **Carbohydrates**: {carbs:.1f}g")
        
        if "FIBTG" in nutrients:
            fiber = nutrients["FIBTG"]["quantity"]
            output.append(f"• **Fiber**: {fiber:.1f}g")
        
    elif "nutrients" in nutrition_data:
        # USDA format
        nutrients = nutrition_data["nutrients"]
        
        # Key nutrient IDs
        nutrient_map = {
            208: ("Calories", "kcal"),
            203: ("Protein", "g"),
            204: ("Fat", "g"),
            205: ("Carbohydrates", "g"),
            291: ("Fiber", "g")
        }
        
        for nutrient_id, (name, unit) in nutrient_map.items():
            if nutrient_id in nutrients:
                amount = nutrients[nutrient_id]["amount"]
                # Adjust for portion size (USDA data is per 100g)
                adjusted_amount = amount * (portion_size / 100)
                output.append(f"• **{name}**: {adjusted_amount:.1f}{unit}")
    
    # Detailed nutrients if requested
    if include_detailed:
        output.append("\n**Detailed Nutrients:**")
        
        if "totalNutrients" in nutrition_data:
            # Edamam detailed nutrients
            nutrients = nutrition_data["totalNutrients"]
            
            detailed_nutrients = {
                "NA": ("Sodium", "mg"),
                "SUGAR": ("Sugar", "g"),
                "CA": ("Calcium", "mg"),
                "FE": ("Iron", "mg"),
                "VITC": ("Vitamin C", "mg"),
                "FOLFD": ("Folate", "μg")
            }
            
            for code, (name, unit) in detailed_nutrients.items():
                if code in nutrients:
                    amount = nutrients[code]["quantity"]
                    output.append(f"• **{name}**: {amount:.1f}{unit}")
        
        elif "nutrients" in nutrition_data:
            # USDA detailed nutrients
            nutrients = nutrition_data["nutrients"]
            
            detailed_map = {
                307: ("Sodium", "mg"),
                269: ("Sugar", "g"),
                301: ("Calcium", "mg"),
                303: ("Iron", "mg"),
                401: ("Vitamin C", "mg")
            }
            
            for nutrient_id, (name, unit) in detailed_map.items():
                if nutrient_id in nutrients:
                    amount = nutrients[nutrient_id]["amount"]
                    adjusted_amount = amount * (portion_size / 100)
                    output.append(f"• **{name}**: {adjusted_amount:.1f}{unit}")
    
    # Health labels and diet compliance (Edamam)
    if "healthLabels" in nutrition_data:
        health_labels = nutrition_data["healthLabels"]
        if health_labels:
            output.append("\n**Health Labels:**")
            for label in health_labels[:5]:  # Show top 5
                output.append(f"• {label}")
    
    if "dietLabels" in nutrition_data:
        diet_labels = nutrition_data["dietLabels"]
        if diet_labels:
            output.append("\n**Diet Labels:**")
            for label in diet_labels:
                output.append(f"• {label}")
    
    # Cautions if any
    if "cautions" in nutrition_data:
        cautions = nutrition_data["cautions"]
        if cautions:
            output.append("\n**⚠️ Cautions:**")
            for caution in cautions:
                output.append(f"• {caution}")
    
    return "\n".join(output)


def format_meal_plan(meal_plan: Dict[str, Any], target_calories: int) -> str:
    """Format meal plan into human-readable text."""
    if not meal_plan:
        return "Unable to generate meal plan."
    
    output = []
    
    # Header
    output.append(f"🍽️ **Personalized Meal Plan**")
    output.append(f"Target: {target_calories} calories per day")
    output.append(f"Duration: {meal_plan.get('days', 1)} day(s)")
    
    if meal_plan.get("dietary_restrictions"):
        restrictions = ", ".join(meal_plan["dietary_restrictions"])
        output.append(f"Dietary Restrictions: {restrictions}")
    
    output.append("")
    
    # Daily plans
    for daily_plan in meal_plan.get("daily_plans", []):
        day_num = daily_plan["day"]
        output.append(f"## Day {day_num}")
        output.append("")
        
        total_daily_calories = 0
        
        for meal in daily_plan["meals"]:
            meal_name = meal["name"]
            target_meal_calories = meal["target_calories"]
            foods = meal.get("foods", [])
            
            output.append(f"### {meal_name} (~{target_meal_calories} kcal)")
            
            meal_calories = 0
            for food in foods:
                food_name = food["food"]
                amount = food["amount"]
                unit = food["unit"]
                
                # Estimate calories (simplified)
                estimated_calories = estimate_food_calories(food_name, amount, unit)
                meal_calories += estimated_calories
                
                output.append(f"• {amount}{unit} {food_name} (~{estimated_calories:.0f} kcal)")
            
            total_daily_calories += meal_calories
            output.append(f"**Meal Total: {meal_calories:.0f} kcal**")
            output.append("")
        
        output.append(f"**Daily Total: {total_daily_calories:.0f} kcal**")
        output.append("---")
        output.append("")
    
    # Meal prep tips
    output.append("## 💡 Meal Prep Tips:")
    output.append("• Prepare grains and proteins in batches")
    output.append("• Wash and chop vegetables at the start of the week")
    output.append("• Store prepared ingredients in clear containers")
    output.append("• Keep healthy snacks portioned and ready")
    
    return "\n".join(output)


def estimate_food_calories(food_name: str, amount: float, unit: str) -> float:
    """Estimate calories for a food item (simplified estimation)."""
    # Simplified calorie database per 100g
    calorie_db = {
        "chicken breast": 165,
        "salmon": 208,
        "brown rice": 123,
        "white rice": 130,
        "broccoli": 34,
        "spinach": 23,
        "banana": 89,
        "apple": 52,
        "oatmeal": 68,
        "almonds": 579,
        "avocado": 160,
        "sweet potato": 86,
        "quinoa": 120,
        "tofu": 76,
        "lentils": 116,
        "eggs": 155
    }
    
    # Convert amount to grams (simplified)
    grams = amount
    if unit.lower() in ["cup", "cups"]:
        grams = amount * 200  # Rough estimate
    elif unit.lower() in ["tbsp", "tablespoon"]:
        grams = amount * 15
    elif unit.lower() in ["tsp", "teaspoon"]:
        grams = amount * 5
    elif unit.lower() in ["oz", "ounce"]:
        grams = amount * 28.35
    elif unit.lower() in ["lb", "pound"]:
        grams = amount * 453.6
    
    # Find matching food
    food_lower = food_name.lower()
    calories_per_100g = 50  # Default fallback
    
    for food_key, calories in calorie_db.items():
        if food_key in food_lower or food_lower in food_key:
            calories_per_100g = calories
            break
    
    return (calories_per_100g * grams) / 100


def calculate_nutritional_ratios(nutrition_data: Dict[str, Any]) -> Dict[str, float]:
    """Calculate macronutrient ratios and other nutritional metrics."""
    ratios = {}
    
    if not nutrition_data:
        return ratios
    
    # Extract calories and macronutrients
    total_calories = 0
    protein_grams = 0
    carb_grams = 0
    fat_grams = 0
    
    if "calories" in nutrition_data:
        # Edamam format
        total_calories = nutrition_data["calories"]
        nutrients = nutrition_data.get("totalNutrients", {})
        
        if "PROCNT" in nutrients:
            protein_grams = nutrients["PROCNT"]["quantity"]
        if "CHOCDF" in nutrients:
            carb_grams = nutrients["CHOCDF"]["quantity"]
        if "FAT" in nutrients:
            fat_grams = nutrients["FAT"]["quantity"]
    
    elif "nutrients" in nutrition_data:
        # USDA format
        nutrients = nutrition_data["nutrients"]
        
        if 208 in nutrients:  # Energy
            total_calories = nutrients[208]["amount"]
        if 203 in nutrients:  # Protein
            protein_grams = nutrients[203]["amount"]
        if 205 in nutrients:  # Carbs
            carb_grams = nutrients[205]["amount"]
        if 204 in nutrients:  # Fat
            fat_grams = nutrients[204]["amount"]
    
    # Calculate calorie percentages
    if total_calories > 0:
        protein_calories = protein_grams * 4  # 4 kcal per gram
        carb_calories = carb_grams * 4
        fat_calories = fat_grams * 9  # 9 kcal per gram
        
        ratios["protein_percent"] = (protein_calories / total_calories) * 100
        ratios["carb_percent"] = (carb_calories / total_calories) * 100
        ratios["fat_percent"] = (fat_calories / total_calories) * 100
        
        # Additional metrics
        ratios["calories_per_gram"] = total_calories / max(1, protein_grams + carb_grams + fat_grams)
        ratios["protein_to_fat_ratio"] = protein_grams / max(1, fat_grams)
    
    return ratios


def handle_api_error(error: Exception, context: str = None) -> str:
    """Handle and format API errors for user display."""
    error_message = str(error)
    
    # Common error patterns and user-friendly messages
    if "rate limit" in error_message.lower():
        msg = "⚠️ API rate limit exceeded. Please wait a moment and try again."
    elif "api key" in error_message.lower() or "unauthorized" in error_message.lower():
        msg = "🔑 API authentication error. Please check your API key configuration."
    elif "timeout" in error_message.lower():
        msg = "⏱️ Request timed out. Please try again or check your internet connection."
    elif "not found" in error_message.lower():
        msg = "🔍 The requested item was not found. Please check your search terms."
    elif "invalid" in error_message.lower():
        msg = "❌ Invalid request format. Please check your input and try again."
    elif "network" in error_message.lower() or "connection" in error_message.lower():
        msg = "🌐 Network connection error. Please check your internet connection and try again."
    else:
        # Generic error message
        msg = f"❌ An error occurred: {error_message}"
    if context:
        return f"{msg} (while {context})"
    return msg


def handle_rate_limiting(func: Callable) -> Callable:
    """Decorator to handle API rate limiting with backoff strategy."""
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e).lower()
                
                if "rate limit" in error_msg or "429" in error_msg:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Rate limited, retrying in {delay}s", 
                                     attempt=attempt + 1, 
                                     max_retries=max_retries)
                        await asyncio.sleep(delay)
                        continue
                
                # Re-raise if not rate limit or max retries exceeded
                raise
        
        # Should not reach here
        raise Exception("Max retries exceeded")
    
    return wrapper


def cache_response(ttl: int = 3600) -> Callable:
    """Decorator to cache API responses with TTL."""
    cache = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check if we have a valid cached response
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl:
                    logger.debug("Returning cached response", cache_key=cache_key)
                    return cached_data
                else:
                    # Remove expired cache entry
                    del cache[cache_key]
            
            # Call the actual function
            result = await func(*args, **kwargs)
            
            # Cache the result
            if result is not None:
                cache[cache_key] = (result, time.time())
                logger.debug("Cached response", cache_key=cache_key)
            
            return result
        
        return wrapper
    
    return decorator


def clean_food_name(food_name: str) -> str:
    """Clean and standardize food names for API queries."""
    if not food_name:
        return ""
    
    # Remove extra whitespace and convert to title case
    cleaned = " ".join(food_name.strip().split())
    
    # Common substitutions for better API results
    substitutions = {
        "vs": "versus",
        "&": "and",
        "w/": "with",
        "wo/": "without"
    }
    
    for old, new in substitutions.items():
        cleaned = cleaned.replace(old, new)
    
    return cleaned


def parse_ingredient_text(ingredient_text: str) -> List[Dict[str, Any]]:
    """Parse ingredient text into structured format."""
    ingredients = []
    
    for line in ingredient_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Try to parse amount, unit, and ingredient
        parts = line.split()
        if len(parts) >= 2:
            amount_str = parts[0]
            
            # Try to convert first part to a number
            try:
                amount = float(amount_str)
                unit = parts[1] if len(parts) > 1 else ""
                ingredient = " ".join(parts[2:]) if len(parts) > 2 else parts[1]
                
                ingredients.append({
                    "amount": amount,
                    "unit": unit,
                    "ingredient": ingredient,
                    "original": line
                })
            except ValueError:
                # If first part isn't a number, treat whole line as ingredient
                ingredients.append({
                    "amount": 1,
                    "unit": "serving",
                    "ingredient": line,
                    "original": line
                })
        else:
            # Single word or phrase
            ingredients.append({
                "amount": 1,
                "unit": "serving",
                "ingredient": line,
                "original": line
            })
    
    return ingredients


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def calculate_bmi(weight_kg: float, height_m: float) -> Dict[str, Any]:
    """Calculate BMI and category."""
    if height_m <= 0 or weight_kg <= 0:
        return {"error": "Invalid weight or height"}
    
    bmi = weight_kg / (height_m ** 2)
    
    # BMI categories
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return {
        "bmi": round(bmi, 1),
        "category": category,
        "healthy_range": "18.5 - 24.9"
    }


def get_daily_calorie_needs(age: int, gender: str, weight_kg: float, height_cm: float, activity_level: str) -> Dict[str, Any]:
    """Calculate daily calorie needs using Mifflin-St Jeor equation."""
    
    # Base metabolic rate (BMR)
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:  # female
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    # Activity multipliers
    activity_multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.375)
    tdee = bmr * multiplier
    
    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "activity_level": activity_level,
        "weight_loss": round(tdee - 500),  # 500 calorie deficit
        "weight_gain": round(tdee + 500),  # 500 calorie surplus
        "maintenance": round(tdee)
    }
