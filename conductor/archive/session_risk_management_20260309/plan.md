# Implementation Plan - Session Risk Management

## Phase 1: Service Layer and Local State Persistence
- [x] Task: Implement `SessionService` for JSON state management
    - [x] Create `src/moomoo_mcp/services/session_service.py`
    - [x] Implement reading/writing to `transaction-state.json`
    - [x] Define data structure for transactions, session limits (`daily_limit`, `daily_loss`), and **Agent Inventory**
- [x] Task: Implement Portfolio Snapshotting
    - [x] Add `snapshot_portfolio` method to `SessionService` to capture existing "Human" positions (ticker, quantity, unit price)
- [x] Task: Write Tests for `SessionService`
    - [x] Create `tests/test_services/test_session_service.py`
    - [x] Verify reading/writing, budget calculation, and loss limit enforcement
- [x] Task: Conductor - User Manual Verification 'Phase 1: Service Layer and Local State Persistence' (Protocol in workflow.md)

## Phase 2: Risk Enforcement and Trading Integration
- [x] Task: Integrate `SessionService` into `TradeService`
    - [x] Update `TradeService` to check with `SessionService` before `place_order` (specifically for BUYS)
    - [x] Implement `check_risk_limits` to stop BUYS if `daily_limit` or `daily_loss` is hit
- [x] Task: Agent Inventory and Transaction Logging
    - [x] Update `place_order` to record successful trades as "AGENT" source
    - [x] Implement logic to ensure only AGENT-owned inventory can be sold by automated tools
    - [x] Calculate realized P/L for sells using session-acquired cost basis
- [x] Task: Write Integration Tests
    - [x] Verify that new BUY trades are blocked when limits are hit
    - [x] Verify that SELLS are still allowed for agent inventory after loss limit hit
- [x] Task: Conductor - User Manual Verification 'Phase 2: Risk Enforcement and Trading Integration' (Protocol in workflow.md)

## Phase 3: Reporting Tools and UI
- [x] Task: Implement Session Status Tool
    - [x] Create `get_session_status` tool in `src/moomoo_mcp/tools/session.py`
    - [x] Tool should print current Agent P/L, remaining budget, and transaction log
- [x] Task: Implement Session Initialization Tool
    - [x] Create `init_session` tool to set `--daily-limit`, `--daily-loss`, and perform the initial portfolio snapshot
- [x] Task: Final Verification and Documentation
    - [x] Update README with instructions for session risk management and agent safety
    - [x] Perform a full end-to-end test with the `moomoo-news-trader` skill
- [x] Task: Conductor - User Manual Verification 'Phase 3: Reporting Tools and UI' (Protocol in workflow.md)
