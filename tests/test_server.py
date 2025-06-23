"""
Tests for the main MCP server functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from mcp.types import Tool, Resource, Prompt, TextContent

from src.server import create_server
from src.config import get_settings


class TestMCPServer:
    """Test cases for the MCP server."""
    
    @pytest.fixture
    def server(self):
        """Create a test server instance."""
        with patch('src.config.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                USDA_API_KEY="test_key",
                EDAMAM_APP_ID="test_id",
                EDAMAM_APP_KEY="test_key",
                VERSION="1.0.0"
            )
            return create_server()
    
    @pytest.mark.asyncio
    async def test_server_creation(self, server):
        """Test that server is created successfully."""
        assert server is not None
        assert server.name == "food-nutrition-intelligence"
    
    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """Test that tools are listed correctly."""
        # Get the list_tools handler
        list_tools_handler = None
        for handler_name, handler in server._handlers.items():
            if "list_tools" in handler_name:
                list_tools_handler = handler
                break
        
        assert list_tools_handler is not None
        
        # Call the handler
        tools = await list_tools_handler()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Check that all returned items are Tool objects
        for tool in tools:
            assert isinstance(tool, Tool)
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')
        
        # Check for expected tool names
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "nutrition_get_food_data",
            "nutrition_search_foods",
            "meal_generate_plan",
            "dietary_analyze_daily_intake"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    

    @pytest.mark.asyncio
    async def test_call_tool_invalid_name(self, server):
        """Test calling a tool with invalid name."""
        # Get the call_tool handler
        call_tool_handler = None
        for handler_name, handler in server._handlers.items():
            if "call_tool" in handler_name:
                call_tool_handler = handler
                break
        
        assert call_tool_handler is not None
        
        # Call with invalid tool name
        result = await call_tool_handler(
            name="invalid_tool_name",
            arguments={}
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        assert "error" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_list_resources(self, server):
        """Test that resources are listed correctly."""
        # Get the list_resources handler
        list_resources_handler = None
        for handler_name, handler in server._handlers.items():
            if "list_resources" in handler_name:
                list_resources_handler = handler
                break
        
        assert list_resources_handler is not None
        
        # Call the handler
        resources = await list_resources_handler()
        
        assert isinstance(resources, list)
        assert len(resources) > 0
        
        # Check that all returned items are Resource objects
        for resource in resources:
            assert isinstance(resource, Resource)
            assert hasattr(resource, 'uri')
            assert hasattr(resource, 'name')
            assert hasattr(resource, 'description')
        
        # Check for expected resource URIs
        resource_uris = [resource.uri for resource in resources]
        expected_resources = [
            "nutrition://usda/food-categories",
            "nutrition://dietary-guidelines",
            "nutrition://food-safety"
        ]
        
        for expected_resource in expected_resources:
            assert expected_resource in resource_uris
    
    @pytest.mark.asyncio
    async def test_read_resource(self, server):
        """Test reading a resource."""
        # Get the read_resource handler
        read_resource_handler = None
        for handler_name, handler in server._handlers.items():
            if "read_resource" in handler_name:
                read_resource_handler = handler
                break
        
        assert read_resource_handler is not None
        
        # Read a resource
        result = await read_resource_handler("nutrition://dietary-guidelines")
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "dietary guidelines" in result.lower()
    
    @pytest.mark.asyncio
    async def test_read_resource_invalid_uri(self, server):
        """Test reading an invalid resource URI."""
        # Get the read_resource handler
        read_resource_handler = None
        for handler_name, handler in server._handlers.items():
            if "read_resource" in handler_name:
                read_resource_handler = handler
                break
        
        assert read_resource_handler is not None
        
        # Should raise an exception for invalid URI
        with pytest.raises(ValueError):
            await read_resource_handler("invalid://resource/uri")
    
    @pytest.mark.asyncio
    async def test_list_prompts(self, server):
        """Test that prompts are listed correctly."""
        # Get the list_prompts handler
        list_prompts_handler = None
        for handler_name, handler in server._handlers.items():
            if "list_prompts" in handler_name:
                list_prompts_handler = handler
                break
        
        assert list_prompts_handler is not None
        
        # Call the handler
        prompts = await list_prompts_handler()
        
        assert isinstance(prompts, list)
        assert len(prompts) > 0
        
        # Check that all returned items are Prompt objects
        for prompt in prompts:
            assert isinstance(prompt, Prompt)
            assert hasattr(prompt, 'name')
            assert hasattr(prompt, 'description')
        
        # Check for expected prompt names
        prompt_names = [prompt.name for prompt in prompts]
        expected_prompts = [
            "analyze_meal_nutrition",
            "create_meal_plan",
            "nutrition_education"
        ]
        
        for expected_prompt in expected_prompts:
            assert expected_prompt in prompt_names
    
    @pytest.mark.asyncio
    async def test_get_prompt(self, server):
        """Test getting a prompt with arguments."""
        # Get the get_prompt handler
        get_prompt_handler = None
        for handler_name, handler in server._handlers.items():
            if "get_prompt" in handler_name:
                get_prompt_handler = handler
                break
        
        assert get_prompt_handler is not None
        
        # Get a prompt
        result = await get_prompt_handler(
            name="analyze_meal_nutrition",
            arguments={
                "meal_description": "grilled chicken with vegetables",
                "dietary_goals": "weight loss",
                "health_conditions": "none"
            }
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "grilled chicken" in result
        assert "weight loss" in result
    
    @pytest.mark.asyncio
    async def test_get_prompt_missing_arguments(self, server):
        """Test getting a prompt with missing arguments."""
        # Get the get_prompt handler
        get_prompt_handler = None
        for handler_name, handler in server._handlers.items():
            if "get_prompt" in handler_name:
                get_prompt_handler = handler
                break
        
        assert get_prompt_handler is not None
        
        # Should raise an exception for missing arguments
        with pytest.raises(ValueError):
            await get_prompt_handler(
                name="analyze_meal_nutrition",
                arguments={"meal_description": "chicken"}  # Missing required arguments
            )
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self, server):
        """Test that tool errors are handled gracefully."""
        with patch('src.services.usda_service.USDAService.get_food_details') as mock_get_food:
            mock_get_food.side_effect = Exception("API Error")
            
            # Get the call_tool handler
            call_tool_handler = None
            for handler_name, handler in server._handlers.items():
                if "call_tool" in handler_name:
                    call_tool_handler = handler
                    break
            
            assert call_tool_handler is not None
            
            # Call the tool
            result = await call_tool_handler(
                name="nutrition_get_food_data",
                arguments={"food_name": "chicken breast"}
            )
            
            assert isinstance(result, list)
            assert len(result) > 0
            assert isinstance(result[0], TextContent)
            # Should contain error message
            assert any(word in result[0].text.lower() for word in ["error", "failed", "unable"])


class TestServerConfiguration:
    """Test server configuration and setup."""
    
    @pytest.mark.asyncio
    async def test_server_with_missing_api_keys(self):
        """Test server behavior with missing API keys."""
        with patch('src.config.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                USDA_API_KEY="",
                EDAMAM_APP_ID="",
                EDAMAM_APP_KEY="",
                VERSION="1.0.0"
            )
            
            # Server should still be created but tools might fail
            server = create_server()
            assert server is not None
    
    @pytest.mark.asyncio
    async def test_server_logging_configuration(self):
        """Test that logging is configured properly."""
        import structlog
        
        # Check that structlog is configured
        logger = structlog.get_logger("test")
        assert logger is not None
        
        # Test logging doesn't raise exceptions
        logger.info("Test log message")
        logger.error("Test error message")


class TestServerHandlers:
    """Test individual server handlers."""
    
    @pytest.fixture
    def server(self):
        """Create a test server instance."""
        with patch('src.config.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                USDA_API_KEY="test_key",
                EDAMAM_APP_ID="test_id",
                EDAMAM_APP_KEY="test_key",
                VERSION="1.0.0"
            )
            return create_server()
    
    @pytest.mark.asyncio
    async def test_nutrition_tools_integration(self, server):
        """Test that nutrition tools are properly integrated."""
        # Get the call_tool handler
        call_tool_handler = None
        for handler_name, handler in server._handlers.items():
            if "call_tool" in handler_name:
                call_tool_handler = handler
                break
        
        assert call_tool_handler is not None
        
        # Test nutrition tool routing
        with patch('src.tools.nutrition_tools.NutritionTools.call_tool') as mock_call:
            mock_call.return_value = [TextContent(type="text", text="Test response")]
            
            result = await call_tool_handler(
                name="nutrition_get_food_data",
                arguments={"food_name": "apple"}
            )
            
            mock_call.assert_called_once()
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_meal_planning_tools_integration(self, server):
        """Test that meal planning tools are properly integrated."""
        # Get the call_tool handler
        call_tool_handler = None
        for handler_name, handler in server._handlers.items():
            if "call_tool" in handler_name:
                call_tool_handler = handler
                break
        
        assert call_tool_handler is not None
        
        # Test meal planning tool routing
        with patch('src.tools.meal_planning_tools.MealPlanningTools.call_tool') as mock_call:
            mock_call.return_value = [TextContent(type="text", text="Test meal plan")]
            
            result = await call_tool_handler(
                name="meal_generate_plan",
                arguments={"target_calories": 2000}
            )
            
            mock_call.assert_called_once()
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_dietary_analysis_tools_integration(self, server):
        """Test that dietary analysis tools are properly integrated."""
        # Get the call_tool handler
        call_tool_handler = None
        for handler_name, handler in server._handlers.items():
            if "call_tool" in handler_name:
                call_tool_handler = handler
                break
        
        assert call_tool_handler is not None
        
        # Test dietary analysis tool routing
        with patch('src.tools.dietary_analysis_tools.DietaryAnalysisTools.call_tool') as mock_call:
            mock_call.return_value = [TextContent(type="text", text="Test analysis")]
            
            result = await call_tool_handler(
                name="dietary_analyze_daily_intake",
                arguments={"daily_meals": [{"meal_name": "test", "foods": [{"food": "apple", "amount": 1, "unit": "medium"}]}]}
            )
            
            mock_call.assert_called_once()
            assert len(result) > 0


class TestServerValidation:
    """Test server input validation."""
    
    @pytest.fixture
    def server(self):
        """Create a test server instance."""
        with patch('src.config.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                USDA_API_KEY="test_key",
                EDAMAM_APP_ID="test_id",
                EDAMAM_APP_KEY="test_key",
                VERSION="1.0.0"
            )
            return create_server()
    
    @pytest.mark.asyncio
    async def test_tool_argument_validation(self, server):
        """Test that tool arguments are validated."""
        # Get the call_tool handler
        call_tool_handler = None
        for handler_name, handler in server._handlers.items():
            if "call_tool" in handler_name:
                call_tool_handler = handler
                break
        
        assert call_tool_handler is not None
        
        # Test with invalid arguments
        result = await call_tool_handler(
            name="nutrition_get_food_data",
            arguments={"invalid_arg": "value"}  # Missing required food_name
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        # Should contain validation error
        assert any(word in result[0].text.lower() for word in ["validation", "error", "missing"])
    
    @pytest.mark.asyncio
    async def test_resource_uri_validation(self, server):
        """Test that resource URIs are validated."""
        # Get the read_resource handler
        read_resource_handler = None
        for handler_name, handler in server._handlers.items():
            if "read_resource" in handler_name:
                read_resource_handler = handler
                break
        
        assert read_resource_handler is not None
        
        # Test with malformed URI
        with pytest.raises(ValueError):
            await read_resource_handler("malformed-uri")
    
    @pytest.mark.asyncio
    async def test_prompt_argument_validation(self, server):
        """Test that prompt arguments are validated."""
        # Get the get_prompt handler
        get_prompt_handler = None
        for handler_name, handler in server._handlers.items():
            if "get_prompt" in handler_name:
                get_prompt_handler = handler
                break
        
        assert get_prompt_handler is not None
        
        # Test with missing required arguments
        with pytest.raises(ValueError):
            await get_prompt_handler(
                name="analyze_meal_nutrition",
                arguments={}  # Missing all required arguments
            )
