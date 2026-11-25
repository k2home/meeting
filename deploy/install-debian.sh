#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Bitte mit sudo ausführen: sudo bash deploy/install-debian.sh" >&2
  exit 1
fi

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="/opt/meeting-manager"
DB_NAME="meeting_manager"
DB_USER="meetingapp"

echo "==> Installiere Systempakete"
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  python3 python3-venv python3-dev build-essential libpq-dev \
  postgresql postgresql-contrib nginx git openssl sudo libcairo2 clamav-daemon clamav-freshclam

echo "==> Richte Dienstkonto und Verzeichnisse ein"
if ! id meetingapp >/dev/null 2>&1; then
  useradd --system --home-dir "$APP_DIR" --shell /usr/sbin/nologin --gid www-data meetingapp
fi
install -d -o meetingapp -g www-data "$APP_DIR" "$APP_DIR/media" "$APP_DIR/staticfiles"
cp -a "$SOURCE_DIR/." "$APP_DIR/"
chown -R root:www-data "$APP_DIR"
chown -R meetingapp:www-data "$APP_DIR/media" "$APP_DIR/staticfiles"

DEFAULT_HOST="$(hostname -f 2>/dev/null || hostname)"
read -r -p "Hostname oder IP, unter der die Website erreichbar ist [$DEFAULT_HOST]: " SITE_HOST
SITE_HOST="${SITE_HOST:-$DEFAULT_HOST}"
if [[ ! "$SITE_HOST" =~ ^[A-Za-z0-9.-]+$ ]]; then
  echo "Bitte einen gültigen Hostnamen oder eine IPv4-Adresse eingeben. IPv6-Adressen bitte über einen DNS-Namen verwenden." >&2
  exit 1
fi

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

DEFAULT_PROXY="$(read_existing_env TRUSTED_PROXY)"
DEFAULT_PROXY="${DEFAULT_PROXY:-127.0.0.1}"
read -r -p "IP-Adresse/CIDR des vorgeschalteten HTTPS-Reverse-Proxys [$DEFAULT_PROXY]: " TRUSTED_PROXY
TRUSTED_PROXY="${TRUSTED_PROXY:-$DEFAULT_PROXY}"
if ! python3 -c 'import ipaddress, sys; ipaddress.ip_network(sys.argv[1], strict=False)' "$TRUSTED_PROXY" 2>/dev/null; then
  echo "Ungültige Proxy-Adresse. Erwartet wird eine IPv4-/IPv6-Adresse oder ein CIDR-Netz." >&2
  exit 1
fi

# Reuse existing infrastructure credentials on reinstalls; never rotate a
# working database password or SECRET_KEY merely because the installer ran again.
if [[ -f "$APP_DIR/.env" ]]; then
  SECRET_KEY="$(read_existing_env SECRET_KEY)"
  DB_PASSWORD="$(read_existing_env POSTGRES_PASSWORD)"
  if [[ -z "$SECRET_KEY" || -z "$DB_PASSWORD" ]]; then
    echo "Die vorhandene .env enthält keinen SECRET_KEY oder POSTGRES_PASSWORD. Bitte zuerst manuell sichern und korrigieren." >&2
    exit 1
  fi
else
  SECRET_KEY="$(openssl rand -hex 48)"
  DB_PASSWORD="$(openssl rand -hex 24)"
fi

echo "==> Richte lokale PostgreSQL-Datenbank ein"
# DB_PASSWORD is generated as hex on first install or reused from the protected .env.
if ! runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
  runuser -u postgres -- psql -c "CREATE ROLE $DB_USER LOGIN PASSWORD '$DB_PASSWORD';"
else
  runuser -u postgres -- psql -c "ALTER ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASSWORD';"
fi
if ! runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
  runuser -u postgres -- createdb --owner="$DB_USER" "$DB_NAME"
fi

echo "==> Erzeuge Python-Umgebung"
# Recreate only the virtual environment; application data and PostgreSQL stay intact.
rm -rf "$APP_DIR/.venv"
install -d -o meetingapp -g www-data "$APP_DIR/.venv"
runuser -u meetingapp -- python3 -m venv "$APP_DIR/.venv"
runuser -u meetingapp -- "$APP_DIR/.venv/bin/python" -m pip install --upgrade pip
runuser -u meetingapp -- "$APP_DIR/.venv/bin/python" -m pip install -r "$APP_DIR/requirements.txt" -c "$APP_DIR/requirements-constraints.txt"

if [[ ! -f "$APP_DIR/.env" ]]; then
  umask 077
  cat > "$APP_DIR/.env" <<EOF
SECRET_KEY=$SECRET_KEY
DEBUG=0
ALLOWED_HOSTS=$SITE_HOST,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://$SITE_HOST
POSTGRES_DB=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
TIME_ZONE=Europe/Berlin
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=0
SECURE_HSTS_PRELOAD=0
TRUST_PROXY_SSL=1
USE_X_FORWARDED_HOST=1
TRUSTED_PROXY=$TRUSTED_PROXY
EOF
else
  # Remove the obsolete activation code from installations created by older versions.
  sed -i '/^SETUP_TOKEN=/d' "$APP_DIR/.env"
  # Keep reverse-proxy, HTTPS and other local settings intact on existing systems.
  CURRENT_HOSTS="$(read_existing_env ALLOWED_HOSTS)"
  if [[ -n "$CURRENT_HOSTS" && ",$CURRENT_HOSTS," != *",$SITE_HOST,"* ]]; then
    sed -i "s/^ALLOWED_HOSTS=.*/ALLOWED_HOSTS=$CURRENT_HOSTS,$SITE_HOST/" "$APP_DIR/.env"
  fi
