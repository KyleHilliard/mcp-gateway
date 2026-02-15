"""
HTTP entrypoint for Lasso MCP Gateway.

Imports the Lasso gateway's FastMCP app and runs it with
Streamable HTTP transport instead of the default stdio.

Uses only the official MCP Python SDK — no third-party bridge needed.
"""

import os
import sys

# Parse Lasso's own CLI args first (it needs --mcp-json-path)
from mcp_gateway.gateway import parse_args, cli_args, mcp
import mcp_gateway.gateway as gw

def main():
    # Parse args and set global config (Lasso uses a global for this)
    gw.cli_args = parse_args()

    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8484"))

    print(f"Starting MCP Gateway (Streamable HTTP) on {host}:{port}")
    mcp.run(transport="streamable-http", host=host, port=port)

if __name__ == "__main__":
    main()
