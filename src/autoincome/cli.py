"""AutoIncome CLI entry point.

Provides command-line interface for starting the server,
running scans, and managing the application.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

import uvicorn

from autoincome import __version__
from autoincome.core.config import get_settings


def _start_server(host: str, port: int, reload: bool) -> None:
    """Start the FastAPI development server."""
    uvicorn.run(
        "autoincome.api.main:app",
        host=host,
        port=port,
        reload=reload,
    )


def _version() -> None:
    """Print version and exit."""
    print(f"AutoIncome {__version__}")


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="autoincome",
        description="AutoIncome - AI-powered passive income opportunity aggregator",
    )
    parser.add_argument(
        "--version", action="store_true", help="Show version and exit"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Server command
    server_parser = subparsers.add_parser("server", help="Start the API server")
    server_parser.add_argument(
        "--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)"
    )
    server_parser.add_argument(
        "--port", type=int, default=8080, help="Bind port (default: 8080)"
    )
    server_parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload (development)"
    )

    # Config command
    config_parser = subparsers.add_parser("config", help="Show configuration")

    args = parser.parse_args(argv)

    if args.version:
        _version()
        return 0

    if args.command == "server":
        _start_server(args.host, args.port, args.reload)
        return 0

    if args.command == "config":
        settings = get_settings()
        print(f"Environment: {settings.env}")
        print(f"Debug: {settings.debug}")
        print(f"Host: {settings.host}")
        print(f"Port: {settings.port}")
        print(f"Database: {settings.db_path}")
        print(f"Registration: {'enabled' if settings.enable_registration else 'disabled'}")
        return 0

    # Default: start server
    _start_server("0.0.0.0", 8080, False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
