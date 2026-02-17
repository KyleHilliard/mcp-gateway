# MCP Gateway

Centralized MCP (Model Context Protocol) server gateway using [Lasso MCP Gateway](https://github.com/lasso-security/mcp-gateway).

Runs as a Docker container on Unraid, accessible to all AI clients (Codex, Claude Code, Claude Desktop) via Tailscale.

## Quick Start

```bash
# 1. Clone to Unraid
git clone <repo-url> && cd mcp-gateway

# 2. Copy and fill in secrets
cp .env.example .env
# Edit .env with real credentials

# 3. Build and run
docker compose up -d --build

# 4. Check status
docker compose logs -f mcp-gateway
```

## Connectivity

* **Host**: `tower` (LAN: `10.0.0.37` | Tailscale: `100.94.202.54`)
* **Port**: `8484`
* **SSE Endpoint**: `http://<host>:8484/sse`

### Connect via Codex / Claude Desktop

To connect your Mac client to this gateway, edit your configuration file (e.g., `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "unraid-gateway": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sse",
        "http://10.0.0.37:8484/sse"
      ]
    }
  }
}
```

> **Note**: Replace `10.0.0.37` with the Tailscale IP (`100.94.202.54`) if connecting remotely.

## Architecture

```
Client (Mac Mini) ──Streamable HTTP via Tailscale──▶ Lasso Gateway (Unraid)
                                                          │
                                                    ┌─────┼─────┐
                                                    ▼     ▼     ▼
                                               monarch  tick   fabric*
                                               money    tick   mcp*

* fabric-mcp: future, requires Tailscale bridge to Mac Mini Fabric API
```

## Project Structure

```
├── docker-compose.yml     # Main compose stack
├── Dockerfile             # Gateway + MCP servers image
├── mcp.json               # Server configurations for Lasso
├── .env.example           # Template (safe to commit)
├── .env                   # Real secrets (GITIGNORED)
├── .gitignore
├── configs/               # Per-server config overrides
├── docs/                  # Documentation
└── README.md
```

## Security

* Credentials stored in `.env` on gateway host only.
* Lasso `basic` plugin: masks sensitive tokens in responses.
* Lasso `presidio` plugin: PII detection and redaction.
* **DNS Rebinding**: A monkeypatch in `http_entrypoint.py` allows connections from Tailscale/LAN IPs.
