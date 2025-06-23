"""
Validation functions for input data and API parameters.
"""

from typing import Optional, List, Dict, Any
import re
import structlog

logger = structlog.get_logger(__name__)


def validate_food_query(food_name: str) -> Optional[str]:
    """Validate food query input."""
    if not food_name:
        return "Food name cannot be empty"
    
    # Remove extra whitespace
    food_name = food_name.strip()
    
    if len(food_name) < 2:
        return "Food name must be at least 2 characters long"
    
    if len(food_name) > 200:
        return "Food name cannot exceed 200 characters"
    
    # Check for suspicious patterns
    if re.search(r'[<>{}[\]\\]', food_name):
        return "Food name contains invalid characters"
    
    # Check for SQL injection patterns (basic)
    sql_patterns = [
        r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|OR|AND)\b',
        r'[;\'"--]',
        r'\b(EXEC|EXECUTE)\b'
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, food_name, re.IGNORECASE):
            return "Food name contains invalid characters"
    
    return None


def validate_nutrient_request(nutrient_name: str, food_list: List[str]) -> Optional[str]:
    """Validate nutrient comparison request."""
    if not nutrient_name:
        return "Nutrient name cannot be empty"
    
    if not food_list:
        return "Food list cannot be empty"
    
    if len(food_list) > 20:
        return "Cannot compare more than 20 foods at once"
    
    # Validate nutrient name
    valid_nutrients = [
        "protein", "fat", "carbs", "carbohydrates", "calories", "energy",
        "fiber", "sugar", "sodium", "calcium", "iron", "vitamin c",
        "vitamin a", "vitamin d", "vitamin e", "vitamin k", "folate",
        "b12", "thiamin", "riboflavin", "niacin", "potassium", "zinc",
        "magnesium", "phosphorus", "selenium"
    ]
    
    if nutrient_name.lower() not in valid_nutrients:
        logger.warning("Nutrient not in predefined list", nutrient=nutrient_name)
        # Don't return error - allow flexibility for API to handle
    
    # Validate each food in the list
    for food in food_list:
        error = validate_food_query(food)
        if error:
            return f"Invalid food '{food}': {error}"
    
    return None


def validate_dietary_requirements(target_calories: int, dietary_restrictions: List[str]) -> Optional[str]:
    """Validate dietary requirements for meal planning."""
    if target_calories < 800:
        return "Target calories cannot be less than 800 per day"
    
    if target_calories > 5000:
        return "Target calories cannot exceed 5000 per day"
    
    # Validate dietary restrictions
    valid_restrictions = [
        "vegetarian", "vegan", "gluten-free", "dairy-free", "keto", 
        "paleo", "low-sodium", "low-carb", "high-protein", "mediterranean",
        "dash", "pescatarian", "kosher", "halal"
    ]
    
    for restriction in dietary_restrictions:
        if restriction.lower() not in valid_restrictions:
            return f"Unknown dietary restriction: {restriction}"
    
    # Check for conflicting restrictions
    conflicts = [
        (["vegetarian", "vegan"], ["pescatarian"]),
        (["vegan"], ["vegetarian"]),  # Vegan is stricter than vegetarian
        (["keto"], ["high-carb"]),
        (["low-carb"], ["high-carb"])
    ]
    
    restriction_set = set(r.lower() for r in dietary_restrictions)
    
    for group1, group2 in conflicts:
        if any(r in restriction_set for r in group1) and any(r in restriction_set for r in group2):
            return f"Conflicting dietary restrictions: {group1} and {group2}"
    
    return None


