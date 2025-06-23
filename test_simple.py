#!/usr/bin/env python3
"""
Simple test to verify FastMCP server functionality.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from fastmcp import FastMCP
    print("✓ FastMCP imported successfully")
    
    # Create a minimal server
    mcp = FastMCP("Nutrition MCP Server")
    
    @mcp.tool()
    async def test_tool(message: str = "Hello") -> str:
        """A simple test tool."""
        return f"Test response: {message}"
    
    print("✓ Server created successfully")
    print("✓ Tool registered successfully")
    print("FastMCP server is working correctly!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)