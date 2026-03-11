# Implementation Plan: Docker Compose Integration

## Phase 1: Environment and Compose Scaffold
- [x] Task: Create `.env.example` with all supported environment variables and documentation. [43b392d]
- [ ] Task: Create the initial `docker-compose.yml` file.
    - [ ] Define the `mcp-server` service using the `moomoo-api-mcp` image.
    - [ ] Implement `network_mode: host` for gateway access.
    - [ ] Add `env_file` reference to `.env`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Scaffold' (Protocol in workflow.md)

## Phase 2: Persistence and Logging Configuration
- [ ] Task: Configure volume mounts in `docker-compose.yml`.
    - [ ] Mount `./moomoo_risk.db` to `/app/moomoo_risk.db`.
    - [ ] Mount a local logs directory to the SDK log path in the container.
- [ ] Task: Verify persistence by running a mock transaction and restarting the container.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Persistence' (Protocol in workflow.md)

## Phase 3: Healthchecks and Documentation
- [ ] Task: Add a `healthcheck` block to `docker-compose.yml` using `curl`.
- [ ] Task: Update `README.md` with a section on using Docker Compose.
- [ ] Task: Final end-to-end verification of the healthy container status.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Health and Docs' (Protocol in workflow.md)
