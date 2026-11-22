#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/meeting-manager"
if [[ "$EUID" -ne 0 ]]; then
  echo "Bitte mit sudo ausführen: sudo $APP_DIR/deploy/update.sh"
  exit 1
fi

# Refuse to update a mixed working tree. The live .env is handled separately
# below because it is intentionally local and may have been tracked by old releases.
if ! git -C "$APP_DIR" diff --quiet -- . ':(exclude).env' \
  || ! git -C "$APP_DIR" diff --cached --quiet -- . ':(exclude).env'; then
  echo "Update abgebrochen: Es gibt lokale Änderungen an versionierten Dateien außerhalb von .env." >&2
  git -C "$APP_DIR" status --short
  exit 1
fi
UNTRACKED_FILES="$(git -C "$APP_DIR" ls-files --others --exclude-standard | grep -vxF '.env' || true)"
if [[ -n "$UNTRACKED_FILES" ]]; then
  echo "Update abgebrochen: Es gibt nicht versionierte Dateien im Repository:" >&2
  printf '%s\n' "$UNTRACKED_FILES" >&2
  exit 1
fi

# Preserve the live environment file while upgrading from releases where
# .env was tracked in Git. Restore it after the repository removes that file.
ENV_BACKUP=""
restore_env() {
  if [[ -n "$ENV_BACKUP" && -f "$ENV_BACKUP" ]]; then
    install -o root -g www-data -m 0640 "$ENV_BACKUP" "$APP_DIR/.env"
    rm -f "$ENV_BACKUP"
  fi
}
if [[ -f "$APP_DIR/.env" ]]; then
  ENV_BACKUP="$(mktemp /root/meeting-manager-env.XXXXXX)"
  install -m 0600 "$APP_DIR/.env" "$ENV_BACKUP"
  trap restore_env EXIT
  if git -C "$APP_DIR" ls-files --error-unmatch .env >/dev/null 2>&1; then
    git -C "$APP_DIR" checkout -- .env
  fi
fi
git -C "$APP_DIR" pull --ff-only
restore_env
trap - EXIT
runuser -u meetingapp -- "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt" -c "$APP_DIR/requirements-constraints.txt"
runuser -u meetingapp -- bash -c 'set -a; source /opt/meeting-manager/.env; set +a; exec "$@"' _ \
  "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" migrate --fake-initial --noinput
# Keep collected CSS/JS readable and traversable by Nginx (www-data).
umask 027
runuser -u meetingapp -- bash -c 'set -a; source /opt/meeting-manager/.env; set +a; exec "$@"' _ \
  "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" collectstatic --noinput
chown -R meetingapp:www-data "$APP_DIR/staticfiles"
find "$APP_DIR/staticfiles" -type d -exec chmod 750 {} +
find "$APP_DIR/staticfiles" -type f -exec chmod 640 {} +
systemctl restart meeting-manager
systemctl --no-pager --full status meeting-manager
