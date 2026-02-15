# =============================================================================
# Lasso MCP Gateway + MCP Servers
# Multi-stage build: installs gateway + all MCP server dependencies
# =============================================================================

FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Lasso MCP Gateway with presidio plugin for PII masking
RUN pip install --no-cache-dir \
    "mcp-gateway[presidio]"

# Install MCP servers that will run as stdio subprocesses
# ticktick-mcp: available on PyPI
# monarch-mcp-server: NOT on PyPI, install from GitHub
RUN pip install --no-cache-dir \
    ticktick-mcp \
    "monarch-mcp-server @ git+https://github.com/robcerda/monarch-mcp-server.git"

# Create log directory
RUN mkdir -p /logs

# Expose gateway port
EXPOSE 3000

# Default entrypoint — args passed from docker-compose command
ENTRYPOINT ["mcp-gateway"]
