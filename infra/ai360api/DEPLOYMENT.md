# Deployment Guide for ai360api Infrastructure

## Prerequisites

- Access to AIGARDEN02 server (public IP: 51.91.105.16)
- Root or sudo privileges for iptables configuration
- Python 3.6+ installed
- Linux system with `ss` command available
- Internal VMs/containers with assigned private IPs
- Network interface name (default: `vmbr0`)

## Security Checklist

Before deployment, ensure:

- [ ] No credentials are committed to the repository
- [ ] Internal VM IPs are documented securely (not in git)
- [ ] Firewall rules are reviewed and approved
- [ ] Monitoring and alerting are configured
- [ ] Intrusion detection (fail2ban, etc.) is active
- [ ] Backup of current iptables rules is created
- [ ] Change management approval is obtained

## Deployment Steps

### Step 1: Generate Port Ranges

The first script identifies available ports in the 60000–61999 range, avoiding:
- Currently listening ports (detected via `ss -tuln`)
- Ephemeral port range (typically 32768–60999)

```bash
cd /home/runner/work/nervesys/nervesys/infra/ai360api
chmod +x generate_port_ranges_fixed.py
./generate_port_ranges_fixed.py
```

**Output**: `ranges.csv` containing 40 chunks of 50 ports each

**Validation**:
```bash
# Verify CSV file was created
ls -lh ranges.csv

# Check number of chunks (should be 40)
tail -n +2 ranges.csv | wc -l

# Preview first few chunks
head -5 ranges.csv
```

### Step 2: Configure Internal IPs

Edit `generate_mappings.py` to add your internal VM IP addresses:

```bash
vim generate_mappings.py
```

Locate the `internal_ips` list (around line 18) and populate it:

```python
# Example for 20 VMs:
internal_ips = [
    "10.0.10.11",
    "10.0.10.12",
    "10.0.10.13",
    # ... add up to 20 IPs (each VM gets 100 ports)
]
```

**Important**: 
- Maximum 20 VMs supported (40 chunks ÷ 2 chunks per VM = 20 VMs)
- Each VM receives 100 ports (2 × 50-port chunks)
- IPs must be reachable from AIGARDEN02

### Step 3: Generate Port Mappings

```bash
chmod +x generate_mappings.py
./generate_mappings.py
```

**Output**: `mappings.csv` with columns:
- `subdomain`: VM identifier (e.g., vm-1.vm.ai360api.com)
- `protocol`: tcp or udp
- `external_port`: Port on public IP (51.91.105.16)
- `internal_ip`: Target VM private IP
- `internal_port`: Target port on VM (same as external by default)

**Validation**:
```bash
# Check mappings file
ls -lh mappings.csv

# Count total port mappings (should be 100 × number of VMs)
tail -n +2 mappings.csv | wc -l

# Preview mappings for first VM
head -10 mappings.csv
```

### Step 4: Backup Current iptables Rules

**CRITICAL**: Always backup before modifying iptables:

```bash
# Save current rules
sudo iptables-save > /tmp/iptables-backup-$(date +%Y%m%d-%H%M%S).rules

# Verify backup
ls -lh /tmp/iptables-backup-*.rules
```

### Step 5: Test NAT Rules (Dry-Run)

Preview the iptables commands without applying them:

```bash
chmod +x nat-map.sh
./nat-map.sh --dry-run
```

**Review Output**:
- Check DNAT rules format: `iptables -t nat -A PREROUTING ...`
- Check FORWARD rules format: `iptables -A FORWARD ...`
- Verify public IP (51.91.105.16) and interface (vmbr0)
- Confirm internal IPs and ports are correct

### Step 6: Apply NAT Rules

Once dry-run output is verified:

```bash
sudo ./nat-map.sh --apply
```

**Verification**:
```bash
# List NAT PREROUTING rules
sudo iptables -t nat -L PREROUTING -n -v | grep OWALAI-AI360 | head -20

# List FORWARD rules
sudo iptables -L FORWARD -n -v | grep OWALAI-AI360 | head -20

# Count applied rules
sudo iptables -t nat -L PREROUTING -n | grep OWALAI-AI360 | wc -l
```

### Step 7: Test Connectivity

