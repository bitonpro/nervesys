# ai360api Infrastructure Tools

## Overview

This directory contains scripts and templates to support port allocation and NAT mapping for the ai360api infrastructure on AIGARDEN02 (public IP: 51.91.105.16).

The toolset allocates 2,000 ports in the range 60000–61999 into 40 chunks of 50 ports each, and maps them to internal VMs/containers. Each VM receives 100 ports (2 chunks).

## Purpose

- **Port Range Allocation**: Generate non-overlapping port ranges that avoid system listening ports and ephemeral port ranges
- **VM Mapping**: Assign port chunks to individual VMs with corresponding internal IPs
- **NAT Configuration**: Apply iptables DNAT rules to route external traffic to internal VMs

## Files

- **generate_port_ranges_fixed.py**: Generates `ranges.csv` with 40 chunks of 50 ports each (2,000 total ports)
- **generate_mappings.py**: Reads `ranges.csv` and produces `mappings.csv` mapping external ports to internal VM IPs
- **nat-map.sh**: Bash script to apply/remove iptables NAT rules based on `mappings.csv`
- **DEPLOYMENT.md**: Detailed deployment instructions and operational procedures
- **.gitignore**: Excludes credentials and generated CSV files from git

## Security Warnings

⚠️ **CRITICAL SECURITY NOTES**:

1. **NO SECRETS IN REPOSITORY**: This repository contains NO credentials, passwords, or sensitive authentication data. All placeholders must be filled by operators during deployment.

2. **Honeypot Consideration**: When deploying port mappings at scale (2,000 ports), be aware that open ports may attract automated scanning and exploitation attempts. Implement appropriate security measures:
   - Use fail2ban or similar intrusion prevention
   - Monitor access logs continuously
   - Implement rate limiting
   - Use strong authentication on all exposed services
   - Keep all software updated

3. **Internal IP Placeholders**: The `internal_ips` list in `generate_mappings.py` is empty by default. Operators must fill this with actual internal VM IPs before running.

4. **Generated Files**: Files like `ranges.csv`, `mappings.csv`, and any credential files are automatically ignored by git (see `.gitignore`).

## Quick Start

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

```bash
# 1. Generate port ranges
cd infra/ai360api
./generate_port_ranges_fixed.py

# 2. Edit generate_mappings.py to add internal IPs
# Edit the internal_ips list with your VM IPs

# 3. Generate mappings
./generate_mappings.py

# 4. Test NAT rules (dry-run)
./nat-map.sh --dry-run

# 5. Apply NAT rules (when ready)
sudo ./nat-map.sh --apply
```

## Support

For issues or questions, please open an issue in the repository or contact the infrastructure team.

## License

See repository root for license information.
