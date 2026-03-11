# Specification: Persistent Risk Management (Track ID: global_limit_20260311)

## Overview
Implement a unified, persistent risk management system using SQLite. This replaces the current JSON-based `transaction-state.json` and in-memory session tracking. The system will manage three types of limits:
1.  **Global Limit:** A persistent, multi-currency budget that spans sessions and only replenishes on profit.
2.  **Daily Limit:** A multi-currency budget that resets daily.
3.  **Daily Loss Limit:** A multi-currency realized loss threshold that resets daily.

## Functional Requirements
1.  **Unified SQLite Persistence:**
    - Migrate all data from `transaction-state.json` to a structured SQLite database.
    - Tables:
        - `limits`: Stores `type` (GLOBAL, DAILY_BUDGET, DAILY_LOSS), `account_id`, `currency`, `hard_cap`, and `current_value`.
        - `agent_inventory`: Tracks tickers, quantities, and cost basis (average price) for the agent's trades.
        - `transactions`: A full audit trail of all agent-initiated trades and limit adjustments.
2.  **Multi-Currency Support:**
    - Support defining limits via environment variables or CLI arguments:
        - `GLOBAL_LIMIT` / `--global-limit`
        - `MOOMOO_DAILY_LIMIT` / `--daily-limit`
        - `MOOMOO_DAILY_LOSS` / `--daily-loss`
    - Format: `1000USD,500SGD`.
3.  **Logic & Enforcement:**
    - **Global Limit:** Persistent. Reduces on 'Buy', replenishes on 'Sell' (cost basis + profit).
    - **Daily Limit:** Resets daily. Tracks total 'Buy' volume for the current day.
    - **Daily Loss Limit:** Resets daily. Tracks total realized P/L for the current day.
    - **Strict Blocking:** If ANY limit is exceeded for a given account/currency, the trade is blocked.
4.  **Auto-Reset Mechanism:**
    - On server startup or when a trade is requested, the system must check the last reset timestamp for `DAILY` limits. If the calendar day has changed, reset `current_value` to zero (for limits) or the hard cap.
5.  **Tracking Independence:**
    - The system only tracks funds and assets it has specifically handled, maintaining independence from the broader portfolio.

## Non-Functional Requirements
- **Data Integrity:** Use database transactions to ensure limit updates and trade records are atomic.
- **Performance:** SQLite is sufficient for the scale of a single-user MCP server.
- **Auditability:** Every limit change must be traceable to a specific transaction ID.

## Acceptance Criteria
- [ ] All session state (Daily Limit/Loss) is stored in SQLite instead of JSON.
- [ ] Global Limit persists across days and restarts.
- [ ] Daily limits/losses correctly reset when a new day begins.
- [ ] Agent inventory is accurately tracked in SQLite.
- [ ] Multi-currency configurations are correctly parsed and synced with the DB.
- [ ] Trades are blocked if any applicable limit is violated.

## Out of Scope
- Historical portfolio value tracking (outside of agent trades).
- Automated currency conversion (FX rates).
