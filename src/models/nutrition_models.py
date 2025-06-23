"""
Pydantic data models for Food & Nutrition Intelligence MCP Server.
"""

from typing import List, Dict, Optional, Any, Union
from datetime import datetime, date
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum


class GenderEnum(str, Enum):
    """Gender enumeration."""
    MALE = "male"
    FEMALE = "female"


class ActivityLevelEnum(str, Enum):
    """Activity level enumeration."""
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTRA_ACTIVE = "extra_active"


class DietaryRestrictionEnum(str, Enum):
    """Dietary restriction enumeration."""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten-free"
    DAIRY_FREE = "dairy-free"
    KETO = "keto"
    PALEO = "paleo"
    LOW_SODIUM = "low-sodium"
    LOW_CARB = "low-carb"
    HIGH_PROTEIN = "high-protein"
    MEDITERRANEAN = "mediterranean"
    DASH = "dash"
    PESCATARIAN = "pescatarian"
    KOSHER = "kosher"
    HALAL = "halal"


class UnitEnum(str, Enum):
    """Unit enumeration for measurements."""
    # Weight units
    GRAM = "g"
    KILOGRAM = "kg"
    MILLIGRAM = "mg"
    OUNCE = "oz"
    POUND = "lb"
    
    # Volume units
    MILLILITER = "ml"
    LITER = "l"
    CUP = "cup"
    TABLESPOON = "tbsp"
    TEASPOON = "tsp"
    FLUID_OUNCE = "fl oz"
    PINT = "pint"
    QUART = "quart"
    GALLON = "gallon"
    
    # Count units
    PIECE = "piece"
    SLICE = "slice"
    SERVING = "serving"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    WHOLE = "whole"
    HALF = "half"


class NutrientInfo(BaseModel):
    """Information about a specific nutrient."""
    
    id: Optional[int] = Field(None, description="Nutrient ID (USDA format)")
    code: Optional[str] = Field(None, description="Nutrient code (Edamam format)")
    name: str = Field(..., description="Nutrient name")
    amount: float = Field(..., ge=0, description="Amount of nutrient")
    unit: str = Field(..., description="Unit of measurement")
    daily_value_percent: Optional[float] = Field(None, ge=0, le=1000, description="Percentage of daily value")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 203,
                "code": "PROCNT",
                "name": "Protein",
                "amount": 25.4,
                "unit": "g",
                "daily_value_percent": 50.8
            }
        }


class FoodPortion(BaseModel):
    """Food portion information."""
    
    modifier: Optional[str] = Field(None, description="Portion modifier (e.g., 'medium', 'large')")
    gram_weight: float = Field(..., gt=0, description="Weight in grams")
    amount: float = Field(1.0, gt=0, description="Amount of this portion")
    measure_unit: str = Field(..., description="Unit of measurement")
    
    class Config:
        schema_extra = {
            "example": {
                "modifier": "medium",
                "gram_weight": 182.0,
                "amount": 1.0,
                "measure_unit": "apple"
            }
        }


class FoodItem(BaseModel):
    """Represents a food item with nutritional information."""
    
    fdc_id: Optional[int] = Field(None, description="USDA FDC ID")
    description: str = Field(..., min_length=1, max_length=500, description="Food description")
    food_category: Optional[str] = Field(None, description="Food category")
    data_type: Optional[str] = Field(None, description="Data type (Foundation, SR Legacy, etc.)")
    brand_owner: Optional[str] = Field(None, description="Brand owner")
    ingredients: Optional[str] = Field(None, description="Ingredient list")
    serving_size: Optional[float] = Field(None, gt=0, description="Standard serving size")
    serving_size_unit: Optional[str] = Field(None, description="Unit for serving size")
    nutrients: Dict[str, NutrientInfo] = Field(default_factory=dict, description="Nutrient information")
    portions: List[FoodPortion] = Field(default_factory=list, description="Available portion sizes")
    
    class Config:
        schema_extra = {
            "example": {
                "fdc_id": 747447,
                "description": "Chicken, broiler or fryers, breast, skinless, boneless, meat only, cooked, grilled",
                "food_category": "Poultry Products",
                "data_type": "Foundation",
                "serving_size": 85.0,
                "serving_size_unit": "g",
                "nutrients": {},
                "portions": []
            }
        }


class IngredientItem(BaseModel):
    """Represents an ingredient in a recipe or meal."""
    
    food: str = Field(..., min_length=1, max_length=200, description="Food name")
    amount: float = Field(..., gt=0, le=10000, description="Amount")
    unit: UnitEnum = Field(..., description="Unit of measurement")
    
    @validator('food')
    def validate_food_name(cls, v):
        """Validate food name."""
        import re
        if re.search(r'[<>{}[\]\\]', v):
            raise ValueError('Food name contains invalid characters')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "food": "chicken breast",
                "amount": 150.0,
                "unit": "g"
            }
        }


