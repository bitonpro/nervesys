# Firewall Architecture — yohay.ai Fleet

> Last updated: 2026-06-26 | Author: Claude via bar@yohay.ai

## Overview: 3-Layer Defense

All production servers in yohay.ai fleet run a 3-layer firewall:

| Layer | Technology | Purpose | Management |
|-------|-----------|---------|------------|
| **1. Packet Filter** | nftables | Base networking rules, default DROP/ACCEPT | Direct SSH / ufw |
| **2. Behavioral IPS** | CrowdSec | Detects & blocks attack patterns (CVE, brute force, scans) | `cscli` via SSH |
| **3. Auth-based IPS** | Fail2ban | Blocks based on failed auth in app logs (SSH, Asterisk, etc.) | Fail2ban-UI v1.4.9 via SSH |

---

## Per-Server Status

### dgxmain (10.100.102.241 / 100.124.217.84)
- **nftables INPUT**: **policy DROP** 🔴
- **CrowdSec**: ✅ running with firewall bouncer
- **Fail2ban**: ✅ 2 jails (sshd, asterisk)
- **Management**: Fail2ban-UI via SSH on :22

**INPUT chain flow:**
```
INCOMING → KUBE-ROUTER → CROWDSEC_CHAIN → KUBE-PROXY → KUBE-NODEPORTS
→ KUBE-EXT-SERVICES → KUBE-FIREWALL → ts-input (Tailscale ACCEPT all)
→ LIBVIRT → ufw chains → POLICY DROP
```

**What's accepted:**
- All Tailscale traffic (iif tailscale0 accept)
- Kubernetes-managed ports
- libvirt DNS/DHCP on virbr0
- What ufw explicitly allows

**What's blocked:** Everything else (new ports need explicit ACCEPT)

| Server | nftables Policy | CrowdSec | Fail2ban | Jails |
|--------|----------------|----------|----------|-------|
| dgxmain | DROP | ✅ bouncer | ✅ | sshd, asterisk |
| dgxsec | DROP | ✅ | ✅ | sshd |
| arcai | DROP | ✅ bouncer | ✅ | sshd |
| gama-2 | ACCEPT | ✅ bouncer | ✅ | sshd |
| storai | ACCEPT | ❌ | ✅ | sshd |
| openwebui-vps | ? | ✅ | ✅ crazymax | sshd, asterisk? |
| 5060ihome | ? | ❌ | ✅ | sshd |

---

## Fail2ban-UI Architecture

- **Version**: v1.4.9 Swissmakers GmbH
- **Location**: Docker container `crazymax/fail2ban:latest` on openwebui-vps
- **Connection**: SSH to each server (port 22) to manage fail2ban directly
- **UI**: Web interface (exact port TBD — likely on openwebui-vps)
- **Servers managed**: dgxmain (confirmed), likely arcai, gama-2, storai, dgxsec

---

## Critical Rules

1. **dgxmain nftables policy DROP** — Any new service port needs explicit ACCEPT rule via `ufw allow` or direct nftables
2. **Tailscale bypasses everything** — `iif tailscale0 accept` is in ts-input chain, so Tailscale traffic is never blocked
3. **arcai blocks non-Tailscale SIP** — explicit `saddr != 100.0.0.0/8 tcp/udp dport 5060 drop`
4. **gama-2/storai fully open** — policy ACCEPT, no CrowdSec bouncer on storai
5. **CrowdSec on dgxmain**: Collections for apache2, nginx, sshd, base-http, http-cve, linux; Custom whitelist: `whitelist-cluster.yaml`
6. **Fail2ban asterisk jail**: Systemd backend watching `asterisk.service` journal; filter at `/etc/fail2ban/filter.d/asterisk.conf`

---

## Operational Commands

### Check nftables
```bash
sudo nft list table ip filter    # Full ruleset
sudo nft list chain ip filter INPUT  # INPUT chain only
```

### Check CrowdSec
```bash
sudo cscli decisions list        # Active bans
sudo cscli bouncers list         # Bouncer status
sudo cscli metrics               # Detection stats
```

### Check Fail2ban
```bash
sudo fail2ban-client status      # List all jails
sudo fail2ban-client status sshd # SSH jail detail
sudo fail2ban-client status asterisk  # Asterisk jail detail
```

### Add port (on DROP-policy servers)
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5060/udp
sudo ufw allow 10000:20000/udp
```

### Ban/Unban IP
```bash
# Fail2ban
sudo fail2ban-client set sshd banip 1.2.3.4
sudo fail2ban-client set sshd unbanip 1.2.3.4
# CrowdSec
sudo cscli decisions add --ip 1.2.3.4 --duration 24h
sudo cscli decisions delete --ip 1.2.3.4
```
