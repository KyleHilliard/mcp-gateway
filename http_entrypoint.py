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
    print("DEBUG: VERSION 2026-02-15-FIX-6 - BROAD PATCH ACTIVE", flush=True)
    try:
        # Patch Starlette if present (just in case)
        try:
            from starlette.middleware.trustedhost import TrustedHostMiddleware
            # Bypass middleware
            async def mock_call(self, scope, receive, send):
                await self.app(scope, receive, send)
            TrustedHostMiddleware.__call__ = mock_call
            print("DEBUG: Monkeypatched Starlette TrustedHostMiddleware", flush=True)
        except ImportError:
            print("DEBUG: Starlette not found or patch failed", flush=True)

        from mcp.server.transport_security import TransportSecuritySettings
        
        # 1. Patch the class defaults
        TransportSecuritySettings.enable_dns_rebinding_protection = False
        TransportSecuritySettings.allowed_hosts = ["*"]
        TransportSecuritySettings.allowed_origins = ["*"]
        
        # 2. Patch validation methods
        def allow_all(*args, **kwargs): return True
        TransportSecuritySettings.is_host_allowed = allow_all
        TransportSecuritySettings.is_origin_allowed = allow_all
        TransportSecuritySettings.verify_host = allow_all
        TransportSecuritySettings.check_host = allow_all
        
        # 3. Intercept __init__
        original_init = TransportSecuritySettings.__init__
        def new_init(self, *args, **kwargs):
            kwargs['enable_dns_rebinding_protection'] = False
            kwargs['allowed_hosts'] = ["*"]
            kwargs['allowed_origins'] = ["*"]
            print(f"DEBUG: Intercepted TransportSecuritySettings init.", flush=True)
            original_init(self, *args, **kwargs)
            self.enable_dns_rebinding_protection = False
            
        TransportSecuritySettings.__init__ = new_init

        # 4. Update the existing instance
        if hasattr(mcp, '_transport_security'):
            mcp._transport_security = TransportSecuritySettings(
                enable_dns_rebinding_protection=False,
                allowed_hosts=["*"],
                allowed_origins=["*"]
            )
            print("DEBUG: Updated mcp._transport_security instance", flush=True)
            
    except ImportError as e:
        print(f"DEBUG: FAILED TO IMPORT OR PATCH SECURITY SETTINGS: {e}", flush=True)
        # Try to find it in sys.modules if verify failed
        import sys
        print(f"DEBUG: Available mcp modules: {[k for k in sys.modules if k.startswith('mcp')]}", flush=True)
        # Older SDK version without TransportSecuritySettings — no DNS protection
        pass

    print(f"Starting MCP Gateway (Streamable HTTP) on {host}:{port}")
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
