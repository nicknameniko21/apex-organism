#!/bin/bash
# ============================================
# APEX ORGANISM v0.1 - Oracle Cloud Deployment
# ============================================
# Run this script on your Oracle Cloud VM after SSH-ing in.
# Usage: bash deploy_oracle.sh
#
# This script will:
# 1. Update the system
# 2. Install Python 3.11+ and dependencies
# 3. Set up APEX Organism
# 4. Configure firewall rules
# 5. Create a systemd service for auto-start
# 6. Start the APEX dashboard
# ============================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════╗"
echo "║     APEX ORGANISM v0.1 - Deployment Script    ║"
echo "╚═══════════════════════════════════════════════╝"
echo -e "${NC}"

# ─── Step 1: System Update ──────────────────────────────────────
echo -e "${YELLOW}[1/6] Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# ─── Step 2: Install Python 3.11+ ──────────────────────────────
echo -e "${YELLOW}[2/6] Installing Python and dependencies...${NC}"
sudo apt install -y python3 python3-pip python3-venv git curl wget

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}  Python version: ${PYTHON_VERSION}${NC}"

# ─── Step 3: Set up APEX ────────────────────────────────────────
echo -e "${YELLOW}[3/6] Setting up APEX Organism...${NC}"

# Create project directory
APEX_DIR="$HOME/apex_organism"
if [ ! -d "$APEX_DIR" ]; then
    echo "  Creating APEX directory at $APEX_DIR"
    mkdir -p "$APEX_DIR"
fi

# Copy files (assumes you've uploaded them via SCP)
echo "  Checking for APEX files..."
if [ ! -f "$APEX_DIR/apex_main.py" ]; then
    echo -e "${RED}  APEX files not found in $APEX_DIR${NC}"
    echo "  Please upload the APEX codebase first:"
    echo "    scp -r apex_organism/* ubuntu@YOUR_SERVER_IP:~/apex_organism/"
    echo ""
    echo "  Or clone from your repository:"
    echo "    git clone YOUR_REPO_URL $APEX_DIR"
    exit 1
fi

# Create virtual environment
echo "  Creating Python virtual environment..."
cd "$APEX_DIR"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "  Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}  Dependencies installed successfully!${NC}"

# ─── Step 4: Configure Firewall ─────────────────────────────────
echo -e "${YELLOW}[4/6] Configuring firewall rules...${NC}"

# Open required ports via iptables
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8080 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT

# Persist iptables rules
sudo apt install -y iptables-persistent
sudo netfilter-persistent save

echo -e "${GREEN}  Ports 80, 443, 8080 opened.${NC}"

# ─── Step 5: Create Systemd Service ─────────────────────────────
echo -e "${YELLOW}[5/6] Creating systemd service for auto-start...${NC}"

sudo tee /etc/systemd/system/apex.service > /dev/null << EOF
[Unit]
Description=APEX Organism v0.1 Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APEX_DIR
ExecStart=$APEX_DIR/venv/bin/python $APEX_DIR/apex_main.py --dashboard
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable apex.service

echo -e "${GREEN}  Systemd service created and enabled.${NC}"

# ─── Step 6: Start APEX ─────────────────────────────────────────
echo -e "${YELLOW}[6/6] Starting APEX Organism...${NC}"

sudo systemctl start apex.service

# Wait a moment for startup
sleep 3

# Check status
if sudo systemctl is-active --quiet apex.service; then
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║   APEX ORGANISM IS ALIVE AND RUNNING!                     ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║   Dashboard: http://$(curl -s ifconfig.me):8080            ${NC}"
    echo -e "${GREEN}║   API:       http://$(curl -s ifconfig.me):8080/api/status ${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║   Manage:                                                 ║${NC}"
    echo -e "${GREEN}║     sudo systemctl status apex                            ║${NC}"
    echo -e "${GREEN}║     sudo systemctl restart apex                           ║${NC}"
    echo -e "${GREEN}║     sudo journalctl -u apex -f                            ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}  APEX failed to start. Check logs:${NC}"
    echo "    sudo journalctl -u apex -n 50"
fi
