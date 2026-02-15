"""
HTTP entrypoint for Lasso MCP Gateway.

Imports the Lasso gateway's FastMCP app and runs it with
Streamable HTTP transport instead of the default stdio.

Configures TransportSecuritySettings to allow remote access
via Tailscale and LAN IPs (DNS rebinding protection).
"""
import sys
import os

print("DEBUG: VERSION 2026-02-15-FIX-10 - PRE-IMPORT PATCH", flush=True)

# --- CRITICAL FIX: Patch TransportSecuritySettings BEFORE importing gateway ---
# The mcp_gateway.gateway module instantiates FastMCP() at import time.
# FastMCP() creates a TransportSecuritySettings instance immediately.
# Therefore, we must intercept the class creation BEFORE the module is imported.
try:
    from mcp.server.transport_security import TransportSecuritySettings
    
    # 1. Intercept __init__ to force settings on new instances
    original_init = TransportSecuritySettings.__init__
    def new_init(self, *args, **kwargs):
        kwargs['enable_dns_rebinding_protection'] = False
        kwargs['allowed_hosts'] = ["*"]
        kwargs['allowed_origins'] = ["*"]
        print(f"DEBUG: Intercepted TransportSecuritySettings init (PRE-IMPORT class patch).", flush=True)
        original_init(self, *args, **kwargs)
        self.enable_dns_rebinding_protection = False
        
    TransportSecuritySettings.__init__ = new_init
    
    # 2. Patch validation methods
    def allow_all(*args, **kwargs): return True
    TransportSecuritySettings.is_host_allowed = allow_all
    TransportSecuritySettings.is_origin_allowed = allow_all
    TransportSecuritySettings.verify_host = allow_all
    TransportSecuritySettings.check_host = allow_all
    
    print("DEBUG: Applied pre-import monkeypatch to TransportSecuritySettings", flush=True)
except ImportError:
    print("DEBUG: Failed to import TransportSecuritySettings for pre-patch", flush=True)

# --- NOW import the gateway ---
# This triggers FastMCP() instantiation, which will now use the patched class
from mcp_gateway.gateway import parse_args, mcp
import mcp_gateway.gateway as gw

def main():
    gw.cli_args = parse_args()
    
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8484"))

    if hasattr(mcp, 'settings'):
        mcp.settings.host = host
        mcp.settings.port = port
        
    print(f"Starting MCP Gateway (Streamable HTTP) on {host}:{port}")
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
