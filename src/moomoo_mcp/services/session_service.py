import json
import os
from datetime import datetime
from typing import Any, Dict, List
import re

class SessionService:
    """Service to manage trading session state, limits, and inventory tracking."""

    MARKET_CURRENCY_MAP = {
        "US": "USD",
        "HK": "HKD",
        "SG": "SGD",
        "JP": "JPY",
        "CN": "CNH",
    }

    def __init__(self, state_file: str = "transaction-state.json"):
        self.state_file = state_file
        # Load hard limits from environment variables if set (Format: "1000USD,500SGD")
        self.hard_limits = self._parse_multi_currency_env("MOOMOO_DAILY_LIMIT")
        self.hard_losses = self._parse_multi_currency_env("MOOMOO_DAILY_LOSS")
        self._ensure_state_exists()

    def _parse_multi_currency_env(self, key: str) -> Dict[str, float]:
        """Parse string like '1000USD,500SGD' into {'USD': 1000.0, 'SGD': 500.0}."""
        val = os.environ.get(key)
        if not val:
            return {}
        
        limits = {}
        # Support both comma and space separators
        parts = re.split(r'[,\s]+', val.strip())
        for part in parts:
            # Match number followed by optional letters (currency)
            match = re.match(r'([\d.]+)([A-Z]*)', part.upper())
            if match:
                amount = float(match.group(1))
                currency = match.group(2) or "DEFAULT"
                limits[currency] = amount
        return limits

    def _get_currency_from_code(self, ticker: str) -> str:
        """Extract currency based on ticker prefix (e.g., 'US.AAPL' -> 'USD')."""
        if "." in ticker:
            market = ticker.split(".")[0].upper()
            return self.MARKET_CURRENCY_MAP.get(market, "DEFAULT")
        return "DEFAULT"

    def _ensure_state_exists(self) -> None:
        """Create initial state file if it doesn't exist."""
        if not os.path.exists(self.state_file):
            self._save_state(self._get_default_state())
        else:
            # Update current state if hard limits are set in environment
            if self.hard_limits or self.hard_losses:
                state = self._load_state()
                if self.hard_limits:
                    state["session"]["daily_limits"].update(self.hard_limits)
                if self.hard_losses:
                    state["session"]["daily_losses"].update(self.hard_losses)
                self._save_state(state)

    def _get_default_state(self) -> Dict[str, Any]:
        """Return the default session state structure."""
        has_env_limits = bool(self.hard_limits or self.hard_losses)
        return {
            "session": {
                "daily_limits": self.hard_limits or {},
                "daily_losses": self.hard_losses or {},
                "volumes": {}, # {currency: total_buy_volume}
                "p_ls": {},     # {currency: total_realized_p_l}
                "initialized_at": datetime.utcnow().isoformat() if has_env_limits else None,
                "is_active": True if has_env_limits else False
            },
            "snapshot": {},
            "inventory": {},
            "transactions": []
        }

    def _load_state(self) -> Dict[str, Any]:
        """Read state from JSON file."""
        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return self._get_default_state()

    def _save_state(self, state: Dict[str, Any]) -> None:
        """Write state to JSON file."""
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def init_session(self, daily_limit: float, daily_loss: float) -> None:
        """Initialize a new trading session with limits.
        
        Note: This tool uses simple float for backward compat, mapped to DEFAULT.
        Prefer setting hard limits via Env Vars for multi-currency.
        """
        state = self._load_state()
        
        # Merge Tool Input into DEFAULT currency if no hard limits exist
        if "DEFAULT" not in self.hard_limits:
            state["session"]["daily_limits"]["DEFAULT"] = daily_limit
        if "DEFAULT" not in self.hard_losses:
            state["session"]["daily_losses"]["DEFAULT"] = daily_loss
            
        state["session"].update({
            "initialized_at": datetime.utcnow().isoformat(),
            "is_active": True
        })
        state["session"]["volumes"] = {}
        state["session"]["p_ls"] = {}
        state["inventory"] = {}
        state["transactions"] = []
        self._save_state(state)

    def snapshot_portfolio(self, positions: List[Dict[str, Any]]) -> None:
        """Snapshot current portfolio as 'Human' positions.

        Args:
            positions: List of dictionaries from get_positions().
        """
        state = self._load_state()
        snapshot = {}
        for pos in positions:
            ticker = pos.get("code")
            if ticker:
                snapshot[ticker] = {
                    "qty": pos.get("qty", 0),
                    "unit_price": pos.get("cost_price", 0.0)
                }
        state["snapshot"] = snapshot
        self._save_state(state)

    def is_agent_position(self, ticker: str, quantity: int) -> bool:
        """Check if the agent has enough inventory of a ticker to sell."""
        state = self._load_state()
        inv = state["inventory"].get(ticker)
        if not inv:
            return False
        return inv["qty"] >= quantity

    def record_transaction(self, ticker: str, action: str, price: float, quantity: int, acc_id: int) -> None:
        """Record an agent transaction and update inventory/limits."""
        state = self._load_state()
        if not state["session"]["is_active"]:
            raise RuntimeError("Session not initialized. Call init_session first.")

        currency = self._get_currency_from_code(ticker)
        timestamp = datetime.utcnow().isoformat()
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

        transaction = {
            "timestamp": timestamp,
            "date": date_str,
            "ticker": ticker,
            "currency": currency,
            "action": action.upper(),
            "price": price,
            "quantity": quantity,
            "acc_id": acc_id,
            "realized_p_l": 0.0
        }

        if action.upper() == "BUY":
            cost = price * quantity
            state["session"]["volumes"][currency] = state["session"]["volumes"].get(currency, 0.0) + cost
            
            # Update agent inventory
            inv = state["inventory"].get(ticker, {"qty": 0, "avg_price": 0.0})
            new_qty = inv["qty"] + quantity
            new_avg = ((inv["qty"] * inv["avg_price"]) + cost) / new_qty
            state["inventory"][ticker] = {"qty": new_qty, "avg_price": new_avg}
            
        elif action.upper() == "SELL":
            inv = state["inventory"].get(ticker)
            if not inv or inv["qty"] < quantity:
                raise ValueError(f"Insufficient agent inventory to sell {quantity} of {ticker}")
            
            # Calculate realized P/L
            realized = (price - inv["avg_price"]) * quantity
            transaction["realized_p_l"] = realized
            state["session"]["p_ls"][currency] = state["session"]["p_ls"].get(currency, 0.0) + realized
            
            # Update inventory
            inv["qty"] -= quantity
            if inv["qty"] == 0:
                del state["inventory"][ticker]

        state["transactions"].append(transaction)
        self._save_state(state)

    def get_status(self) -> Dict[str, Any]:
        """Return the current session status metrics."""
        state = self._load_state()
        session = state["session"]
        
        # Calculate remaining budget per defined limit
        remaining = {}
        for curr, limit in session["daily_limits"].items():
            remaining[curr] = max(0.0, limit - session["volumes"].get(curr, 0.0))

        return {
            "is_active": session["is_active"],
            "daily_limits": session["daily_limits"],
            "daily_losses": session["daily_losses"],
            "remaining_budgets": remaining,
            "realized_p_ls": session["p_ls"],
            "inventory": state["inventory"],
            "transaction_count": len(state["transactions"])
        }

    def can_buy(self, amount: float, ticker: str) -> bool:
        """Check if a buy operation is allowed under specific currency limits."""
        state = self._load_state()
        session = state["session"]
        
        if not session["is_active"]:
            return False
            
        currency = self._get_currency_from_code(ticker)
        
        # Check budget for this currency
        limit = session["daily_limits"].get(currency)
        if limit is not None:
            if session["volumes"].get(currency, 0.0) + amount > limit:
                return False
            
        # Check loss for this currency
        loss_limit = session["daily_losses"].get(currency)
        if loss_limit is not None:
            if session["p_ls"].get(currency, 0.0) <= -abs(loss_limit):
                return False
            
        return True