def validate_dietary_data(daily_meals: List[Dict[str, Any]]) -> Optional[str]:
    """Validate dietary data for analysis."""
    if not daily_meals:
        return "Daily meals data cannot be empty"
    
    if len(daily_meals) > 10:
        return "Cannot analyze more than 10 meals per day"
    
    for i, meal in enumerate(daily_meals):
        if not isinstance(meal, dict):
            return f"Meal {i+1} must be a dictionary"
        
        if "meal_name" not in meal:
            return f"Meal {i+1} missing 'meal_name' field"
        
        if "foods" not in meal:
            return f"Meal {i+1} missing 'foods' field"
        
        meal_name = meal["meal_name"]
        if not meal_name or not isinstance(meal_name, str):
            return f"Meal {i+1} has invalid meal name"
        
        foods = meal["foods"]
        if not isinstance(foods, list):
            return f"Meal {i+1} foods must be a list"
        
        if not foods:
            return f"Meal {i+1} ({meal_name}) has no foods"
        
        if len(foods) > 50:
            return f"Meal {i+1} ({meal_name}) has too many foods (max 50)"
        
        # Validate each food item
        for j, food_item in enumerate(foods):
            if not isinstance(food_item, dict):
                return f"Food item {j+1} in meal {i+1} must be a dictionary"
            
            required_fields = ["food", "amount", "unit"]
            for field in required_fields:
                if field not in food_item:
                    return f"Food item {j+1} in meal {i+1} missing '{field}' field"
            
            # Validate food name
            food_error = validate_food_query(food_item["food"])
            if food_error:
                return f"Food item {j+1} in meal {i+1}: {food_error}"
            
            # Validate amount
            amount = food_item["amount"]
            if not isinstance(amount, (int, float)) or amount <= 0:
                return f"Food item {j+1} in meal {i+1} has invalid amount"
            
            if amount > 10000:  # Reasonable upper limit
                return f"Food item {j+1} in meal {i+1} amount too large (max 10000)"
            
            # Validate unit
            unit = food_item["unit"]
            if not isinstance(unit, str) or not unit.strip():
                return f"Food item {j+1} in meal {i+1} has invalid unit"
            
            valid_units = [
                "g", "kg", "mg", "oz", "lb", "lbs",
                "cup", "cups", "tsp", "tbsp", "teaspoon", "tablespoon",
                "ml", "l", "fl oz", "pint", "quart", "gallon",
                "piece", "pieces", "slice", "slices", "serving", "servings",
                "small", "medium", "large", "whole", "half"
            ]
            
            if unit.lower() not in valid_units:
                logger.warning("Unit not in predefined list", unit=unit)
                # Don't return error - allow flexibility
    
    return None


def validate_person_profile(profile: Dict[str, Any]) -> Optional[str]:
    """Validate person profile data."""
    if not profile:
        return None  # Profile is optional
    
    # Age validation
    if "age" in profile:
        age = profile["age"]
        if not isinstance(age, int) or age < 1 or age > 120:
            return "Age must be between 1 and 120 years"
    
    # Gender validation
    if "gender" in profile:
        gender = profile["gender"]
        if gender not in ["male", "female"]:
            return "Gender must be 'male' or 'female'"
    
    # Weight validation
    if "weight_kg" in profile:
        weight = profile["weight_kg"]
        if not isinstance(weight, (int, float)) or weight < 20 or weight > 300:
            return "Weight must be between 20 and 300 kg"
    
    # Height validation
    if "height_cm" in profile:
        height = profile["height_cm"]
        if not isinstance(height, (int, float)) or height < 100 or height > 250:
            return "Height must be between 100 and 250 cm"
    
    # Activity level validation
    if "activity_level" in profile:
        activity = profile["activity_level"]
        valid_levels = ["sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"]
        if activity not in valid_levels:
            return f"Activity level must be one of: {', '.join(valid_levels)}"
    
    return None


