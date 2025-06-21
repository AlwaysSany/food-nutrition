"""
Tests for MCP tools functionality.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from mcp.types import TextContent

from src.tools.nutrition_tools import NutritionTools
from src.tools.meal_planning_tools import MealPlanningTools
from src.tools.dietary_analysis_tools import DietaryAnalysisTools


class TestNutritionTools:
    """Test cases for nutrition tools."""
    
    @pytest.fixture
    def nutrition_tools(self):
        """Create nutrition tools instance."""
        with patch('src.services.usda_service.USDAService'):
            return NutritionTools()
    
    @pytest.mark.asyncio
    async def test_list_tools(self, nutrition_tools):
        """Test listing nutrition tools."""
        tools = await nutrition_tools.list_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "nutrition_get_food_data",
            "nutrition_search_foods",
            "nutrition_get_nutrient_data",
            "nutrition_analyze_recipe"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    

    @pytest.mark.asyncio
    async def test_get_food_data_validation_error(self, nutrition_tools):
        """Test food data retrieval with validation error."""
        result = await nutrition_tools.call_tool(
            "nutrition_get_food_data",
            {
                "food_name": "",  # Empty food name should fail validation
                "portion_size": 100
            }
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        assert "validation error" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_search_foods(self, nutrition_tools, sample_usda_food_data):
        """Test food search functionality."""
        with patch.object(nutrition_tools.usda_service, 'search_foods') as mock_search:
            mock_search.return_value = [sample_usda_food_data]
            
            result = await nutrition_tools.call_tool(
                "nutrition_search_foods",
                {
                    "query": "chicken",
                    "limit": 10
                }
            )
            
            assert isinstance(result, list)
            assert len(result) > 0
            assert isinstance(result[0], TextContent)
            assert "chicken" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_search_foods_no_results(self, nutrition_tools):
        """Test food search with no results."""
        with patch.object(nutrition_tools.usda_service, 'search_foods') as mock_search:
            mock_search.return_value = []
            
            result = await nutrition_tools.call_tool(
                "nutrition_search_foods",
                {
                    "query": "nonexistent_food_12345",
                    "limit": 10
                }
            )
            
            assert isinstance(result, list)
            assert len(result) > 0
            assert isinstance(result[0], TextContent)
            assert "no foods found" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_get_nutrient_data(self, nutrition_tools):
        """Test nutrient data comparison."""
        mock_comparison_data = [
            {
                "food_name": "chicken breast",
                "nutrient_content": 31.0,
                "unit": "g",
                "food_description": "Chicken, cooked"
            },
            {
                "food_name": "salmon",
                "nutrient_content": 22.0,
                "unit": "g", 
                "food_description": "Salmon, cooked"
            }
        ]
        
        with patch.object(nutrition_tools.usda_service, 'get_nutrient_comparison') as mock_compare:
            mock_compare.return_value = mock_comparison_data
            
            result = await nutrition_tools.call_tool(
                "nutrition_get_nutrient_data",
                {
                    "nutrient_name": "protein",
                    "food_list": ["chicken breast", "salmon"],
                    "sort_by_content": True
                }
            )
            
            assert isinstance(result, list)
            assert len(result) > 0
            assert isinstance(result[0], TextContent)
            assert "protein" in result[0].text.lower()
            assert "chicken" in result[0].text.lower()
    
   
    
    @pytest.mark.asyncio
    async def test_invalid_tool_name(self, nutrition_tools):
        """Test calling an invalid tool name."""
        result = await nutrition_tools.call_tool(
            "invalid_tool_name",
            {}
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        assert "unknown" in result[0].text.lower() and "tool" in result[0].text.lower()


class TestMealPlanningTools:
    """Test cases for meal planning tools."""
    
    @pytest.fixture
    def meal_planning_tools(self):
        """Create meal planning tools instance."""
        with patch('src.services.usda_service.USDAService'):
            return MealPlanningTools()
    
    @pytest.mark.asyncio
    async def test_list_tools(self, meal_planning_tools):
        """Test listing meal planning tools."""
        tools = await meal_planning_tools.list_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "meal_generate_plan",
            "meal_calculate_nutrition",
            "meal_suggest_alternatives",
            "meal_balance_checker"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @pytest.mark.asyncio
    async def test_generate_meal_plan(self, meal_planning_tools):
        """Test meal plan generation."""
        result = await meal_planning_tools.call_tool(
            "meal_generate_plan",
            {
                "target_calories": 2000,
                "dietary_restrictions": ["vegetarian"],
                "meals_per_day": 3,
                "days": 7
            }
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        assert "meal plan" in result[0].text.lower()
        assert "2000" in result[0].text  # Target calories should be mentioned
    
    @pytest.mark.asyncio
    async def test_generate_meal_plan_validation_error(self, meal_planning_tools):
        """Test meal plan generation with validation error."""
        result = await meal_planning_tools.call_tool(
            "meal_generate_plan",
            {
                "target_calories": 500,  # Too low, should fail validation
                "meals_per_day": 3
            }
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        assert "validation error" in result[0].text.lower()
    

    
    @pytest.mark.asyncio
    async def test_suggest_alternatives(self, meal_planning_tools):
        """Test food alternatives suggestion."""
        result = await meal_planning_tools.call_tool(
            "meal_suggest_alternatives",
            {
                "current_foods": ["white rice", "ground beef"],
                "health_goal": "weight_loss",
                "max_alternatives": 3
            }
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        assert "alternatives" in result[0].text.lower()
        assert "weight loss" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_balance_checker(self, meal_planning_tools):
        """Test meal balance checking."""
        sample_meals = [
            {
                "name": "Breakfast",
                "foods": [
                    {"food": "oatmeal", "amount": 50, "unit": "g"},
                    {"food": "banana", "amount": 1, "unit": "medium"}
                ]
            }
        ]
        
        result = await meal_planning_tools.call_tool(
            "meal_balance_checker",
            {
                "meals": sample_meals,
                "person_profile": {
                    "age": 30,
                    "gender": "female",
                    "activity_level": "moderately_active"
                }
            }
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        assert "balance" in result[0].text.lower()


class TestDietaryAnalysisTools:
    """Test cases for dietary analysis tools."""
    
    @pytest.fixture
    def dietary_analysis_tools(self):
        """Create dietary analysis tools instance."""
        with patch('src.services.usda_service.USDAService'):
            return DietaryAnalysisTools()
    
    @pytest.mark.asyncio
    async def test_list_tools(self, dietary_analysis_tools):
        """Test listing dietary analysis tools."""
        tools = await dietary_analysis_tools.list_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "dietary_analyze_daily_intake",
            "dietary_check_compliance",
            "dietary_generate_report",
            "dietary_identify_patterns"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    
    @pytest.mark.asyncio
    async def test_analyze_daily_intake_validation_error(self, dietary_analysis_tools):
        """Test daily intake analysis with validation error."""
        result = await dietary_analysis_tools.call_tool(
            "dietary_analyze_daily_intake",
            {
                "daily_meals": [],  # Empty meals should fail validation
                "analysis_focus": ["calories"]
            }
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        assert "validation error" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_check_compliance(self, dietary_analysis_tools):
        """Test dietary compliance checking."""
        food_log = [
            {
                "date": "2025-06-20",
                "meals": [
                    {
                        "meal_name": "Breakfast",
                        "foods": [
                            {"food": "oatmeal", "amount": 50, "unit": "g"}
                        ]
                    }
                ]
            }
        ]
        
        result = await dietary_analysis_tools.call_tool(
            "dietary_check_compliance",
            {
                "food_log": food_log,
                "dietary_guidelines": "mediterranean",
                "custom_restrictions": []
            }
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        assert "compliance" in result[0].text.lower()
        assert "mediterranean" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_generate_report(self, dietary_analysis_tools):
        """Test nutrition report generation."""
        analysis_period = {
            "start_date": "2025-06-01",
            "end_date": "2025-06-07",
            "daily_logs": [
                {
                    "date": "2025-06-01",
                    "meals": [
                        {
                            "meal_name": "Breakfast",
                            "foods": [
                                {"food": "oatmeal", "amount": 50, "unit": "g"}
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = await dietary_analysis_tools.call_tool(
            "dietary_generate_report",
            {
                "analysis_period": analysis_period,
                "report_sections": ["summary", "recommendations"]
            }
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        assert "report" in result[0].text.lower()
        assert "2025-06-01" in result[0].text
    
    @pytest.mark.asyncio
    async def test_identify_patterns(self, dietary_analysis_tools):
        """Test eating pattern identification."""
        food_diary = [
            {
                "date": "2025-06-20",
                "day_of_week": "Tuesday",
                "meals": [
                    {
                        "meal_name": "Breakfast",
                        "time": "08:00",
                        "foods": [
                            {"food": "oatmeal", "amount": 50, "unit": "g"}
                        ]
                    }
                ]
            }
        ]
        
        result = await dietary_analysis_tools.call_tool(
            "dietary_identify_patterns",
            {
                "food_diary": food_diary,
                "pattern_types": ["meal_timing", "calorie_trends"]
            }
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        assert "pattern" in result[0].text.lower()


class TestToolsIntegration:
    """Test integration between different tools."""
    
    @pytest.fixture
    def all_tools(self):
        """Create all tool instances."""
        with patch('src.services.usda_service.USDAService'):
            return {
                'nutrition': NutritionTools(),
                'meal_planning': MealPlanningTools(),
                'dietary_analysis': DietaryAnalysisTools()
            }
    
    
    @pytest.mark.asyncio
    async def test_tool_error_isolation(self, all_tools):
        """Test that errors in one tool don't affect others."""
        # Cause an error in nutrition tools
        with patch.object(all_tools['nutrition'].usda_service, 'get_food_details') as mock_get_food:
            mock_get_food.side_effect = Exception("API Error")
            
            nutrition_result = await all_tools['nutrition'].call_tool(
                "nutrition_get_food_data",
                {"food_name": "chicken breast"}
            )
            
            # Should contain error message
            assert "error" in nutrition_result[0].text.lower()
        
        # But other tools should still work
        meal_plan_result = await all_tools['meal_planning'].call_tool(
            "meal_generate_plan",
            {"target_calories": 2000}
        )
        
        # Should not contain error message
        assert "error" not in meal_plan_result[0].text.lower()


