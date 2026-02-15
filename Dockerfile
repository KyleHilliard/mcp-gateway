# =============================================================================
# Lasso MCP Gateway + Transport Bridge
# Installs: supergateway (stdio→HTTP bridge) + Lasso Gateway + MCP servers
# =============================================================================

FROM python:3.12-slim

WORKDIR /app

# System deps + Node.js for supergateway
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install supergateway (stdio → Streamable HTTP bridge)
RUN npm install -g supergateway

# Install Lasso MCP Gateway with presidio plugin
RUN pip install --no-cache-dir \
    "mcp-gateway[presidio]"

# Install MCP servers (stdio subprocesses managed by Lasso)
# ticktick-mcp: available on PyPI
# monarch-mcp-server: NOT on PyPI, install from GitHub
RUN pip install --no-cache-dir \
    ticktick-mcp \
    "monarch-mcp-server @ git+https://github.com/robcerda/monarch-mcp-server.git"

# Create log directory
RUN mkdir -p /logs

EXPOSE 8484

# supergateway wraps mcp-gateway stdio → Streamable HTTP on port 8484
CMD ["supergateway", \
    "--transport", "streamablehttp", \
    "--port", "8484", \
    "--", \
    "mcp-gateway", \
    "--mcp-json-path", "/config/mcp.json", \
    "--plugin", "basic"]
