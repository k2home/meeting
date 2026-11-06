#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/meeting-manager"
if [[ "$EUID" -ne 0 ]]; then
  echo "Bitte mit sudo ausführen: sudo $APP_DIR/deploy/update.sh"
  exit 1
fi

git -C "$APP_DIR" pull --ff-only
runuser -u meetingapp -- "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"
runuser -u meetingapp -- "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" migrate --run-syncdb --noinput
runuser -u meetingapp -- "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" collectstatic --noinput
systemctl restart meeting-manager
systemctl --no-pager --full status meeting-manager
