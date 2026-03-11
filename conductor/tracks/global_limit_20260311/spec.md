# Specification: Global Limit Tracking (Track ID: global_limit_20260311)

## Overview
Implement a persistent, multi-currency global budget (limit) for trading agents. This is a total budget that persists across sessions and is per-account. It tracks its own 'spent' amount independently of the portfolio's actual value, only replenishing when the agent's trades result in realized gains (profit).

## Functional Requirements
1.  **Multi-Currency Persistent Limits:**
    - Support defining multiple limits via environment variables (e.g., `GLOBAL_LIMIT=1000USD,1000SGD`) or CLI arguments (e.g., `--global-limit=1000USD,1000SGD`).
    - The CLI argument takes precedence over the environment variable if both are provided.
    - Store limits and their current 'spent' state in a persistent SQLite database.
    - Limits are unique to each Moomoo Account ID.
2.  **Spending Logic:**
    - Every 'Buy' order placed by the agent reduces the available global limit for that account/currency by the total order value (including fees).
    - If a buy order would exceed the remaining limit, the trade is blocked (Strict Blocking).
3.  **Replenishment (Profit-Based):**
    - The limit is only restored when the agent 'Sells' a position that was tracked by the global limit.
    - If a sale results in a profit, the 'cost basis' (initial spent amount) is restored to the limit, potentially with the realized profit also being added back (up to the original cap).
    - Selling assets does not allow the limit to exceed the 'Hard Cap' set by the environment/arguments.
4.  **Limit Overrides (Env/Arg Sync):**
    - The environment/argument value acts as the 'Hard Cap' for the current session.
    - If the value changes between sessions (e.g., 1000 -> 800), the new value becomes the limit. Existing 'spent' amounts in the database are preserved.
5.  **Tracking Independence:**
    - The global limit only tracks funds it has specifically allocated for trades, not the total portfolio value retrieved from Moomoo.

## Non-Functional Requirements
- **Persistence:** Use SQLite to ensure limits survive server restarts.
- **Precision:** Use decimal/high-precision math for limit calculations.
- **Auditability:** Log all limit changes (debits/credits) with trade IDs for debugging.

## Acceptance Criteria
- [ ] Agent can set a multi-currency limit via environment variable or CLI.
- [ ] Buying assets correctly reduces the remaining limit in the DB.
- [ ] Buying assets is blocked if the limit is insufficient.
- [ ] Selling assets restores the limit based on profit logic.
- [ ] Changing the configuration correctly updates the limit cap for the next session.
- [ ] Limits are tracked independently per account ID.

## Out of Scope
- Automatic currency conversion (limits are per-currency).
- Integration with external risk management tools beyond the internal SQLite DB.
