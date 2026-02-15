import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

app = FastAPI()

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:8484")
# Endpoint for SSE. If gateway is at :8484, usually /sse if explicitly mounted, 
# but StreamableHTTP defaults might be different. Let's try /sse first.
SSE_ENDPOINT = f"{GATEWAY_URL}/sse"

async def fetch_tools(url: str):
    """
    Connect to MCP Gateway using the official Python SDK client.
    Returns list of tools, resources, and prompts.
    """
    results = {
        "status": "connected",
        "tools": [],
        "resources": [],
        "prompts": [],
        "error": None
    }
    
    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                
                # Fetch capabilities in parallel
                tools_result = await session.list_tools()
                resources_result = await session.list_resources()
                prompts_result = await session.list_prompts()
                
                results["tools"] = [t.model_dump() for t in tools_result.tools]
                results["resources"] = [r.model_dump() for r in resources_result.resources]
                results["prompts"] = [p.model_dump() for p in prompts_result.prompts]
                
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
        
    return results

@app.get("/api/status")
async def get_status():
    """
    Proxy endpoint to fetch MCP metadata from Gateway.
    Handles the SSE session establishment and cleanup per request (or cached).
    """
    # For now, simple per-request connection. Optimization: Keep session alive?
    # Session lifecycle management is complex for stateless HTTP.
    # Connecting on demand is safer for a dashboard.
    data = await fetch_tools(SSE_ENDPOINT)
    if data["status"] == "error":
         # If /sse fails, maybe try /mcp/sse? Or user can configure via env var.
         return JSONResponse(status_code=502, content=data)
    return data

# Serve frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8585)
