"""Session and Risk Management tools."""

from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

from moomoo_mcp.server import AppContext, mcp


@mcp.tool()
async def init_session(
    ctx: Context[ServerSession, AppContext],
    daily_limit: float,
    daily_loss: float,
) -> dict:
    """Initialize a new trading session with risk limits and portfolio snapshot.

    This tool MUST be called before any automated trading begins. It sets the
    budget for the session and snapshots existing positions to protect them.

    Args:
        daily_limit: Total budget (buy volume) allowed for this session in currency.
        daily_loss: Maximum allowed realized loss amount before buying is blocked.

    Returns:
        Dictionary confirming session initialization and snapshot details.
    """
    session_service = ctx.request_context.lifespan_context.session_service
    trade_service = ctx.request_context.lifespan_context.trade_service

    # 1. Initialize session with limits
    session_service.init_session(daily_limit=daily_limit, daily_loss=daily_loss)

    # 2. Snapshot current portfolio (Human positions)
    # Note: We snapshot across both REAL and SIMULATE by default or based on session needs?
    # Usually session is for one environment. We'll use the current trade_service context.
    try:
        # Defaulting to REAL for snapshot as per project preference, 
        # but in practice, users should be aware.
        positions = trade_service.get_positions(trd_env="REAL")
        session_service.snapshot_portfolio(positions)
        snapshot_count = len(positions)
    except Exception as e:
        await ctx.error(f"Failed to snapshot portfolio: {e}")
        snapshot_count = 0

    await ctx.info(
        f"Session initialized. Budget: {daily_limit}, Loss Limit: {daily_loss}. "
        f"Snapshotted {snapshot_count} existing positions."
    )

    return {
        "status": "initialized",
        "daily_limit": daily_limit,
        "daily_loss": daily_loss,
        "snapshotted_positions_count": snapshot_count
    }


@mcp.tool()
async def get_session_status(
    ctx: Context[ServerSession, AppContext]
) -> dict:
    """Get current session P/L, remaining budget, and transaction history.

    Returns:
        Dictionary with 'session' metrics, 'inventory' (agent-owned), and 'transactions'.
    """
    session_service = ctx.request_context.lifespan_context.session_service
    status = session_service.get_status()
    
    # We also include the full state for detailed analysis
    state = session_service._load_state()
    
    return {
        "metrics": status,
        "agent_inventory": state["inventory"],
        "transactions": state["transactions"]
    }
