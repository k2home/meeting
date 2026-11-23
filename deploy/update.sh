#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/meeting-manager"
TARGET_BRANCH="${1:-}"
if [[ "$#" -gt 1 ]]; then
  echo "Verwendung: $0 [beta|main]" >&2
  exit 2
fi
if [[ -n "$TARGET_BRANCH" && "$TARGET_BRANCH" != "beta" && "$TARGET_BRANCH" != "main" ]]; then
  echo "Unzulässiger Update-Branch. Erlaubt sind ausschließlich beta und main." >&2
  exit 2
fi
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

# Keep enough information to restore the previous source revision if the
# checkout itself succeeded but a later pre-installation step fails. Once
# dependency installation or migrations begin, automatic code rollback is
# deliberately disabled because the virtualenv/database may already have
# moved forward and an older application revision may no longer be compatible.
PREVIOUS_BRANCH="$(git -C "$APP_DIR" branch --show-current)"
PREVIOUS_COMMIT="$(git -C "$APP_DIR" rev-parse HEAD)"
CODE_SWITCHED=0
ROLLBACK_SAFE=1
ENV_BACKUP=""

restore_env() {
  if [[ -n "$ENV_BACKUP" && -f "$ENV_BACKUP" ]]; then
    install -o root -g www-data -m 0640 "$ENV_BACKUP" "$APP_DIR/.env"
    rm -f "$ENV_BACKUP"
    ENV_BACKUP=""
  fi
}

handle_update_exit() {
  local exit_code=$?
  trap - EXIT

  if [[ -n "$ENV_BACKUP" && -f "$ENV_BACKUP" ]]; then
    if ! restore_env; then
      echo "FEHLER: Die lokale .env-Datei konnte nicht wiederhergestellt werden." >&2
    fi
  fi

  if [[ "$exit_code" -ne 0 && "$CODE_SWITCHED" -eq 1 ]]; then
    if [[ "$ROLLBACK_SAFE" -eq 1 ]]; then
      echo "Update fehlgeschlagen; stelle den vorherigen Quellcode-Stand wieder her." >&2
      ROLLBACK_ENV_BACKUP=""
      if [[ -f "$APP_DIR/.env" ]]; then
        ROLLBACK_ENV_BACKUP="$(mktemp /root/meeting-manager-rollback-env.XXXXXX)"
        cp -a "$APP_DIR/.env" "$ROLLBACK_ENV_BACKUP"
      fi
      if git -C "$APP_DIR" checkout --force --detach "$PREVIOUS_COMMIT"; then
        if [[ -n "$PREVIOUS_BRANCH" ]]; then
          if ! git -C "$APP_DIR" branch -f "$PREVIOUS_BRANCH" "$PREVIOUS_COMMIT" \
            || ! git -C "$APP_DIR" switch "$PREVIOUS_BRANCH"; then
            echo "FEHLER: Der vorherige Branch konnte nicht wieder aktiviert werden." >&2
          fi
        fi
        if [[ -n "$ROLLBACK_ENV_BACKUP" && -f "$ROLLBACK_ENV_BACKUP" ]]; then
          cp -a "$ROLLBACK_ENV_BACKUP" "$APP_DIR/.env"
          rm -f "$ROLLBACK_ENV_BACKUP"
        fi
        systemctl restart meeting-manager || echo "FEHLER: Der Dienst konnte nach der Wiederherstellung nicht gestartet werden." >&2
      else
        if [[ -n "$ROLLBACK_ENV_BACKUP" && -f "$ROLLBACK_ENV_BACKUP" ]]; then
          cp -a "$ROLLBACK_ENV_BACKUP" "$APP_DIR/.env"
          rm -f "$ROLLBACK_ENV_BACKUP"
        fi
        echo "FEHLER: Der vorherige Git-Stand konnte nicht wiederhergestellt werden." >&2
      fi
    else
      echo "Der Quellcode bleibt auf dem Zielstand: Abhängigkeiten oder Datenbankmigrationen wurden bereits begonnen. Bitte Protokoll prüfen und bei Bedarf aus einem Backup wiederherstellen." >&2
    fi
  fi
  exit "$exit_code"
}
trap handle_update_exit EXIT

