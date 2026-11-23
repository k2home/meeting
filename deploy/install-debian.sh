#!/usr/bin/env bash
set -euo pipefail
if [[ "$EUID" -ne 0 ]]; then
  echo "Bitte mit sudo ausführen: sudo bash deploy/install-debian.sh"
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
  postgresql postgresql-contrib nginx git openssl sudo

echo "==> Richte Dienstkonto und Verzeichnisse ein"
if ! id meetingapp >/dev/null 2>&1; then
  useradd --system --home-dir "$APP_DIR" --shell /usr/sbin/nologin --gid www-data meetingapp
fi
install -d -o meetingapp -g www-data "$APP_DIR" "$APP_DIR/media" "$APP_DIR/staticfiles"
cp -a "$SOURCE_DIR/." "$APP_DIR/"
chown -R root:www-data "$APP_DIR"
chown -R meetingapp:www-data "$APP_DIR/media" "$APP_DIR/staticfiles"

echo "==> Richte lokale PostgreSQL-Datenbank ein"
DB_PASSWORD="$(openssl rand -hex 24)"
if ! runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
  runuser -u postgres -- psql -c "CREATE ROLE $DB_USER LOGIN PASSWORD '$DB_PASSWORD';"
else
  runuser -u postgres -- psql -c "ALTER ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASSWORD';"
fi
if ! runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
  runuser -u postgres -- createdb --owner="$DB_USER" "$DB_NAME"
fi

echo "==> Erzeuge Python-Umgebung mit korrekten Berechtigungen"
# Remove an incomplete virtualenv from a previous failed installation.
rm -rf "$APP_DIR/.venv"
install -d -o meetingapp -g www-data "$APP_DIR/.venv"
runuser -u meetingapp -- python3 -m venv "$APP_DIR/.venv"
runuser -u meetingapp -- "$APP_DIR/.venv/bin/python" -m pip install --upgrade pip
runuser -u meetingapp -- "$APP_DIR/.venv/bin/python" -m pip install -r "$APP_DIR/requirements.txt" -c "$APP_DIR/requirements-constraints.txt"

read -r -p "Hostname oder IP, unter der die Website erreichbar ist (z.B. meeting.intern): " SITE_HOST
SITE_HOST="${SITE_HOST:-localhost}"
if [[ ! "$SITE_HOST" =~ ^[A-Za-z0-9.-]+$ ]]; then
  echo "Bitte einen gültigen Hostnamen oder eine IPv4-Adresse eingeben. IPv6-Adressen bitte über einen DNS-Namen verwenden." >&2
  exit 1
fi
read -r -p "Django SECRET_KEY eingeben (leer = sicher zufällig erzeugen): " -s SECRET_KEY_INPUT
echo
SECRET_KEY="${SECRET_KEY_INPUT:-$(openssl rand -hex 48)}"
read -r -p "PostgreSQL-Passwort eingeben (leer = sicher zufällig erzeugen): " -s DB_PASSWORD_INPUT
echo
DB_PASSWORD="${DB_PASSWORD_INPUT:-$(openssl rand -hex 24)}"
if [[ ! "$SECRET_KEY" =~ ^[A-Za-z0-9._-]{50,}$ ]]; then
  echo "SECRET_KEY muss mindestens 50 Zeichen enthalten (Buchstaben, Zahlen, Punkt, _ oder -)." >&2
  exit 1
fi
if [[ ! "$DB_PASSWORD" =~ ^[A-Za-z0-9._-]{16,}$ ]]; then
  echo "Das Datenbankpasswort muss mindestens 16 Zeichen enthalten (Buchstaben, Zahlen, Punkt, _ oder -)." >&2
  exit 1
fi
runuser -u postgres -- psql -c "ALTER ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASSWORD';"
read -r -p "Wird HTTPS durch einen vorgeschalteten Reverse Proxy terminiert? [j/N]: " USE_PROXY
USE_PROXY="${USE_PROXY:-N}"
TRUST_PROXY_SSL=0
SECURE_SSL_REDIRECT=0
SESSION_COOKIE_SECURE=0
CSRF_COOKIE_SECURE=0
USE_X_FORWARDED_HOST=0
CSRF_TRUSTED_ORIGINS=""
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=0
SECURE_HSTS_PRELOAD=0
if [[ "$USE_PROXY" =~ ^[JjYy]$ ]]; then
  read -r -p "IP-Adresse oder CIDR des vorgeschalteten Reverse Proxy: " TRUSTED_PROXY
  if ! python3 -c 'import ipaddress, sys; ipaddress.ip_network(sys.argv[1], strict=False)' "$TRUSTED_PROXY" 2>/dev/null; then
    echo "Bitte eine gültige IPv4-/IPv6-Adresse oder ein CIDR-Netz angeben." >&2
    exit 1
  fi
  TRUST_PROXY_SSL=1
  SECURE_SSL_REDIRECT=1
  SESSION_COOKIE_SECURE=1
  CSRF_COOKIE_SECURE=1
  USE_X_FORWARDED_HOST=1
  CSRF_TRUSTED_ORIGINS="https://$SITE_HOST"
  SECURE_HSTS_SECONDS=31536000
  read -r -p "Sind alle Subdomains dauerhaft ausschließlich über HTTPS erreichbar? [j/N]: " HSTS_SUBDOMAINS
  if [[ "$HSTS_SUBDOMAINS" =~ ^[JjYy]$ ]]; then
    SECURE_HSTS_INCLUDE_SUBDOMAINS=1
    read -r -p "Soll die Domain für HSTS Preload vorbereitet werden? Nur bei vollständiger HTTPS-Abdeckung aller Subdomains. [j/N]: " HSTS_PRELOAD
    if [[ "$HSTS_PRELOAD" =~ ^[JjYy]$ ]]; then
      SECURE_HSTS_PRELOAD=1
    fi
  fi
