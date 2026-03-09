# Implementation Plan - Session Risk Management

## Phase 1: Service Layer and Local State Persistence
- [ ] Task: Implement `SessionService` for JSON state management
    - [ ] Create `src/moomoo_mcp/services/session_service.py`
    - [ ] Implement reading/writing to `transaction-state.json`
    - [ ] Define data structure for transactions and session limits
- [ ] Task: Implement Portfolio Snapshotting
    - [ ] Add `snapshot_portfolio` method to `SessionService` to capture existing positions (ticker, quantity, unit price)
- [ ] Task: Write Tests for `SessionService`
    - [ ] Create `tests/test_services/test_session_service.py`
    - [ ] Verify reading/writing and P/L calculation logic
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Service Layer and Local State Persistence' (Protocol in workflow.md)

## Phase 2: Risk Enforcement and Trading Integration
- [ ] Task: Integrate `SessionService` into `TradeService`
    - [ ] Update `TradeService` to check with `SessionService` before `place_order`
    - [ ] Implement `check_risk_limits` to stop trading if the daily loss limit is reached
- [ ] Task: Automatic Transaction Logging
    - [ ] Update `place_order` to record successful trades in `transaction-state.json` with timestamp and realized P/L (for sells)
- [ ] Task: Write Integration Tests
    - [ ] Verify that trades are blocked when the daily loss limit is exceeded
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Risk Enforcement and Trading Integration' (Protocol in workflow.md)

## Phase 3: Reporting Tools and UI
- [ ] Task: Implement Session Status Tool
    - [ ] Create `get_session_status` tool in `src/moomoo_mcp/tools/system.py` or new `session.py`
    - [ ] Tool should print current session P/L, total deployed budget, and daily transaction list
- [ ] Task: Implement Session Initialization Tool
    - [ ] Create `init_session` tool to set budget, allowed loss percentage, and perform initial snapshot
- [ ] Task: Final Verification and Documentation
    - [ ] Update README with instructions for session risk management
    - [ ] Perform a full end-to-end test with the `moomoo-news-trader` skill
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Reporting Tools and UI' (Protocol in workflow.md)
