#!/bin/bash
set -e

WORK_DIR="/opt/bitonpro/work/sentinel-mcp"
REPO_URL="https://github.com/satyajiit/aster-mcp.git"

echo "Starting Sentinel Rebrand Bootstrap..."

phase_preflight() {
    echo "--- Phase 0: Preflight ---"
    command -v node >/dev/null 2>&1 || { echo >&2 "Node is required but not installed. Aborting."; return 1; }
    echo "Preflight complete."
}

phase_fork() {
    echo "--- Phase 1: Fork ---"
    mkdir -p /opt/bitonpro/work
    if [ ! -d "$WORK_DIR" ]; then
        git clone "$REPO_URL" "$WORK_DIR" || return 1
    fi
    cd "$WORK_DIR"
    git remote set-url origin https://gitea.yohay.ai/bitonpro/sentinel-mcp.git || git remote add origin https://gitea.yohay.ai/bitonpro/sentinel-mcp.git
    echo "Fork complete."
}

phase_rebrand() {
    echo "--- Phase 2-6: Rebrand ---"
    if [ ! -d "$WORK_DIR" ]; then echo "Run fork first."; return 1; fi
    cd "$WORK_DIR"

    # Python script for safe rebranding
    cat << 'PYEOF' > /tmp/rebrand.py
import os, json

replacements = {
    "Aster": "Sentinel",
    "aster-mcp": "@bitonpro/sentinel-mcp",
    "aster_mcp": "sentinel_mcp",
    "aster.theappstack.in": "sentinel.bitonpro.ai",
    "satyajiit/aster-mcp": "bitonpro/sentinel-mcp",
    "Satyajit Pradhan": "BitOn.Pro"
}

for root, dirs, files in os.walk("."):
    if "node_modules" in root or ".git" in root: continue
    for file in files:
        if file == "LICENSE": continue
        if file.endswith((".md", ".json", ".ts", ".vue", ".kt", ".xml", ".gradle", ".html", ".css")):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
                new_content = content
                for k, v in replacements.items(): new_content = new_content.replace(k, v)
                if content != new_content:
                    with open(filepath, 'w', encoding='utf-8') as f: f.write(new_content)
            except Exception as e:
                pass
PYEOF
    python3 /tmp/rebrand.py
    echo "Rebrand complete."
}

phase_verify() {
    echo "--- Phase 7: Verify ---"
    cd "$WORK_DIR" || return 1
    echo "Checking for leftovers..."
    grep -ril "aster" . --exclude-dir=node_modules --exclude-dir=.git --exclude=LICENSE || echo "Clean!"
}

case "$1" in
    preflight) phase_preflight ;;
    fork) phase_fork ;;
    rebrand) phase_rebrand ;;
    verify) phase_verify ;;
    all)
        phase_preflight
        phase_fork
        phase_rebrand
        phase_verify
        ;;
    *) echo "Usage: $0 {preflight|fork|rebrand|verify|all}" ;;
esac