From an external machine, test connectivity to mapped ports:

```bash
# Test a specific port (replace 60000 with actual assigned port)
nc -zv 51.91.105.16 60000

# Or use telnet
telnet 51.91.105.16 60000
```

From internal VM, ensure services are listening:

```bash
# On the VM, check listening ports
ss -tuln | grep -E ":(60000|60001|60002)"
```

### Step 8: Make Rules Persistent

iptables rules are lost on reboot. To persist:

**Option A: Using iptables-persistent (Debian/Ubuntu)**
```bash
sudo apt-get install iptables-persistent
sudo netfilter-persistent save
```

**Option B: Manual save/restore**
```bash
# Save rules
sudo iptables-save > /etc/iptables/rules.v4

# Add to /etc/rc.local or systemd service to restore on boot
sudo iptables-restore < /etc/iptables/rules.v4
```

## Rollback Procedure

If issues arise, flush the rules created by this script:

```bash
sudo ./nat-map.sh --flush
```

Or restore from backup:

```bash
sudo iptables-restore < /tmp/iptables-backup-TIMESTAMP.rules
```

## Maintenance

### Updating Mappings

To modify port mappings:

1. Flush existing rules: `sudo ./nat-map.sh --flush`
2. Edit `generate_mappings.py` (update internal_ips)
3. Regenerate: `./generate_mappings.py`
4. Reapply: `sudo ./nat-map.sh --apply`

### Monitoring

Regularly monitor:
- Connection attempts: `sudo iptables -t nat -L PREROUTING -n -v`
- Failed connections: Check `/var/log/kern.log` or firewall logs
- VM availability: Ping internal IPs
- Port availability: Scan with `nmap` periodically

### Security Hardening

1. **Implement fail2ban**: Block repeated failed connection attempts
   ```bash
   sudo apt-get install fail2ban
   # Configure jail for common attacks
   ```

2. **Rate Limiting**: Add iptables rate limits to FORWARD rules
   ```bash
   iptables -A FORWARD -p tcp -m limit --limit 25/minute --limit-burst 100 -j ACCEPT
   ```

3. **Logging**: Enable logging for dropped packets
   ```bash
   iptables -A FORWARD -j LOG --log-prefix "DROPPED: " --log-level 4
   ```

4. **Regular Updates**: Keep VMs and host system updated
   ```bash
   sudo apt-get update && sudo apt-get upgrade
   ```

## Troubleshooting

### Ports Still Blocked

- Check if firewall (ufw, firewalld) is blocking: `sudo ufw status`
- Verify IP forwarding is enabled: `cat /proc/sys/net/ipv4/ip_forward` (should be `1`)
- Enable if needed: `sudo sysctl -w net.ipv4.ip_forward=1`

### Rules Not Applied

- Check iptables command output for errors
- Verify you have root/sudo privileges
- Ensure mappings.csv is properly formatted (no extra spaces, correct CSV structure)

### Internal VM Not Reachable

- Ping internal IP from AIGARDEN02: `ping <internal_ip>`
- Check VM firewall settings
- Verify VM network interface configuration

### Performance Issues

- Too many concurrent connections may overwhelm the system
- Consider reducing the number of exposed ports
- Implement connection limits per IP
- Use connection tracking limits: `sysctl net.netfilter.nf_conntrack_max`

## Best Practices

1. **Document Changes**: Keep a changelog of all modifications
2. **Test in Staging**: If possible, test on a non-production system first
3. **Gradual Rollout**: Start with a small subset of ports/VMs
4. **Monitor Continuously**: Set up alerts for unusual traffic patterns
5. **Regular Audits**: Review rules and mappings quarterly
6. **Principle of Least Privilege**: Only expose necessary ports

## Emergency Contacts

- Infrastructure Team: [Add contact info]
- Security Team: [Add contact info]
- On-Call Engineer: [Add contact info]

## References

- iptables documentation: https://netfilter.org/documentation/
- NAT configuration guide: https://www.netfilter.org/documentation/HOWTO/NAT-HOWTO.html
- Security best practices: https://www.cisecurity.org/

---

**Last Updated**: 2025-12-11  
**Version**: 1.0  
**Maintainer**: Infrastructure Team
