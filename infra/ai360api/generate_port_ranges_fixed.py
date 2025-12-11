#!/usr/bin/env python3
"""
generate_port_ranges_fixed.py
Produce chunks of 50 ports inside 60000-61999 avoiding listening ports and ephemeral range.
Output: ranges.csv (chunk_id,start_port,end_port,count,ports)
"""
import subprocess, re, csv
from pathlib import Path

MIN_PORT = 60000
MAX_PORT = 61999  # 2000 ports: 60000..61999
CHUNK = 50
TOTAL = 2000

def get_used_ports():
    used = set()
    try:
        out = subprocess.check_output(["ss", "-tuln"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return used
    for m in re.finditer(r":(\d+)\b", out):
        used.add(int(m.group(1)))
    return used

def read_ephemeral():
    try:
        with open("/proc/sys/net/ipv4/ip_local_port_range") as f:
            a,b = f.read().strip().split()
            return int(a), int(b)
    except:
        return 32768, 60999

def build_allowed(used, avoid_ephemeral=True):
    ports = set(range(MIN_PORT, MAX_PORT+1)) - used
    if avoid_ephemeral:
        e1,e2 = read_ephemeral()
        # if ephemeral overlaps our fixed range, exclude those ports
        forbidden = set(range(max(MIN_PORT,e1), min(MAX_PORT,e2)+1))
        ports = ports - forbidden
    return sorted(ports)

def find_contiguous_blocks(allowed, min_len):
    blocks=[]
    if not allowed: return blocks
    start=allowed[0]; prev=allowed[0]
    for p in allowed[1:]:
        if p==prev+1:
            prev=p
        else:
            if prev-start+1>=min_len: blocks.append((start,prev))
            start=p; prev=p
    if prev-start+1>=min_len: blocks.append((start,prev))
    return blocks

def allocate_blocks(blocks, chunk, needed):
    starts=[]
    for s,e in blocks:
        cur=s
        while cur+chunk-1<=e and len(starts)<needed:
            starts.append(cur)
            cur += chunk
        if len(starts)>=needed: break
    return [(st, st+chunk-1) for st in starts]

def main():
    used = get_used_ports()
    print(f"Detected {len(used)} used ports on system.")
    allowed = build_allowed(used, avoid_ephemeral=True)
    print(f"Candidate allowed ports count in {MIN_PORT}-{MAX_PORT}: {len(allowed)}")
    # need chunks
    chunks_needed = TOTAL // CHUNK
    blocks = find_contiguous_blocks(allowed, CHUNK)
    print(f"Found {len(blocks)} contiguous blocks >= {CHUNK}")
    allocations = allocate_blocks(blocks, CHUNK, chunks_needed)
    if len(allocations) < chunks_needed:
        # fallback: fill remaining from allowed by greedy picking non-overlapping segments
        flat_allowed = sorted(allowed)
        cur_idx = 0
        while len(allocations) < chunks_needed and cur_idx <= len(flat_allowed)-CHUNK:
            st = flat_allowed[cur_idx]
            # ensure contiguous CHUNK from this index
            seq = flat_allowed[cur_idx:cur_idx+CHUNK]
            if seq[-1] - seq[0] == CHUNK-1:
                allocations.append((seq[0], seq[-1]))
                cur_idx += CHUNK
            else:
                cur_idx += 1
    if len(allocations) < chunks_needed:
        print("ERROR: insufficient contiguous allocations; exiting.")
        return
    # write CSV
    out = Path("ranges.csv")
    with out.open("w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["chunk_id","start_port","end_port","count","ports"])
        for i,(s,e) in enumerate(allocations, start=1):
            ports = list(range(s,e+1))
            w.writerow([i,s,e,len(ports)," ".join(map(str,ports))])
    print(f"Wrote {len(allocations)} chunks to {out}")

if __name__ == "__main__":
    main()
