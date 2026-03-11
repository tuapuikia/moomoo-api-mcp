# Implementation Plan: Persistent Risk Management (Track ID: global_limit_20260311)

## Phase 1: SQLite Persistence & Migration Layer [checkpoint: 8a740cb]
Establish the SQLite database and migrate existing JSON/Session logic into a unified service.

- [x] Task: Create `RiskManagementService` to replace `SessionService` state tracking. 0547052
    - [x] Define SQLAlchemy models for `limits` (type, account_id, currency, cap, current_value, last_reset).
    - [x] Define models for `agent_inventory` (ticker, qty, avg_price) and `transactions`.
- [x] Task: Implement Migration from `transaction-state.json`. 7c7d13a
    - [x] Create a utility to read existing JSON data and seed the SQLite DB.
- [x] Task: Implement Multi-Limit Logic in SQLite. 4bd00f0
    - [x] Logic for `GLOBAL_LIMIT`, `DAILY_LIMIT`, and `DAILY_LOSS`.
    - [x] Support parsing and syncing Env/CLI args into the `limits` table.
- [x] Task: Implement Auto-Reset Logic for Daily Limits. 4bd00f0
    - [x] Add a check on initialization or trade request to reset daily counters based on the current date.
- [x] Task: Write Tests for `RiskManagementService`. 0547052
    - [x] Verify that limits persist and reset correctly across simulated day boundaries.
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) 8a740cb

## Phase 2: Trade Enforcement & Spending Logic [checkpoint: c5fa579]
Integrate the risk management checks into the trade flow, replacing the session-based checks.

- [x] Task: Refactor `TradeService` to use `RiskManagementService`. 67bf551
    - [x] Update `place_order` flow to check and spend from ALL applicable limits (Global & Daily).
    - [x] Ensure atomic updates: order placement and limit debiting must be synchronized.
- [x] Task: Write Tests for Enforcement Logic (TDD). 67bf551
    - [x] Verify that a trade is blocked if any of the three limits (Global, Daily, Loss) is violated.
    - [x] Verify that successful trades correctly update the SQLite DB tables.
- [x] Task: Implement Trade Failure Rollback. 67bf551
    - [x] Handle Moomoo order failure by restoring the limit in the DB.
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md) c5fa579

## Phase 3: Inventory & Replenishment Logic [checkpoint: 8478955]
Implement logic to restore global limits and update inventory based on sale transactions.

- [x] Task: Implement `record_sale_and_replenish` in `RiskManagementService`. fb6a9d9
    - [x] Update `agent_inventory` on sale.
    - [x] Calculate realized profit and credit the `GLOBAL_LIMIT` for that account/currency (up to the cap).
- [x] Task: Write Tests for Inventory & Replenishment (TDD). fb6a9d9
    - [x] Test sale transactions and verify that inventory and limits are updated correctly.
    - [x] Verify profit-based replenishment doesn't exceed the hard cap.
- [x] Task: Update the `get_status` tool/resource. fb6a9d9
    - [x] Provide a consolidated view of all risk management metrics to the agent.
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md) 8478955

## Phase 4: Audit, Cleanup & Final Integration [checkpoint: 2e366d6]
Finalize audit trails, remove old JSON code, and perform end-to-end verification.

- [x] Task: Implement Comprehensive Audit Logging. 02b74d2
    - [x] Log every limit modification with the associated transaction and reason.
- [x] Task: Remove `transaction-state.json` and legacy session logic. 02b74d2
    - [x] Clean up `SessionService` and remove unused file-based state.
- [x] Task: Final End-to-End Tests. 67bf551
    - [x] Simulate a full agent session across virtual days to verify persistent and resetting limits.
- [x] Task: Update Documentation. 02b74d2
    - [x] Add instructions for all three limit types to README.md.
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md) 2e366d6