class TestToolValidation:
    """Test tool input validation."""
    
    @pytest.fixture
    def nutrition_tools(self):
        """Create nutrition tools instance."""
        with patch('src.services.usda_service.USDAService'):
            return NutritionTools()
    
    @pytest.mark.asyncio
    async def test_food_name_validation(self, nutrition_tools):
        """Test food name validation."""
        # Test empty food name
        result = await nutrition_tools.call_tool(
            "nutrition_get_food_data",
            {"food_name": ""}
        )
        assert "validation error" in result[0].text.lower()
        
        # Test food name with special characters
        result = await nutrition_tools.call_tool(
            "nutrition_get_food_data",
            {"food_name": "<script>alert('xss')</script>"}
        )
        assert "validation error" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_portion_size_validation(self, nutrition_tools):
        """Test portion size validation."""
        # Test negative portion size
        result = await nutrition_tools.call_tool(
            "nutrition_get_food_data",
            {"food_name": "apple", "portion_size": -10}
        )
        # Should handle gracefully or show validation error
        assert isinstance(result, list) and len(result) > 0
    
    @pytest.mark.asyncio
    async def test_nutrient_list_validation(self, nutrition_tools):
        """Test nutrient comparison list validation."""
        # Test empty food list
        result = await nutrition_tools.call_tool(
            "nutrition_get_nutrient_data",
            {"nutrient_name": "protein", "food_list": []}
        )
        assert "validation error" in result[0].text.lower()
        
        # Test too many foods
        large_food_list = [f"food_{i}" for i in range(25)]
        result = await nutrition_tools.call_tool(
            "nutrition_get_nutrient_data",
            {"nutrient_name": "protein", "food_list": large_food_list}
        )
        assert "validation error" in result[0].text.lower()


class TestToolPerformance:
    """Test tool performance and caching."""
    
    @pytest.fixture
    def nutrition_tools(self):
        """Create nutrition tools instance."""
        with patch('src.services.usda_service.USDAService'):
            return NutritionTools()
    
