#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Bitte mit sudo ausführen: sudo bash deploy/install-docker.sh" >&2
  exit 1
fi

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="/opt/meeting-manager"
COMPOSE_FILE="$APP_DIR/docker/compose.yaml"

if [[ "$SOURCE_DIR" != "$APP_DIR" ]]; then
  echo "Bitte das Repository zuerst nach $APP_DIR klonen und das Skript dort starten." >&2
  echo "Beispiel: sudo git clone https://github.com/k2home/meeting.git $APP_DIR" >&2
  exit 1
fi
cd "$APP_DIR"
if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
  echo "Docker Engine und Docker Compose v2 müssen vor der Installation eingerichtet sein." >&2
  exit 1
fi

echo "==> Prüfe Docker"
command -v openssl >/dev/null 2>&1 || { echo "openssl muss installiert sein." >&2; exit 1; }
docker info >/dev/null

read_existing_env() {
  local key="$1"
  if [[ -f "$APP_DIR/.env" ]]; then
    sed -n "s/^$key=//p" "$APP_DIR/.env" | head -n 1
  fi
}

set_env_value() {
  local key="$1" value="$2"
  if grep -q "^${key}=" "$APP_DIR/.env"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "$APP_DIR/.env"
  else
    printf '%s=%s\n' "$key" "$value" >> "$APP_DIR/.env"
  fi
}

DEFAULT_HOST=""
while IFS= read -r candidate; do
  case "$candidate" in ""|localhost|127.0.0.1|'*') continue ;; esac
  if [[ "$candidate" =~ ^[A-Za-z0-9.-]+$ ]]; then
    DEFAULT_HOST="$candidate"
    break
  fi
done < <(read_existing_env ALLOWED_HOSTS | tr ',' '\n')
DEFAULT_HOST="${DEFAULT_HOST:-$(hostname -f 2>/dev/null || hostname)}"
read -r -p "Öffentlicher Hostname bzw. IP-Adresse der Website [$DEFAULT_HOST]: " SITE_HOST
SITE_HOST="${SITE_HOST:-$DEFAULT_HOST}"
if [[ ! "$SITE_HOST" =~ ^[A-Za-z0-9.-]+$ ]]; then
  echo "Bitte einen gültigen öffentlichen Hostnamen oder eine IPv4-Adresse eingeben. IPv6 bitte über einen DNS-Namen verwenden." >&2
  exit 1
fi

if [[ ! -f "$APP_DIR/.env" ]]; then
  SECRET_KEY="$(openssl rand -hex 48)"
  DB_PASSWORD="$(openssl rand -hex 24)"
  umask 077
  cat > "$APP_DIR/.env" <<EOF
SECRET_KEY=$SECRET_KEY
DEBUG=0
ALLOWED_HOSTS=$SITE_HOST,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://$SITE_HOST
POSTGRES_DB=meeting_manager
POSTGRES_USER=meetingapp
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_HOST=db
POSTGRES_PORT=5432
TIME_ZONE=Europe/Berlin
WEB_PORT=8080
WEB_BIND_ADDRESS=127.0.0.1
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=0
SECURE_HSTS_PRELOAD=0
TRUST_PROXY_SSL=1
USE_X_FORWARDED_HOST=1
EOF
  chmod 600 "$APP_DIR/.env"
else
  # Remove the obsolete activation code from installations created by older versions.
  sed -i '/^SETUP_TOKEN=/d' "$APP_DIR/.env"
  chown root:root "$APP_DIR/.env"
  chmod 600 "$APP_DIR/.env"
  if ! grep -q '^SECRET_KEY=.' "$APP_DIR/.env" || ! grep -q '^POSTGRES_PASSWORD=.' "$APP_DIR/.env"; then
    echo "Die vorhandene .env benötigt gültige Werte für SECRET_KEY und POSTGRES_PASSWORD." >&2
    exit 1
  fi
  echo "Vorhandene .env wird beibehalten; Sicherheitsoptionen werden auf HTTPS-Betrieb gesetzt."
fi

CURRENT_HOSTS="$(read_existing_env ALLOWED_HOSTS)"
if [[ -n "$CURRENT_HOSTS" && ",$CURRENT_HOSTS," != *",$SITE_HOST,"* ]]; then
  set_env_value "ALLOWED_HOSTS" "$SITE_HOST,$CURRENT_HOSTS"
fi

# Productive installs require HTTPS at a same-host reverse proxy.
set_env_value "CSRF_TRUSTED_ORIGINS" "https://$SITE_HOST"
set_env_value "WEB_BIND_ADDRESS" "127.0.0.1"
set_env_value "SECURE_SSL_REDIRECT" "1"
set_env_value "SESSION_COOKIE_SECURE" "1"
set_env_value "CSRF_COOKIE_SECURE" "1"
set_env_value "TRUST_PROXY_SSL" "1"
set_env_value "USE_X_FORWARDED_HOST" "1"

echo "==> Prüfe Compose-Konfiguration"
docker compose -f "$COMPOSE_FILE" config --quiet

echo "==> Installiere den eingeschränkten Docker-Updater"
bash "$APP_DIR/deploy/install-docker-updater.sh"

echo "==> Lade Images und starte Meeting Manager"
docker compose -f "$COMPOSE_FILE" pull
docker compose -f "$COMPOSE_FILE" up -d

echo
echo "Installation abgeschlossen."
WEB_PORT="$(read_existing_env WEB_PORT)"
WEB_PORT="${WEB_PORT:-8080}"
echo "Interne Anwendung: http://127.0.0.1:$WEB_PORT (nur lokaler HTTPS-Reverse-Proxy)"
echo "Öffentliche Adresse: https://$SITE_HOST/"
echo "Reverse-Proxy-Upstream: http://127.0.0.1:$WEB_PORT; X-Forwarded-Proto muss auf https gesetzt werden."
echo "Status:     docker compose -f $COMPOSE_FILE ps"
echo "Logs:       docker compose -f $COMPOSE_FILE logs -f app"
echo "Secrets:    $APP_DIR/.env (nur root lesbar)"
echo "HTTPS ist erzwungen: Ohne vorgeschalteten TLS-Reverse-Proxy mit gültigem Zertifikat ist die Anwendung nicht nutzbar."
