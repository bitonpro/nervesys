---
name: ks7 Cluster Infrastructure Status
description: Current state of all servers, NFS mounts, services, and the np05j tablet in the ks7 cluster
type: project
---

## Cluster NFS Status (2026-04-10)

NFS Master: storai-1 (100.92.89.14) — was crashed (Address already in use), fixed by resetting nfsd kernel module.

| Server | NFS Mount | Notes |
|--------|-----------|-------|
| storai-1 | Master (local) | NFS server fixed and running |
| dgxmain | Mounted | OK |
| dgxsec | Mounted | OK |
| arcai | Mounted | OK |
| cloudai | Mounted | Uses public IP 162.19.126.209, TS node "cloudai" (100.115.88.71) offline 42d |
| gama-2 | Mounted | OK |
| 5060i | Mounted | Was unmounted, fixed + fstab updated |
| np05j (tablet) | rsync sync every 5min | Android/Termux, no NFS possible |
| mainh | DOWN | Offline 16 days in Tailscale (yohay5060, tagged-devices, relay only) |
| lapai | No SSH | Windows machine (lapyohayai), SSH timeout |

## gama-2 Services

- **Nginx** — main reverse proxy, 5 sites: FreePBX, Open WebUI, WordPress, Ollama, gama2
- **Caddy** — runs in Docker container `caddy-openclaw` on port 18800 (proxy to localhost:18789). Systemd caddy.service disabled (was conflicting).

## np05j Tablet (RedMagic NP05J)

- Android 15, Snapdragon, 22GB RAM, 933GB storage (825GB free)
- Termux SSH on port 8022 (user: yohay, pass: Odemo680)
- Python 3.13, Node.js 24, Rust 1.94, Claude Code installed
- Ubuntu 22 chroot available (start-ubuntu22.sh)
- ks7-memory synced via rsync cron job every 5 min
- Tailscale via Android app (no CLI in Termux), all servers pingable

**Why:** Central reference for cluster state so any chevruta instance can quickly understand what's up/down.
**How to apply:** Check this before running cross-server operations. Verify against live state if memory is old.