class NutritionData(BaseModel):
    """Complete nutrition data for a food item or meal."""
    
    calories: float = Field(0.0, ge=0, description="Total calories")
    total_weight: float = Field(0.0, ge=0, description="Total weight in grams")
    total_time: Optional[int] = Field(None, description="Total preparation time")
    
    # Macronutrients
    protein: float = Field(0.0, ge=0, description="Protein in grams")
    carbohydrates: float = Field(0.0, ge=0, alias="carbs", description="Carbohydrates in grams")
    fat: float = Field(0.0, ge=0, description="Fat in grams")
    fiber: float = Field(0.0, ge=0, description="Fiber in grams")
    sugar: float = Field(0.0, ge=0, description="Sugar in grams")
    
    # Micronutrients
    sodium: float = Field(0.0, ge=0, description="Sodium in mg")
    calcium: float = Field(0.0, ge=0, description="Calcium in mg")
    iron: float = Field(0.0, ge=0, description="Iron in mg")
    vitamin_c: float = Field(0.0, ge=0, description="Vitamin C in mg")
    vitamin_a: float = Field(0.0, ge=0, description="Vitamin A in μg")
    
    # Additional nutrients
    nutrients: Dict[str, NutrientInfo] = Field(default_factory=dict, description="Detailed nutrient breakdown")
    
    # Labels and classifications
    diet_labels: List[str] = Field(default_factory=list, description="Diet labels (vegetarian, vegan, etc.)")
    health_labels: List[str] = Field(default_factory=list, description="Health labels (low-sodium, etc.)")
    cautions: List[str] = Field(default_factory=list, description="Health cautions")
    
    # Ratios and percentages
    protein_percent: Optional[float] = Field(None, ge=0, le=100, description="Protein percentage of calories")
    carb_percent: Optional[float] = Field(None, ge=0, le=100, description="Carb percentage of calories")
    fat_percent: Optional[float] = Field(None, ge=0, le=100, description="Fat percentage of calories")
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "calories": 165.0,
                "total_weight": 100.0,
                "protein": 31.0,
                "carbohydrates": 0.0,
                "fat": 3.6,
                "fiber": 0.0,
                "sugar": 0.0,
                "sodium": 74.0,
                "diet_labels": [],
                "health_labels": ["low-carb", "high-protein"]
            }
        }


class MealInfo(BaseModel):
    """Information about a single meal."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Meal name")
    foods: List[IngredientItem] = Field(..., min_items=1, max_items=50, description="Foods in the meal")
    time: Optional[str] = Field(None, regex=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', description="Meal time (HH:MM)")
    target_calories: Optional[int] = Field(None, gt=0, description="Target calories for this meal")
    nutrition: Optional[NutritionData] = Field(None, description="Calculated nutrition data")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Breakfast",
                "time": "08:00",
                "target_calories": 400,
                "foods": [
                    {"food": "oatmeal", "amount": 50, "unit": "g"},
                    {"food": "banana", "amount": 1, "unit": "medium"}
                ]
            }
        }


class DailyMealPlan(BaseModel):
    """Daily meal plan with multiple meals."""
    
    date: date = Field(..., description="Date for this meal plan")
    day_of_week: Optional[str] = Field(None, description="Day of the week")
    meals: List[MealInfo] = Field(..., min_items=1, max_items=10, description="Meals for the day")
    total_nutrition: Optional[NutritionData] = Field(None, description="Total daily nutrition")
    target_calories: Optional[int] = Field(None, gt=0, description="Target daily calories")
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2025-06-20",
                "day_of_week": "Tuesday",
                "target_calories": 2000,
                "meals": []
            }
        }


class MealPlan(BaseModel):
    """Complete meal plan for multiple days."""
    
    title: Optional[str] = Field(None, description="Meal plan title")
    start_date: date = Field(..., description="Start date")
    end_date: date = Field(..., description="End date")
    target_calories: int = Field(..., gt=800, le=5000, description="Target daily calories")
    meals_per_day: int = Field(3, ge=1, le=6, description="Number of meals per day")
    dietary_restrictions: List[DietaryRestrictionEnum] = Field(default_factory=list, description="Dietary restrictions")
    daily_plans: List[DailyMealPlan] = Field(..., min_items=1, description="Daily meal plans")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validate that end date is after start date."""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        if 'start_date' in values and (v - values['start_date']).days > 365:
            raise ValueError('meal plan cannot exceed 365 days')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Weekly Healthy Meal Plan",
                "start_date": "2025-06-20",
                "end_date": "2025-06-26",
                "target_calories": 2000,
                "meals_per_day": 3,
                "dietary_restrictions": ["vegetarian"],
                "daily_plans": []
            }
        }


