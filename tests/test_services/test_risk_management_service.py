import pytest
import os
import json
from datetime import datetime, timedelta, timezone
from moomoo_mcp.services.risk_management_service import RiskManagementService, LimitType

@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_risk.db")

@pytest.fixture
def risk_service(db_path):
    return RiskManagementService(db_url=f"sqlite:///{db_path}")

def test_init_limits(risk_service):
    # Test setting initial limits via env-style dict
    limits = {
        "GLOBAL": {"USD": 1000.0, "SGD": 2000.0},
        "DAILY_BUDGET": {"USD": 500.0},
        "DAILY_LOSS": {"USD": 100.0}
    }
    risk_service.sync_limits(12345, limits)
    
    status = risk_service.get_status(12345)
    assert status["GLOBAL"]["USD"]["cap"] == 1000.0
    assert status["DAILY_BUDGET"]["USD"]["cap"] == 500.0
    assert status["DAILY_LOSS"]["USD"]["cap"] == 100.0

def test_spend_global_limit(risk_service):
    acc_id = 12345
    risk_service.sync_limits(acc_id, {"GLOBAL": {"USD": 1000.0}})
    
    # Spend 400
    risk_service.record_transaction(acc_id, "US.AAPL", "BUY", 200.0, 2)
    
    status = risk_service.get_status(acc_id)
    assert status["GLOBAL"]["USD"]["spent"] == 400.0
    assert status["GLOBAL"]["USD"]["remaining"] == 600.0

def test_daily_limit_reset(risk_service, db_path):
    acc_id = 12345
    risk_service.sync_limits(acc_id, {"DAILY_BUDGET": {"USD": 500.0}})
    
    # Spend 200 today
    risk_service.record_transaction(acc_id, "US.AAPL", "BUY", 100.0, 2)
    assert risk_service.get_status(acc_id)["DAILY_BUDGET"]["USD"]["spent"] == 200.0
    
    # Simulate "tomorrow" by manually updating the last_reset in DB
    from sqlalchemy import create_engine, text
    engine = create_engine(f"sqlite:///{db_path}")
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    with engine.connect() as conn:
        conn.execute(text("UPDATE limits SET last_reset = :y WHERE type = 'DAILY_BUDGET'"), {"y": yesterday})
        conn.commit()
    
    # Check status again - should be reset
    status = risk_service.get_status(acc_id)
    assert status["DAILY_BUDGET"]["USD"]["spent"] == 0.0
    assert status["DAILY_BUDGET"]["USD"]["remaining"] == 500.0

def test_global_limit_replenishment(risk_service):
    acc_id = 12345
    risk_service.sync_limits(acc_id, {"GLOBAL": {"USD": 1000.0}})
    
    # Buy 2 shares at 100 (Spent 200)
    risk_service.record_transaction(acc_id, "US.AAPL", "BUY", 100.0, 2)
    
    # Sell 1 share at 120 (Cost 100, Profit 20)
    # Total replenishment = 100 (cost) + 20 (profit) = 120
    risk_service.record_transaction(acc_id, "US.AAPL", "SELL", 120.0, 1)
    
    status = risk_service.get_status(acc_id)
    # Initial 1000, Spent 200 -> 800 left. Replenish 120 -> 920 left. Spent = 80.
    assert status["GLOBAL"]["USD"]["spent"] == 80.0
    assert status["GLOBAL"]["USD"]["remaining"] == 920.0

def test_migration_from_json(tmp_path):
    # Create legacy JSON state
    json_path = tmp_path / "old_state.json"
    old_state = {
        "session": {
            "daily_limits": {"USD": 1000.0},
            "daily_losses": {"USD": 200.0},
            "volumes": {"USD": 300.0},
            "p_ls": {"USD": -50.0},
            "is_active": True
        },
        "inventory": {
            "US.AAPL": {"qty": 10, "avg_price": 150.0}
        },
        "transactions": []
    }
    with open(json_path, "w") as f:
        json.dump(old_state, f)
    
    db_path = str(tmp_path / "migrated.db")
    service = RiskManagementService(db_url=f"sqlite:///{db_path}")
    
    # Perform migration
    service.migrate_from_json(str(json_path), acc_id=12345)
    
    status = service.get_status(12345)
    assert status["DAILY_BUDGET"]["USD"]["cap"] == 1000.0
    assert status["DAILY_BUDGET"]["USD"]["spent"] == 300.0
    assert status["DAILY_LOSS"]["USD"]["spent"] == 50.0 # Loss is positive spent in this model
    
    inv = service.get_inventory(12345)
    assert inv["US.AAPL"]["qty"] == 10
    assert inv["US.AAPL"]["avg_price"] == 150.0

def test_strict_blocking(risk_service):
    acc_id = 12345
    risk_service.sync_limits(acc_id, {
        "GLOBAL": {"USD": 500.0},
        "DAILY_BUDGET": {"USD": 1000.0}
    })
    
    # Can buy 400
    assert risk_service.can_buy(acc_id, "US.AAPL", 400.0) is True
    
    # Cannot buy 600 (Global limit hit)
    assert risk_service.can_buy(acc_id, "US.AAPL", 600.0) is False
    
    # Spend 400
    risk_service.record_transaction(acc_id, "US.AAPL", "BUY", 400.0, 1)
    
    # Cannot buy 200 more
    assert risk_service.can_buy(acc_id, "US.AAPL", 200.0) is False