# Preserve the live environment file while upgrading from releases where
# .env was tracked in Git. Restore it after the repository removes that file.
if [[ -f "$APP_DIR/.env" ]]; then
  ENV_BACKUP_TMP="$(mktemp /root/meeting-manager-env.XXXXXX)"
  if install -m 0600 "$APP_DIR/.env" "$ENV_BACKUP_TMP"; then
    ENV_BACKUP="$ENV_BACKUP_TMP"
  else
    rm -f "$ENV_BACKUP_TMP"
    echo "Die lokale .env-Datei konnte nicht gesichert werden; Update abgebrochen." >&2
    exit 1
  fi
  if git -C "$APP_DIR" ls-files --error-unmatch .env >/dev/null 2>&1; then
    git -C "$APP_DIR" checkout -- .env
  fi
fi
if [[ -n "$TARGET_BRANCH" ]]; then
  echo "==> Aktualisiere Quellcode aus Branch $TARGET_BRANCH"
  git -C "$APP_DIR" fetch --prune origin "$TARGET_BRANCH"
  CODE_SWITCHED=1
  git -C "$APP_DIR" switch --force-create "$TARGET_BRANCH" "origin/$TARGET_BRANCH"
else
  CODE_SWITCHED=1
  git -C "$APP_DIR" pull --ff-only
fi
restore_env

# Apply the cache policy to the active Nginx site without replacing local
# reverse-proxy settings (for example, trusted-proxy allow/deny rules).
ACTIVE_NGINX="/etc/nginx/sites-available/meeting-manager"
if [[ -f "$ACTIVE_NGINX" ]]; then
  NGINX_BACKUP="$(mktemp)"
  cp -a "$ACTIVE_NGINX" "$NGINX_BACKUP"
  if python3 - "$ACTIVE_NGINX" <<'PY'
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
content = path.read_text(encoding="utf-8")
policy = '        add_header Cache-Control "no-store, no-cache, must-revalidate, max-age=0" always;'

static_pattern = r"(location /static/\s*\{)(.*?)(\n    \})"
root_pattern = r"(location /\s*\{)(.*?)(\n    \})"
static_match = re.search(static_pattern, content, re.S)
root_match = re.search(root_pattern, content, re.S)
if not static_match or not root_match:
    print("Aktive Nginx-Konfiguration nicht im erwarteten Format; Cache-Konfiguration bleibt unverändert.", file=sys.stderr)
    sys.exit(2)

static_body = static_match.group(2)
static_body = re.sub(r"^\s*expires\s+[^;]+;\s*$", "", static_body, flags=re.M)
static_body = re.sub(r'^\s*add_header Cache-Control "[^"]+"(?:\s+always)?;\s*$', "", static_body, flags=re.M)
static_body = static_body.rstrip() + "\n" + policy
content = content[:static_match.start(2)] + static_body + content[static_match.end(2):]

root_match = re.search(root_pattern, content, re.S)
root_body = root_match.group(2)
root_body = re.sub(r'^\s*add_header Cache-Control "[^"]+"(?:\s+always)?;\s*$', "", root_body, flags=re.M)
root_body = root_body.rstrip() + "\n" + policy
content = content[:root_match.start(2)] + root_body + content[root_match.end(2):]
path.write_text(content, encoding="utf-8")
PY
  then
    if nginx -t; then
      systemctl reload nginx
      rm -f "$NGINX_BACKUP"
      echo "Nginx-Cache deaktiviert: HTML-Seiten und statische Assets werden nicht mehr zwischengespeichert."
    else
      cp -a "$NGINX_BACKUP" "$ACTIVE_NGINX"
      rm -f "$NGINX_BACKUP"
      nginx -t
      echo "Nginx-Änderung zurückgerollt; aktive Konfiguration blieb unverändert." >&2
      exit 1
    fi
  else
    cp -a "$NGINX_BACKUP" "$ACTIVE_NGINX"
    rm -f "$NGINX_BACKUP"
    echo "Update abgebrochen: Nginx-Cache-Konfiguration konnte nicht sicher angepasst werden." >&2
    exit 1
  fi
fi

# From this point onward the environment or database may no longer be
# compatible with the previous source revision; do not switch code back blindly.
ROLLBACK_SAFE=0
# CairoSVG wraps the native Cairo library; install it on Debian hosts too.
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends libcairo2
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
