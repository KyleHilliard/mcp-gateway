# =============================================================================
# Lasso MCP Gateway + Streamable HTTP Transport
# Uses only the official MCP Python SDK — no third-party transport bridge
# =============================================================================

FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Lasso MCP Gateway with presidio plugin
RUN pip install --no-cache-dir \
    "mcp-gateway[presidio]"

# Install MCP servers (stdio subprocesses managed by Lasso)
# ticktick-mcp: available on PyPI
# monarch-mcp-server: NOT on PyPI, install from GitHub
RUN pip install --no-cache-dir \
    ticktick-mcp \
    "monarch-mcp-server @ git+https://github.com/robcerda/monarch-mcp-server.git"

# Copy our HTTP entrypoint wrapper
COPY http_entrypoint.py /app/http_entrypoint.py

# Create log directory
RUN mkdir -p /logs

EXPOSE 8484

# Run the HTTP wrapper instead of default stdio entrypoint
CMD ["python", "/app/http_entrypoint.py", \
    "--mcp-json-path", "/config/mcp.json", \
    "--plugin", "basic"]
