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

if [[ ! -f "$APP_DIR/.env" ]]; then
  DEFAULT_HOST="$(hostname -f 2>/dev/null || hostname)"
  read -r -p "Hostname oder IP, unter der die Website erreichbar ist [$DEFAULT_HOST]: " SITE_HOST
  SITE_HOST="${SITE_HOST:-$DEFAULT_HOST}"
  if [[ ! "$SITE_HOST" =~ ^[A-Za-z0-9.-]+$ ]]; then
    echo "Bitte einen gültigen Hostnamen oder eine IPv4-Adresse eingeben. IPv6 bitte über einen DNS-Namen verwenden." >&2
    exit 1
  fi

  SECRET_KEY="$(openssl rand -hex 48)"
  DB_PASSWORD="$(openssl rand -hex 24)"
  umask 077
  cat > "$APP_DIR/.env" <<EOF
SECRET_KEY=$SECRET_KEY
DEBUG=0
ALLOWED_HOSTS=$SITE_HOST,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=
POSTGRES_DB=meeting_manager
POSTGRES_USER=meetingapp
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_HOST=db
POSTGRES_PORT=5432
TIME_ZONE=Europe/Berlin
WEB_PORT=8080
SECURE_SSL_REDIRECT=0
SESSION_COOKIE_SECURE=0
CSRF_COOKIE_SECURE=0
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=0
SECURE_HSTS_PRELOAD=0
TRUST_PROXY_SSL=0
USE_X_FORWARDED_HOST=0
EOF
  chmod 600 "$APP_DIR/.env"
else
  chmod 600 "$APP_DIR/.env"
  if ! grep -q '^SECRET_KEY=.' "$APP_DIR/.env" || ! grep -q '^POSTGRES_PASSWORD=.' "$APP_DIR/.env"; then
    echo "Die vorhandene .env benötigt gültige Werte für SECRET_KEY und POSTGRES_PASSWORD." >&2
    exit 1
  fi
  echo "Vorhandene .env wird unverändert beibehalten."
fi

echo "==> Prüfe Compose-Konfiguration"
docker compose -f "$COMPOSE_FILE" config --quiet

echo "==> Installiere den eingeschränkten Docker-Updater"
bash "$APP_DIR/deploy/install-docker-updater.sh"

echo "==> Lade Images und starte Meeting Manager"
docker compose -f "$COMPOSE_FILE" pull
docker compose -f "$COMPOSE_FILE" up -d

echo
echo "Installation abgeschlossen."
WEB_PORT="$(sed -n 's/^WEB_PORT=//p' "$APP_DIR/.env" | tail -n 1 | tr -d '\r')"
WEB_PORT="${WEB_PORT:-8080}"
echo "Webzugriff: http://<SERVER-IP>:$WEB_PORT/"
echo "Status:     docker compose -f $COMPOSE_FILE ps"
echo "Logs:       docker compose -f $COMPOSE_FILE logs -f app"
echo "Secrets:    $APP_DIR/.env (nur root lesbar)"
echo "HTTPS: Für produktiven Zugriff HTTPS über einen vorgeschalteten Reverse Proxy konfigurieren."
echo "Admin: Das erste Administratorkonto muss nach dem Start einmalig angelegt werden (siehe README)."
