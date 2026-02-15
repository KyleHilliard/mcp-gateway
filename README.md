# MCP Gateway

Centralized MCP (Model Context Protocol) server gateway using [Lasso MCP Gateway](https://github.com/lasso-security/mcp-gateway).

Runs as a Docker container on Unraid, accessible to all AI clients (Claude Code, Claude Desktop, Antigravity) via Tailscale.

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
│   ├── monarchmoney/
│   └── ticktick/
├── docs/
│   └── unraid-setup.md    # Unraid-specific deployment guide
└── README.md
```

## Servers

| Server | Description | Status |
|---|---|---|
| monarchmoney | Monarch Money personal finance API | ✅ Configured |
| ticktick | TickTick task management API | ✅ Configured |
| fabric-mcp | Fabric AI framework bridge | 🔜 Phase 2 (needs Tailscale) |

## Clients

All clients connect to `http://100.94.202.54:3000` (Tailscale) or `http://10.0.0.37:3000` (LAN).

| Client | Config Location |
|---|---|
| Claude Code | `~/.claude.json` |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Antigravity | TBD |

## Security

- Credentials stored in `.env` on gateway host only (never in client configs)
- Lasso `basic` plugin: masks sensitive tokens in responses
- Lasso `presidio` plugin: PII detection and redaction
- Network access via Tailscale (authenticated mesh)
