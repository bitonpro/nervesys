#!/bin/bash
# Install MCP Firewall Server on Linux
set -e

echo "=== Installing mcp-fw ==="

# Install Python deps
pip3 install mcp

# Copy server
mkdir -p /opt/mcp-fw
cp server.py /opt/mcp-fw/
chmod +x /opt/mcp-fw/server.py

echo ""
echo "✅ mcp-fw installed at /opt/mcp-fw/server.py"
echo ""
echo "Add to LibreChat librechat.yaml:"
echo ""
echo 'mcp_servers:'
echo '  mcp-fw:'
echo '    type: stdio'
echo '    command: python3'
echo '    args: ["/opt/mcp-fw/server.py"]'
echo '    env:'
echo '      PATH: /usr/local/bin:/usr/bin:/bin'
