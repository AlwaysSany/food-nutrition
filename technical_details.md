# Food & Nutrition Intelligence MCP Server

## Overview

This project is a comprehensive Model Context Protocol (MCP) server that provides food and nutrition intelligence capabilities. It integrates with multiple nutrition APIs (USDA FoodData Central, Edamam, and optionally Nutritionix) to deliver detailed nutrition data, meal planning, and dietary analysis tools. The server is built using Python 3.11+ with modern async/await patterns and follows MCP protocol specifications.

## System Architecture

The application follows a modular, service-oriented architecture with clear separation of concerns:

### Core Components
- **MCP Server**: Main server implementation handling protocol communication
- **Service Layer**: External API integrations (USDA, Edamam, Nutritionix)
- **Tools Layer**: MCP tool implementations for different functionality domains
- **Resources Layer**: Static nutrition databases and information access
- **Prompts Layer**: AI prompt templates for nutrition guidance
- **Models Layer**: Pydantic data models for type safety and validation
- **Utils Layer**: Helper functions, validators, and common utilities

### Architecture Patterns
- **Async/Await**: Full asynchronous implementation for better performance
- **Dependency Injection**: Services are injected into tool classes
- **Factory Pattern**: Server creation through factory function
- **Repository Pattern**: Service layer abstracts external API access
- **Strategy Pattern**: Different nutrition data sources handled uniformly

## Key Components

### Tools
1. **NutritionTools**: Core nutrition data retrieval and food analysis
2. **MealPlanningTools**: Meal plan generation based on dietary requirements
3. **DietaryAnalysisTools**: Nutritional intake analysis and compliance checking

### Services
1. **USDAService**: USDA FoodData Central API integration with rate limiting and caching
2. **EdamamService**: Edamam Nutrition Analysis API for detailed nutrition analysis
3. **NutritionixService**: Optional third-party nutrition API (referenced but not implemented)

### Resources
- **NutritionResources**: Access to nutrition databases, dietary guidelines, food safety info, and allergen data

### Prompts
- **NutritionPrompts**: AI prompt templates for meal analysis, dietary planning, and nutrition education

## Data Flow

1. **Request Flow**: MCP client → Server → Tools → Services → External APIs
2. **Response Flow**: External APIs → Services (with caching) → Tools (with formatting) → Server → MCP client
3. **Caching**: Responses cached at service layer with configurable TTL (default 1 hour)
4. **Rate Limiting**: Applied at service layer to respect API limits
5. **Error Handling**: Comprehensive error handling with structured logging throughout the stack

## External Dependencies

### APIs
- **USDA FoodData Central**: Primary nutrition database (requires API key)
- **Edamam Nutrition Analysis**: Detailed nutrition analysis (requires app ID and key)
- **Nutritionix**: Optional additional nutrition data source

### Python Dependencies
- **mcp**: Model Context Protocol implementation (≥0.3.0)
- **httpx**: HTTP client with HTTP/2 support for API calls
- **pydantic**: Data validation and settings management
- **structlog**: Structured logging for better observability
- **python-dotenv**: Environment variable management

### Development Dependencies
- **pytest**: Testing framework with async support
- **black**: Code formatting
- **isort**: Import sorting
- **mypy**: Static type checking

## Deployment Strategy

### Environment Configuration
- Environment variables managed through `.env` file
- Pydantic settings with validation and type safety
- API keys and configuration separated from code

### Rate Limiting Strategy
- Configurable rate limiting per API (default 60 requests/minute)
- Built-in retry logic with exponential backoff
- Request queuing to prevent API limit violations

### Caching Strategy
- In-memory caching with TTL support
- Cache keys based on request parameters
- Configurable cache duration (default 1 hour)

### Error Handling
- Structured error responses with context
- Graceful degradation when APIs are unavailable
- Comprehensive logging for debugging and monitoring

### Testing Strategy
- Unit tests for all major components
- Mock external API dependencies
- Async test support with pytest-asyncio
- Test coverage tracking with pytest-cov