fi

# Keep the ClamAV TCP listener local to this host; never expose port 3310 publicly.
if grep -qE '^[[:space:]]*#?[[:space:]]*TCPSocket' /etc/clamav/clamd.conf; then
  sed -E -i 's/^[[:space:]]*#?[[:space:]]*TCPSocket.*/TCPSocket 3310/' /etc/clamav/clamd.conf
else
  printf '\nTCPSocket 3310\n' >> /etc/clamav/clamd.conf
fi
if grep -qE '^[[:space:]]*#?[[:space:]]*TCPAddr' /etc/clamav/clamd.conf; then
  sed -E -i 's/^[[:space:]]*#?[[:space:]]*TCPAddr.*/TCPAddr 127.0.0.1/' /etc/clamav/clamd.conf
else
  printf 'TCPAddr 127.0.0.1\n' >> /etc/clamav/clamd.conf
fi
if grep -qE '^[[:space:]]*#?[[:space:]]*StreamMaxLength' /etc/clamav/clamd.conf; then
  sed -E -i 's/^[[:space:]]*#?[[:space:]]*StreamMaxLength.*/StreamMaxLength 32M/' /etc/clamav/clamd.conf
else
  printf 'StreamMaxLength 32M\n' >> /etc/clamav/clamd.conf
fi
systemctl enable --now clamav-freshclam
systemctl restart clamav-daemon

# Productive installs require a reachable malware scanner; uploads fail closed if it stops.
set_env_value "CLAMD_ENABLED" "1"
set_env_value "CLAMD_HOST" "127.0.0.1"
set_env_value "CLAMD_PORT" "3310"

# Productive installs always require HTTPS at the trusted reverse proxy.
set_env_value "CSRF_TRUSTED_ORIGINS" "https://$SITE_HOST"
set_env_value "SECURE_SSL_REDIRECT" "1"
set_env_value "SESSION_COOKIE_SECURE" "1"
set_env_value "CSRF_COOKIE_SECURE" "1"
set_env_value "TRUST_PROXY_SSL" "1"
set_env_value "USE_X_FORWARDED_HOST" "1"
set_env_value "TRUSTED_PROXY" "$TRUSTED_PROXY"

chown root:www-data "$APP_DIR/.env"
chmod 640 "$APP_DIR/.env"

echo "==> Erzeuge Datenbanktabellen und statische Dateien"
runuser -u meetingapp -- bash -c 'set -a; source /opt/meeting-manager/.env; set +a; exec "$@"' _ \
  "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" migrate --fake-initial --noinput
# Nginx serves static files as www-data.
umask 027
runuser -u meetingapp -- bash -c 'set -a; source /opt/meeting-manager/.env; set +a; exec "$@"' _ \
  "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" collectstatic --noinput
chown -R meetingapp:www-data "$APP_DIR/staticfiles"
find "$APP_DIR/staticfiles" -type d -exec chmod 750 {} +
find "$APP_DIR/staticfiles" -type f -exec chmod 640 {} +

echo "==> Installiere systemd- und Nginx-Konfiguration"
install -m 0644 "$APP_DIR/deploy/meeting-manager.service" /etc/systemd/system/meeting-manager.service
bash "$APP_DIR/deploy/install-debian-updater.sh"
NGINX_CONFIG="/etc/nginx/sites-available/meeting-manager"
install -m 0644 "$APP_DIR/deploy/nginx-meeting-manager.conf" "$NGINX_CONFIG"

sed -i "s|server_name _;|server_name $SITE_HOST;\\n    allow $TRUSTED_PROXY;\\n    deny all;|" "$NGINX_CONFIG"
ln -sfn "$NGINX_CONFIG" /etc/nginx/sites-enabled/meeting-manager
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl daemon-reload
systemctl enable --now meeting-manager
systemctl enable --now nginx
systemctl reload nginx

echo
echo "Installation abgeschlossen."
echo "Interne Anwendung: http://127.0.0.1:8080 (nur vom HTTPS-Reverse-Proxy $TRUSTED_PROXY erreichbar)"
echo "Öffentliche Adresse: https://$SITE_HOST/"
echo "Reverse-Proxy-Upstream: Port 8080 dieses Servers (bei lokalem Proxy http://127.0.0.1:8080); X-Forwarded-Proto muss auf https gesetzt werden."
echo "Status:  systemctl status meeting-manager"
echo "Logs:    journalctl -u meeting-manager -f"
echo
echo "Die technischen Zugangsdaten wurden automatisch erzeugt und in $APP_DIR/.env gespeichert."
echo "WICHTIG: .env enthält Secrets und ist nur für root und www-data lesbar. Nicht einchecken oder weitergeben."
echo "HTTPS ist erzwungen: Ohne vorgeschalteten TLS-Reverse-Proxy mit gültigem Zertifikat ist die Anwendung nicht nutzbar."
echo "Django vertraut X-Forwarded-Proto ausschließlich über Nginx-Zugriffe von $TRUSTED_PROXY."
