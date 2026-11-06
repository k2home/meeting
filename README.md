# Meeting Manager

Django/PostgreSQL-Anwendung für wiederkehrende Besprechungen, Themenlisten und druckbare Protokolle. Oberfläche und Zeitzone sind auf Deutsch bzw. Europe/Berlin eingestellt.

## Start auf Proxmox (Docker in einer Debian/Ubuntu-VM)

1. Repository in die VM klonen.
2. `.env.example` nach `.env` kopieren und mindestens `SECRET_KEY`, `POSTGRES_PASSWORD` und `ALLOWED_HOSTS` ändern.
3. `docker compose up -d --build`
4. Admin-Konto anlegen: `docker compose exec web python manage.py createsuperuser`
5. Weboberfläche auf Port 8000 öffnen.

Datenbank und Uploads liegen in Docker-Volumes. Der Ordner `./network-files` wird read-only nach `/network-files` eingebunden. Für ein NAS diesen Ordner in der VM entsprechend mounten, bevor Compose gestartet wird. Netzwerkpfade werden als Referenz angezeigt; SMB-Freigaben lassen sich nicht zuverlässig direkt aus jedem Browser öffnen.

## Funktionsumfang dieses ersten MVP

- Besprechungsreihen und automatische Terminserien (wöchentlich, 14-tägig, monatlich); Verwaltung nur für Staff/Admin.
- Themen mit Fälligkeitsdatum, Status und Zuordnung zu einer Reihe.
- Fällige Themen werden beim Öffnen eines Meetings in die Tagesordnung übernommen.
- Tagesordnungstext kann pro Meeting bearbeitet werden.
- Beim administrativen Abschluss wird ein Protokoll-Snapshot gespeichert; Protokolle können alle angemeldeten Benutzer drucken.
- Uploads und mehrere Netzwerkpfad-/Link-Referenzen pro Thema.

## Wichtige Grenzen / Sicherheit

**Dies ist ein MVP und noch nicht produktionsreif.** Die aktuelle Anmeldung akzeptiert nur einen Benutzernamen und legt unbekannte Namen automatisch an. Das ist keine belastbare Identitätsprüfung und erlaubt Identitätsübernahme im LAN. Vor produktivem Einsatz bitte Passwort-/SSO-Login aktivieren, HTTPS und Firewall einsetzen, Backups einrichten und Tests ergänzen.

Weitere geplante Ausbauschritte: komfortable Terminänderung und -vorschau, expliziter Themen-Transfer mit Historie zwischen Reihen, Themenarchiv/Wiedereröffnung, Benutzerverwaltung in der Oberfläche, Berechtigungs-/Audit-Tests und automatisierte CI-Tests.