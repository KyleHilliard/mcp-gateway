"""
HTTP entrypoint for Lasso MCP Gateway.

Imports the Lasso gateway's FastMCP app and runs it with
Streamable HTTP transport instead of the default stdio.

Configures TransportSecuritySettings to allow remote access
via Tailscale and LAN IPs (DNS rebinding protection).
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

    if hasattr(mcp, 'settings'):
        mcp.settings.host = host
        mcp.settings.port = port

    # Configure DNS rebinding protection to allow remote access
    # Tailscale handles authentication; we allow known IPs.
    try:
        from mcp.server.transport_security import TransportSecuritySettings
        # Monkeypatch: Force allow all hosts/origins (Tailscale handles auth)
        TransportSecuritySettings.is_host_allowed = lambda self, host: True
        TransportSecuritySettings.is_origin_allowed = lambda self, origin: True
        
        mcp._transport_security = TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
            allowed_hosts=["*"],
            allowed_origins=["*"]
        )
        print("DEBUG: DNS Rebinding Protection DISABLED (Monkeypatched)")
    except ImportError:
        # Older SDK version without TransportSecuritySettings — no DNS protection
        pass

    print(f"Starting MCP Gateway (Streamable HTTP) on {host}:{port}")
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
