# Implementation Plan: Persistent Risk Management (Track ID: global_limit_20260311)

## Phase 1: SQLite Persistence & Migration Layer
Establish the SQLite database and migrate existing JSON/Session logic into a unified service.

- [ ] Task: Create `RiskManagementService` to replace `SessionService` state tracking.
    - [ ] Define SQLAlchemy models for `limits` (type, account_id, currency, cap, current_value, last_reset).
    - [ ] Define models for `agent_inventory` (ticker, qty, avg_price) and `transactions`.
- [ ] Task: Implement Migration from `transaction-state.json`.
    - [ ] Create a utility to read existing JSON data and seed the SQLite DB.
- [ ] Task: Implement Multi-Limit Logic in SQLite.
    - [ ] Logic for `GLOBAL_LIMIT`, `DAILY_LIMIT`, and `DAILY_LOSS`.
    - [ ] Support parsing and syncing Env/CLI args into the `limits` table.
- [ ] Task: Implement Auto-Reset Logic for Daily Limits.
    - [ ] Add a check on initialization or trade request to reset daily counters based on the current date.
- [ ] Task: Write Tests for `RiskManagementService`.
    - [ ] Verify that limits persist and reset correctly across simulated day boundaries.
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Trade Enforcement & Spending Logic
Integrate the risk management checks into the trade flow, replacing the session-based checks.

- [ ] Task: Refactor `TradeService` to use `RiskManagementService`.
    - [ ] Update `place_order` flow to check and spend from ALL applicable limits (Global & Daily).
    - [ ] Ensure atomic updates: order placement and limit debiting must be synchronized.
- [ ] Task: Write Tests for Enforcement Logic (TDD).
    - [ ] Verify that a trade is blocked if any of the three limits (Global, Daily, Loss) is violated.
    - [ ] Verify that successful trades correctly update the SQLite DB tables.
- [ ] Task: Implement Trade Failure Rollback.
    - [ ] Handle Moomoo order failure by restoring the limit in the DB.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Inventory & Replenishment Logic
Implement logic to restore global limits and update inventory based on sale transactions.

- [ ] Task: Implement `record_sale_and_replenish` in `RiskManagementService`.
    - [ ] Update `agent_inventory` on sale.
    - [ ] Calculate realized profit and credit the `GLOBAL_LIMIT` for that account/currency (up to the cap).
- [ ] Task: Write Tests for Inventory & Replenishment (TDD).
    - [ ] Test sale transactions and verify that inventory and limits are updated correctly.
    - [ ] Verify profit-based replenishment doesn't exceed the hard cap.
- [ ] Task: Update the `get_status` tool/resource.
    - [ ] Provide a consolidated view of all risk management metrics to the agent.
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Audit, Cleanup & Final Integration
Finalize audit trails, remove old JSON code, and perform end-to-end verification.

- [ ] Task: Implement Comprehensive Audit Logging.
    - [ ] Log every limit modification with the associated transaction and reason.
- [ ] Task: Remove `transaction-state.json` and legacy session logic.
    - [ ] Clean up `SessionService` and remove unused file-based state.
- [ ] Task: Final End-to-End Tests.
    - [ ] Simulate a full agent session across virtual days to verify persistent and resetting limits.
- [ ] Task: Update Documentation.
    - [ ] Add instructions for all three limit types to README.md.
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
