# Specification: HTTP SSE Support and Dockerization

## Overview
This track adds support for the SSE (Server-Sent Events) transport protocol to the Moomoo API MCP server, allowing it to communicate over HTTP in addition to the standard `stdio`. It also includes a Dockerfile to package the application for containerized deployment, specifically optimized for HTTP/SSE mode.

## Functional Requirements
- **SSE Transport**: Implement HTTP/SSE support using the FastMCP `transport="sse"` parameter.
- **Configurable HTTP Server**:
    - Add a CLI flag (e.g., `--sse`) to toggle between `stdio` and `sse` modes.
    - Support a configurable port via a `--port` flag or `PORT` environment variable (default: 8000).
- **Dual Transport Support**: Ensure the server remains fully functional in `stdio` mode when the `--sse` flag is absent.
- **Dockerization**:
    - Create an optimized `Dockerfile`.
    - Base image: `python:3.14-rc-slim`.
    - Default behavior in container: Start in SSE mode on port 8000.
    - Expose port 8000 for the MCP server.
- **Environment Variable Pass-through**:
    - The container must support all existing environment variables:
        - `MOOMOO_TRADE_PASSWORD` / `MOOMOO_TRADE_PASSWORD_MD5`
        - `MOOMOO_SECURITY_FIRM`
        - `MOOMOO_DAILY_LIMIT`
        - `MOOMOO_DAILY_LOSS`
        - `GLOBAL_LIMIT`

## Non-Functional Requirements
- **Image Optimization**: Exclude test files, documentation, `.git` folder, and the local `moomoo_risk.db` file from the final image using `.dockerignore`.
- **Scalability**: The SSE implementation should handle multiple concurrent client connections.

## Acceptance Criteria
- [ ] Running the server with `--sse` starts an HTTP server listening on the specified port.
- [ ] Running the server without `--sse` continues to work via `stdio`.
- [ ] The Docker image successfully builds and can be started with `docker run`.
- [ ] Environment variables passed to `docker run` are correctly picked up by the server inside the container.
- [ ] The `moomoo_risk.db` is NOT included in the image.

## Out of Scope
- Bundling Moomoo OpenD inside the same Docker image.
- Testing within the container image.
