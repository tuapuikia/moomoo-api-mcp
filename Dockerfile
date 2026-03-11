# Use a modern Python Alpine image
FROM python:3.14-alpine

# Set working directory
WORKDIR /app

# Install system dependencies required for building pandas/numpy on Alpine
RUN apk add --no-cache \
    build-base \
    gcc \
    g++ \
    musl-dev \
    libstdc++ \
    linux-headers

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy metadata files first to leverage Docker cache
COPY pyproject.toml LICENSE README.md ./

# Install dependencies into the system environment
# Note: This might take longer on Alpine if wheels are missing for 3.14
RUN uv pip install --system ".[sse]" || uv pip install --system .

# Copy the rest of the application source
COPY src/ ./src/

# Set environment variable defaults
ENV PORT=8000
ENV MOOMOO_SECURITY_FIRM=FUTUSG
ENV PYTHONPATH=/app/src

# Expose the configured port
EXPOSE ${PORT}

# Run the MCP server in HTTP mode by default
ENTRYPOINT ["python", "-m", "moomoo_mcp.server", "--http"]
CMD ["--port", "8000"]
