import enum
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from decimal import Decimal

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
    text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

Base = declarative_base()

class LimitType(enum.Enum):
    GLOBAL = "GLOBAL"
    DAILY_BUDGET = "DAILY_BUDGET"
    DAILY_LOSS = "DAILY_LOSS"

class Limit(Base):
    __tablename__ = "limits"
    id = Column(Integer, primary_key=True)
    type = Column(Enum(LimitType), nullable=False)
    account_id = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    hard_cap = Column(Float, nullable=False)
    spent = Column(Float, default=0.0)
    last_reset = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AgentInventory(Base):
    __tablename__ = "agent_inventory"
    id = Column(Integer, primary_key=True)
    account_id = Column(String, nullable=False)
    ticker = Column(String, nullable=False)
    qty = Column(Integer, nullable=False)
    avg_price = Column(Float, nullable=False)

class RiskTransaction(Base):
    __tablename__ = "risk_transactions"
    id = Column(Integer, primary_key=True)
    account_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ticker = Column(String, nullable=False)
    action = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    currency = Column(String, nullable=False)
    realized_p_l = Column(Float, default=0.0)

class RiskManagementService:
    def __init__(self, db_url: str = "sqlite:///moomoo_risk.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.SessionLocal()

    def sync_limits(self, account_id: str, limit_configs: Dict[str, Dict[str, float]]):
        """
        Sync limits from environment/CLI args.
        limit_configs: {"GLOBAL": {"USD": 1000.0}, ...}
        """
        account_id = str(account_id)
        session = self._get_session()
        try:
            for l_type_str, currencies in limit_configs.items():
                l_type = LimitType[l_type_str]
                for curr, cap in currencies.items():
                    limit = session.query(Limit).filter_by(
                        account_id=account_id, type=l_type, currency=curr
                    ).first()
                    if limit:
                        limit.hard_cap = cap
                    else:
                        limit = Limit(
                            account_id=account_id,
                            type=l_type,
                            currency=curr,
                            hard_cap=cap,
                            spent=0.0
                        )
                        session.add(limit)
            session.commit()
        finally:
            session.close()

    def _check_and_reset_daily(self, session: Session, account_id: str):
        now = datetime.now(timezone.utc)
        daily_limits = session.query(Limit).filter(
            Limit.account_id == account_id,
            Limit.type.in_([LimitType.DAILY_BUDGET, LimitType.DAILY_LOSS])
        ).all()
        
        for limit in daily_limits:
            if limit.last_reset.date() < now.date():
                limit.spent = 0.0
                limit.last_reset = now
        session.flush()

    def get_status(self, account_id: str) -> Dict[str, Any]:
        account_id = str(account_id)
        session = self._get_session()
        try:
            self._check_and_reset_daily(session, account_id)
            limits = session.query(Limit).filter_by(account_id=account_id).all()
            result = {}
            for l in limits:
                if l.type.name not in result:
                    result[l.type.name] = {}
                result[l.type.name][l.currency] = {
                    "cap": l.hard_cap,
                    "spent": l.spent,
                    "remaining": max(0.0, l.hard_cap - l.spent)
                }
            return result
        finally:
            session.close()

    def can_buy(self, account_id: str, ticker: str, amount: float) -> bool:
        account_id = str(account_id)
        currency = self._get_currency_from_ticker(ticker)
        session = self._get_session()
        try:
            self._check_and_reset_daily(session, account_id)
            # Check Global and Daily Budget
            limits = session.query(Limit).filter(
                Limit.account_id == account_id,
                Limit.currency == currency,
                Limit.type.in_([LimitType.GLOBAL, LimitType.DAILY_BUDGET, LimitType.DAILY_LOSS])
            ).all()
            
            for l in limits:
                if l.type == LimitType.DAILY_LOSS:
                    # For loss, 'spent' is realized loss. If loss exceeds cap, block.
                    if l.spent >= l.hard_cap:
                        return False
                else:
                    if l.spent + amount > l.hard_cap:
                        return False
            return True
        finally:
            session.close()

    def record_transaction(self, account_id: str, ticker: str, action: str, price: float, quantity: int):
        account_id = str(account_id)
        currency = self._get_currency_from_ticker(ticker)
        session = self._get_session()
        try:
            self._check_and_reset_daily(session, account_id)
            amount = price * quantity
            realized_p_l = 0.0

            if action.upper() == "BUY":
                # Update Global and Daily Budget
                budget_limits = session.query(Limit).filter(
                    Limit.account_id == account_id,
                    Limit.currency == currency,
                    Limit.type.in_([LimitType.GLOBAL, LimitType.DAILY_BUDGET])
                ).all()
                for l in budget_limits:
                    l.spent += amount
                
                # Update Inventory
                inv = session.query(AgentInventory).filter_by(account_id=account_id, ticker=ticker).first()
                if inv:
                    new_qty = inv.qty + quantity
                    inv.avg_price = ((inv.qty * inv.avg_price) + amount) / new_qty
                    inv.qty = new_qty
                else:
                    inv = AgentInventory(account_id=account_id, ticker=ticker, qty=quantity, avg_price=price)
                    session.add(inv)

            elif action.upper() == "SELL":
                inv = session.query(AgentInventory).filter_by(account_id=account_id, ticker=ticker).first()
                if not inv or inv.qty < quantity:
                    raise ValueError(f"Insufficient inventory for {ticker}")
                
                realized_p_l = (price - inv.avg_price) * quantity
                cost_basis = inv.avg_price * quantity
                
                # Update Global Limit (Replenish)
                global_limit = session.query(Limit).filter_by(
                    account_id=account_id, currency=currency, type=LimitType.GLOBAL
                ).first()
                if global_limit:
                    # Replenish cost basis + profit (but profit only restores what was spent)
                    # Actually, requirements say: restore cost basis, and potentially profit up to cap.
                    # Simplified: if we spent X and get back Y, we reduce 'spent' by Y.
                    # But 'spent' cannot go below 0.
                    replenishment = cost_basis + realized_p_l
                    global_limit.spent = max(0.0, global_limit.spent - replenishment)

                # Update Daily Loss (if realized_p_l is negative, it increases 'spent' loss)
                if realized_p_l < 0:
                    loss_limit = session.query(Limit).filter_by(
                        account_id=account_id, currency=currency, type=LimitType.DAILY_LOSS
                    ).first()
                    if loss_limit:
                        loss_limit.spent += abs(realized_p_l)

                # Update Inventory
                inv.qty -= quantity
                if inv.qty == 0:
                    session.delete(inv)

            # Record Transaction
            tx = RiskTransaction(
                account_id=account_id,
                ticker=ticker,
                action=action.upper(),
                price=price,
                quantity=quantity,
                currency=currency,
                realized_p_l=realized_p_l
            )
            session.add(tx)
            session.commit()
        finally:
            session.close()

    def rollback_transaction(self, account_id: str, ticker: str, action: str, price: float, quantity: int):
        """
        Reverse the effects of a recorded transaction (e.g., if API call fails).
        Only supports 'BUY' rollback for now (returning funds to limit and removing inventory).
        """
        if action.upper() != "BUY":
            return # Only BUY requires rollback of 'spent' funds for now

        account_id = str(account_id)
        currency = self._get_currency_from_ticker(ticker)
        session = self._get_session()
        try:
            amount = price * quantity
            # 1. Restore Limits
            limits = session.query(Limit).filter(
                Limit.account_id == account_id,
                Limit.currency == currency,
                Limit.type.in_([LimitType.GLOBAL, LimitType.DAILY_BUDGET])
            ).all()
            for l in limits:
                l.spent = max(0.0, l.spent - amount)
            
            # 2. Revert Inventory
            inv = session.query(AgentInventory).filter_by(account_id=account_id, ticker=ticker).first()
            if inv:
                if inv.qty <= quantity:
                    session.delete(inv)
                else:
                    new_qty = inv.qty - quantity
                    inv.avg_price = ((inv.qty * inv.avg_price) - amount) / new_qty
                    inv.qty = new_qty
            
            session.commit()
        finally:
            session.close()

    def get_inventory(self, account_id: str) -> Dict[str, Any]:
        account_id = str(account_id)
        session = self._get_session()
        try:
            items = session.query(AgentInventory).filter_by(account_id=account_id).all()
            return {i.ticker: {"qty": i.qty, "avg_price": i.avg_price} for i in items}
        finally:
            session.close()

    def migrate_from_json(self, json_path: str, acc_id: str):
        if not os.path.exists(json_path):
            return
        
        with open(json_path, "r") as f:
            data = json.load(f)
        
        acc_id = str(acc_id)
        session = self._get_session()
        try:
            # Migrate Limits
            s = data.get("session", {})
            daily_limits = s.get("daily_limits", {})
            daily_losses = s.get("daily_losses", {})
            volumes = s.get("volumes", {})
            p_ls = s.get("p_ls", {})

            for curr, cap in daily_limits.items():
                spent = volumes.get(curr, 0.0)
                limit = Limit(account_id=acc_id, type=LimitType.DAILY_BUDGET, currency=curr, hard_cap=cap, spent=spent)
                session.add(limit)
            
            for curr, cap in daily_losses.items():
                realized_pl = p_ls.get(curr, 0.0)
                spent = abs(realized_pl) if realized_pl < 0 else 0.0
                limit = Limit(account_id=acc_id, type=LimitType.DAILY_LOSS, currency=curr, hard_cap=cap, spent=spent)
                session.add(limit)

            # Migrate Inventory
            inventory = data.get("inventory", {})
            for ticker, inv_data in inventory.items():
                inv = AgentInventory(
                    account_id=acc_id,
                    ticker=ticker,
                    qty=inv_data["qty"],
                    avg_price=inv_data["avg_price"]
                )
                session.add(inv)

            # Migrate Transactions
            transactions = data.get("transactions", [])
            for tx_data in transactions:
                # Parse timestamp if available, else use now
                ts_str = tx_data.get("timestamp")
                ts = datetime.fromisoformat(ts_str) if ts_str else datetime.now(timezone.utc)
                tx = RiskTransaction(
                    account_id=acc_id,
                    timestamp=ts,
                    ticker=tx_data["ticker"],
                    action=tx_data["action"],
                    price=tx_data["price"],
                    quantity=tx_data["quantity"],
                    currency=tx_data["currency"],
                    realized_p_l=tx_data.get("realized_p_l", 0.0)
                )
                session.add(tx)

            session.commit()
        finally:
            session.close()

    def _get_currency_from_ticker(self, ticker: str) -> str:
        MARKET_CURRENCY_MAP = {
            "US": "USD",
            "HK": "HKD",
            "SG": "SGD",
            "JP": "JPY",
            "CN": "CNH",
        }
        if "." in ticker:
            market = ticker.split(".")[0].upper()
            return MARKET_CURRENCY_MAP.get(market, "DEFAULT")
        return "DEFAULT"