def validate_recipe_data(recipe: Dict[str, Any]) -> Optional[str]:
    """Validate recipe data structure."""
    if not recipe:
        return "Recipe data cannot be empty"
    
    if "ingredients" not in recipe:
        return "Recipe missing 'ingredients' field"
    
    ingredients = recipe["ingredients"]
    if not isinstance(ingredients, list):
        return "Recipe ingredients must be a list"
    
    if not ingredients:
        return "Recipe must have at least one ingredient"
    
    if len(ingredients) > 100:
        return "Recipe cannot have more than 100 ingredients"
    
    # Validate each ingredient
    for i, ingredient in enumerate(ingredients):
        if isinstance(ingredient, str):
            # String format is acceptable
            if not ingredient.strip():
                return f"Ingredient {i+1} cannot be empty"
            if len(ingredient) > 500:
                return f"Ingredient {i+1} description too long (max 500 characters)"
        
        elif isinstance(ingredient, dict):
            # Dictionary format
            if "name" not in ingredient:
                return f"Ingredient {i+1} missing 'name' field"
            
            name = ingredient["name"]
            if not isinstance(name, str) or not name.strip():
                return f"Ingredient {i+1} has invalid name"
            
            # Validate amount if present
            if "amount" in ingredient:
                amount = ingredient["amount"]
                if not isinstance(amount, (int, float)) or amount <= 0:
                    return f"Ingredient {i+1} has invalid amount"
            
            # Validate unit if present
            if "unit" in ingredient:
                unit = ingredient["unit"]
                if not isinstance(unit, str) or not unit.strip():
                    return f"Ingredient {i+1} has invalid unit"
        
        else:
            return f"Ingredient {i+1} must be a string or dictionary"
    
    # Validate servings if present
    if "servings" in recipe:
        servings = recipe["servings"]
        if not isinstance(servings, int) or servings < 1 or servings > 50:
            return "Recipe servings must be between 1 and 50"
    
    return None


def validate_api_key(api_key: str, service_name: str = "API") -> Optional[str]:
    """Validate API key format."""
    if not api_key:
        return f"{service_name} key cannot be empty"
    
    if not isinstance(api_key, str):
        return f"{service_name} key must be a string"
    
    # Remove whitespace
    api_key = api_key.strip()
    
    if len(api_key) < 10:
        return f"{service_name} key too short (minimum 10 characters)"
    
    if len(api_key) > 200:
        return f"{service_name} key too long (maximum 200 characters)"
    
    # Check for suspicious patterns
    if re.search(r'[<>{}[\]\\]', api_key):
        return f"{service_name} key contains invalid characters"
    
    return None


def validate_date_range(start_date: str, end_date: str) -> Optional[str]:
    """Validate date range format and logic."""
    if not start_date or not end_date:
        return "Both start and end dates are required"
    
    # Basic date format validation (YYYY-MM-DD)
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    
    if not re.match(date_pattern, start_date):
        return "Start date must be in YYYY-MM-DD format"
    
    if not re.match(date_pattern, end_date):
        return "End date must be in YYYY-MM-DD format"
    
    # Parse dates for comparison
    try:
        from datetime import datetime
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start > end:
            return "Start date cannot be after end date"
        
        # Check for reasonable range (not more than 1 year)
        delta = end - start
        if delta.days > 365:
            return "Date range cannot exceed 365 days"
        
    except ValueError as e:
        return f"Invalid date format: {str(e)}"
    
    return None


def sanitize_input(input_text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not input_text:
        return ""
    
    # Remove or escape potentially dangerous characters
    sanitized = input_text.strip()
    
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    
    # Limit length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
    
    # Remove HTML tags (basic)
    sanitized = re.sub(r'<[^>]+>', '', sanitized)
    
    return sanitized


def validate_portion_size(portion_size: float, unit: str = "g") -> Optional[str]:
    """Validate portion size input."""
    if not isinstance(portion_size, (int, float)):
        return "Portion size must be a number"
    
    if portion_size <= 0:
        return "Portion size must be greater than 0"
    
    # Set reasonable limits based on unit
    max_limits = {
        "g": 5000,      # 5kg max
        "kg": 5,        # 5kg max
        "oz": 176,      # ~5kg max
        "lb": 11,       # ~5kg max
        "cup": 50,      # 50 cups max
        "ml": 5000,     # 5L max
        "l": 5          # 5L max
    }
    
    max_limit = max_limits.get(unit.lower(), 1000)
    
    if portion_size > max_limit:
        return f"Portion size too large (max {max_limit} {unit})"
    
    return None
