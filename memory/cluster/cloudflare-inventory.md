# Cloudflare Inventory — ks7 Flow
**Updated: 2026-04-10**

## Account
- Email: meni@biton.pro
- Account ID: a182e69b048ebabb970ffd4e91cc741b

## Zones (3)
| Zone | ID | Status |
|------|----|--------|
| annima.ai | 75f4445149f471d0fd4d1c19991b585c | active |
| yohay.ai | 729e5afe1753f82f06c3416dc2e1aca0 | active |
| yohayai.com | dddc86f53a22fd8ac83e647c55ab04a7 | active |

## Tunnels (6 healthy)
| Name | Tunnel ID | Node |
|------|-----------|------|
| 5060i | cec8e581 | RTX 5060 Ti Home |
| arcai-wp | 8b6d2c04 | arcai 24TB |
| dgxmain | 95fae914 | DGX Spark A |
| dgxsec | b29902f6 | DGX Spark B |
| gama2 | e63f90be | cloudai OVH |
| storai-wp | 9f0c0d5d | storai NFS Master |
> Deleted 2026-04-10: arcai, gama, storai (replaced by -wp variants)

## Security (all zones)
- SSL: strict
- Always HTTPS: on
- Min TLS: 1.2 + TLS 1.3 enabled
- Security Level: high
- HSTS: 15552000s + includeSubdomains
- Automatic HTTPS rewrites: on

## Zero Trust Access (62 apps)
- Policy: allow meni@biton.pro + bar@yohay.ai
- Session: 24h
- All yohayai.com tunnel services protected

## Workers (3)
| Name | Route | Status |
|------|-------|--------|
| cliodai | *-cliodai.meni-a18.workers.dev | active, Zero Trust protected |
| ks7-gateway | app.yohay.ai/* | active (gateway worker) |
| llm-chat-app-template | (none) | deployed, no route |

## Workers KV (2)
- SAYBR HA HA HA [06b93b7a]
- SESSIONS [b2dcf438]

## D1 Databases (1)
- cloadai-database [17fe8589] (note: likely typo for cloudai-database)

## DNS Summary
### annima.ai
- Root → 185.230.63.107 (Wix)
- www → pointing.wixdns.net (Wix)

### yohay.ai
- Root → tunnel:gama2 (fixed 2026-04-10)
- app → tunnel:gama2 (fixed 2026-04-10, Worker route: ks7-gateway)
- ai, aster, ollama, openclaw → tunnel:5060i
- arc, ollama-arc → tunnel:arcai-wp
- gama, ollama-gama → tunnel:gama2 (fixed 2026-04-10)
- owui, stor → tunnel:storai-wp (fixed 2026-04-10)
- MX → Google Workspace

### yohayai.com
- Root → 185.230.63.107 (Wix)
- www → pointing.wixdns.net (Wix)
- deep → 100.65.11.71 (Tailscale direct)
- 59 subdomains → 6 tunnels (all Zero Trust protected)
- MX → Google Workspace

## Certs (earliest expiry)
- annima.ai universal: 2026-06-28
- yohay.ai advanced: 2026-05-15 (has newer certs 06-26, 07-08)
- yohayai.com universal: 2026-07-09
