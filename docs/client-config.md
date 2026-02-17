# Client Configuration Guide

Connect your AI tools to the local Unraid Gateway.

## Universal Settings

| Setting | Value |
|---|---|
| **URL (External/Tailscale)** | `http://100.94.202.54:8484/mcp` |
| **URL (Internal/LAN)** | `http://10.0.0.37:8484/mcp` |
| **Protocol** | Streamable HTTP (recommended) |
| **Auth** | Managed by the Gateway server (no client token needed) |

---

## 1. Codex / Cursor / VS Code (Recommended)

Ideally, use an extension or built-in MCP support that allows **Streamable HTTP**.

* **Name**: `Unraid Gateway`
* **Type**: `Streamable HTTP`
* **URL**: `http://10.0.0.37:8484/mcp`

---

## 2. Claude Desktop (macOS)

Claude Desktop currently requires a local bridge to convert STDIO to HTTP. You can use `npx` with a bridge utility.

**Config File**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "unraid-gateway": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sse-client",
        "http://10.0.0.37:8484/mcp"
      ]
    }
  }
}
```

*(Note: If the `server-sse-client` fails with Streamable HTTP, try `mcp-proxy` or verify if your client supports direct HTTP URL configuration).*

---

## 3. Zed (Editor)

Add to your `.zed/settings.json`:

```json
"mcp_servers": {
  "unraid-gateway": {
     "type": "http",
     "url": "http://10.0.0.37:8484/mcp"
  }
}
```

---

## 4. Status Dashboard (Web)

* **URL**: `http://10.0.0.37:8585`
* Shows active status and available tools.
