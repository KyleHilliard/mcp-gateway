# Unraid Deployment Guide

## Prerequisites

- Unraid 6.12+ with Docker Compose plugin installed
- Tailscale running on Unraid (IP: `100.94.202.54`)
- Git installed (via Nerd Tools or similar)

## Deployment Steps

### 1. Clone the repo on Unraid

```bash
# SSH into Unraid or use terminal in web UI
cd /mnt/user/appdata
git clone <repo-url> mcp-gateway
cd mcp-gateway
```

### 2. Set up credentials

```bash
cp .env.example .env
nano .env  # Fill in real values
```

### 3. Deploy via Docker Compose plugin

**Option A: Unraid Compose Manager UI**

1. Open Unraid web UI → Docker → Compose
2. Add new stack → point to `/mnt/user/appdata/mcp-gateway/docker-compose.yml`
3. Click "Compose Up"

**Option B: CLI**

```bash
cd /mnt/user/appdata/mcp-gateway
docker compose up -d --build
```

### 4. Verify

```bash
docker compose logs -f mcp-gateway
# Should see: Gateway started, servers loaded
```

### 5. Test connectivity from Mac Mini

```bash
# Via Tailscale
curl http://100.94.202.54:3000/health

# Via LAN
curl http://10.0.0.37:3000/health
```

## Updating

```bash
cd /mnt/user/appdata/mcp-gateway
git pull
docker compose up -d --build
```

## Networking

| Interface | Address | Use |
|---|---|---|
| LAN | `10.0.0.37:3000` | Local network access |
| Tailscale | `100.94.202.54:3000` | Remote / secure access |

## Storage

| Path | Purpose |
|---|---|
| `/mnt/user/appdata/mcp-gateway` | Project files |
| `/mnt/user/appdata/mcp-gateway/logs` | Gateway logs |

## Troubleshooting

```bash
# View logs
docker compose logs mcp-gateway

# Restart
docker compose restart mcp-gateway

# Rebuild after changes
docker compose up -d --build

# Check Tailscale connectivity
tailscale ping 100.86.129.100  # Mac Mini
```
