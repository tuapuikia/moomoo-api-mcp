"""Session and Risk Management tools."""

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
import os

from moomoo_mcp.server import AppContext, mcp


@mcp.tool()
async def init_session(
    ctx: Context[ServerSession, AppContext],
    daily_limit: str | None = None,
    daily_loss: str | None = None,
    global_limit: str | None = None,
) -> dict:
    """Initialize or update risk limits and portfolio snapshot.

    Args:
        daily_limit: Optional daily budget limit (e.g., '1000USD,500SGD').
        daily_loss: Optional daily loss limit (e.g., '200USD').
        global_limit: Optional persistent global budget (e.g., '5000USD').

    Returns:
        Dictionary confirming current risk status.
    """
    risk_service = ctx.request_context.lifespan_context.risk_service
    trade_service = ctx.request_context.lifespan_context.trade_service

    # 1. Gather all accounts to sync limits for each
    try:
        accounts = trade_service.get_accounts()
        account_ids = [str(a["acc_id"]) for acc in accounts] if accounts else ["0"]
    except Exception:
        account_ids = ["0"]

    # 2. Parse limits from args or environment
    limit_configs = {}
    
    # Mapping tool args to DB types and env keys
    configs_to_process = [
        ("GLOBAL", global_limit, "GLOBAL_LIMIT"),
        ("DAILY_BUDGET", daily_limit, "MOOMOO_DAILY_LIMIT"),
        ("DAILY_LOSS", daily_loss, "MOOMOO_DAILY_LOSS"),
    ]

    for l_type, arg_val, env_key in configs_to_process:
        val_to_parse = arg_val or os.environ.get(env_key)
        if val_to_parse:
            parsed = risk_service.parse_multi_currency_string(val_to_parse)
            if parsed:
                limit_configs[l_type] = parsed

    # 3. Sync with DB for all accounts
    for acc_id in account_ids:
        risk_service.sync_limits(acc_id, limit_configs)

    # 4. Handle Legacy SessionService (Optional, for backward compatibility)
    # If daily_limit was a float, we'd need to handle it, but here it's string.
    # We'll skip deep integration with SessionService for now as it's deprecated.

    await ctx.info(f"Risk limits initialized/synced for {len(account_ids)} accounts.")

    return {
        "status": "limits_synced",
        "accounts_processed": len(account_ids),
        "applied_configs": limit_configs
    }


@mcp.tool()
async def get_session_status(
    ctx: Context[ServerSession, AppContext],
    account_id: str | None = None
) -> dict:
    """Get current risk metrics, inventory, and transaction history.

    Args:
        account_id: Optional account ID filter. Defaults to the first active account.
    """
    risk_service = ctx.request_context.lifespan_context.risk_service
    trade_service = ctx.request_context.lifespan_context.trade_service
    
    # Determine account_id
    if not account_id:
        try:
            accounts = trade_service.get_accounts()
            account_id = str(accounts[0]["acc_id"]) if accounts else "0"
        except Exception:
            account_id = "0"

    status = risk_service.get_status(account_id)
    inventory = risk_service.get_inventory(account_id)
    
    return {
        "account_id": account_id,
        "limits": status,
        "agent_inventory": inventory
    }
