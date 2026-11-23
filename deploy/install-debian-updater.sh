#!/usr/bin/env bash
set -euo pipefail

if [[ "$EUID" -ne 0 ]]; then
  echo "Bitte mit sudo ausführen: sudo bash deploy/install-debian-updater.sh" >&2
  exit 1
fi

APP_DIR="/opt/meeting-manager"
if ! id meetingapp >/dev/null 2>&1; then
  echo "Das Dienstkonto meetingapp ist nicht vorhanden. Bitte zuerst die Debian-Installation abschließen." >&2
  exit 1
fi
getent group www-data >/dev/null

install -d -o root -g www-data -m 0750 /var/lib/meeting-manager-updater
install -o root -g root -m 0644 "$APP_DIR/deploy/meeting-manager.service" /etc/systemd/system/meeting-manager.service
if [[ ! -x /usr/bin/systemd-run ]]; then
  echo "systemd-run ist nicht verfügbar; ein systemd-basierter Dienst wird benötigt." >&2
  exit 1
fi
install -o root -g root -m 0755 "$APP_DIR/deploy/meeting-manager-update" /usr/local/sbin/meeting-manager-update
install -o root -g root -m 0755 "$APP_DIR/deploy/meeting-manager-update-runner" /usr/local/sbin/meeting-manager-update-runner
install -o root -g root -m 0440 "$APP_DIR/deploy/meeting-manager-update.sudoers" /etc/sudoers.d/meeting-manager-update
visudo -cf /etc/sudoers.d/meeting-manager-update
systemctl daemon-reload
if systemctl is-active --quiet meeting-manager.service; then
  systemctl restart meeting-manager.service
fi

echo "Debian-Web-Updater eingerichtet."
echo "Erlaubte Ziele: beta und main. Der Dienst meetingapp darf ausschließlich diesen Wrapper aufrufen."
