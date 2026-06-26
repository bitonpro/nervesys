#!/usr/bin/env python3
"""
MCP Firewall Server — yohay.ai Fleet
Manages all 3 firewall layers across the fleet:
  1. nftables (packet filter)
  2. CrowdSec (behavioral IPS)
  3. Fail2ban (auth-based IPS)

Connects via SSH (Tailscale) to all production servers.
"""

import json
import subprocess
import sys
from typing import Any

# MCP SDK
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationCapabilities
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# --- SERVER DEFINITIONS ---
SERVERS = {
    "dgxmain":  {"host": "100.124.217.84", "user": "bitonx", "desc": "DGX Main - ARM64, K8s, NVIDIA"},
    "dgxsec":   {"host": "100.78.185.72",  "user": "bitonx", "desc": "DGX Sec - LibreChat, n8n, OpenHands"},
    "arcai":    {"host": "100.81.132.108", "user": "bitonx", "desc": "Arcai - OVH SBG, Fail2ban-UI"},
    "gama-2":   {"host": "100.122.148.62", "user": "bitbit", "desc": "GAMA-2 - OVH GRA, auth.yohay.ai"},
    "storai":   {"host": "100.92.89.14",   "user": "bitonx", "desc": "STORAI - OVH LIM, Aster MCP"},
    "openwebui-vps": {"host": "100.115.82.76", "user": "bitonx", "desc": "OpenWebUI VPS - Kortix Suna"},
    "5060ihome": {"host": "100.90.81.47",  "user": "bitonx", "desc": "5060ihome - SIP Server, RTX 5060Ti"},
}

# SSH settings
SSH_OPTS = "-o StrictHostKeyChecking=no -o ConnectTimeout=5 -o LogLevel=ERROR"

# --- SSH EXECUTION ---
def ssh_run(server: str, command: str, sudo: bool = True, timeout: int = 15) -> dict:
    """Run command on server via SSH"""
    if server not in SERVERS:
        return {"ok": False, "error": f"Unknown server: {server}"}
    
    s = SERVERS[server]
    prefix = "sudo " if sudo else ""
    ssh_cmd = f"ssh {SSH_OPTS} {s['user']}@{s['host']} '{prefix}{command}'"
    
    try:
        r = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return {
            "ok": r.returncode == 0,
            "rc": r.returncode,
            "stdout": r.stdout.strip(),
            "stderr": r.stderr.strip(),
            "server": server,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"SSH timeout after {timeout}s", "server": server}
    except Exception as e:
        return {"ok": False, "error": str(e), "server": server}


