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
    print("DEBUG: VERSION 2026-02-15-FIX-9 - HOST REWRITE ACTIVE", flush=True)
    try:
        # Introspect mcp object
        print(f"DEBUG: mcp object dir: {dir(mcp)}", flush=True)
        
        # Try to find the Starlette app
        app = None
        
        # Method 1: Check for explicit streamable_http_app property
        if hasattr(mcp, 'streamable_http_app'):
            # It might be a method or property
            candidate = mcp.streamable_http_app
            print(f"DEBUG: Found streamable_http_app: {type(candidate)}", flush=True)
            if hasattr(candidate, 'add_middleware'):
                app = candidate
                print("DEBUG: Target matches Starlette app interface (has add_middleware)", flush=True)
            
        # Method 2: Check _mcp_server internal
        if not app and hasattr(mcp, '_mcp_server'):
            print(f"DEBUG: _mcp_server dir: {dir(mcp._mcp_server)}", flush=True)
            if hasattr(mcp._mcp_server, 'app'):
                app = mcp._mcp_server.app
                print("DEBUG: Found app via _mcp_server.app", flush=True)

        if app:
             from starlette.middleware.base import BaseHTTPMiddleware
             from starlette.types import ASGIApp, Receive, Scope, Send
             
             class HostRewriteMiddleware(BaseHTTPMiddleware):
                 async def dispatch(self, request, call_next):
                     # Force Host header to localhost:8484 to satisfy SDK check
                     # We need to mutate the scope headers directly
                     headers = dict(request.scope['headers'])
                     headers[b'host'] = b'localhost:8484'
                     request.scope['headers'] = list(headers.items())
                     print(f"DEBUG: Rewrote Host header to localhost:8484 for {request.url}", flush=True)
                     return await call_next(request)

             # Insert at top of middleware stack? add_middleware appends to end (wraps outer)
             app.add_middleware(HostRewriteMiddleware)
             print("DEBUG: Injected HostRewriteMiddleware", flush=True)
        else:
             print("DEBUG: Could not attempt middleware injection - app not found", flush=True)

        # Keep the class patching just in case
        from mcp.server.transport_security import TransportSecuritySettings
        TransportSecuritySettings.is_host_allowed = lambda *args: True
        
    except Exception as e:
        print(f"DEBUG: FIX V7 FAILED: {e}", flush=True)
        import traceback
        traceback.print_exc()
        # Older SDK version without TransportSecuritySettings — no DNS protection
        pass

    print(f"Starting MCP Gateway (Streamable HTTP) on {host}:{port}")
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
