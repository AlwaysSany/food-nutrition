#!/usr/bin/env python3
"""
Food & Nutrition Intelligence MCP Server
Entry point for the MCP server application.
"""

import asyncio
import sys
from src.server import create_server
from src.config import get_settings
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Create the server instance at the global scope
server = create_server()

def main():
    """Main entry point for the MCP server."""
    try:
        settings = get_settings()
        logger.info("Starting Food & Nutrition Intelligence MCP Server", 
                   version=settings.VERSION)
        
        # Run the FastMCP server (handles asyncio internally)
        server.run()
            
    except Exception as e:
        logger.error("Failed to start server", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
