# Implementation Plan: HTTP SSE Support and Dockerization

## Phase 1: Core SSE Support and CLI Extensions
- [x] Task: Add `sse` and `port` CLI arguments to `src/moomoo_mcp/server.py` and map them to `mcp.run()`. [checkpoint: main 6987031]
    - [x] Add `--sse` and `--port` to `argparse`.
    - [x] Support `PORT` env var as default for `--port`.
- [x] Task: Implement TDD for CLI and transport switching logic.
    - [x] Create `tests/test_server_cli.py` to test the CLI parsing.
    - [x] Verify `mcp.run()` is called with the correct `transport` and `port` based on CLI/env.
- [x] Task: Implement logic in `src/moomoo_mcp/server.py` to handle `transport="sse"`.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Core SSE Support' (Protocol in workflow.md)

## Phase 2: Dockerization and Environment Configuration
- [ ] Task: Create `.dockerignore` to exclude local state, tests, and sensitive files.
    - [ ] Exclude `moomoo_risk.db`, `.git`, `tests/`, `__pycache__`, etc.
- [ ] Task: Create `Dockerfile` based on `python:3.14-rc-slim`.
    - [ ] Install dependencies from `pyproject.toml`.
    - [ ] Set `ENV` defaults (e.g., `PORT=8000`).
    - [ ] CMD: Start server in SSE mode by default.
- [ ] Task: Verify environment variable propagation in the container.
    - [ ] Run container with a mock `MOOMOO_DAILY_LIMIT` and check if server parses it correctly.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Dockerization' (Protocol in workflow.md)

## Phase 3: Final Integration and Documentation
- [ ] Task: Update `README.md` with instructions on how to run via Docker and connect via HTTP/SSE.
- [ ] Task: Final end-to-end verification.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Integration' (Protocol in workflow.md)
