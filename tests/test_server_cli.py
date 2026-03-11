import pytest
import os
import argparse
from unittest.mock import MagicMock, patch
from moomoo_mcp.server import main

def test_arg_parsing_default():
    with patch("sys.argv", ["moomoo-api-mcp"]):
        with patch("moomoo_mcp.server.mcp.run") as mock_run:
            # We need to catch SystemExit if parse_known_args fails, 
            # but here it should succeed with defaults.
            main()
            mock_run.assert_called_once_with()

def test_arg_parsing_sse_flag():
    with patch("sys.argv", ["moomoo-api-mcp", "--sse"]):
        with patch("moomoo_mcp.server.mcp.run") as mock_run:
            main()
            mock_run.assert_called_once_with(transport="sse", host="0.0.0.0", port=8000)

def test_arg_parsing_custom_port():
    with patch("sys.argv", ["moomoo-api-mcp", "--sse", "--port", "9000"]):
        with patch("moomoo_mcp.server.mcp.run") as mock_run:
            main()
            mock_run.assert_called_once_with(transport="sse", host="0.0.0.0", port=9000)

def test_arg_parsing_port_env_var():
    with patch.dict(os.environ, {"PORT": "7000"}):
        with patch("sys.argv", ["moomoo-api-mcp", "--sse"]):
            with patch("moomoo_mcp.server.mcp.run") as mock_run:
                main()
                mock_run.assert_called_once_with(transport="sse", host="0.0.0.0", port=7000)

def test_arg_parsing_risk_limits():
    with patch("sys.argv", ["moomoo-api-mcp", "--daily-limit", "100USD"]):
        with patch("moomoo_mcp.server.mcp.run"):
            main()
            assert os.environ.get("MOOMOO_DAILY_LIMIT") == "100USD"
