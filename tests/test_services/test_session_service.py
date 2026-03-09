import os
import json
import pytest
from moomoo_mcp.services.session_service import SessionService

@pytest.fixture
def session_service(tmp_path):
    state_file = tmp_path / "transaction-state.json"
    return SessionService(state_file=str(state_file))

def test_init_session(session_service):
    session_service.init_session(daily_limit=1000.0, daily_loss=200.0)
    status = session_service.get_status()
    assert status["is_active"] is True
    assert status["daily_limit"] == 1000.0
    assert status["daily_loss"] == 200.0
    assert status["remaining_budget"] == 1000.0

def test_snapshot_portfolio(session_service):
    positions = [
        {"code": "US.AAPL", "qty": 10, "cost_price": 150.0},
        {"code": "US.TSLA", "qty": 5, "cost_price": 200.0}
    ]
    session_service.snapshot_portfolio(positions)
    state = session_service._load_state()
    assert state["snapshot"]["US.AAPL"]["qty"] == 10
    assert state["snapshot"]["US.TSLA"]["unit_price"] == 200.0

def test_record_buy_transaction(session_service):
    session_service.init_session(daily_limit=1000.0, daily_loss=200.0)
    session_service.record_transaction("US.AAPL", "BUY", 150.0, 2, 12345)
    
    status = session_service.get_status()
    assert status["total_realized_p_l"] == 0.0
    assert status["remaining_budget"] == 700.0 # 1000 - (150 * 2)
    assert status["inventory"]["US.AAPL"]["qty"] == 2
    assert status["inventory"]["US.AAPL"]["avg_price"] == 150.0

def test_record_sell_transaction_with_p_l(session_service):
    session_service.init_session(daily_limit=1000.0, daily_loss=200.0)
    # Buy 2 shares at 150
    session_service.record_transaction("US.AAPL", "BUY", 150.0, 2, 12345)
    # Sell 1 share at 160 (Profit 10)
    session_service.record_transaction("US.AAPL", "SELL", 160.0, 1, 12345)
    
    status = session_service.get_status()
    assert status["total_realized_p_l"] == 10.0
    assert status["inventory"]["US.AAPL"]["qty"] == 1
    
    # Sell 1 share at 140 (Loss 10)
    session_service.record_transaction("US.AAPL", "SELL", 140.0, 1, 12345)
    status = session_service.get_status()
    assert status["total_realized_p_l"] == 0.0
    assert "US.AAPL" not in status["inventory"]

def test_can_buy_limits(session_service):
    session_service.init_session(daily_limit=500.0, daily_loss=100.0)
    
    # Allowed
    assert session_service.can_buy(200.0) is True
    
    # Exceed budget
    assert session_service.can_buy(600.0) is False
    
    # Hit loss limit
    session_service.record_transaction("US.AAPL", "BUY", 100.0, 1, 12345)
    session_service.record_transaction("US.AAPL", "SELL", 0.0, 1, 12345) # Loss 100
    
    assert session_service.can_buy(1.0) is False

def test_agent_inventory_check(session_service):
    session_service.init_session(daily_limit=1000.0, daily_loss=200.0)
    session_service.record_transaction("US.AAPL", "BUY", 150.0, 10, 12345)
    
    assert session_service.is_agent_position("US.AAPL", 5) is True
    assert session_service.is_agent_position("US.AAPL", 15) is False
    assert session_service.is_agent_position("US.TSLA", 1) is False
