#!/usr/bin/env python3
"""
generate_mappings.py
Input: ranges.csv (from generate_port_ranges_fixed.py)
Assign two chunks per VM (100 ports each).
Outputs: mappings.csv with one line per external port:
subdomain,protocol,external_port,internal_ip,internal_port
"""
import csv
from pathlib import Path

RANGES_FILE = "ranges.csv"
OUT_FILE = "mappings.csv"
VM_PREFIX = "vm"  # will produce vm-1, vm-2, etc.
ZONE = "vm.ai360api.com"  # base domain; final pattern will be vm-1.vm.ai360api.com, vm-2.vm.ai360api.com, etc.

# Placeholder internal IPs: you MUST replace these with real internal IPs for your containers/VMs
# Example: internal_ips = ["10.0.10.11", "10.0.10.12", ...]
internal_ips = []  # <-- REPLACE: provide list of internal IPs (one per VM)

def read_ranges():
    chunks=[]
    with open(RANGES_FILE, newline='') as f:
        r = csv.DictReader(f)
        for row in r:
            ports = [int(x) for x in row['ports'].split()]
            chunks.append(ports)
    return chunks

def assign_chunks_to_vms(chunks, internal_ips):
    if len(internal_ips)==0:
        raise SystemExit("Provide internal_ips list in the script before running.")
    # every VM gets 2 chunks => need 2*VMs <= len(chunks)
    vm_count = len(internal_ips)
    if 2*vm_count > len(chunks):
        raise SystemExit(f"Not enough chunks ({len(chunks)}) for {vm_count} VMs (need 2*VMs).")
    mappings = []
    for i, ip in enumerate(internal_ips, start=1):
        chunk1 = chunks[(i-1)*2]
        chunk2 = chunks[(i-1)*2 + 1]
        all_ports = chunk1 + chunk2
        subdomain = f"{VM_PREFIX}-{i}.{ZONE}"
        for p in all_ports:
            # map external p -> same internal port p by default (you can change)
            mappings.append([subdomain, "tcp", p, ip, p])
    return mappings

def write_mappings(mappings):
    with open(OUT_FILE, "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["subdomain","protocol","external_port","internal_ip","internal_port"])
        for row in mappings:
            w.writerow(row)
    print(f"Wrote {len(mappings)} mappings to {OUT_FILE}")

def main():
    chunks = read_ranges()
    # TODO: fill internal_ips
    # Example placeholder:
    # internal_ips = ["10.0.10.11","10.0.10.12", ..., up to vm count]
    # Place them above in script and rerun.
    mappings = assign_chunks_to_vms(chunks, internal_ips)
    write_mappings(mappings)

if __name__ == "__main__":
    main()
