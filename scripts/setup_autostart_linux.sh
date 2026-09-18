#!/bin/bash
# Linux systemd service installer for AI Instagram Reels Autopilot

SERVICE_NAME="instagram-autopilot"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo ./setup_autostart_linux.sh"
    exit 1
fi

cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=AI Instagram Reels Autopilot Service
After=network.target docker.service

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/docker compose up
ExecStop=/usr/bin/docker compose down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

echo "Instagram Autopilot systemd service successfully installed and started!"
echo "Check status with: systemctl status $SERVICE_NAME"
