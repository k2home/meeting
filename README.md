# Meeting Manager

Django-Anwendung für wiederkehrende Besprechungen, Themenlisten und druckbare Protokolle. Oberfläche und Zeitzone sind auf Deutsch bzw. Europe/Berlin eingestellt.

## Installation ohne Docker (Debian/Ubuntu-VM auf Proxmox)

Die Anwendung läuft direkt auf Linux: Python-Virtualenv + Gunicorn + PostgreSQL + systemd + Nginx. Es werden weder Docker noch Docker Compose benötigt.

### Schnellinstallation

1. Eine Debian- oder Ubuntu-VM auf Proxmox bereitstellen und per SSH anmelden.
2. Repository klonen:
   `git clone https://github.com/k2home/meeting.git`
3. In das Verzeichnis wechseln und Installationsskript ausführen:
   ```bash
   cd meeting
   sudo bash deploy/install-debian.sh
   ```
4. Beim Installieren die IP-Adresse oder den DNS-Namen der VM angeben.
5. Administratorkonto erstellen:
   ```bash
   sudo -u meetingapp bash -c 'set -a; source /etc/meeting-manager.env; set +a; exec /opt/meeting-manager/.venv/bin/python /opt/meeting-manager/manage.py createsuperuser'
   ```
6. Im Browser `http://SERVER-IP/` öffnen (Nginx auf Port 80).

Das Installationsskript installiert PostgreSQL, Nginx und Python-Abhängigkeiten, richtet eine lokale Datenbank sowie den systemd-Dienst `meeting-manager` ein und startet beide Dienste automatisch nach dem Booten. Gunicorn lauscht nur lokal auf Port 8000; Nginx nimmt Verbindungen aus dem LAN auf Port 80 entgegen und liefert statische Dateien aus.

### Dienst verwalten

```bash
sudo systemctl status meeting-manager
sudo systemctl restart meeting-manager
sudo journalctl -u meeting-manager -f
sudo systemctl status nginx
```

Updates nach dem Abruf neuer Änderungen:

```bash
sudo /opt/meeting-manager/deploy/update.sh
```

### Benutzerkonten

Die Anmeldung erfolgt mit persönlichem Benutzernamen und Passwort. Unbekannte Benutzernamen werden nicht automatisch angelegt. Administratoren legen Konten im Menüpunkt „Benutzer“ an, aktivieren/deaktivieren sie, vergeben Administratorrechte und setzen Passwörter zurück. Der erste Administrator wird mit `createsuperuser` eingerichtet. Superuser-Konten bleiben zusätzlich geschützt.

### Netzwerkdateien / NAS

Netzwerkfreigaben werden auf der **VM selbst** gemountet. Beispiel: NAS-Freigabe nach `/mnt/meeting-share` mounten und diesen Pfad in den Themen als Netzwerkpfad hinterlegen. SMB-Pfade werden als Referenz gespeichert; Browser öffnen SMB-Pfade nicht zuverlässig direkt. Uploads liegen unter `/opt/meeting-manager/media`.

### Backups

Mindestens PostgreSQL und den Upload-Ordner `/opt/meeting-manager/media` regelmäßig sichern. Beispiel für einen Datenbank-Dump:

```bash
sudo -u postgres pg_dump meeting_manager > meeting_manager-$(date +%F).sql
```

## Aktueller Funktionsumfang

- Besprechungsreihen und automatische Terminserien (wöchentlich, 14-tägig, monatlich); Verwaltung nur für Staff/Admin.
- Gemeinsamer Terminkalender für alle Nutzer; Administratoren können einzelne Termine hinzufügen, verschieben, löschen und zukünftige Serientermine ergänzen.
- Themen mit Fälligkeitsdatum, Status und Zuordnung zu einer Reihe.
- Fällige Themen werden beim Öffnen eines Meetings in die Tagesordnung übernommen; offene Themen aus dem letzten abgeschlossenen Meeting werden weitergeführt.
- Tagesordnungstext kann pro Meeting bearbeitet werden.
- Beim administrativen Abschluss wird ein Protokoll-Snapshot gespeichert; Protokolle können alle angemeldeten Benutzer drucken.
- Uploads und mehrere Netzwerkpfad-/Link-Referenzen pro Thema.
- Themen können archiviert und wieder geöffnet werden.
- Themen können in eine andere Besprechungsreihe übertragen werden; die Übertragung wird mit Zeit, Benutzer und optionaler Notiz protokolliert.
- Anmeldung mit Benutzername und Passwort; Benutzerkonten werden nicht automatisch angelegt.\n- Benutzerverwaltung für Administratoren: Konten anlegen, bearbeiten, deaktivieren/reaktivieren, Adminrechte vergeben und Passwörter zurücksetzen. Normale Benutzer haben keinen Zugriff auf diese Funktionen.

## Sicherheit und Grenzen

**Die Anwendung ist weiterhin ein MVP und noch nicht produktionsreif.** Vor produktivem Einsatz bitte HTTPS und Firewall einsetzen, Backups einrichten, die Benutzerverwaltung testen und automatisierte Tests ausführen. Port 80 nur im internen Netz freigeben. Hochgeladene Dateien werden derzeit über Nginx direkt aus dem Media-Verzeichnis ausgeliefert und sollten daher keine vertraulichen Inhalte enthalten. Passwörter werden von Django gehasht gespeichert.

Weitere Ausbauschritte: sichere Downloadberechtigungen für vertrauliche Uploads, durchgängige Audit-Historie und erweiterte automatisierte CI-Tests.

## Datenbankschema

Die Anwendung verwendet versionierte Django-Migrationsdateien. Bei bestehenden Installationen übernimmt `migrate --fake-initial` vorhandene Tabellen, während neue Migrationen fehlende Tabellen ergänzen. Vor jedem Update sollte trotzdem ein PostgreSQL-Backup erstellt werden.
