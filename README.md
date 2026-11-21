# Meeting Manager

Django-Anwendung zur Verwaltung wiederkehrender Besprechungen, offener Themen, Tagesordnungen und nachvollziehbarer Besprechungsprotokolle. Die Benutzeroberfläche ist deutschsprachig; als Zeitzone ist standardmäßig `Europe/Berlin` konfiguriert.

- **Betrieb:** Debian-/Ubuntu-VM, z. B. auf Proxmox
- **Stack:** Django, PostgreSQL, Gunicorn und Nginx
- **Installation:** direkt auf Linux, ohne Docker
- **Zugriff:** für interne Netze vorgesehen

## Inhaltsverzeichnis

- [Funktionsübersicht](#funktionsübersicht)
- [Rollen und Berechtigungen](#rollen-und-berechtigungen)
- [Benutzer und Serienzuweisungen verwalten](#benutzer-und-serienzuweisungen-verwalten)
- [Installation](#installation)
- [Updates und Betrieb](#updates-und-betrieb)
- [Arbeitsabläufe in der Anwendung](#arbeitsabläufe-in-der-anwendung)
- [Netzwerkfreigaben und Anlagen](#netzwerkfreigaben-und-anlagen)
- [Backup und Wiederherstellung](#backup-und-wiederherstellung)
- [Sicherheit und bekannte Grenzen](#sicherheit-und-bekannte-grenzen)
- [Entwicklung und Tests](#entwicklung-und-tests)
- [Datenbankmigrationen](#datenbankmigrationen)
- [Fehlerbehebung](#fehlerbehebung)

## Funktionsübersicht

### Besprechungsreihen und Termine

- Wiederkehrende Reihen mit wöchentlichem, 14-tägigem oder monatlichem Rhythmus.
- Automatische Erzeugung der Besprechungstermine anhand von Startdatum, Wochentag und optionalem Enddatum.
- Einzelne noch nicht abgeschlossene Termine können verschoben werden.
- Leere, noch nicht bearbeitete Einzeltermine können gelöscht werden.
- Besprechungsreihen können von Moderator*innen und Admins verwaltet werden.

### Themen und Aufgaben

- Themen mit Beschreibung, Fälligkeitsdatum, Status, Besprechungsreihe und verantwortlicher Person.
- Suche über Titel, Beschreibung, Reihe und verantwortliche Person.
- Filter nach Status, Reihe, Zuständigkeit und Fälligkeit.
- Themen können archiviert, wieder geöffnet und zwischen zugänglichen Besprechungsreihen übertragen werden.
- Kommentare und nächste Schritte werden chronologisch am Thema gesammelt.
- „Meine Aufgaben“ zeigt die einer angemeldeten Person zugewiesenen offenen Themen.
- Anlagen können als Datei oder als Netzwerkpfad bzw. Link hinterlegt werden.

### Tagesordnung und Protokolle

- Fällige Themen werden beim Öffnen einer Besprechung in die Tagesordnung übernommen.
- Offene Themen aus dem letzten abgeschlossenen Termin werden weitergeführt.
- Tagesordnungspunkte lassen sich per Drag-and-drop oder über die Pfeil-Schaltflächen sortieren.
- Tagesordnungstexte und Teilnehmerliste können bis zum Abschluss bearbeitet werden.
- Beim Abschluss wird ein unveränderlicher Protokoll-Snapshot gespeichert.
- Protokolle können als HTML angezeigt, gedruckt sowie als PDF oder Word-Dokument exportiert werden.
- Exporte abgeschlossener Besprechungen verwenden den gesicherten Snapshot.

### Änderungsverlauf

Wichtige Änderungen an Themen, Status, Fälligkeiten, Anlagen, Kommentaren, Tagesordnungstexten und Besprechungsabschlüssen werden mit Benutzer und Zeitpunkt protokolliert. Der Änderungsverlauf ist innerhalb der jeweils zugänglichen Besprechungsreihen einsehbar.

## Rollen und Berechtigungen

Die Anwendung verwendet vier Django-Gruppen. Die Gruppe eines Kontos bestimmt die Rolle; zusätzlich wird jeder regulären Benutzerin bzw. jedem regulären Benutzer ausdrücklich zugewiesen, auf welche Besprechungsreihen sie oder er zugreifen darf.

### Berechtigungsmatrix

| Funktion | Leser*in | Nutzer*in | Moderator*in | Admin |
|---|:---:|:---:|:---:|
| Zugewiesene Besprechungsreihen und deren Inhalte ansehen | Ja | Ja | Ja | Alle Reihen |
| Protokolle und Änderungsverlauf ansehen | Ja | Ja | Ja | Alle Reihen |
| Kommentare schreiben | Nein | Ja | Ja | Ja |
| Themen anlegen und bearbeiten | Nein | Ja | Ja | Ja |
| Themen archivieren und wieder öffnen | Nein | Ja | Ja | Ja |
| Themen zwischen zugänglichen Reihen übertragen | Nein | Ja | Ja | Ja |
| Tagesordnung und Teilnehmer verwalten | Nein | Ja | Ja | Ja |
| Besprechungen abschließen | Nein | Ja | Ja | Ja |
| Abgeschlossene Besprechungen wieder öffnen | Nein | Nein | Ja | Ja |
| Besprechungstermine verschieben oder löschen | Nein | Nein | Ja | Ja |
| Besprechungsreihen anlegen, ändern und löschen | Nein | Nein | Ja* | Ja |
| Benutzer, Gruppen und Serienzuweisungen verwalten | Nein | Nein | Nein | Ja |
| Globaler Zugriff auf alle Besprechungsreihen | Nein | Nein | Nein | Ja |

\* Moderator*innen dürfen nur die ihnen zugewiesenen Reihen verwalten. Eine von einer Moderatorin oder einem Moderator neu angelegte Reihe wird dieser Person automatisch zugewiesen.

### Was die Rollen im Alltag bedeuten

**Leser*in**

- Sieht alle Themen, Besprechungstermine, Protokolle und Änderungsverläufe der ausdrücklich zugewiesenen Besprechungsreihen.
- Ist kein Besprechungsteilnehmer und erscheint nicht in Teilnehmerlisten oder Protokoll-Teilnehmerangaben.
- Hat ausschließlich Leserechte: keine Kommentare, Änderungen, Anlagen, Tagesordnungsaktionen, Abschlüsse oder Verwaltungsfunktionen.

**Nutzer*in**

- Sieht ausschließlich die ausdrücklich zugewiesenen Besprechungsreihen.
- Kann innerhalb dieser Reihen Themen anlegen und bearbeiten, Themen archivieren oder übertragen, Kommentare schreiben und Tagesordnungen sowie Teilnehmer verwalten.
- Kann Besprechungen abschließen, aber nicht wieder öffnen.
- Kann keine Besprechungsreihen oder Benutzerkonten verwalten.

**Moderator*in**

- Hat innerhalb der eigenen zugewiesenen Reihen dieselben fachlichen Rechte wie Nutzer*innen.
- Kann zusätzlich abgeschlossene Besprechungen wieder öffnen.
- Kann eigene zugewiesene Besprechungsreihen anlegen, ändern und löschen sowie deren Termine verwalten.
- Kann nicht auf fremde, nicht zugewiesene Reihen zugreifen und keine Benutzerrollen oder Serienzuweisungen anderer Konten verwalten.

**Admin**

- Hat Zugriff auf alle Besprechungsreihen und deren Inhalte.
- Kann Besprechungsreihen, Benutzerkonten, Gruppen und Serienzuweisungen global verwalten.
- Kann alle Besprechungen abschließen und wieder öffnen.
- Die Admin-Rolle wird über die Gruppe **Admin** vergeben. Django-Superuser haben ebenfalls globalen Zugriff.

### Wichtig: Rolle und Serienzuweisung sind zwei getrennte Dinge

Eine Rolle allein gewährt Nutzer*innen und Moderator*innen keinen Zugriff auf sämtliche Reihen. Der Zugriff wird zusätzlich pro Benutzerkonto und Besprechungsreihe eingetragen. Dadurch können Personen derselben Rolle unterschiedliche Reihen sehen.

Bei der Einführung der Serienberechtigungen werden bestehende Konten automatisch zugeordnet:

- Bisherige Staff-Konten erhalten die Gruppe **Admin**.
- Andere bestehende Konten erhalten die Gruppe **Nutzer*in**.
- Bestehende Nicht-Admin-Konten erhalten zunächst Zugriff auf alle zu diesem Zeitpunkt vorhandenen Besprechungsreihen. So bleibt der bisherige Zugriff nach dem Update erhalten. Diese Zuweisungen können anschließend auf die tatsächlich benötigten Reihen eingeschränkt werden.

Neue Benutzerkonten benötigen eine Rolle und – sofern sie kein Admin sind – mindestens eine Serienzuweisung.

## Benutzer und Serienzuweisungen verwalten

Die Verwaltung befindet sich unter `/django-admin/` und ist nur für Admins bzw. Django-Superuser vorgesehen.

1. Mit einem Admin-Konto anmelden und **Verwaltung** öffnen.
2. Unter **Benutzer** ein neues Konto anlegen oder ein vorhandenes Konto öffnen.
3. Im Bereich **Gruppen** genau die gewünschte Rolle auswählen: **Leser*in**, **Nutzer*in**, **Moderator*in** oder **Admin**.
4. Im Inline-Bereich **Serienberechtigungen** die Besprechungsreihen hinzufügen, die das Konto sehen und bearbeiten darf.
5. Änderungen speichern.

Die Serienzuweisungen können alternativ direkt an einer Besprechungsreihe im Bereich **Besprechungsreihen** gepflegt werden. Beide Ansichten bearbeiten dieselben Zuordnungen.

**Empfehlung:** Admin nur an wenige verantwortliche Personen vergeben. Für alle anderen Konten Nutzer*in oder Moderator*in auswählen und den Zugriff auf die benötigten Reihen begrenzen.

## Installation

### Voraussetzungen

- Debian- oder Ubuntu-VM (beispielsweise unter Proxmox)
- SSH- bzw. Konsolenzugriff mit sudo-Rechten
- Eine feste IP-Adresse oder ein DNS-Name für die Anwendung
- Zugriff auf das interne Netzwerk, in dem die Anwendung genutzt werden soll

Die Installation richtet PostgreSQL, Nginx, Python-Abhängigkeiten, eine virtuelle Python-Umgebung, den systemd-Dienst und die Verzeichnisse der Anwendung ein.

### Schnellinstallation

1. Eine Debian-/Ubuntu-VM bereitstellen und per SSH anmelden.
2. Repository klonen:

   ```bash
   git clone https://github.com/k2home/meeting.git
   cd meeting
   ```

3. Installationsskript starten:

   ```bash
   sudo bash deploy/install-debian.sh
   ```

4. Während der Installation die IP-Adresse oder den DNS-Namen eingeben, unter dem die Website erreichbar sein soll.
5. Ein erstes Administratorkonto anlegen:

   ```bash
   sudo -u meetingapp bash -c 'set -a; source /etc/meeting-manager.env; set +a; exec /opt/meeting-manager/.venv/bin/python /opt/meeting-manager/manage.py createsuperuser'
   ```

6. Im Browser `http://SERVER-IP/` öffnen und mit dem Superuser anmelden.

Das Installationsskript erstellt die Datenbank `meeting_manager`, das Datenbankkonto `meetingapp` und die Konfigurationsdatei `/etc/meeting-manager.env`. Das Passwort der Datenbank und der Django-`SECRET_KEY` werden zufällig erzeugt. Gunicorn lauscht nur auf `127.0.0.1:8000`; Nginx nimmt HTTP-Verbindungen auf Port 80 entgegen.

### Wichtige Pfade und Dienste

| Zweck | Pfad / Name |
|---|---|
| Installationsverzeichnis | `/opt/meeting-manager` |
| Konfiguration und Zugangsdaten | `/etc/meeting-manager.env` |
| Hochgeladene Dateien | `/opt/meeting-manager/media` |
| Statische Dateien | `/opt/meeting-manager/staticfiles` |
| PostgreSQL-Datenbank | `meeting_manager` |
| PostgreSQL-Benutzer | `meetingapp` |
| systemd-Dienst | `meeting-manager` |
| Nginx-Konfiguration | `/etc/nginx/sites-available/meeting-manager` |

Die Datei `/etc/meeting-manager.env` enthält Geheimnisse. Sie darf nicht öffentlich geteilt oder in Git eingecheckt werden.

## Updates und Betrieb

### Anwendung aktualisieren

Auf der VM wird die Anwendung im Verzeichnis `/opt/meeting-manager` aktualisiert. Vorher sollte ein aktuelles Backup vorhanden sein.

```bash
sudo bash /opt/meeting-manager/deploy/update.sh
```

Das Skript:

1. Holt Änderungen des aktuell ausgecheckten Git-Branches mit `git pull --ff-only`.
2. Installiert bzw. aktualisiert Python-Abhängigkeiten.
3. Führt ausstehende Datenbankmigrationen aus.
4. Sammelt statische Dateien für Nginx.
5. Startet den Dienst `meeting-manager` neu und zeigt dessen Status an.

Das Skript aktualisiert den Branch, der auf dem Server ausgecheckt ist. Für den regulären Betrieb sollte das der freigegebene Hauptbranch sein.

### Dienste und Protokolle

```bash
# Anwendungsdienst prüfen
sudo systemctl status meeting-manager

# Anwendung neu starten
sudo systemctl restart meeting-manager

# Anwendungsprotokoll live verfolgen
sudo journalctl -u meeting-manager -f

# Nginx prüfen
sudo systemctl status nginx

# Nginx-Konfiguration testen
sudo nginx -t
```

### Django-Verwaltungsbefehle manuell ausführen

Für manuelle `manage.py`-Befehle müssen die Umgebungsvariablen aus der Konfigurationsdatei geladen werden:

```bash
sudo -u meetingapp bash -c 'set -a; source /etc/meeting-manager.env; set +a; exec /opt/meeting-manager/.venv/bin/python /opt/meeting-manager/manage.py showmigrations'
```

Dasselbe Muster gilt für weitere `manage.py`-Befehle, zum Beispiel `check` oder `test`. So werden dieselben Umgebungsvariablen und Dateiberechtigungen wie beim Anwendungsdienst verwendet. Keine Zugangsdaten direkt in Befehlszeilen oder Tickets schreiben.

## Arbeitsabläufe in der Anwendung

### 1. Besprechungsreihe anlegen

Moderator*innen öffnen **Besprechungsreihen** in der Navigation. Dort werden Name, Beschreibung, Wiederholungsrhythmus, Wochentag sowie Start- und optionales Enddatum festgelegt. Beim Speichern erzeugt die Anwendung die zugehörigen Termine. Die neu angelegte Reihe wird der erstellenden Moderatorin bzw. dem erstellenden Moderator automatisch zugewiesen.

### 2. Themen pflegen

Über **Neues Thema** oder die Themenübersicht lassen sich Titel, Beschreibung, Fälligkeit, Status, Besprechungsreihe und verantwortliche Person pflegen. Die auswählbaren Reihen sind auf die eigenen Zuweisungen begrenzt. Kommentare, Anlagen und Netzwerkpfade werden direkt am Thema gesammelt.

### 3. Besprechung vorbereiten und durchführen

In der Übersicht einen Termin öffnen. Dort können Teilnehmende ausgewählt und Tagesordnungstexte bearbeitet werden. Tagesordnungspunkte lassen sich per Ziehen oder über die Pfeiltasten sortieren. Die Änderungen werden gespeichert, solange die Besprechung noch nicht abgeschlossen ist.

### 4. Besprechung abschließen

Mit **Besprechung abschließen & Protokollstand sichern** wird ein Snapshot des aktuellen Protokollstands erstellt. Danach sind Teilnehmerliste und Tagesordnungstexte gesperrt. Das Protokoll kann angezeigt, gedruckt oder als PDF bzw. Word exportiert werden.

Nur Moderator*innen und Admins können eine abgeschlossene Besprechung wieder öffnen. Nach dem Wiederöffnen kann sie erneut bearbeitet und abgeschlossen werden.

### 5. Aufgaben nachverfolgen

Die Seite **Meine Aufgaben** zeigt die offenen Themen, die dem angemeldeten Konto zugewiesen sind. Die Themenübersicht und der Änderungsverlauf berücksichtigen stets die eigenen Serienberechtigungen.

## Netzwerkfreigaben und Anlagen

Netzwerkfreigaben werden auf der **VM selbst** eingebunden, nicht auf dem Arbeitsplatz des Benutzers. Beispiel: Eine NAS-Freigabe nach `/mnt/meeting-share` mounten und diesen Pfad am Thema hinterlegen.

SMB-Pfade werden als Referenz gespeichert. Browser können SMB-Pfade nicht zuverlässig direkt öffnen; die Freigabe muss auf dem jeweiligen Arbeitsplatz erreichbar sein. Hochgeladene Dateien liegen unter `/opt/meeting-manager/media`.

## Backup und Wiederherstellung

Mindestens die PostgreSQL-Datenbank und das gesamte Upload-Verzeichnis `/opt/meeting-manager/media` regelmäßig und getrennt vom Anwendungsserver sichern. Backups sollten verschlüsselt und gegen unbefugten Zugriff geschützt aufbewahrt werden.

### Datenbank sichern

```bash
sudo -u postgres pg_dump meeting_manager | sudo tee meeting_manager-$(date +%F).sql > /dev/null
```

### Uploads sichern

Beispiel mit `tar`:

```bash
sudo tar -czf meeting-media-$(date +%F).tar.gz -C /opt/meeting-manager media
```

### Datenbank wiederherstellen

Die Wiederherstellung überschreibt Daten in der Zieldatenbank. Vorher sicherstellen, dass die richtige Datenbank ausgewählt ist und ein zusätzlicher Sicherungsstand existiert.

```bash
sudo -u postgres psql -d meeting_manager < meeting_manager-YYYY-MM-DD.sql
```

Anschließend das passende Media-Backup nach `/opt/meeting-manager/media` zurückspielen und die Eigentümerrechte prüfen. Datenbank und Media-Verzeichnis müssen aus zueinander passenden Sicherungszeitpunkten stammen.

## Sicherheit und bekannte Grenzen

**Die Anwendung ist ein internes MVP und sollte vor einem produktiven Einsatz weiter gehärtet werden.**

- Zugriff auf das interne Netzwerk begrenzen und eine Firewall einsetzen.
- Für Zugriffe über nicht vertrauenswürdige Netze HTTPS mit gültigem Zertifikat konfigurieren. Die Standardinstallation verwendet HTTP.
- Regelmäßige, getestete Backups von Datenbank und Media-Verzeichnis einrichten.
- Admin-Rechte nur gezielt vergeben und Serienzuweisungen regelmäßig überprüfen.
- Hochgeladene Dateien werden derzeit über Nginx aus dem Media-Verzeichnis ausgeliefert. Dort keine Dateien ablegen, die unabhängig von der Anwendung vertraulich bleiben müssen.
- Passwörter werden durch Django gehasht gespeichert. Zugangsdaten und `SECRET_KEY` gehören ausschließlich in die geschützte Umgebungsdatei.
- Vor produktivem Einsatz automatisierte Tests und die Berechtigungen mit separaten Testkonten aller drei Rollen prüfen.

Screenshots sind derzeit nicht eingebettet: Die Anwendung wird in einem geschützten internen Netz betrieben und für diese Dokumentationsänderung stand keine authentifizierte Browser-Sitzung zur Verfügung. Es werden deshalb keine nachgebildeten Bilder als echte Anwendungsansichten ausgegeben. Sinnvolle spätere Screenshots wären die Übersicht, eine Besprechung mit Tagesordnung, die Themenbearbeitung und die Benutzer-/Serienzuweisung in der Verwaltung. Vor dem Einchecken sollten Namen, Kommentare und andere personenbezogene bzw. vertrauliche Daten unkenntlich gemacht werden.

## Entwicklung und Tests

### Lokale Umgebung

Die Anwendung benötigt Python-Abhängigkeiten aus `requirements.txt` sowie eine konfigurierte Datenbank. Für die produktive Installation werden PostgreSQL und die Umgebungsvariablen aus `/etc/meeting-manager.env` verwendet.

### Django-Prüfungen und Tests

Im aktivierten Virtualenv und mit geladener Konfiguration:

```bash
sudo -u meetingapp bash -c 'set -a; source /etc/meeting-manager.env; set +a; exec /opt/meeting-manager/.venv/bin/python /opt/meeting-manager/manage.py check'
sudo -u meetingapp bash -c 'set -a; source /etc/meeting-manager.env; set +a; exec /opt/meeting-manager/.venv/bin/python /opt/meeting-manager/manage.py test'
```

Die Berechtigungstests liegen in `meetings/test_permissions.py`; weitere Anwendungstests liegen in `meetings/tests.py`.

## Datenbankmigrationen

Das Datenbankschema wird mit versionierten Django-Migrationen verwaltet. Neue Migrationen liegen unter `meetings/migrations/` und werden beim regulären Update automatisch mit `manage.py migrate` angewendet.

Die Migration `0006_series_access_and_roles` ergänzt die expliziten Serienzuweisungen und richtet die drei Rollen-Gruppen ein. Sie erhält den bisherigen Zugriff bestehender Konten, indem Nicht-Admin-Konten zunächst allen bereits vorhandenen Reihen zugeordnet werden. Die Zuordnungen können danach durch Admins eingeschränkt werden.

Migrationen nicht manuell aus der Datenbank löschen und nicht mit `migrate --fake` überspringen, außer wenn ein bewusst geplanter und geprüfter Reparaturvorgang dies erfordert.