fi
umask 077
cat > "$APP_DIR/.env" <<EOF
SECRET_KEY=$SECRET_KEY
DEBUG=0
ALLOWED_HOSTS=$SITE_HOST,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=$CSRF_TRUSTED_ORIGINS
POSTGRES_DB=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
TIME_ZONE=Europe/Berlin
SECURE_SSL_REDIRECT=$SECURE_SSL_REDIRECT
SESSION_COOKIE_SECURE=$SESSION_COOKIE_SECURE
CSRF_COOKIE_SECURE=$CSRF_COOKIE_SECURE
SECURE_HSTS_SECONDS=$SECURE_HSTS_SECONDS
SECURE_HSTS_INCLUDE_SUBDOMAINS=$SECURE_HSTS_INCLUDE_SUBDOMAINS
SECURE_HSTS_PRELOAD=$SECURE_HSTS_PRELOAD
TRUST_PROXY_SSL=$TRUST_PROXY_SSL
USE_X_FORWARDED_HOST=$USE_X_FORWARDED_HOST
EOF
chown root:www-data "$APP_DIR/.env"
chmod 640 "$APP_DIR/.env"
# Generate the host-specific Nginx configuration outside the Git working
# tree. The tracked file is a clean template and must remain unchanged so
# deploy/update.sh can safely detect unrelated local modifications.
NGINX_CONFIG="$(mktemp)"
trap 'rm -f "$NGINX_CONFIG"' EXIT
cp "$APP_DIR/deploy/nginx-meeting-manager.conf" "$NGINX_CONFIG"
if [[ "$TRUST_PROXY_SSL" == "1" ]]; then
  # Only the explicitly configured reverse proxy may reach this local Nginx
  # listener; this prevents clients from spoofing X-Forwarded-Proto.
  sed -i "s|server_name _;|server_name _;\\n    allow $TRUSTED_PROXY;\\n    deny all;|" "$NGINX_CONFIG"
  sed -i 's/proxy_set_header X-Forwarded-Proto \$scheme;/proxy_set_header X-Forwarded-Proto \$http_x_forwarded_proto;/' "$NGINX_CONFIG"
fi

echo "==> Erzeuge Datenbanktabellen und statische Dateien"
runuser -u meetingapp -- bash -c 'set -a; source /opt/meeting-manager/.env; set +a; exec "$@"' _ \
  "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" migrate --fake-initial --noinput
# Nginx serves static files as www-data. Do not let the restrictive umask
# used for the environment file make collected admin assets unreadable.
umask 027
runuser -u meetingapp -- bash -c 'set -a; source /opt/meeting-manager/.env; set +a; exec "$@"' _ \
  "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" collectstatic --noinput
chown -R meetingapp:www-data "$APP_DIR/staticfiles"
find "$APP_DIR/staticfiles" -type d -exec chmod 750 {} +
find "$APP_DIR/staticfiles" -type f -exec chmod 640 {} +

echo "==> Installiere systemd- und Nginx-Konfiguration"
install -m 0644 "$APP_DIR/deploy/meeting-manager.service" /etc/systemd/system/meeting-manager.service
install -o root -g root -m 0755 "$APP_DIR/deploy/meeting-manager-update" /usr/local/sbin/meeting-manager-update
install -o root -g root -m 0440 "$APP_DIR/deploy/meeting-manager-update.sudoers" /etc/sudoers.d/meeting-manager-update
visudo -cf /etc/sudoers.d/meeting-manager-update
install -m 0644 "$NGINX_CONFIG" /etc/nginx/sites-available/meeting-manager
ln -sfn /etc/nginx/sites-available/meeting-manager /etc/nginx/sites-enabled/meeting-manager
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl daemon-reload
systemctl enable --now meeting-manager
systemctl enable --now nginx
systemctl reload nginx

echo
echo "Installation abgeschlossen."
if [[ "$TRUST_PROXY_SSL" == "1" ]]; then echo "Website: https://$SITE_HOST/ (über vorgeschalteten Reverse Proxy)"; else echo "Website: http://$SITE_HOST/"; fi
echo "Status:  systemctl status meeting-manager"
echo "Logs:    journalctl -u meeting-manager -f"
echo "Admin:   sudo -u meetingapp bash -c 'set -a; source /opt/meeting-manager/.env; set +a; exec /opt/meeting-manager/.venv/bin/python /opt/meeting-manager/manage.py createsuperuser'"
echo
echo "WICHTIG: Die .env enthält Secrets und ist nur für root und www-data lesbar. Nicht einchecken oder weitergeben."
