#!/usr/bin/env bash
# Pi setup script for PhillyTrains.
# Run from the repo root after cloning: bash setup.sh
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info() { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$PROJECT_DIR/.venv"
PYTHON="$VENV/bin/python3"
PIP="$VENV/bin/pip"
SERVICE=phillytrains

info "Project: $PROJECT_DIR"
info "User:    $(whoami)"
echo ""

# ── 1. System packages ────────────────────────────────────────────────────────
info "Updating apt and installing build dependencies..."
sudo apt-get update -y -q
sudo apt-get install -y -q python3-dev python3-venv python3-pil cython3

# ── 2. Disable audio (must happen before the matrix will work) ────────────────
if [ -f /boot/firmware/config.txt ]; then
    CONFIG=/boot/firmware/config.txt   # Bookworm
else
    CONFIG=/boot/config.txt            # Bullseye and older
fi

if grep -q "dtparam=audio=on" "$CONFIG"; then
    sudo sed -i 's/dtparam=audio=on/dtparam=audio=off/' "$CONFIG"
    REBOOT_NEEDED=true
    info "Audio disabled in $CONFIG (was on)."
elif grep -q "dtparam=audio=off" "$CONFIG"; then
    REBOOT_NEEDED=false
    info "Audio already disabled."
else
    echo "dtparam=audio=off" | sudo tee -a "$CONFIG" > /dev/null
    REBOOT_NEEDED=true
    info "Added dtparam=audio=off to $CONFIG."
fi

# ── 3. Python virtual environment ─────────────────────────────────────────────
if [ ! -d "$VENV" ]; then
    info "Creating virtual environment..."
    python3 -m venv "$VENV"
else
    info "Virtual environment already exists, skipping."
fi

info "Installing Python dependencies..."
"$PIP" install --upgrade pip -q
"$PIP" install -r "$PROJECT_DIR/requirements.txt" -q

# ── 4. rpi-rgb-led-matrix ─────────────────────────────────────────────────────
info "Installing rpi-rgb-led-matrix (compiles C++ — may take a few minutes)..."
"$PIP" install git+https://github.com/hzeller/rpi-rgb-led-matrix

info "Verifying rgbmatrix import..."
"$PYTHON" -c "from rgbmatrix import RGBMatrix; print('  rgbmatrix OK')"

# ── 5. Systemd service ────────────────────────────────────────────────────────
info "Installing systemd service..."
sudo tee /etc/systemd/system/${SERVICE}.service > /dev/null <<EOF
[Unit]
Description=PhillyTrains LED Display
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
ExecStart=$PYTHON -u $PROJECT_DIR/main.py
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE"
info "Service installed and enabled (not yet started)."

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════"
echo " Setup complete."
echo "════════════════════════════════════════"
echo ""

if [ "$REBOOT_NEEDED" = true ]; then
    warn "A reboot is required to disable the audio driver."
    warn "After rebooting, verify hardware:"
    warn "  sudo $PYTHON $PROJECT_DIR/test_matrix.py"
    warn "Then start the service:"
    warn "  sudo systemctl start $SERVICE"
    echo ""
    read -r -p "Reboot now? [y/N] " response
    if [[ "${response,,}" == "y" ]]; then
        sudo reboot
    fi
else
    echo "Verify hardware:  sudo $PYTHON $PROJECT_DIR/test_matrix.py"
    echo "Start service:    sudo systemctl start $SERVICE"
    echo "Check logs:       sudo journalctl -u $SERVICE -f"
fi
