from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class NutritionQuery(BaseModel):
    food_item: str = Field(..., description="Food item to analyze")
    quantity: Optional[str] = Field(
        None, description="Quantity (e.g., '1 cup', '100g')"
    )

    @field_validator("food_item")
    @classmethod
    def validate_food_item(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Food item must be at least 2 characters long")
        return v.strip()


class RecipeQuery(BaseModel):
    query: str = Field(..., description="Recipe search query")
    diet_type: Optional[str] = Field(None, description="Diet type filter")
    max_results: Optional[int] = Field(10, description="Maximum number of results")

    @field_validator("max_results")
    @classmethod
    def validate_max_results(cls, v):
        if v and (v < 1 or v > 50):
            raise ValueError("max_results must be between 1 and 50")
        return v


class DietPlanQuery(BaseModel):
    target_calories: int = Field(..., description="Target daily calories")
    diet_type: Optional[str] = Field(None, description="Diet type preference")
    allergies: Optional[List[str]] = Field(None, description="Food allergies")
    preferences: Optional[List[str]] = Field(None, description="Food preferences")

    @field_validator("target_calories")
    @classmethod
    def validate_calories(cls, v):
        if v < 800 or v > 5000:
            raise ValueError("Target calories must be between 800 and 5000")
        return v


class UserProfile(BaseModel):
    age: int = Field(..., description="Age in years")
    gender: str = Field(..., description="Gender (male/female)")
    weight_kg: float = Field(..., description="Weight in kilograms")
    height_cm: float = Field(..., description="Height in centimeters")
    activity_level: str = Field(..., description="Activity level")

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if v < 1 or v > 120:
            raise ValueError("Age must be between 1 and 120")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v.lower() not in ["male", "female"]:
            raise ValueError("Gender must be 'male' or 'female'")
        return v.lower()

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v):
        if v < 20 or v > 300:
            raise ValueError("Weight must be between 20 and 300 kg")
        return v

    @field_validator("height_cm")
    @classmethod
    def validate_height(cls, v):
        if v < 100 or v > 250:
            raise ValueError("Height must be between 100 and 250 cm")
        return v

    @field_validator("activity_level")
    @classmethod
    def validate_activity_level(cls, v):
        valid_levels = ["sedentary", "light", "moderate", "active", "very_active"]
        if v.lower() not in valid_levels:
            raise ValueError(f"Activity level must be one of: {valid_levels}")
        return v.lower()