class DietaryProfile(BaseModel):
    """User's dietary profile and preferences."""
    
    # Demographics
    age: Optional[int] = Field(None, ge=1, le=120, description="Age in years")
    gender: Optional[GenderEnum] = Field(None, description="Gender")
    weight_kg: Optional[float] = Field(None, gt=20, le=300, description="Weight in kilograms")
    height_cm: Optional[float] = Field(None, gt=100, le=250, description="Height in centimeters")
    activity_level: Optional[ActivityLevelEnum] = Field(None, description="Activity level")
    
    # Dietary preferences and restrictions
    dietary_restrictions: List[DietaryRestrictionEnum] = Field(default_factory=list, description="Dietary restrictions")
    food_allergies: List[str] = Field(default_factory=list, description="Food allergies")
    disliked_foods: List[str] = Field(default_factory=list, description="Disliked foods")
    preferred_cuisines: List[str] = Field(default_factory=list, description="Preferred cuisines")
    
    # Health goals
    health_goals: List[str] = Field(default_factory=list, description="Health and fitness goals")
    medical_conditions: List[str] = Field(default_factory=list, description="Relevant medical conditions")
    
    # Calculated values
    bmr: Optional[float] = Field(None, description="Basal Metabolic Rate")
    tdee: Optional[float] = Field(None, description="Total Daily Energy Expenditure")
    target_calories: Optional[int] = Field(None, description="Target daily calories")
    
    class Config:
        schema_extra = {
            "example": {
                "age": 30,
                "gender": "female",
                "weight_kg": 65.0,
                "height_cm": 165.0,
                "activity_level": "moderately_active",
                "dietary_restrictions": ["vegetarian"],
                "health_goals": ["weight_maintenance", "muscle_gain"],
                "target_calories": 2000
            }
        }


class RecipeData(BaseModel):
    """Recipe data structure."""
    
    title: str = Field(..., min_length=1, max_length=200, description="Recipe title")
    description: Optional[str] = Field(None, max_length=1000, description="Recipe description")
    ingredients: List[Union[IngredientItem, str]] = Field(..., min_items=1, max_items=100, description="Recipe ingredients")
    instructions: Optional[List[str]] = Field(None, description="Cooking instructions")
    servings: int = Field(1, ge=1, le=50, description="Number of servings")
    prep_time: Optional[int] = Field(None, ge=0, description="Preparation time in minutes")
    cook_time: Optional[int] = Field(None, ge=0, description="Cooking time in minutes")
    total_time: Optional[int] = Field(None, ge=0, description="Total time in minutes")
    difficulty_level: Optional[str] = Field(None, description="Difficulty level")
    cuisine_type: Optional[str] = Field(None, description="Cuisine type")
    nutrition: Optional[NutritionData] = Field(None, description="Nutritional information")
    
    @root_validator
    def validate_times(cls, values):
        """Validate time relationships."""
        prep_time = values.get('prep_time', 0) or 0
        cook_time = values.get('cook_time', 0) or 0
        total_time = values.get('total_time')
        
        if total_time and total_time < max(prep_time, cook_time):
            raise ValueError('total_time cannot be less than prep_time or cook_time')
        
        return values
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Grilled Chicken Salad",
                "description": "Healthy grilled chicken salad with mixed greens",
                "servings": 2,
                "prep_time": 15,
                "cook_time": 10,
                "ingredients": [
                    {"food": "chicken breast", "amount": 200, "unit": "g"},
                    {"food": "mixed greens", "amount": 100, "unit": "g"}
                ]
            }
        }


class FoodSearchResult(BaseModel):
    """Result from food search operations."""
    
    fdc_id: Optional[int] = Field(None, description="USDA FDC ID")
    description: str = Field(..., description="Food description")
    food_category: Optional[str] = Field(None, description="Food category")
    data_type: Optional[str] = Field(None, description="Data type")
    brand_owner: Optional[str] = Field(None, description="Brand owner")
    score: Optional[float] = Field(None, ge=0, le=1, description="Search relevance score")
    
    class Config:
        schema_extra = {
            "example": {
                "fdc_id": 747447,
                "description": "Chicken, broiler or fryers, breast, skinless, boneless, meat only, cooked, grilled",
                "food_category": "Poultry Products",
                "data_type": "Foundation",
                "score": 0.95
            }
        }


class NutrientComparison(BaseModel):
    """Comparison of nutrient content across foods."""
    
    nutrient_name: str = Field(..., description="Name of the nutrient being compared")
    nutrient_unit: str = Field(..., description="Unit of measurement")
    foods: List[Dict[str, Any]] = Field(..., description="List of foods with nutrient content")
    sorted_by_content: bool = Field(True, description="Whether results are sorted by content")
    
    class Config:
        schema_extra = {
            "example": {
                "nutrient_name": "Protein",
                "nutrient_unit": "g",
                "sorted_by_content": True,
                "foods": [
                    {
                        "food_name": "chicken breast",
                        "nutrient_content": 31.0,
                        "description": "Chicken, broiler or fryers, breast, skinless, boneless, meat only, cooked, grilled"
                    }
                ]
            }
        }


