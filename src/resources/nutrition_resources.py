"""
Nutrition resources for FastMCP server.
"""

from typing import List
import structlog
import json

from ..services.usda_service import USDAService
from ..config import get_settings

logger = structlog.get_logger(__name__)


class NutritionResources:
    """Resource handler for nutrition databases and information."""
    
    def __init__(self):
        self.usda_service = USDAService()
        self.settings = get_settings()
    
    async def get_usda_food_categories(self) -> str:
        """Get USDA food categories and classification system."""
        try:
            categories = {
                "food_categories": [
                    {"id": "dairy", "name": "Dairy and Egg Products", "description": "Milk, cheese, yogurt, eggs"},
                    {"id": "spices", "name": "Spices and Herbs", "description": "Seasonings, spices, herbs"},
                    {"id": "fats_oils", "name": "Fats and Oils", "description": "Cooking oils, butter, margarine"},
                    {"id": "poultry", "name": "Poultry Products", "description": "Chicken, turkey, duck"},
                    {"id": "soups", "name": "Soups, Sauces, and Gravies", "description": "Prepared soups and sauces"},
                    {"id": "sausages", "name": "Sausages and Luncheon Meats", "description": "Processed meats"},
                    {"id": "breakfast", "name": "Breakfast Cereals", "description": "Ready-to-eat and hot cereals"},
                    {"id": "fruits", "name": "Fruits and Fruit Juices", "description": "Fresh, frozen, dried fruits"},
                    {"id": "pork", "name": "Pork Products", "description": "Fresh and processed pork"},
                    {"id": "vegetables", "name": "Vegetables and Vegetable Products", "description": "Fresh, frozen, canned vegetables"},
                    {"id": "nuts", "name": "Nut and Seed Products", "description": "Tree nuts, peanuts, seeds"},
                    {"id": "beef", "name": "Beef Products", "description": "Fresh and processed beef"},
                    {"id": "beverages", "name": "Beverages", "description": "Non-alcoholic drinks"},
                    {"id": "finfish", "name": "Finfish and Shellfish Products", "description": "Fresh and processed seafood"},
                    {"id": "legumes", "name": "Legumes and Legume Products", "description": "Beans, peas, lentils"},
                    {"id": "lamb", "name": "Lamb, Veal, and Game Products", "description": "Specialty meats"},
                    {"id": "baked", "name": "Baked Products", "description": "Breads, cookies, pastries"},
                    {"id": "sweets", "name": "Sweets", "description": "Candy, chocolate, sweeteners"},
                    {"id": "cereal", "name": "Cereal Grains and Pasta", "description": "Rice, wheat, pasta"},
                    {"id": "fast_foods", "name": "Fast Foods", "description": "Restaurant and fast food items"},
                    {"id": "snacks", "name": "Snacks", "description": "Chips, crackers, snack foods"},
                    {"id": "ethnic", "name": "Ethnic Foods", "description": "International cuisine"},
                    {"id": "restaurant", "name": "Restaurant Foods", "description": "Chain restaurant items"}
                ]
            }
            return json.dumps(categories, indent=2)
        except Exception as e:
            logger.error("Error getting USDA food categories", error=str(e))
            return f"Error retrieving USDA food categories: {str(e)}"
    
    async def get_dietary_guidelines(self) -> str:
        """Get current dietary guidelines and recommendations."""
        guidelines = """# Dietary Guidelines for Americans 2020-2025

## Key Recommendations

### Core Elements of Healthy Eating Patterns:
- **Vegetables**: Dark green, red and orange, legumes, starchy, and other vegetables
- **Fruits**: Especially whole fruits
- **Grains**: At least half should be whole grains
- **Dairy**: Fat-free or low-fat milk, yogurt, cheese, and/or fortified soy beverages
- **Protein Foods**: Seafood, lean meats and poultry, eggs, legumes, nuts, seeds, and soy products
- **Oils**: Replace solid fats with oils when possible

### Limits:
- **Added Sugars**: Less than 10% of calories per day for ages 2 years and older
- **Saturated Fat**: Less than 10% of calories per day starting at age 2
- **Sodium**: Less than 2,300mg per day for ages 14 years and older
- **Alcoholic Beverages**: Adults of legal drinking age can choose not to drink, or to drink in moderation

### Special Populations:
- **Infants and Toddlers**: Breast milk is the ideal source of nutrition for about the first 6 months
- **Pregnant and Breastfeeding Women**: Follow a healthy eating pattern and take a prenatal vitamin
- **Adults 65 and Older**: Focus on nutrient-dense foods and adequate protein

### Physical Activity:
- **Adults**: At least 150 minutes of moderate-intensity aerobic activity per week
- **Children and Adolescents**: 60 minutes or more of physical activity daily

## MyPlate Recommendations:
- Fill half your plate with fruits and vegetables
- Make at least half your grains whole grains
- Move to low-fat or fat-free dairy
- Vary your protein routine
- Stay hydrated with water

For more detailed information, visit: https://www.dietaryguidelines.gov/
"""
        return guidelines
    
    async def get_food_safety_info(self) -> str:
        """Get food safety information and guidelines."""
        safety_info = """# Food Safety Guidelines

## Core Principles (Clean, Separate, Cook, Chill):

### Clean:
- Wash hands with soap and water for 20 seconds before and after handling food
- Clean all surfaces and utensils with hot, soapy water after each use
- Rinse fresh fruits and vegetables under running water
- Use separate cutting boards for raw meat and ready-to-eat foods

### Separate:
- Keep raw meat, poultry, seafood, and eggs separate from other foods
- Use one cutting board for raw meat and another for ready-to-eat foods
- Never place cooked food on a plate that previously held raw meat
- Store raw meat on the bottom shelf of the refrigerator

### Cook:
- Use a food thermometer to ensure safe minimum internal temperatures:
  - Beef, pork, lamb (steaks, roasts, chops): 145°F with 3-minute rest
  - Ground meats: 160°F
  - Whole poultry: 165°F
  - Poultry parts: 165°F
  - Fish and shellfish: 145°F
  - Eggs: 160°F or until yolk and white are firm

### Chill:
- Refrigerate perishable foods within 2 hours (1 hour if temperature is above 90°F)
- Keep refrigerator at 40°F or below
- Keep freezer at 0°F or below
- Thaw food safely in refrigerator, cold water, or microwave

## Storage Guidelines:
- **Pantry Items**: Store in cool, dry places away from heat and light
- **Refrigerated Foods**: Use within recommended timeframes
- **Frozen Foods**: Most maintain quality for 3-12 months
- **Leftovers**: Use within 3-4 days or freeze for longer storage

## High-Risk Foods:
- Raw or undercooked eggs, meat, poultry, and seafood
- Unpasteurized dairy products
- Raw sprouts
- Unwashed fresh produce

## When in Doubt, Throw it Out:
- If food has been left out too long
- If food smells, looks, or tastes unusual
- If you're unsure about storage time or temperature

For more information, visit: https://www.foodsafety.gov/
"""
        return safety_info
    
    async def get_allergen_database(self) -> str:
        """Get common food allergens and intolerance information."""
        allergen_info = """# Food Allergens and Intolerances Database

## Major Food Allergens (FDA "Big 8"):

### 1. Milk
- **Common Names**: Dairy, lactose, casein, whey, butter, cheese, yogurt
- **Hidden Sources**: Baked goods, processed meats, non-dairy creamers
- **Symptoms**: Digestive issues, skin reactions, respiratory problems

### 2. Eggs
- **Common Names**: Albumin, lecithin, lysozyme, mayonnaise
- **Hidden Sources**: Baked goods, pasta, processed foods, vaccines
- **Symptoms**: Skin rash, digestive upset, respiratory issues

### 3. Fish
- **Common Names**: Finfish (salmon, tuna, halibut, etc.)
- **Hidden Sources**: Caesar dressing, Worcestershire sauce, fish sauce
- **Symptoms**: Hives, swelling, digestive problems, anaphylaxis

### 4. Shellfish
- **Common Names**: Crustaceans (shrimp, crab, lobster), mollusks (clams, mussels)
- **Hidden Sources**: Surimi, some Asian sauces, supplements
- **Symptoms**: Most common adult food allergy, can cause severe reactions

### 5. Tree Nuts
- **Common Names**: Almonds, walnuts, pecans, cashews, pistachios, etc.
- **Hidden Sources**: Baked goods, cereals, ice cream, pesto
- **Symptoms**: Severe allergic reactions, anaphylaxis possible

### 6. Peanuts
- **Common Names**: Groundnuts, monkey nuts, beer nuts
- **Hidden Sources**: Asian cuisine, baked goods, candy, sauces
- **Symptoms**: Can cause severe, life-threatening reactions

### 7. Wheat
- **Common Names**: Flour, semolina, spelt, bulgur, farina
- **Hidden Sources**: Soy sauce, processed meats, beer, supplements
- **Symptoms**: Digestive issues, skin problems, respiratory symptoms

### 8. Soy
- **Common Names**: Soybean, edamame, tofu, tempeh, miso
- **Hidden Sources**: Processed foods, baked goods, canned tuna
- **Symptoms**: Digestive upset, skin reactions

## Additional Common Allergens:

### Sesame
- **Common Names**: Tahini, hummus, sesame oil
- **Hidden Sources**: Bread, crackers, processed foods
- **Note**: Recognized as major allergen in many countries

## Food Intolerances:

### Lactose Intolerance
- **Cause**: Lack of lactase enzyme
- **Symptoms**: Bloating, gas, diarrhea after consuming dairy
- **Management**: Lactose-free products, lactase supplements

### Gluten Sensitivity/Celiac Disease
- **Trigger**: Gluten protein in wheat, barley, rye
- **Symptoms**: Digestive issues, fatigue, headaches
- **Management**: Strict gluten-free diet

### FODMAP Sensitivity
- **Trigger**: Fermentable carbohydrates
- **Symptoms**: IBS-like symptoms
- **Management**: Low-FODMAP diet under medical supervision

## Reading Labels:
- Check ingredient lists carefully
- Look for allergen statements ("Contains" or "May contain")
- Be aware of cross-contamination warnings
- Learn alternative names for allergens

## Emergency Response:
- Epinephrine auto-injector for severe allergies
- Immediate medical attention for anaphylaxis
- Allergy action plan from healthcare provider

For medical advice, consult with an allergist or healthcare provider.
"""
        return allergen_info
    
    async def list_resources(self):
        """List all available nutrition resources."""
        resources = [
            {"uri": "nutrition://usda/food-categories", "name": "USDA Food Categories", "description": "USDA food classification system"},
            {"uri": "nutrition://guidelines/dietary", "name": "Dietary Guidelines", "description": "Current dietary guidelines and recommendations"},
            {"uri": "nutrition://safety/food", "name": "Food Safety Guidelines", "description": "Food safety information and best practices"},
            {"uri": "nutrition://allergens/database", "name": "Allergen Database", "description": "Common food allergens and intolerances"}
        ]
        return resources
    
    async def read_resource(self, uri: str) -> str:
        """Read a specific nutrition resource."""
        if uri == "nutrition://usda/food-categories":
            return await self.get_usda_food_categories()
        elif uri == "nutrition://guidelines/dietary":
            return await self.get_dietary_guidelines()
        elif uri == "nutrition://safety/food":
            return await self.get_food_safety_info()
        elif uri == "nutrition://allergens/database":
            return await self.get_allergen_database()
        else:
            raise ValueError(f"Unknown resource URI: {uri}")