# Technology Stack

## Programming Language
- **Python (>= 3.10):** Core language for the server implementation.

## Frameworks & Protocols
- **Model Context Protocol (MCP):** The underlying protocol for the server.
- **FastMCP:** Framework used for building the MCP server.

## Core Dependencies
- **moomoo-api:** Official Moomoo Python SDK for trading and market data.
- **pandas:** Data manipulation and analysis library.
- **sqlalchemy:** SQL toolkit and Object Relational Mapper for persistence.
- **sqlite:** Lightweight, disk-based database for persistent risk management.
- **starlette & uvicorn:** ASGI framework and server for HTTP SSE transport support.

## Deployment
- **Docker:** Official containerization support using `python:3.14-alpine` for a minimal runtime footprint.

## Testing & Linting
- **pytest & pytest-asyncio:** Testing frameworks for synchronous and asynchronous code.
- **ruff:** Linter and code formatter.

## Package Management
- **uv / hatchling:** Build system and package management.