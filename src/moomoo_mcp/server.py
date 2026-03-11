import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass


from mcp.server.fastmcp import FastMCP
from moomoo.common import ft_logger
from moomoo_mcp.services.base_service import MoomooService
from moomoo_mcp.services.market_data_service import MarketDataService
from moomoo_mcp.services.trade_service import TradeService
from moomoo_mcp.services.session_service import SessionService
from moomoo_mcp.services.risk_management_service import RiskManagementService

logger = logging.getLogger(__name__)


# Disable moomoo library console logging to prevent corruption of MCP stdout protocol
if hasattr(ft_logger, "logger") and hasattr(ft_logger.logger, "console_logger"):
    # Clear existing handlers
    ft_logger.logger.console_logger.handlers = []
    # Replace the internal consoleHandler reference with a NullHandler.
    # This ensures that when fontColor/info/error is called and it tries to re-add 
    # self.consoleHandler, it adds a harmless NullHandler instead of a StreamHandler.
    ft_logger.logger.consoleHandler = logging.NullHandler()


@dataclass
class AppContext:
    """Application context with typed dependencies."""
    moomoo_service: MoomooService
    trade_service: TradeService
    market_data_service: MarketDataService
    session_service: SessionService
    risk_service: RiskManagementService


def _auto_unlock_trade(trade_service: TradeService) -> None:
    """Attempt to auto-unlock trade using environment variables.

    Reads MOOMOO_TRADE_PASSWORD (plain text, preferred) or MOOMOO_TRADE_PASSWORD_MD5.
    Logs status and handles failures gracefully without crashing.
    """
    password = os.environ.get("MOOMOO_TRADE_PASSWORD")
    password_md5 = os.environ.get("MOOMOO_TRADE_PASSWORD_MD5")

    if not password and not password_md5:
        logger.info(
            "No trade password configured (MOOMOO_TRADE_PASSWORD or "
            "MOOMOO_TRADE_PASSWORD_MD5 not set). Running in SIMULATE-only mode."
        )
        return

    try:
        # Must fetch account list before unlock to initialize account context
        accounts = trade_service.get_accounts()
        logger.info(f"Found {len(accounts)} trading account(s)")

        if password:
            trade_service.unlock_trade(password=password)
            logger.info("Trade unlocked successfully. REAL account access enabled.")
        else:
            trade_service.unlock_trade(password_md5=password_md5)
            logger.info("Trade unlocked successfully (via MD5). REAL account access enabled.")
    except RuntimeError as e:
        logger.warning(
            f"Failed to unlock trade: {e}. "
            "REAL account access will not be available. "
            "Use unlock_trade tool to retry manually."
        )


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage moomoo connections lifecycle."""
    moomoo_service = MoomooService()
    moomoo_service.connect()

    # Read security firm from environment (e.g., FUTUSG for Singapore, FUTUSECURITIES for HK)
    security_firm = os.environ.get("MOOMOO_SECURITY_FIRM")
    if security_firm:
        logger.info(f"Using security firm: {security_firm}")

    risk_service = RiskManagementService()
    session_service = SessionService()
    trade_service = TradeService(
        security_firm=security_firm,
        session_service=session_service,
        risk_management_service=risk_service
    )
    trade_service.connect()

    # Auto-unlock trade if password is configured in environment
    _auto_unlock_trade(trade_service)

    # Create market data service using the shared quote context
    market_data_service = MarketDataService(quote_ctx=moomoo_service.quote_ctx)

    try:
        yield AppContext(
            moomoo_service=moomoo_service,
            trade_service=trade_service,
            market_data_service=market_data_service,
            session_service=session_service,
            risk_service=risk_service,
        )
    finally:
        trade_service.close()
        moomoo_service.close()

mcp = FastMCP(
    "Moomoo Trading",
    lifespan=app_lifespan,
    dependencies=["moomoo-api", "pandas", "sqlalchemy"] 
)

# Import tools to register them
import moomoo_mcp.tools.system
import moomoo_mcp.tools.account
import moomoo_mcp.tools.market_data
import moomoo_mcp.tools.trading
import moomoo_mcp.tools.session
import argparse

def main():
    """Entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="Moomoo API MCP Server")
    parser.add_argument("--daily-limit", type=str, help="Daily budget limit (e.g., 1000USD,500SGD).")
    parser.add_argument("--daily-loss", type=str, help="Daily loss limit (e.g., 200USD).")
    parser.add_argument("--global-limit", type=str, help="Persistent global budget limit (e.g., 5000USD).")
    # Extract known args and pass others to mcp.run (which uses click/typer)
    args, unknown = parser.parse_known_args()

    if args.daily_limit is not None:
        os.environ["MOOMOO_DAILY_LIMIT"] = str(args.daily_limit)
    if args.daily_loss is not None:
        os.environ["MOOMOO_DAILY_LOSS"] = str(args.daily_loss)
    if args.global_limit is not None:
        os.environ["GLOBAL_LIMIT"] = str(args.global_limit)

    # Note: FastMCP.run() handles stdio/server startup
    # We pass empty list to run if we parsed our own args to avoid conflicts
    # but FastMCP might need its own flags. We'll let it handle its own.
    mcp.run()

if __name__ == "__main__":
    main()
