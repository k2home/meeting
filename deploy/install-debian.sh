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
  postgresql postgresql-contrib nginx git openssl

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
runuser -u meetingapp -- "$APP_DIR/.venv/bin/python" -m pip install -r "$APP_DIR/requirements.txt"

read -r -p "Hostname oder IP, unter der die Website erreichbar ist (z.B. 192.168.1.50): " SITE_HOST
SITE_HOST="${SITE_HOST:-localhost}"
SECRET_KEY="$(openssl rand -hex 48)"
umask 077
cat > /etc/meeting-manager.env <<EOF
SECRET_KEY=$SECRET_KEY
DEBUG=0
ALLOWED_HOSTS=$SITE_HOST,localhost,127.0.0.1
POSTGRES_DB=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
TIME_ZONE=Europe/Berlin
EOF
chmod 600 /etc/meeting-manager.env

echo "==> Erzeuge Datenbanktabellen und statische Dateien"
# Load the same settings for one-off management commands that systemd loads
# for the long-running service. Keep the env file out of the root shell.
runuser -u meetingapp -- bash -c 'set -a; source /etc/meeting-manager.env; set +a; exec "$@"' _ \
  "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" migrate --run-syncdb --noinput
runuser -u meetingapp -- bash -c 'set -a; source /etc/meeting-manager.env; set +a; exec "$@"' _ \
  "$APP_DIR/.venv/bin/python" "$APP_DIR/manage.py" collectstatic --noinput

echo "==> Installiere systemd- und Nginx-Konfiguration"
install -m 0644 "$APP_DIR/deploy/meeting-manager.service" /etc/systemd/system/meeting-manager.service
install -m 0644 "$APP_DIR/deploy/nginx-meeting-manager.conf" /etc/nginx/sites-available/meeting-manager
ln -sfn /etc/nginx/sites-available/meeting-manager /etc/nginx/sites-enabled/meeting-manager
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl daemon-reload
systemctl enable --now meeting-manager
systemctl enable --now nginx
systemctl reload nginx

echo
echo "Installation abgeschlossen."
echo "Website: http://$SITE_HOST/"
echo "Status:  systemctl status meeting-manager"
echo "Logs:    journalctl -u meeting-manager -f"
echo "Admin:   sudo -u meetingapp $APP_DIR/.venv/bin/python $APP_DIR/manage.py createsuperuser"
echo
echo "WICHTIG: HTTP nur im internen LAN freigeben. Benutzername-ohne-Passwort-Login ist nicht sicher."
