# Food & Nutrition Intelligence MCP Server

A comprehensive Model Context Protocol (MCP) server for food and nutrition intelligence, providing tools, resources, and prompts for nutrition data retrieval, meal planning, and dietary analysis.

## Features

- **Nutrition Data Tools**: Retrieve detailed nutrition information from USDA FoodData Central and Edamam APIs
- **Meal Planning**: Generate meal plans based on dietary requirements and preferences
- **Dietary Analysis**: Analyze nutritional content of meals and diets
- **Resource Endpoints**: Access nutrition databases and food information
- **AI Prompts**: Pre-built prompt templates for nutrition-related AI interactions

## Installation

1. Install Python 3.11+ if not already installed.
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```
3. Install [UV](https://github.com/astral-sh/uv) (optional, for fast dependency management):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
4. Install project dependencies:
   ```bash
   uv pip install -r requirements.txt  # If requirements.txt is present
   # OR, using pyproject.toml (preferred):
   uv pip install .
   # Or with pip:
   pip install .
   ```

## Usage

To start the Food & Nutrition Intelligence MCP server:

```bash
python3 main.py
```

Or, if you have an entrypoint defined (e.g., via FastMCP CLI):

```bash
fastmcp run main.py
```

The server exposes a set of MCP tools for nutrition data, meal planning, and dietary analysis. You can interact with it via a compatible MCP client or by integrating it into your AI workflow.

# Run on debug mode

```bash
npx @modelcontextprotocol/inspector uv run main.py
```

### Example API Usage

- **Get Nutrition Data:**
  - Tool: `nutrition_get_food_data(food_name: str, portion_size: float = 100.0, include_detailed: bool = False)`
- **Generate Meal Plan:**
  - Tool: `meal_plan_generate(dietary_preferences: dict, calories: int)`
- **Analyze Diet:**
  - Tool: `dietary_analysis(analyzed_meals: list)`

See the technical details for more tool signatures and usage patterns.

## Project Structure

- `src/server.py` — Main server entrypoint and tool registration
- `src/tools/` — Nutrition, meal planning, and dietary analysis tools
- `src/services/` — Integrations with USDA, Edamam, and other APIs
- `src/resources/` — Nutrition databases and static resources
- `src/prompts/` — AI prompt templates
- `src/models/` — Data models (Pydantic)
- `src/utils/` — Utilities and helpers

## Contributing

Contributions are welcome! Please see the guidelines below:

1. Fork the repository and create a new branch for your feature or fix.
2. Install development dependencies:
   ```bash
   uv pip install .[dev]
   # Or
   pip install .[dev]
   ```
3. Run tests:
   ```bash
   pytest
   ```
4. Format code with Black and check typing with MyPy:
   ```bash
   black src/
   mypy src/
   ```
5. Submit a pull request describing your changes.

## License

MIT License. See `LICENSE` file for details.

## More Information

- For advanced architecture and technical details, see [`technical_details.md`](./technical_details.md).
- For questions or support, open an issue or contact the maintainer listed in `pyproject.toml`.
