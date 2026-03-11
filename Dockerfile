# Use a modern Python slim image
FROM python:3.14-rc-slim

# Set working directory
WORKDIR /app

# Install system dependencies if any are needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy metadata files first to leverage Docker cache
COPY pyproject.toml LICENSE README.md ./

# Install dependencies into the system environment
RUN uv pip install --system ".[sse]" || uv pip install --system .

# Copy the rest of the application source
COPY src/ ./src/

# Set environment variable defaults
ENV PORT=8000
ENV MOOMOO_SECURITY_FIRM=FUTUSG
ENV PYTHONPATH=/app/src

# Expose the configured port
EXPOSE ${PORT}

# Run the MCP server in SSE mode by default
ENTRYPOINT ["python", "-m", "moomoo_mcp.server", "--sse"]
CMD ["--port", "8000"]
