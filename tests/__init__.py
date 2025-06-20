"""
Test package for Food & Nutrition Intelligence MCP Server.
"""

import pytest
import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Pytest configuration for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from unittest.mock import Mock
    
    settings = Mock()
    settings.USDA_API_KEY = "test_usda_key"
    settings.EDAMAM_APP_ID = "test_edamam_id"
    settings.EDAMAM_APP_KEY = "test_edamam_key"
    settings.USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
    settings.EDAMAM_BASE_URL = "https://api.edamam.com/api/nutrition-data/v2"
    settings.REQUEST_TIMEOUT = 30
    settings.MAX_RETRIES = 3
    settings.MAX_REQUESTS_PER_MINUTE = 60
    settings.CACHE_TTL = 3600
    settings.DEBUG = True
    settings.LOG_LEVEL = "DEBUG"
    settings.VERSION = "1.0.0"
    
    return settings


@pytest.fixture
def sample_nutrition_data():
    """Sample nutrition data for testing."""
    return {
        "calories": 165,
        "totalWeight": 100,
        "totalNutrients": {
            "PROCNT": {
                "label": "Protein",
                "quantity": 31.0,
                "unit": "g"
            },
            "FAT": {
                "label": "Total lipid (fat)",
                "quantity": 3.6,
                "unit": "g"
            },
            "CHOCDF": {
                "label": "Carbohydrate, by difference",
                "quantity": 0.0,
                "unit": "g"
            },
            "FIBTG": {
                "label": "Fiber, total dietary",
                "quantity": 0.0,
                "unit": "g"
            },
            "NA": {
                "label": "Sodium, Na",
                "quantity": 74.0,
                "unit": "mg"
            }
        },
        "totalDaily": {
            "PROCNT": {
                "label": "Protein",
                "quantity": 62.0,
                "unit": "%"
            },
            "FAT": {
                "label": "Total lipid (fat)",
                "quantity": 5.5,
                "unit": "%"
            }
        },
        "dietLabels": [],
        "healthLabels": ["LOW_CARB", "HIGH_PROTEIN"],
        "cautions": [],
        "ingredients": [
            {
                "text": "100g chicken breast",
                "parsed": [
                    {
                        "quantity": 100,
                        "measure": "gram",
                        "food": "chicken breast"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def sample_usda_food_data():
    """Sample USDA food data for testing."""
    return {
        "fdcId": 747447,
        "description": "Chicken, broiler or fryers, breast, skinless, boneless, meat only, cooked, grilled",
        "foodCategory": "Poultry Products",
        "dataType": "Foundation",
        "foodNutrients": [
            {
                "nutrient": {
                    "id": 208,
                    "name": "Energy",
                    "unitName": "kcal"
                },
                "amount": 165.0
            },
            {
                "nutrient": {
                    "id": 203,
                    "name": "Protein",
                    "unitName": "g"
                },
                "amount": 31.0
            },
            {
                "nutrient": {
                    "id": 204,
                    "name": "Total lipid (fat)",
                    "unitName": "g"
                },
                "amount": 3.6
            }
        ],
        "foodPortions": [
            {
                "modifier": "fillet",
                "gramWeight": 174.0,
                "amount": 1.0,
                "measureUnit": {
                    "name": "fillet"
                }
            }
        ]
    }


@pytest.fixture
def sample_meal_data():
    """Sample meal data for testing."""
    return {
        "meal_name": "Breakfast",
        "foods": [
            {
                "food": "oatmeal",
                "amount": 50,
                "unit": "g"
            },
            {
                "food": "banana",
                "amount": 1,
                "unit": "medium"
            },
            {
                "food": "almonds",
                "amount": 20,
                "unit": "g"
            }
        ]
    }


@pytest.fixture
def sample_daily_meals():
    """Sample daily meals data for testing."""
    return [
        {
            "meal_name": "Breakfast",
            "foods": [
                {"food": "oatmeal", "amount": 50, "unit": "g"},
                {"food": "banana", "amount": 1, "unit": "medium"}
            ]
        },
        {
            "meal_name": "Lunch",
            "foods": [
                {"food": "chicken breast", "amount": 150, "unit": "g"},
                {"food": "brown rice", "amount": 80, "unit": "g"},
                {"food": "broccoli", "amount": 100, "unit": "g"}
            ]
        },
        {
            "meal_name": "Dinner",
            "foods": [
                {"food": "salmon", "amount": 150, "unit": "g"},
                {"food": "sweet potato", "amount": 200, "unit": "g"},
                {"food": "spinach", "amount": 100, "unit": "g"}
            ]
        }
    ]


@pytest.fixture
def sample_person_profile():
    """Sample person profile for testing."""
    return {
        "age": 30,
        "gender": "female",
        "weight_kg": 65.0,
        "height_cm": 165.0,
        "activity_level": "moderately_active"
    }


@pytest.fixture
def sample_recipe_data():
    """Sample recipe data for testing."""
    return {
        "title": "Grilled Chicken Salad",
        "ingredients": [
            {"food": "chicken breast", "amount": 200, "unit": "g"},
            {"food": "mixed greens", "amount": 100, "unit": "g"},
            {"food": "cherry tomatoes", "amount": 50, "unit": "g"},
            {"food": "olive oil", "amount": 1, "unit": "tbsp"}
        ],
        "servings": 2,
        "prep_time": 15,
        "cook_time": 10
    }


# Test utilities
def assert_nutrition_data_structure(data):
    """Assert that nutrition data has the expected structure."""
    assert isinstance(data, dict)
    assert "calories" in data
    assert isinstance(data["calories"], (int, float))
    assert data["calories"] >= 0


def assert_valid_meal_structure(meal):
    """Assert that meal data has the expected structure."""
    assert isinstance(meal, dict)
    assert "meal_name" in meal
    assert "foods" in meal
    assert isinstance(meal["foods"], list)
    assert len(meal["foods"]) > 0
    
    for food in meal["foods"]:
        assert isinstance(food, dict)
        assert "food" in food
        assert "amount" in food
        assert "unit" in food
        assert isinstance(food["amount"], (int, float))
        assert food["amount"] > 0
