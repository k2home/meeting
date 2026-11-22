#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/meeting-manager"
if [[ "$EUID" -ne 0 ]]; then
  echo "Bitte mit sudo ausführen: sudo $APP_DIR/deploy/update.sh"
  exit 1
fi

# Refuse to update a mixed working tree. The live .env is handled separately
# below because it is intentionally local and may have been tracked by old releases.
# Older installer versions modified the tracked Nginx template in-place
# when configuring a trusted reverse proxy. Recognize only that exact generated
# form, restore the clean template (the active config lives in /etc/nginx), and
# continue. Any other local edit remains protected by the normal dirty-tree check.
NGINX_TEMPLATE="$APP_DIR/deploy/nginx-meeting-manager.conf"
if ! git -C "$APP_DIR" diff --quiet -- "$NGINX_TEMPLATE"; then
  EXPECTED_NGINX="$(mktemp)"
  git -C "$APP_DIR" show "HEAD:deploy/nginx-meeting-manager.conf" > "$EXPECTED_NGINX"
  TRUSTED_PROXY="$(sed -n 's/^[[:space:]]*allow \([^;]*\);$/\1/p' "$NGINX_TEMPLATE")"
  ALLOW_COUNT="$(grep -Ec '^[[:space:]]*allow [^;]+;$' "$NGINX_TEMPLATE" || true)"
  DENY_COUNT="$(grep -Ec '^[[:space:]]*deny all;$' "$NGINX_TEMPLATE" || true)"
  if [[ -n "$TRUSTED_PROXY" && "$ALLOW_COUNT" == "1" && "$DENY_COUNT" == "1" ]]; then
    sed -i "s|server_name _;|server_name _;\\n    allow $TRUSTED_PROXY;\\n    deny all;|" "$EXPECTED_NGINX"
    sed -i 's/proxy_set_header X-Forwarded-Proto \$scheme;/proxy_set_header X-Forwarded-Proto \$http_x_forwarded_proto;/' "$EXPECTED_NGINX"
  fi
  if [[ -n "$TRUSTED_PROXY" && "$ALLOW_COUNT" == "1" && "$DENY_COUNT" == "1" ]] \
    && cmp -s "$EXPECTED_NGINX" "$NGINX_TEMPLATE" \
    && [[ -f /etc/nginx/sites-available/meeting-manager ]] \
    && git -C "$APP_DIR" diff --cached --quiet -- "$NGINX_TEMPLATE"; then
    git -C "$APP_DIR" checkout -- "$NGINX_TEMPLATE"
    echo "Hinweis: Alte, vom Installskript erzeugte Nginx-Vorlage wurde bereinigt; die aktive Konfiguration unter /etc/nginx bleibt erhalten."
  fi
  rm -f "$EXPECTED_NGINX"
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