class DietaryAnalysisResult(BaseModel):
    """Results from dietary analysis."""
    
    analysis_date: datetime = Field(default_factory=datetime.now, description="When analysis was performed")
    period_start: date = Field(..., description="Start date of analysis period")
    period_end: date = Field(..., description="End date of analysis period")
    total_days: int = Field(..., ge=1, description="Number of days analyzed")
    
    # Average daily values
    avg_calories: float = Field(0.0, ge=0, description="Average daily calories")
    avg_protein: float = Field(0.0, ge=0, description="Average daily protein (g)")
    avg_carbs: float = Field(0.0, ge=0, description="Average daily carbs (g)")
    avg_fat: float = Field(0.0, ge=0, description="Average daily fat (g)")
    avg_fiber: float = Field(0.0, ge=0, description="Average daily fiber (g)")
    avg_sodium: float = Field(0.0, ge=0, description="Average daily sodium (mg)")
    
    # Analysis results
    nutritional_deficiencies: List[str] = Field(default_factory=list, description="Identified deficiencies")
    nutritional_excesses: List[str] = Field(default_factory=list, description="Identified excesses")
    dietary_compliance: Dict[str, bool] = Field(default_factory=dict, description="Compliance with dietary guidelines")
    health_score: Optional[float] = Field(None, ge=0, le=100, description="Overall health score")
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Dietary recommendations")
    meal_timing_patterns: Dict[str, Any] = Field(default_factory=dict, description="Meal timing analysis")
    food_variety_score: Optional[float] = Field(None, ge=0, le=100, description="Food variety score")
    
    class Config:
        schema_extra = {
            "example": {
                "period_start": "2025-06-01",
                "period_end": "2025-06-07",
                "total_days": 7,
                "avg_calories": 2000.0,
                "avg_protein": 80.0,
                "avg_carbs": 250.0,
                "avg_fat": 67.0,
                "nutritional_deficiencies": ["fiber", "vitamin_d"],
                "health_score": 75.0
            }
        }


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if request failed")
    message: Optional[str] = Field(None, description="Additional message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {"calories": 165, "protein": 31},
                "message": "Nutrition data retrieved successfully",
                "timestamp": "2025-06-20T10:00:00Z"
            }
        }


class HealthMetrics(BaseModel):
    """Health metrics and biomarkers."""
    
    # Basic measurements
    weight_kg: Optional[float] = Field(None, gt=0, description="Current weight in kg")
    height_cm: Optional[float] = Field(None, gt=0, description="Height in cm")
    bmi: Optional[float] = Field(None, gt=0, description="Body Mass Index")
    body_fat_percent: Optional[float] = Field(None, ge=0, le=100, description="Body fat percentage")
    
    # Cardiovascular
    systolic_bp: Optional[int] = Field(None, ge=70, le=250, description="Systolic blood pressure")
    diastolic_bp: Optional[int] = Field(None, ge=40, le=150, description="Diastolic blood pressure")
    resting_heart_rate: Optional[int] = Field(None, ge=30, le=200, description="Resting heart rate")
    
    # Blood markers
    total_cholesterol: Optional[float] = Field(None, ge=0, description="Total cholesterol (mg/dL)")
    ldl_cholesterol: Optional[float] = Field(None, ge=0, description="LDL cholesterol (mg/dL)")
    hdl_cholesterol: Optional[float] = Field(None, ge=0, description="HDL cholesterol (mg/dL)")
    triglycerides: Optional[float] = Field(None, ge=0, description="Triglycerides (mg/dL)")
    blood_glucose: Optional[float] = Field(None, ge=0, description="Blood glucose (mg/dL)")
    hba1c: Optional[float] = Field(None, ge=0, le=20, description="HbA1c percentage")
    
    # Vitamins and minerals
    vitamin_d: Optional[float] = Field(None, ge=0, description="Vitamin D (ng/mL)")
    vitamin_b12: Optional[float] = Field(None, ge=0, description="Vitamin B12 (pg/mL)")
    iron: Optional[float] = Field(None, ge=0, description="Iron (μg/dL)")
    
    # Timestamps
    measurement_date: Optional[date] = Field(None, description="Date of measurements")
    
    class Config:
        schema_extra = {
            "example": {
                "weight_kg": 70.0,
                "height_cm": 170.0,
                "bmi": 24.2,
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "total_cholesterol": 180.0,
                "measurement_date": "2025-06-20"
            }
        }
