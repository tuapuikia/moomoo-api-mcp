import pytest
import os
import argparse
from unittest.mock import MagicMock, patch
from moomoo_mcp.server import main

def test_arg_parsing_default():
    with patch("sys.argv", ["moomoo-api-mcp"]):
        with patch("moomoo_mcp.server.mcp.run") as mock_run:
            main()
            mock_run.assert_called_once_with()

def test_arg_parsing_http_flag():
    with patch("sys.argv", ["moomoo-api-mcp", "--http"]):
        with patch("moomoo_mcp.server.mcp.run") as mock_mcp_run:
            with patch("uvicorn.run") as mock_uvicorn_run:
                main()
                mock_uvicorn_run.assert_called_once()
                args, kwargs = mock_uvicorn_run.call_args
                assert kwargs["port"] == 8000
                assert kwargs["host"] == "0.0.0.0"

def test_arg_parsing_custom_port():
    with patch("sys.argv", ["moomoo-api-mcp", "--http", "--port", "9000"]):
        with patch("uvicorn.run") as mock_uvicorn_run:
            main()
            mock_uvicorn_run.assert_called_once()
            args, kwargs = mock_uvicorn_run.call_args
            assert kwargs["port"] == 9000

def test_arg_parsing_port_env_var():
    with patch.dict(os.environ, {"PORT": "7000"}):
        with patch("sys.argv", ["moomoo-api-mcp", "--http"]):
            with patch("uvicorn.run") as mock_uvicorn_run:
                main()
                mock_uvicorn_run.assert_called_once()
                args, kwargs = mock_uvicorn_run.call_args
                assert kwargs["port"] == 7000

def test_arg_parsing_risk_limits():
    with patch("sys.argv", ["moomoo-api-mcp", "--daily-limit", "100USD"]):
        with patch("moomoo_mcp.server.mcp.run"):
            main()
            assert os.environ.get("MOOMOO_DAILY_LIMIT") == "100USD"
