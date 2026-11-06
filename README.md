# Meeting Manager

Django-Anwendung für wiederkehrende Besprechungen, Themenlisten und druckbare Protokolle. Oberfläche und Zeitzone sind auf Deutsch bzw. Europe/Berlin eingestellt.

## Installation ohne Docker (Debian/Ubuntu-VM auf Proxmox)

Die Anwendung läuft direkt auf Linux: Python-Virtualenv + Gunicorn + PostgreSQL + systemd. Es werden weder Docker noch Docker Compose benötigt.

### Schnellinstallation

1. Eine Debian- oder Ubuntu-VM auf Proxmox bereitstellen und per SSH anmelden.
2. Repository nach dem Merge dieses Pull Requests klonen:
   `git clone https://github.com/k2home/meeting.git`
3. In das Verzeichnis wechseln und Installationsskript ausführen:
   ```bash
   cd meeting
   sudo bash deploy/install-debian.sh
   ```
4. Im Skript die angezeigte Server-IP/den Hostnamen als `ALLOWED_HOSTS` eintragen, falls danach gefragt.
5. Administratorkonto erstellen:
   ```bash
   sudo -u meetingapp /opt/meeting-manager/.venv/bin/python /opt/meeting-manager/manage.py createsuperuser
   ```
6. Im Browser `http://SERVER-IP:8000` öffnen.

Das Installationsskript installiert PostgreSQL und Python-Abhängigkeiten, richtet eine lokale Datenbank und den Systemdienst `meeting-manager` ein und startet die Anwendung automatisch nach dem Booten.

### Dienst verwalten

```bash
sudo systemctl status meeting-manager
sudo systemctl restart meeting-manager
sudo journalctl -u meeting-manager -f
```

Updates nach dem Merge neuer Änderungen:

```bash
sudo /opt/meeting-manager/deploy/update.sh
```

### Netzwerkdateien / NAS

Netzwerkfreigaben werden auf dem **Linux-Host/der VM** gemountet, nicht in einem Container. Beispiel: NAS-Freigabe nach `/mnt/meeting-share` mounten und diesen Pfad in den Themen als Netzwerkpfad hinterlegen. Falls die Anwendung später Dateien direkt ausliefern soll, muss der Pfad zusätzlich mit passenden Leserechten für den Dienstbenutzer eingebunden werden. Browser öffnen SMB-Pfade nicht zuverlässig direkt.

### Backups

Mindestens PostgreSQL und den Upload-Ordner `/opt/meeting-manager/media` regelmäßig sichern. Beispiel für einen Datenbank-Dump:

```bash
sudo -u postgres pg_dump meeting_manager > meeting_manager-$(date +%F).sql
```

## Funktionsumfang dieses ersten MVP

- Besprechungsreihen und automatische Terminserien (wöchentlich, 14-tägig, monatlich); Verwaltung nur für Staff/Admin.
- Themen mit Fälligkeitsdatum, Status und Zuordnung zu einer Reihe.
- Fällige Themen werden beim Öffnen eines Meetings in die Tagesordnung übernommen.
- Tagesordnungstext kann pro Meeting bearbeitet werden.
- Beim administrativen Abschluss wird ein Protokoll-Snapshot gespeichert; Protokolle können alle angemeldeten Benutzer drucken.
- Uploads und mehrere Netzwerkpfad-/Link-Referenzen pro Thema.

## Sicherheit und Grenzen

**Dies ist ein MVP und noch nicht produktionsreif.** Die aktuelle Anmeldung akzeptiert nur einen Benutzernamen und legt unbekannte Namen automatisch an. Das ist keine belastbare Identitätsprüfung und erlaubt Identitätsübernahme im LAN. Vor produktivem Einsatz bitte Passwort-/SSO-Login aktivieren, HTTPS und Firewall einsetzen, Backups einrichten und Tests ergänzen. Port 8000 nur im internen Netz freigeben.

Weitere geplante Ausbauschritte: komfortable Terminänderung und -vorschau, expliziter Themen-Transfer mit Historie zwischen Reihen, Themenarchiv/Wiedereröffnung, Benutzerverwaltung in der Oberfläche, Berechtigungs-/Audit-Tests und automatisierte CI-Tests.

## Hinweis zum Datenbankschema

Das Erstinstallationsskript erstellt die Tabellen für den aktuellen MVP-Stand. Für spätere Modelländerungen müssen reguläre Django-Migrationen erzeugt und mit dem Update ausgerollt werden.
