#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/meeting-manager"
if [[ "$EUID" -ne 0 ]]; then
  echo "Bitte mit sudo ausführen: sudo $APP_DIR/deploy/update.sh"
  exit 1
fi

git -C "$APP_DIR" pull --ff-only
runuser -u meetingapp -- "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"
runuser -u meetingapp -- bash -c 'set -a; source /etc/meeting-manager.env; set +a; exec "$@"' _ \
  "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" migrate --fake-initial --noinput
# Keep collected CSS/JS readable and traversable by Nginx (www-data).
umask 027
runuser -u meetingapp -- bash -c 'set -a; source /etc/meeting-manager.env; set +a; exec "$@"' _ \
  "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" collectstatic --noinput
chown -R meetingapp:www-data "$APP_DIR/staticfiles"
find "$APP_DIR/staticfiles" -type d -exec chmod 750 {} +
find "$APP_DIR/staticfiles" -type f -exec chmod 640 {} +
systemctl restart meeting-manager
systemctl --no-pager --full status meeting-manager
