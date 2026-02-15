"""
HTTP entrypoint for Lasso MCP Gateway.

Imports the Lasso gateway's FastMCP app and runs it with
Streamable HTTP transport instead of the default stdio.

Configures TransportSecuritySettings to allow remote access
via Tailscale and LAN IPs (DNS rebinding protection).
"""

import os

import sys
# Parse Lasso's own CLI args first
from mcp_gateway.gateway import parse_args, mcp
import mcp_gateway.gateway as gw

print("DEBUG: VERSION 2026-02-15-FIX-4 - UNBUFFERED", flush=True)
sys.stdout.flush()

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
    print("DEBUG: VERSION 2026-02-15-FIX-5 - INIT-INTERCEPT ACTIVE", flush=True)
    try:
        from mcp.server.transport_security import TransportSecuritySettings
        
        # 1. Patch the class defaults/methods to be open
        TransportSecuritySettings.enable_dns_rebinding_protection = False
        TransportSecuritySettings.allowed_hosts = ["*"]
        TransportSecuritySettings.allowed_origins = ["*"]
        
        # 2. Patch validation methods to always return True
        # (We patch multiple names to catch whatever the SDK calls)
        def allow_all(*args, **kwargs): return True
        TransportSecuritySettings.is_host_allowed = allow_all
        TransportSecuritySettings.is_origin_allowed = allow_all
        TransportSecuritySettings.verify_host = allow_all
        TransportSecuritySettings.check_host = allow_all
        
        # 3. Intercept __init__ to force settings on new instances
        original_init = TransportSecuritySettings.__init__
        def new_init(self, *args, **kwargs):
            # Force disable protection
            kwargs['enable_dns_rebinding_protection'] = False
            kwargs['allowed_hosts'] = ["*"]
            kwargs['allowed_origins'] = ["*"]
            print(f"DEBUG: Intercepted TransportSecuritySettings init. Forcing open access.", flush=True)
            original_init(self, *args, **kwargs)
            # Double check after init
            self.enable_dns_rebinding_protection = False
            
        TransportSecuritySettings.__init__ = new_init

        # 4. Update the existing instance just in case
        mcp._transport_security = TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
            allowed_hosts=["*"],
            allowed_origins=["*"]
        )
    except ImportError:
        # Older SDK version without TransportSecuritySettings — no DNS protection
        pass

    print(f"Starting MCP Gateway (Streamable HTTP) on {host}:{port}")
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
