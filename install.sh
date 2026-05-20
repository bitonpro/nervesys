#!/bin/bash
# Sentinel (Branded Aster) One-Liner Installer for BitOn.Pro
set -e

echo "🚀 Starting Sentinel (Branded Aster) Installation..."

# 1. Prepare directory
mkdir -p /opt/bitonpro
cd /opt/bitonpro

# 2. Clone fresh Aster
rm -rf sentinel-mcp
git clone https://github.com/satyajiit/aster-mcp.git sentinel-mcp
cd sentinel-mcp

# 3. Apply BitOn.Pro Sentinel Rebranding
cat << 'PYEOF' > /tmp/rebrand.py
import os
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
        if file != "LICENSE" and file.endswith((".md", ".json", ".ts", ".vue", ".kt", ".xml", ".gradle", ".html", ".css")):
            p = os.path.join(root, file)
            try:
                with open(p, 'r', encoding='utf-8') as f: c = f.read()
                nc = c
                for k, v in replacements.items(): nc = nc.replace(k, v)
                if c != nc:
                    with open(p, 'w', encoding='utf-8') as f: f.write(nc)
            except: pass
PYEOF
python3 /tmp/rebrand.py

# 4. Fix bin execution path in package.json to match rebranded name
sed -i 's/"aster":/"sentinel":/g' mcp/package.json 2>/dev/null || true

# 5. Install and Build the MCP Server
cd mcp
echo "📦 Installing dependencies..."
npm install
echo "🔨 Building Sentinel..."
npm run build

# 6. Link globally so you can use it anywhere
sudo npm link

echo "✅ Sentinel Installed successfully!"
echo "👉 To start your branded server, type: sentinel start"
