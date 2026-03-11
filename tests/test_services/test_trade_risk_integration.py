import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from moomoo_mcp.services.trade_service import TradeService
from moomoo_mcp.services.risk_management_service import RiskManagementService

@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_risk.db")

@pytest.fixture
def risk_service(db_path):
    return RiskManagementService(db_url=f"sqlite:///{db_path}")

@pytest.fixture
def mock_trade_ctx():
    return MagicMock()

@pytest.fixture
def trade_service(mock_trade_ctx, risk_service):
    service = TradeService(risk_management_service=risk_service)
    service.trade_ctx = mock_trade_ctx
    return service

def test_place_buy_order_enforces_risk_limit(trade_service, risk_service, mock_trade_ctx):
    acc_id = 12345
    risk_service.sync_limits(acc_id, {"GLOBAL": {"USD": 500.0}})
    
    # 1. Try to buy 600 USD - should fail
    with pytest.raises(RuntimeError, match="Order blocked by risk limits"):
        trade_service.place_order(
            code="US.AAPL",
            price=300.0,
            qty=2,
            trd_side="BUY",
            acc_id=acc_id
        )
    
    mock_trade_ctx.place_order.assert_not_called()

def test_place_buy_order_records_in_risk_service(trade_service, risk_service, mock_trade_ctx):
    acc_id = 12345
    risk_service.sync_limits(acc_id, {"GLOBAL": {"USD": 1000.0}})
    
    # Setup mock for successful order
    df = pd.DataFrame([{"order_id": "123", "order_status": "SUBMITTED"}])
    mock_trade_ctx.place_order.return_value = (0, df)
    
    # 2. Buy 200 USD
    trade_service.place_order(
        code="US.AAPL",
        price=100.0,
        qty=2,
        trd_side="BUY",
        acc_id=acc_id
    )
    
    status = risk_service.get_status(acc_id)
    assert status["GLOBAL"]["USD"]["spent"] == 200.0
    
    inv = risk_service.get_inventory(acc_id)
    assert inv["US.AAPL"]["qty"] == 2

def test_place_sell_order_replenishes_limit(trade_service, risk_service, mock_trade_ctx):
    acc_id = 12345
    risk_service.sync_limits(acc_id, {"GLOBAL": {"USD": 1000.0}})
    
    # 1. Buy 2 shares at 100 (Spent 200)
    risk_service.record_transaction(acc_id, "US.AAPL", "BUY", 100.0, 2)
    
    # Setup mock for successful sell order
    df = pd.DataFrame([{"order_id": "124", "order_status": "SUBMITTED"}])
    mock_trade_ctx.place_order.return_value = (0, df)
    
    # 2. Sell 1 share at 150 (Cost 100, Profit 50) -> Replenish 150
    trade_service.place_order(
        code="US.AAPL",
        price=150.0,
        qty=1,
        trd_side="SELL",
        acc_id=acc_id
    )
    
    status = risk_service.get_status(acc_id)
    # 200 spent - 150 replenishment = 50 spent.
    assert status["GLOBAL"]["USD"]["spent"] == 50.0
    
    inv = risk_service.get_inventory(acc_id)
    assert inv["US.AAPL"]["qty"] == 1

def test_rollback_on_api_failure(trade_service, risk_service, mock_trade_ctx):
    acc_id = 12345
    risk_service.sync_limits(acc_id, {"GLOBAL": {"USD": 1000.0}})
    
    # API fails
    mock_trade_ctx.place_order.return_value = (-1, "API error")
    
    with pytest.raises(RuntimeError, match="place_order failed"):
        trade_service.place_order(
            code="US.AAPL",
            price=100.0,
            qty=2,
            trd_side="BUY",
            acc_id=acc_id
        )
    
    # Limit should NOT be spent if API failed (or rolled back)
    status = risk_service.get_status(acc_id)
    assert status["GLOBAL"]["USD"]["spent"] == 0.0
