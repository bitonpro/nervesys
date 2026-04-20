# BitOn.Pro - Child Safety Auto Setup

## Quick Install
After MDM enrollment (`afw#setup`), open Termux on the child's phone and run:

```bash
curl -sL https://raw.githubusercontent.com/bitonpro/child-setup/main/setup.sh | bash
```

## What it does
1. Updates Termux packages
2. Sets up SSH access
3. Checks Tailscale VPN
4. Downloads & installs Aster MCP + Shizuku
5. Configures Aster to connect to gama-2 server
6. Sets up watchdog (heartbeat every 5 min)
7. Auto-start on boot
8. Reports setup completion to BitOn server

## APKs included
- `aster-mcp.apk` - Device control via MCP (v1.2.61)
- `shizuku.apk` - System permissions without root (v13.6.0)

## MDM Policy: child-safety
- Tailscale + Termux: force installed
- Location: always on
- Factory reset: blocked
- App install/uninstall: blocked
- Play Store: whitelist only

## Server
- BitOn API: https://enroll.yohay.ai
- Aster MCP: 100.122.148.62:5988
- OpenClaw: 100.122.148.62:18789

## Enterprise
Biton AI Fleet (LC04701uaw) - bar@yohay.ai
