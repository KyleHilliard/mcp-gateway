"""
HTTP entrypoint for Lasso MCP Gateway.

Imports the Lasso gateway's FastMCP app and runs it with
Streamable HTTP transport instead of the default stdio.

Host/port configured via FastMCP settings, not run() args.
"""

import os

# Parse Lasso's own CLI args first
from mcp_gateway.gateway import parse_args, mcp
import mcp_gateway.gateway as gw

def main():
    gw.cli_args = parse_args()

    # Configure host/port via FastMCP settings
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8484"))

    # Set settings on the FastMCP instance
    if hasattr(mcp, 'settings'):
        mcp.settings.host = host
        mcp.settings.port = port
    elif hasattr(mcp, '_mcp_server_settings'):
        mcp._mcp_server_settings.host = host
        mcp._mcp_server_settings.port = port

    print(f"Starting MCP Gateway (Streamable HTTP) on {host}:{port}")
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
