# Specification: Session Risk Management

## Goal
Implement a local tracking system for trading sessions to enforce strict risk limits and maintain a clear separation between agent-initiated and human-initiated trades.

## Core Features
1. **Session Initialization (`init_session`):**
   - **`daily_limit`**: Total budget (buy volume) the agent is allowed to deploy in a single day.
   - **`daily_loss`**: Maximum allowed realized loss amount (in currency) before the agent's buying capability is disabled.
   - **Portfolio Snapshot:** Snapshot existing positions at startup. **CRITICAL:** These are "Human" stocks and must not be traded by the agent's automated logic.

2. **Agent Inventory Tracking:**
   - The system must track "Agent-owned" inventory separately from pre-existing or human-bought shares.
   - Only shares bought by the agent during the session can be sold by the agent's automated logic.
   - Use `transaction-state.json` to maintain this inventory.

3. **Transaction Tracking (`transaction-state.json`):**
   - Log every agent trade with `timestamp`, `date`, `ticker`, `action`, `price`, `quantity`, `acc_id`, `realized_p_l`, and `source` (AGENT/HUMAN).
   - Track cumulative `total_buy_volume` and `total_realized_loss`.

4. **Risk Enforcement & Selective Stopping:**
   - **Hard Stop:** If `total_buy_volume >= daily_limit` OR `total_realized_loss >= daily_loss`, the agent is prohibited from placing NEW BUY orders.
   - **Sell-Only Mode:** Even if the loss limit is reached, the agent may still propose or execute SELL orders for its *own* inventory if the price meets favorable criteria (e.g., trailing stop or profit target).

5. **Reporting:**
   - A tool to print the current session's P/L (Agent-only), remaining budget, and transaction log.

## Technical Details
- **State File:** `transaction-state.json` stores the session configuration, snapshot, and transaction history.
- **Logic:** `SessionService` calculates available budget and current drawdown.
- **Verification:** Before any `place_order` (BUY), the `TradeService` must verify with `SessionService` that both limits are within bounds.

