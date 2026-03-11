# Implementation Plan: Global Limit Tracking (Track ID: global_limit_20260311)

## Phase 1: Foundation & Persistence Layer
Set up the SQLite database schema and the core service to manage global limits and their spent state.

- [ ] Task: Create `GlobalLimitService` for SQLite interactions.
    - [ ] Define SQLAlchemy (or raw SQL) models for `global_limits` (account_id, currency, cap, spent) and `limit_transactions` (trade_id, amount, timestamp).
    - [ ] Implement `get_limit(account_id, currency)` and `update_limit_cap(account_id, currency, new_cap)`.
- [ ] Task: Write Tests for `GlobalLimitService`.
    - [ ] Test limit retrieval and cap updates.
    - [ ] Test persistence across service restarts (simulated).
- [ ] Task: Implement CLI/Env parsing for `global-limit`.
    - [ ] Update server startup logic to parse `--global-limit` and `GLOBAL_LIMIT` environment variables.
    - [ ] Sync parsed values with the database on startup (respecting existing spent amounts).
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Spending & Enforcement Logic
Integrate the global limit check into the trade placement flow to block orders that exceed the budget.

- [ ] Task: Implement `check_and_spend_limit` in `TradeService`.
    - [ ] Add a check before `place_order` to verify if the global limit for the account/currency is sufficient.
    - [ ] If sufficient, debit the limit in the DB *before* placing the order (locking the funds).
- [ ] Task: Write Tests for Spending Logic (TDD).
    - [ ] Mock Moomoo API and verify that trades are blocked when the limit is reached.
    - [ ] Verify that successful trades correctly debit the SQLite DB.
- [ ] Task: Implement Trade Failure Rollback.
    - [ ] If the Moomoo order placement fails, ensure the locked global limit is returned to the 'available' pool.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Replenishment & Profit Tracking
Implement logic to restore the global limit when assets are sold, based on the cost basis and realized profit.

- [ ] Task: Implement `replenish_limit_on_sale` in `TradeService`.
    - [ ] Capture the 'cost basis' of the assets being sold (requires tracking which global limit 'funded' which asset).
    - [ ] Calculate realized profit and credit the global limit (up to the original cap).
- [ ] Task: Write Tests for Replenishment Logic (TDD).
    - [ ] Test sale of assets and verify correct replenishment of the global limit.
    - [ ] Verify that replenishment never exceeds the hard cap set by the user.
- [ ] Task: Add `get_global_limit` Tool/Resource.
    - [ ] Expose the current state of global limits to the agent via an MCP tool or resource.
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Audit & Final Integration
Finalize logging, audit trails, and end-to-end verification.

- [ ] Task: Implement Transaction Logging.
    - [ ] Ensure every limit change is logged in the `limit_transactions` table with full context.
- [ ] Task: Final End-to-End Tests.
    - [ ] Simulate a full agent session: set limit -> buy -> sell -> check limit.
- [ ] Task: Update Documentation.
    - [ ] Add instructions for `--global-limit` and `GLOBAL_LIMIT` env var to README.md.
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
