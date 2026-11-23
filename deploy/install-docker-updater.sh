#!/usr/bin/env bash
set -euo pipefail

if [[ "$EUID" -ne 0 ]]; then
  echo "Bitte mit sudo ausführen: sudo bash deploy/install-docker-updater.sh"
  exit 1
fi

APP_DIR="/opt/meeting-manager"
GROUP_NAME="meeting-update"
GROUP_ID="10002"

if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
  echo "Docker Engine und Docker Compose v2 müssen installiert sein." >&2
  exit 1
fi
if ! getent group "$GROUP_NAME" >/dev/null 2>&1; then
  if getent group "$GROUP_ID" >/dev/null 2>&1; then
    echo "Die Gruppen-ID $GROUP_ID ist bereits belegt. Bitte vor der Installation bereinigen." >&2
    exit 1
  fi
  groupadd --system --gid "$GROUP_ID" "$GROUP_NAME"
fi
if [[ "$(getent group "$GROUP_NAME" | cut -d: -f3)" != "$GROUP_ID" ]]; then
  echo "Die Gruppe $GROUP_NAME hat nicht die erwartete GID $GROUP_ID." >&2
  exit 1
fi

install -d -o root -g root -m 0755 /usr/local/lib/meeting-manager
install -d -o root -g root -m 0750 /var/lib/meeting-manager-updater
install -o root -g root -m 0755 "$APP_DIR/deploy/docker-update-agent.py" /usr/local/lib/meeting-manager/docker-update-agent.py
install -o root -g root -m 0644 "$APP_DIR/deploy/meeting-manager-docker-updater.service" /etc/systemd/system/meeting-manager-docker-updater.service

# The agent is deliberately installed outside the application checkout.
sed -i 's|/opt/meeting-manager/deploy/docker-update-agent.py|/usr/local/lib/meeting-manager/docker-update-agent.py|' /etc/systemd/system/meeting-manager-docker-updater.service
systemctl daemon-reload
systemctl enable --now meeting-manager-docker-updater.service
echo "Docker-Updater installiert. Der Socket ist nur für root und die Gruppe $GROUP_NAME zugänglich."
echo "Der App-Container benötigt group_add: $GROUP_ID und den Socket-Verzeichnis-Mount aus docker/compose.yaml."
