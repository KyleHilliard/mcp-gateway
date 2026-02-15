# Lasso MCP Gateway — Reference Documentation

> Pulled from [lasso-security/mcp-gateway](https://github.com/lasso-security/mcp-gateway) on 2026-02-15.

## Overview

MCP Gateway is an advanced intermediary solution for Model Context Protocol (MCP) servers that centralizes and enhances your AI infrastructure.

MCP Gateway acts as an intermediary between LLMs and other MCP servers. It:

1. 📄 Reads server configurations from a `mcp.json` file
2. ⚙️ Manages the lifecycle of configured MCP servers
3. 🛡️ Intercepts requests and responses to sanitize sensitive information
4. 🔗 Provides a unified interface for discovering and interacting with all proxied MCPs
5. 🔒 **Security Scanner** — Analyzes server reputation and security risks before loading MCP servers

## Installation

```bash
pip install mcp-gateway
# With PII masking:
pip install "mcp-gateway[presidio]"
```

## CLI Arguments

| Flag | Description |
|---|---|
| `--mcp-json-path` | Path to `mcp.json` config file (required) |
| `-p`, `--plugin` | Enable plugin (repeatable): `basic`, `presidio`, `lasso`, `xetrack` |
| `--scan` | Enable security scanner |
| `--enable-guardrails` | (deprecated, use `--plugin`) |
| `--enable-tracing` | (deprecated, use `--plugin`) |

## Server Config (`mcp.json`)

```json
{
  "mcpServers": {
    "server-name": {
      "command": "command-to-run",
      "args": ["arg1", "arg2"],
      "env": {
        "KEY": "value"
      }
    }
  }
}
```

## Tools Exposed

- **`get_metadata`** — Provides information about all available proxied MCPs
- **`run_tool`** — Executes capabilities from any proxied MCP after sanitizing

## Plugins

### Guardrails

| Plugin | PII Masking | Token/Secret Masking | Custom Policy | Prompt Injection | Harmful Content |
|:---|:---|:---|:---:|:---:|:---:|
| `basic` | ❌ | ✅ | ❌ | ❌ | ❌ |
| `presidio` | ✅ | ❌ | ❌ | ❌ | ❌ |
| `lasso` | ✅ | ✅ | ✅ | ✅ | ✅ |

#### Basic (`-p basic`)

Masks: Azure client secrets, GitHub tokens/OAuth, GCP API keys, AWS access tokens, JWT tokens, GitLab session cookies, HuggingFace tokens, Microsoft Teams webhooks, Slack app tokens.

#### Presidio (`-p presidio`)

[Microsoft Presidio](https://microsoft.github.io/presidio/) — PII detection and anonymization:
Credit cards, IP addresses, email, phone, SSN, [and more](https://microsoft.github.io/presidio/supported_entities/).

#### Lasso (`-p lasso`)

Requires `LASSO_API_KEY` env var from [lasso.security](https://www.lasso.security/).
Full AI safety guardrails: PII, secrets, custom policies, prompt injection, harmful content.

### Tracing

#### Xetrack (`-p xetrack`)

Requires `pip install xetrack`. Logs tool calls to SQLite/DuckDB.
Env vars: `XETRACK_DB_PATH`, `XETRACK_LOGS_PATH`.

## Security Scanner

```bash
mcp-gateway --scan -p basic
```

- 🔍 Reputation analysis via Smithery, NPM, GitHub
- 🛡️ Tool description scanning for hidden instructions
- ⚡ Auto-blocks risky MCPs (threshold: 30)
- Status values: `"passed"`, `"blocked"`, `"skipped"`, `null`

## Architecture (Internal)

Built on FastMCP (official MCP Python SDK). Entry point is `mcp_gateway.gateway:main()` which calls `mcp.run()`. Default transport is stdio. Our `http_entrypoint.py` overrides transport to Streamable HTTP for remote access.

## License

MIT
