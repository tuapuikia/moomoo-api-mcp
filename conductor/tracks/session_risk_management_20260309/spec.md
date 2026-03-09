# Specification: Session Risk Management

## Goal
Implement a local tracking system for trading sessions to enforce risk limits (budget, loss percentage) and maintain a detailed transaction history for P/L analysis.

## Core Features
1. **Session Initialization:**
   - Define a session budget and allowed loss percentage.
   - Snapshot the current portfolio (ticker, quantity, cost basis/unit price) before starting automated trading.
2. **Transaction Tracking (`transaction-state.json`):**
   - Automatically log every trade executed by the agent.
   - Fields: `timestamp`, `date`, `ticker`, `action`, `price`, `quantity`, `acc_id`, `p_l_realized`.
3. **Risk Enforcement:**
   - Calculate cumulative daily P/L from the JSON state.
   - Automatically stop the agent from proposing or executing new trades if the daily loss limit (allowed loss percentage) is reached.
4. **Status Reporting:**
   - Provide a tool to print the current session's P/L, total deployed budget, and list of transactions for the day.

## Technical Details
- **Persistence:** All session data must be stored in `transaction-state.json` in a local data directory.
- **State Management:** A new `SessionService` will handle reading/writing the JSON file and calculating risk metrics.
- **Integration:** The `TradeService` should check with the `SessionService` before executing any orders.

## Requirements
- **Portfolio Snapshot:** Must capture unit price and count for all existing positions at session start.
- **P/L Calculation:** Realized P/L for sells must be calculated based on the recorded entry price (either from the snapshot or subsequent buys).
- **Daily Reset:** The tracking system should recognize a new trading day and reset/archive previous day's data if needed.
