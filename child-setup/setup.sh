#!/bin/bash
# BitOn.Pro Child Safety - Auto Setup Script
# Run on child's phone via Termux after MDM enrollment
# Usage: curl -sL https://raw.githubusercontent.com/bitonpro/child-setup/main/setup.sh | bash

set -e
echo "======================================"
echo "  BitOn.Pro - Child Safety Setup"
echo "  Automated by Yohay AI Cloud"
echo "======================================"

REPO="https://github.com/bitonpro/child-setup"
RAW="https://raw.githubusercontent.com/bitonpro/child-setup/main"
SETUP_DIR="$HOME/biton-setup"
ASTER_SERVER="100.122.148.62"  # gama-2 via Tailscale
ASTER_PORT="5988"

mkdir -p "$SETUP_DIR/apks"
cd "$SETUP_DIR"

# ===== 1. UPDATE TERMUX =====
echo "[1/8] Updating Termux..."
pkg update -y && pkg upgrade -y 2>/dev/null
pkg install -y wget curl openssh python git termux-api 2>/dev/null

# ===== 2. SETUP SSH =====
echo "[2/8] Setting up SSH..."
mkdir -p ~/.ssh
if [ ! -f ~/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "child-$(hostname)"
fi
# Start SSH server
sshd 2>/dev/null || true
echo "SSH key: $(cat ~/.ssh/id_ed25519.pub)"

# ===== 3. TAILSCALE =====
echo "[3/8] Checking Tailscale..."
if ! command -v tailscale &>/dev/null; then
    echo "Tailscale should be installed by MDM. Checking..."
    if pm list packages 2>/dev/null | grep -q tailscale; then
        echo "Tailscale app installed via MDM"
    else
        echo "WARNING: Tailscale not found. Install from Play Store."
    fi
else
    tailscale status 2>/dev/null | head -5
fi

# ===== 4. DOWNLOAD APKS =====
echo "[4/8] Downloading APKs..."
cd "$SETUP_DIR/apks"

# Aster MCP
if [ ! -f aster-mcp.apk ]; then
    echo "  Downloading Aster MCP..."
    wget -q "${RAW}/apks/aster-mcp.apk" -O aster-mcp.apk 2>/dev/null || \
    curl -sL "https://github.com/satyajiit/aster-mcp/releases/latest/download/app-release.apk" -o aster-mcp.apk
fi

# Shizuku
if [ ! -f shizuku.apk ]; then
    echo "  Downloading Shizuku..."
    wget -q "${RAW}/apks/shizuku.apk" -O shizuku.apk 2>/dev/null || \
    curl -sL "https://github.com/RikkaApps/Shizuku/releases/latest/download/shizuku-v13.6.0.r1086.2650830c-release.apk" -o shizuku.apk
fi

echo "  APKs ready:"
ls -lh "$SETUP_DIR/apks/"

# ===== 5. INSTALL APKS =====
echo "[5/8] Installing APKs..."
# Try installing via Shizuku/pm if we have permissions
for apk in aster-mcp.apk shizuku.apk; do
    echo "  Installing $apk..."
    pm install -r "$SETUP_DIR/apks/$apk" 2>/dev/null && echo "  OK: $apk" || \
    termux-open "$SETUP_DIR/apks/$apk" 2>/dev/null && echo "  Opened: $apk (manual install)" || \
    echo "  SKIP: $apk (need manual install or ADB)"
done

# ===== 6. CONFIGURE ASTER =====
echo "[6/8] Configuring Aster..."
# Create Aster config to connect to gama-2
mkdir -p "$SETUP_DIR/config"
cat > "$SETUP_DIR/config/aster-config.json" << ASTEREOF
{
    "server": "ws://${ASTER_SERVER}:${ASTER_PORT}",
    "autoConnect": true,
    "features": {
        "notifications": true,
        "sms": true,
        "location": true,
        "screenshots": true,
        "accessibility": true
    },
    "webhooks": {
        "openclaw": "http://${ASTER_SERVER}:18789/hooks/agent",
        "biton": "http://${ASTER_SERVER}:9098/api/webhook/event"
    }
}
ASTEREOF
echo "  Aster config written"

# ===== 7. SETUP WATCHDOG =====
echo "[7/8] Setting up watchdog..."
cat > "$SETUP_DIR/watchdog.sh" << 'WATCHEOF'
#!/bin/bash
# BitOn.Pro Watchdog - keeps services running
while true; do
    # Check Tailscale
    if ! tailscale status &>/dev/null; then
        echo "$(date): Tailscale down, restarting..." >> ~/biton-setup/watchdog.log
        am start -n com.tailscale.ipn/.IPNActivity 2>/dev/null
    fi
    # Check Aster
    if ! pm list packages 2>/dev/null | grep -q aster; then
        echo "$(date): Aster not found" >> ~/biton-setup/watchdog.log
    fi
    # Check SSH
    if ! pgrep sshd &>/dev/null; then
        sshd 2>/dev/null
    fi
    # Report to server
    curl -s -X POST "http://100.122.148.62:9098/api/webhook/event" \
        -H "Content-Type: application/json" \
        -d "{\"type\":\"heartbeat\",\"device_id\":\"$(hostname)\",\"battery\":\"$(termux-battery-status 2>/dev/null | python3 -c 'import json,sys;print(json.load(sys.stdin).get(\"percentage\",\"?\"))' 2>/dev/null || echo '?')\"}" \
        -u admin:Biton24680 2>/dev/null
    sleep 300
done
WATCHEOF
chmod +x "$SETUP_DIR/watchdog.sh"

# Auto-start watchdog on Termux boot
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/biton-start.sh << 'BOOTEOF'
#!/bin/bash
termux-wake-lock
sshd
nohup ~/biton-setup/watchdog.sh &
BOOTEOF
chmod +x ~/.termux/boot/biton-start.sh

# ===== 8. REPORT =====
echo "[8/8] Reporting to server..."
DEVICE_INFO=$(termux-telephony-deviceinfo 2>/dev/null || echo '{}')
curl -s -X POST "http://${ASTER_SERVER}:9098/api/webhook/event" \
    -H "Content-Type: application/json" \
    -d "{\"type\":\"device_setup_complete\",\"device_id\":\"$(hostname)\",\"info\":${DEVICE_INFO}}" \
    -u admin:Biton24680 2>/dev/null

echo ""
echo "======================================"
echo "  Setup Complete!"
echo "======================================"
echo "  Aster config: $SETUP_DIR/config/aster-config.json"
echo "  Watchdog: running every 5 min"
echo "  SSH: $(whoami)@$(hostname)"
echo ""
echo "  NEXT STEPS:"
echo "  1. Open Shizuku app and activate"
echo "  2. Open Aster app and connect to server"
echo "  3. Grant Accessibility permissions to Aster"
echo "======================================"