# --- APP ---
app = Server("mcp-fw")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="fw_fleet_status",
            description="Full firewall status across all fleet servers (3 layers)",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="fw_server_status",
            description="Full firewall status for one server: nftables policy, CrowdSec bouncer, Fail2ban jails, active bans",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "enum": list(SERVERS.keys()),
                        "description": "Server to query"
                    }
                },
                "required": ["server"]
            }
        ),
        Tool(
            name="fw_nft_rules",
            description="Show nftables rules for a server (INPUT chain, policy, specific rules)",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "enum": list(SERVERS.keys())
                    }
                },
                "required": ["server"]
            }
        ),
        Tool(
            name="fw_crowdsec_status",
            description="CrowdSec status: bouncers, active decisions, collections, scenarios",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "enum": list(SERVERS.keys())
                    }
                },
                "required": ["server"]
            }
        ),
        Tool(
            name="fw_fail2ban_status",
            description="Fail2ban status: jails, banned IPs, filter rules",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "enum": list(SERVERS.keys())
                    }
                },
                "required": ["server"]
            }
        ),
        Tool(
            name="fw_check_port",
            description="Check if a port is open on a server (checks nftables rules)",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {"type": "string", "enum": list(SERVERS.keys())},
                    "port": {"type": "integer", "description": "Port number"},
                    "proto": {"type": "string", "enum": ["tcp", "udp"], "default": "tcp"}
                },
                "required": ["server", "port"]
            }
        ),
        Tool(
            name="fw_add_port",
            description="Open a port via ufw on a server (use on DROP-policy servers)",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {"type": "string", "enum": list(SERVERS.keys())},
                    "port": {"type": "integer"},
                    "proto": {"type": "string", "enum": ["tcp", "udp"], "default": "tcp"},
                    "comment": {"type": "string", "description": "Rule comment (optional)"}
                },
                "required": ["server", "port"]
            }
        ),
        Tool(
            name="fw_remove_port",
            description="Close a port via ufw on a server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {"type": "string", "enum": list(SERVERS.keys())},
                    "port": {"type": "integer"},
                    "proto": {"type": "string", "enum": ["tcp", "udp"], "default": "tcp"}
                },
                "required": ["server", "port"]
            }
        ),
        Tool(
            name="fw_ban_ip",
            description="Manually ban an IP across all 3 layers or specific layer",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {"type": "string", "enum": list(SERVERS.keys())},
                    "ip": {"type": "string", "description": "IP address to ban"},
                    "layer": {
                        "type": "string",
                        "enum": ["all", "nftables", "crowdsec", "fail2ban"],
                        "default": "all",
                        "description": "Which layer to use"
                    },
                    "jail": {
                        "type": "string",
                        "default": "sshd",
                        "description": "Fail2ban jail (only for fail2ban layer)"
                    },
                    "duration": {
                        "type": "string",
                        "default": "24h",
                        "description": "Ban duration (for CrowdSec)"
                    }
                },
                "required": ["server", "ip"]
            }
        ),
        Tool(
            name="fw_unban_ip",
            description="Unban an IP across all layers",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {"type": "string", "enum": list(SERVERS.keys())},
                    "ip": {"type": "string"},
                    "layer": {"type": "string", "enum": ["all", "nftables", "crowdsec", "fail2ban"], "default": "all"}
                },
                "required": ["server", "ip"]
            }
        ),
        Tool(
            name="fw_list_servers",
            description="List all servers with firewall summary (policy, CrowdSec, Fail2ban)",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    
    if name == "fw_list_servers":
        lines = ["| Server | Policy | CrowdSec | Fail2ban |", "|--------|--------|----------|----------|"]
        for srv in SERVERS:
            r = ssh_run(srv, "nft list table ip filter 2>/dev/null | head -3; systemctl is-active crowdsec fail2ban 2>/dev/null", timeout=8)
            policy = "unknown"
            crowdsec = "❌"
            f2b = "❌"
            if r.get("ok"):
                out = r.get("stdout", "")
                if "policy drop" in out: policy = "DROP 🔴"
                elif "policy accept" in out: policy = "ACCEPT 🟢"
                if "active" in out and "crowdsec" in out.lower(): crowdsec = "✅"
                if "fail2ban" in out and "active" in out: f2b = "✅"
            lines.append(f"| {srv} | {policy} | {crowdsec} | {f2b} |")
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "fw_fleet_status":
        lines = ["# 🔥 yohay.ai Fleet — Full Firewall Status\n"]
        for srv, info in SERVERS.items():
            lines.append(f"## {srv} ({info['desc']})")
            r = ssh_run(srv, "echo '---NFT---'; sudo nft list table ip filter 2>/dev/null | grep 'policy'; echo '---CS---'; systemctl is-active crowdsec 2>/dev/null; echo '---F2B---'; sudo fail2ban-client status 2>/dev/null | tail -5", timeout=10)
            lines.append(f"```\n{r.get('stdout', r.get('error', 'timeout'))}\n```\n---")
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "fw_server_status":
        srv = arguments["server"]
        info = SERVERS[srv]
        lines = [f"# Firewall Status: {srv}", f"Description: {info['desc']}", f"Host: {info['host']}", ""]
        
        # NFT
        r1 = ssh_run(srv, "sudo nft list table ip filter 2>/dev/null | grep -E 'hook input|policy'")
        lines.append(f"## nftables\n```\n{r1.get('stdout', r1.get('error', 'N/A'))}\n```")
        
        # CrowdSec
        r2 = ssh_run(srv, "systemctl is-active crowdsec 2>/dev/null; cscli decisions list 2>/dev/null | head -10; cscli bouncers list 2>/dev/null | head -10")
        lines.append(f"## CrowdSec\n```\n{r2.get('stdout', r2.get('error', 'N/A'))}\n```")
        
        # Fail2ban
        r3 = ssh_run(srv, "sudo fail2ban-client status 2>/dev/null; sudo fail2ban-client status sshd 2>/dev/null | tail -10")
        lines.append(f"## Fail2ban\n```\n{r3.get('stdout', r3.get('error', 'N/A'))}\n```")
        
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "fw_nft_rules":
        srv = arguments["server"]
        r = ssh_run(srv, "sudo nft list table ip filter 2>/dev/null | head -80")
        return [TextContent(type="text", text=f"```\n{r.get('stdout', r.get('error', 'N/A'))}\n```")]

    elif name == "fw_crowdsec_status":
        srv = arguments["server"]
        r = ssh_run(srv, "echo '---BOUNCERS---'; sudo cscli bouncers list 2>/dev/null; echo '---DECISIONS---'; sudo cscli decisions list 2>/dev/null | head -20; echo '---COLLECTIONS---'; sudo cscli collections list 2>/dev/null")
        return [TextContent(type="text", text=f"```\n{r.get('stdout', r.get('error', 'N/A'))}\n```")]

    elif name == "fw_fail2ban_status":
        srv = arguments["server"]
        r = ssh_run(srv, "echo '=== JAILS ==='; sudo fail2ban-client status 2>/dev/null; for j in $(sudo fail2ban-client status 2>/dev/null | grep 'Jail list' | cut -d: -f2 | tr ',' ' '); do echo \"--- $j ---\"; sudo fail2ban-client status $j 2>/dev/null; done")
        return [TextContent(type="text", text=f"```\n{r.get('stdout', r.get('error', 'N/A'))}\n```")]

    elif name == "fw_check_port":
        srv = arguments["server"]
        port = arguments["port"]
        proto = arguments.get("proto", "tcp")
        r = ssh_run(srv, f"sudo nft list table ip filter 2>/dev/null | grep -E '(dport {port}|sport {port}).*{proto}'")
        found = r.get("stdout", "")
        if found:
            return [TextContent(type="text", text=f"✅ Port {port}/{proto} on {srv}: FOUND in nftables\n```\n{found}\n```")]
        else:
            return [TextContent(type="text", text=f"❌ Port {port}/{proto} on {srv}: NOT in nftables rules (policy DROP means BLOCKED)")]

    elif name == "fw_add_port":
        srv = arguments["server"]
        port = arguments["port"]
        proto = arguments.get("proto", "tcp")
        comment = arguments.get("comment", "")
        cmt = f" comment '{comment}'" if comment else ""
        r = ssh_run(srv, f"ufw allow {port}/{proto}{cmt} 2>&1")
        return [TextContent(type="text", text=f"Add port {port}/{proto} on {srv}:\n```\n{r.get('stdout', r.get('error', 'N/A'))}\n```")]

    elif name == "fw_remove_port":
        srv = arguments["server"]
        port = arguments["port"]
        proto = arguments.get("proto", "tcp")
        r = ssh_run(srv, f"ufw delete allow {port}/{proto} 2>&1")
        return [TextContent(type="text", text=f"Remove port {port}/{proto} on {srv}:\n```\n{r.get('stdout', r.get('error', 'N/A'))}\n```")]

    elif name == "fw_ban_ip":
        srv = arguments["server"]
        ip = arguments["ip"]
        layer = arguments.get("layer", "all")
        jail = arguments.get("jail", "sshd")
        duration = arguments.get("duration", "24h")
        results = []
        
        if layer in ("all", "nftables"):
            r = ssh_run(srv, f"nft add rule ip filter INPUT ip saddr {ip} drop 2>&1")
            results.append(f"nftables: {r.get('stdout', r.get('error'))}")
        if layer in ("all", "crowdsec"):
            r = ssh_run(srv, f"cscli decisions add --ip {ip} --duration {duration} 2>&1")
            results.append(f"CrowdSec: {r.get('stdout', r.get('error'))}")
        if layer in ("all", "fail2ban"):
            r = ssh_run(srv, f"fail2ban-client set {jail} banip {ip} 2>&1")
            results.append(f"Fail2ban({jail}): {r.get('stdout', r.get('error'))}")
        
        return [TextContent(type="text", text=f"Ban {ip} on {srv}:\n" + "\n".join(results))]

    elif name == "fw_unban_ip":
        srv = arguments["server"]
        ip = arguments["ip"]
        layer = arguments.get("layer", "all")
        results = []
        
        if layer in ("all", "nftables"):
            r = ssh_run(srv, f"nft delete rule ip filter INPUT ip saddr {ip} drop 2>&1")
            results.append(f"nftables: {r.get('stdout', r.get('error'))}")
        if layer in ("all", "crowdsec"):
            r = ssh_run(srv, f"cscli decisions delete --ip {ip} 2>&1")
            results.append(f"CrowdSec: {r.get('stdout', r.get('error'))}")
        if layer in ("all", "fail2ban"):
            for j in ["sshd", "asterisk"]:
                r = ssh_run(srv, f"fail2ban-client set {j} unbanip {ip} 2>&1")
                results.append(f"Fail2ban({j}): {r.get('stdout', r.get('error'))}")
        
        return [TextContent(type="text", text=f"Unban {ip} on {srv}:\n" + "\n".join(results))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
