# Specification: Docker Compose Integration

## Overview
This track adds a `docker-compose.yml` file and an example configuration to the project. This will allow users to easily deploy the Moomoo API MCP server in a containerized environment with persistent risk management, health monitoring, and simplified network configuration.

## Functional Requirements
- **Docker Compose Setup**: Create a `docker-compose.yml` file to manage the MCP server container.
- **Persistent Data**:
    - Configure a volume mount for the `moomoo_risk.db` SQLite database to ensure risk limits and inventory survive container restarts.
    - Path in container: `/app/moomoo_risk.db`.
- **Logging Persistence**:
    - Configure a volume mount for the Moomoo SDK logs.
- **Network Configuration**:
    - Use `network_mode: host` to allow the container to access the Moomoo OpenD gateway running on the host machine (`127.0.0.1:11111`) with minimal overhead.
- **Environment Management**:
    - Use an `.env` file reference for environment variables.
    - Create a `.env.example` file containing all required and optional variables:
        - `PORT`, `MOOMOO_TRADE_PASSWORD`, `MOOMOO_SECURITY_FIRM`, `MOOMOO_DAILY_LIMIT`, `MOOMOO_DAILY_LOSS`, `GLOBAL_LIMIT`.
- **Health Monitoring**:
    - Implement a Docker `healthcheck` that periodically queries the MCP server's HTTP/SSE endpoint to ensure it is alive.

## Non-Functional Requirements
- **Ease of Use**: The `docker-compose.yml` should be runnable with a single command: `docker compose up`.
- **Security**: The documentation must clearly state that `.env` files containing secrets should never be committed to source control.

## Acceptance Criteria
- [ ] A valid `docker-compose.yml` is present in the root directory.
- [ ] A `.env.example` file is provided with documentation for each variable.
- [ ] `docker compose up` successfully starts the server in SSE mode.
- [ ] The `moomoo_risk.db` file is correctly mounted and data persists after `docker compose down && docker compose up`.
- [ ] The container status shows as "healthy" in Docker.

## Out of Scope
- Containerizing the Moomoo OpenD gateway itself.
- Setting up a reverse proxy (e.g., Nginx) in the compose file.
