# Implementation Plan: Docker Compose Integration

## Phase 1: Environment and Compose Scaffold
- [x] Task: Create `.env.example` with all supported environment variables and documentation. [43b392d]
- [x] Task: Create the initial `docker-compose.yml` file. [33fc06d]
    - [x] Define the `mcp-server` service using the `moomoo-api-mcp` image.
    - [x] Implement `network_mode: host` for gateway access.
    - [x] Add `env_file` reference to `.env`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Scaffold' (Protocol in workflow.md) [checkpoint: main 7a3ca8d]

## Phase 2: Persistence and Logging Configuration
- [x] Task: Configure volume mounts in `docker-compose.yml`. [cab3e7c]
    - [x] Mount `./moomoo_risk.db` to `/app/moomoo_risk.db`.
    - [x] Mount a local logs directory to the SDK log path in the container.
- [x] Task: Verify persistence by running a mock transaction and restarting the container. [cab3e7c]
- [x] Task: Switch transport from SSE to Streamable HTTP. [7ef3a2d]
    - [x] Update `server.py` CLI and run logic.
    - [x] Update `Dockerfile` ENTRYPOINT.
    - [x] Update `tests/test_server_cli.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Persistence' (Protocol in workflow.md)

## Phase 3: Healthchecks and Documentation
- [ ] Task: Add a `healthcheck` block to `docker-compose.yml` using `curl`.
- [ ] Task: Update `README.md` with a section on using Docker Compose.
- [ ] Task: Final end-to-end verification of the healthy container status.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Health and Docs' (Protocol in workflow.md)
