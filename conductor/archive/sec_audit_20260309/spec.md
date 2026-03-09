# Specification: Codebase Security Audit

## Goal
Conduct a comprehensive security audit of the `moomoo-api-mcp` codebase to ensure no credentials, secrets, or sensitive information are exposed and that the trading operations are implemented safely.

## Scope
- All source code in `src/moomoo_mcp/`.
- Configuration files (`pyproject.toml`, `.gitignore`, etc.).
- Testing environment and mock data.
- Environment variable handling for `MOOMOO_TRADE_PASSWORD` and `MOOMOO_SECURITY_FIRM`.

## Requirements
1. **Secret Scanning:** Verify no hardcoded secrets or passwords exist in the repository.
2. **Credential Management:** Ensure `MOOMOO_TRADE_PASSWORD` is only handled via environment variables and never logged or persisted.
3. **Safe Defaults:** Confirm that REAL trading requires explicit unlock and that SIMULATE is the default where applicable.
4. **Input Validation:** Check that all tool inputs are validated to prevent injection or malicious data.
5. **Dependency Audit:** Verify that dependencies are up to date and do not have known vulnerabilities.