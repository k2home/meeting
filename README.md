# Meeting Manager

Django-Anwendung zur Verwaltung wiederkehrender Besprechungen, offener Themen, Tagesordnungen und nachvollziehbarer Besprechungsprotokolle. Die Benutzeroberfläche ist deutschsprachig; als Zeitzone ist standardmäßig `Europe/Berlin` konfiguriert.

- **Betrieb:** Debian-/Ubuntu-VM, z. B. auf Proxmox, oder Docker-Host
- **Stack:** Django, PostgreSQL, Gunicorn und Nginx
- **Installation:** direkt auf Linux oder containerisiert mit Docker Compose
- **Zugriff:** für interne Netze vorgesehen

## Inhaltsverzeichnis

- [Installation](#installation)
  - [Docker Compose](#docker-compose)
  - [Debian / Ubuntu](#debian--ubuntu-mit-systemd-und-nginx)
- [Funktionsübersicht](#funktionsübersicht)
- [Rollen und Berechtigungen](#rollen-und-berechtigungen)
- [Benutzer und Serienzuweisungen verwalten](#benutzer-und-serienzuweisungen-verwalten)
- [Verwaltungsoberfläche](#verwaltungsoberfläche)
- [Updates und Betrieb](#updates-und-betrieb)
- [Arbeitsabläufe in der Anwendung](#arbeitsabläufe-in-der-anwendung)
- [Netzwerkfreigaben und Anlagen](#netzwerkfreigaben-und-anlagen)
- [Backup und Wiederherstellung](#backup-und-wiederherstellung)
- [Sicherheit und bekannte Grenzen](#sicherheit-und-bekannte-grenzen)
- [Entwicklung und Tests](#entwicklung-und-tests)
- [Datenbankmigrationen](#datenbankmigrationen)
- [Fehlerbehebung](#fehlerbehebung)

## Installation

### Docker Compose

Das Anwendungsimage wird über Docker Hub unter [`k2hadocker/meeting-manager`](https://hub.docker.com/r/k2hadocker/meeting-manager) bereitgestellt. GitHub Actions veröffentlicht das Image automatisch: `latest` bei Änderungen auf `main`, `beta` bei Änderungen auf `beta` sowie Versions-Tags bei veröffentlichten GitHub-Releases. Die Images werden für `linux/amd64` und `linux/arm64` gebaut. Die bisherige Veröffentlichung in der GitHub Container Registry (GHCR) bleibt parallel bestehen. Für ein öffentliches Docker-Hub-Repository ist beim Installieren keine Anmeldung erforderlich.

Docker ist eine alternative Bereitstellungsvariante. Beide Installationsarten verwenden denselben Anwendungscode und dieselben Datenbankmigrationen.

**Voraussetzungen**

- Linux-Host oder VM mit Docker Engine und Docker Compose v2
- Netzwerkzugriff auf Docker Hub
- Für den Betrieb erforderlich: ein auf demselben Host eingerichteter HTTPS-Reverse-Proxy mit gültigem TLS-Zertifikat

**Installation**

1. Repository nach `/opt/meeting-manager` klonen:

   ```bash
   sudo git clone https://github.com/k2home/meeting.git /opt/meeting-manager
   cd /opt/meeting-manager
   ```

2. Das öffentliche Docker-Hub-Image kann ohne Anmeldung geladen werden. Falls das Repository in Docker Hub auf **privat** gestellt wurde, vorher als Docker-Hub-Benutzer `k2hadocker` anmelden:

   ```bash
   sudo docker login --username k2hadocker
   ```

   Das Passwort bzw. den Docker-Hub-Access-Token anschließend interaktiv eingeben. Nicht als Klartext in den Befehl schreiben.

3. Den Installer starten:

   ```bash
   sudo bash deploy/install-docker.sh
   ```

   Das Skript fragt nur nach dem Hostnamen bzw. der IP-Adresse. `SECRET_KEY` und Datenbankpasswort werden automatisch kryptografisch zufällig erzeugt und mit restriktiven Dateirechten in `.env` gespeichert. Ein Aktivierungs- oder Einrichtungscode ist nicht erforderlich. Der Installer richtet den eingeschränkten Host-Updater ein, lädt die Images und startet die Container.

4. Der Web-Port wird standardmäßig ausschließlich an `127.0.0.1:8080` gebunden und ist nicht direkt aus dem Netzwerk erreichbar. Einen HTTPS-Reverse-Proxy auf demselben Host einrichten und auf `http://127.0.0.1:8080` weiterleiten. Danach die Anwendung über `https://<HOSTNAME>/` öffnen.

5. Beim ersten Aufruf im Browser startet automatisch der Ersteinrichtungsassistent. Dort wird das erste Administratorkonto angelegt, anschließend werden Organisation und Systemstatus eingerichtet. Ein manueller Django- oder Shell-Befehl ist nicht erforderlich.

**Daten und Persistenz**

- PostgreSQL-Daten liegen im benannten Volume `postgres_data`.
- Hochgeladene Dateien liegen im Volume `media_data`.
- Statische Dateien liegen im Volume `static_data` und werden vom Nginx-Container ausgeliefert.
- Diese Daten bleiben beim Ersetzen oder Aktualisieren der Container erhalten. `docker compose down -v` löscht dagegen die benannten Volumes und damit Datenbank und Uploads – diesen Befehl nicht für normale Updates verwenden.

**Updater und Betrieb**

Der Installer richtet den lokalen Unix-Socket-Updater ein. Nur der Anwendungscontainer erhält Zugriff auf diesen Socket; der Docker-Socket des Hosts wird niemals in einen Container eingebunden. Der Updater listet alle aktuell im Git-Remote verfügbaren Branches. Für jeden gepushten Branch wird ein passendes Image veröffentlicht; Schrägstriche im Branch-Namen werden im Image-Tag durch Bindestriche ersetzt.

```bash
docker compose -f docker/compose.yaml ps
docker compose -f docker/compose.yaml logs -f app
docker compose -f docker/compose.yaml restart app
sudo systemctl status meeting-manager-docker-updater.service
```

Vor Updates Datenbank und Upload-Volume sichern. Ein neues Image wird automatisch gebaut und veröffentlicht, wenn Änderungen in `beta` oder `main` übernommen werden. Das laufende System aktualisiert sich nicht selbstständig. Für eine Installation aus GHCR kann `MEETING_IMAGE=ghcr.io/k2home/meeting:latest` in der `.env` gesetzt werden. Das Standardimage bleibt `docker.io/k2hadocker/meeting-manager:latest`. Netzwerkfreigaben (z. B. SMB/NFS) müssen auf dem Docker-Host eingebunden und bei Bedarf gezielt als zusätzliche Bind-Mounts in den Anwendungscontainer eingebunden werden.

### Debian / Ubuntu mit systemd und Nginx

**Voraussetzungen**

- Debian- oder Ubuntu-VM (beispielsweise unter Proxmox)
- SSH- bzw. Konsolenzugriff mit sudo-Rechten
- Eine feste IP-Adresse oder ein DNS-Name für die Anwendung

**One-Click-Installation**

Auf einer frischen Debian-/Ubuntu-Installation können Git installieren, Repository herunterladen und Installationsskript mit diesen Befehlen direkt nacheinander ausgeführt werden:

```bash
sudo apt update
sudo apt install git -y
git clone https://github.com/k2home/meeting.git
cd meeting
sudo bash deploy/install-debian.sh
```

Anschließend fragt der Installer nach dem Hostnamen bzw. der IP-Adresse und der IP-Adresse/CIDR des vorgeschalteten HTTPS-Reverse-Proxys. Standardmäßig wird ein lokaler Proxy unter 127.0.0.1 erwartet.

**Installation im Einzelnen**

1. Repository klonen:

   ```bash
   git clone https://github.com/k2home/meeting.git
   cd meeting
   ```

2. Installationsskript starten:

   ```bash
   sudo bash deploy/install-debian.sh
   ```

3. Hostnamen bzw. IP-Adresse und die IP-Adresse/CIDR des vorgeschalteten HTTPS-Reverse-Proxys eingeben. Das Skript installiert PostgreSQL, Nginx und Python-Abhängigkeiten, erzeugt automatisch `SECRET_KEY` und Datenbankpasswort, richtet die virtuelle Umgebung und den systemd-Dienst ein und führt Migrationen sowie `collectstatic` aus. Für Django 6.1 wird CPython 3.12 verwaltet unter `/opt/meeting-manager-updater/python` installiert (über `uv` und python-build-standalone); das System-Python von Debian 12 bleibt unverändert. Der lokale Nginx-Zugriff wird auf die angegebene Proxy-Adresse begrenzt; HTTPS-Redirect und sichere Cookies werden erzwungen.

4. Zuerst den HTTPS-Reverse-Proxy mit gültigem Zertifikat konfigurieren. Er muss auf Port 8080 dieses Servers weiterleiten (bei lokalem Proxy z. B. `http://127.0.0.1:8080`) und `X-Forwarded-Proto: https` setzen sowie eingehende Forwarded-Header überschreiben. Danach `https://<HOSTNAME>/` im Browser öffnen. Der Browser-Ersteinrichtungsassistent startet automatisch, solange noch kein Benutzerkonto existiert. Dort wird das erste Administratorkonto ohne zusätzlichen Aktivierungscode angelegt; anschließend werden Organisation und Systemstatus eingerichtet. Ein manueller `createsuperuser`-Befehl ist nicht erforderlich. Während der Ersteinrichtung darf die Anwendung nur im vertrauenswürdigen internen Netz bzw. für den einrichtenden Administrator erreichbar sein, da das erste Konto globale Administratorrechte erhält. Sobald es angelegt ist, wird die öffentliche Erstanlage automatisch gesperrt.


Die Datei `/opt/meeting-manager/.env` enthält die automatisch generierten Infrastruktur-Secrets und ist nur für `root` und die Gruppe `www-data` lesbar. Sie darf nicht öffentlich geteilt oder in Git eingecheckt werden. Gunicorn lauscht nur auf `127.0.0.1:8000`; Nginx nimmt HTTP-Verbindungen auf Port 8080 entgegen.

**HTTPS und Reverse Proxy**

Die Installationsskripte richten den Meeting Manager für den Betrieb hinter einem HTTPS-Reverse-Proxy ein und erzwingen HTTPS auf Anwendungsebene. Sie aktivieren `SECURE_SSL_REDIRECT=1`, `SESSION_COOKIE_SECURE=1`, `CSRF_COOKIE_SECURE=1`, `TRUST_PROXY_SSL=1` und `USE_X_FORWARDED_HOST=1`; `CSRF_TRUSTED_ORIGINS` wird auf die öffentliche HTTPS-Adresse gesetzt.

Bei Debian wird der interne Nginx-Zugang auf die beim Setup angegebene Proxy-IP/CIDR beschränkt. Der Nginx übernimmt `X-Forwarded-Proto` nur von diesem Proxy; der Proxy muss den Header auf `https` setzen und vom Client gelieferte Forwarded-Header überschreiben. Bei Docker wird der veröffentlichte Web-Port standardmäßig ausschließlich an `127.0.0.1` gebunden. Der TLS-Reverse-Proxy muss daher auf demselben Host laufen und an `http://127.0.0.1:8080` weiterleiten (einen abweichenden `WEB_PORT` entsprechend berücksichtigen).

Vor dem produktiven Zugriff muss ein gültiges TLS-Zertifikat eingerichtet und die Proxy-Konfiguration getestet werden. Ohne korrekt eingerichteten TLS-Reverse-Proxy ist die Anwendung absichtlich nicht regulär nutzbar. HSTS zunächst mit kurzer Laufzeit testen; `includeSubDomains` und Preload nur aktivieren, wenn die gesamte Domainstruktur die jeweiligen Voraussetzungen dauerhaft erfüllt.



**Python-Laufzeit:** Django 6.1 benötigt Python 3.12 oder neuer. Auf Debian 12 stellt das Installations- und Update-Skript deshalb eine separate, von `uv` verwaltete CPython-3.12-Laufzeit bereit und baut die Anwendungsumgebung bei Bedarf neu auf. Das vom Betriebssystem verwendete Python wird nicht ersetzt. Für diesen Schritt sind Zugriff auf PyPI und die Veröffentlichungen von python-build-standalone auf GitHub erforderlich; in vollständig offline betriebenen Netzen muss die Laufzeit samt Prüfsummen kontrolliert vorab bereitgestellt werden.

### Wichtige Pfade und Dienste

| Zweck | Pfad / Name |
|---|---|
| Installationsverzeichnis | `/opt/meeting-manager` |
| Konfiguration und Zugangsdaten | `/opt/meeting-manager/.env` |
| Hochgeladene Dateien | `/opt/meeting-manager/media` |
| Statische Dateien | `/opt/meeting-manager/staticfiles` |
| PostgreSQL-Datenbank | `meeting_manager` |
| PostgreSQL-Benutzer | `meetingapp` |
| systemd-Dienst | `meeting-manager` |
| Nginx-Konfiguration | `/etc/nginx/sites-available/meeting-manager` |


## Funktionsübersicht

### Besprechungsreihen und Termine

- Wiederkehrende Reihen mit wählbarem wöchentlichem oder monatlichem Rhythmus und Intervall (1–52 Wochen bzw. 1–52 Monate).
- Automatische Erzeugung der Besprechungstermine anhand von Startdatum, Wochentag und optionalem Enddatum.
- Einzelne noch nicht abgeschlossene Termine können verschoben werden.
- Einzelne offene Termine können gelöscht werden. Enthaltene Tagesordnungspunkte und Teilnehmende werden auf den nächsten offenen Termin übertragen; falls nötig wird ein Folgetermin erzeugt. Bei doppelten Tagesordnungspunkten werden Inhalte zusammengeführt.
- Moderator*innen verwalten ausschließlich die ihnen zugewiesenen Besprechungsreihen. Admins können neue Reihen anlegen und dabei einen ersten Moderator festlegen; die laufende fachliche Verwaltung einer bestehenden Reihe setzt eine eigene Moderatorzuweisung voraus.
- Beim Löschen einer Reihe werden zukünftige Entwurfstermine entfernt. Erhaltene historische Termine und Protokolle bleiben für die bisherigen Serienmitglieder lesbar; Admins behalten den globalen Zugriff.

### Themen und Aufgaben

- Themen mit Titel, Status und zuständiger Besprechungsreihe.
- Der Text und Bearbeitungsstand eines Tagesordnungspunkts werden je Besprechungstermin separat gespeichert.
- Abweichende Zuständigkeiten können einzelnen Tagesordnungspunkten zugewiesen werden.
- Suche über Thementitel, Tagesordnungstexte, Besprechungsreihe und Zuständigkeit; Filter nach Status, Reihe und Zuständigkeit.
- Themen können zwischen zugänglichen Besprechungsreihen übertragen werden. Übertragungen erscheinen im Änderungsverlauf der Ursprungs- und Zielreihe.
- Moderator*innen und Admins können Themen archivieren und wieder öffnen. Archivierte Themen bleiben erhalten, werden aus den aktiven Übersichten ausgeblendet und sind im Archiv erreichbar; beim Wiederöffnen wird der vorherige Themenstatus wiederhergestellt.
- Kommentare und nächste Schritte werden chronologisch am Thema gesammelt.
- „Meine Aufgaben“ trennt die Hauptzuständigkeit für Themen von ausdrücklich zugewiesenen Tagesordnungspunkten zukünftiger Termine.
- Anlagen können als Datei oder als Netzwerkpfad bzw. Link hinterlegt werden.

### Tagesordnung und Protokolle

- Offene Tagesordnungspunkte aus dem letzten abgeschlossenen Termin werden beim Öffnen des Folgetermins bei Bedarf weitergeführt.
- Tagesordnungspunkte lassen sich per Drag-and-drop oder über die Pfeil-Schaltflächen sortieren.
- Tagesordnungstexte und Teilnehmerliste können bis zum Abschluss bearbeitet werden.
- Beim Abschluss wird ein unveränderlicher Protokoll-Snapshot gespeichert.
- Protokolle können als HTML angezeigt, gedruckt und als PDF exportiert werden.
- Exporte abgeschlossener Besprechungen verwenden den gesicherten Snapshot.

### Änderungsverlauf

Anlage und Umbenennung von Themen, Themenarchivierung und -wiederöffnung, Themenübertragungen, Änderungen an Tagesordnungstexten und Zuständigkeiten, Sortierungen, Anlagen, Kommentaren, Teilnehmerlisten, Besprechungsabschlüssen sowie Anlage, Änderung, Verlängerung, Zurücksetzen und Löschen von Besprechungsreihen und Einzelterminen werden mit Benutzer, Zeitpunkt und ausgewählten Änderungsdetails protokolliert. Themenübertragungen sind in beiden beteiligten Serienverläufen sichtbar. Moderator*innen sehen ausschließlich die Verläufe ihrer ausdrücklich moderierten Reihen. Globale Admins sehen Systemereignisse und zusätzlich nur die Serienverläufe, für die sie selbst ausdrücklich Moderatorrechte besitzen. Auditoren sehen ausschließlich Systemereignisse und haben lesenden Zugriff. Im CSV-Export werden Admins und Auditoren auf Systemereignisse beschränkt; Moderator*innen exportieren ausschließlich Ereignisse ihrer eigenen moderierten Reihen. Passwortwerte und hochgeladene Datei-Inhalte werden nicht protokolliert; bei Passwortänderungen wird nur der Änderungsstatus festgehalten. Bei Anlagen können Dateinamen als Metadaten erscheinen. Wird eine abgeschlossene Besprechung wieder geöffnet, bleibt ihr vorheriger gesicherter Protokollstand als Audit-Detail erhalten. In der Oberfläche sind Änderungsdetails zunächst eingeklappt; der CSV-Export enthält die strukturierten Details innerhalb des jeweiligen Rollenbereichs.

### Benutzer-, Rechte- und Organisationsverwaltung

- Integrierte Verwaltungsoberfläche unter `/verwaltung/` für Benutzerkonten, Serienberechtigungen, Organisationseinstellungen und Datenimport/-export.
- Benutzerkonten können angelegt, bearbeitet und aktiviert bzw. deaktiviert werden. Letzte Anmeldung und Erstellungszeitpunkt werden angezeigt.
- Passwörter bestehender Benutzerkonten werden ausschließlich über einen E-Mail-Reset-Link zurückgesetzt; ein direktes Setzen oder Auslesen fremder Passwörter ist nicht vorgesehen.
- Besprechungsreihen-Zuordnungen und die Rollen Leser*in, Teilnehmer*in und Moderator*in können direkt im Nutzerprofil verwaltet werden. Serienzuweisungen lassen sich außerdem suchen und filtern.
- CSV-Import und -Export für Benutzerkonten sowie für Themen und Tagesordnungspunkte sind in die Verwaltungsoberfläche integriert. Benutzer-CSV sowie Vollbackup-/Restore-Funktionen sind globalen Admin-Konten vorbehalten. Themen-CSV-Import und -Export stehen ausschließlich Moderator*innen für ihre ausdrücklich moderierten Reihen zur Verfügung; globale Adminrechte allein reichen dafür nicht. Der Themenimport bietet eine Vorschau; eine Muster-CSV steht bereit.
- Organisationseinstellungen umfassen Name, Kurzname, Zeitzone, Anlagenlimit und das Farbschema mit validierten HEX-Farbwerten.

## Rollen und Berechtigungen

Die Anwendung unterscheidet drei globale Benutzerrollen und drei Serienrollen. **Nutzer**, **Admin** und **Auditor** werden global vergeben. **Leser*in**, **Teilnehmer*in** und **Moderator*in** werden unabhängig davon jeweils pro Besprechungsreihe zugewiesen. Django-Superuser haben immer globale Adminrechte. Auditoren erhalten ausschließlich lesenden Zugriff auf System-Änderungsprotokolle, Benutzerkonten samt globalen Rollen und Serienberechtigungen sowie Organisationseinstellungen. Sie sehen keine Besprechungsreihen oder fachlichen Besprechungsinhalte.

- **Nutzer:** Die fachlichen Zugriffe ergeben sich ausschließlich aus den individuellen Serienberechtigungen.
- **Admin:** Globale Verwaltungsrechte; fachliche Inhalte nur entsprechend eigener Serienberechtigungen.
- **Auditor:** Lesender Zugriff auf System-Änderungsprotokolle, Benutzer und deren globale Rollen/Serienberechtigungen sowie Organisationseinstellungen. Kein Zugriff auf Besprechungsinhalte und keine Änderungsrechte.

### Berechtigungsmatrix nach Funktionsbereichen

Die Matrix beschreibt die Berechtigungen in der Weboberfläche. „Zugewiesen“ bedeutet: nur innerhalb der Besprechungsreihen, denen das Konto zugeordnet ist. Moderatorrechte gelten ebenfalls nur in Reihen mit Moderatorzuweisung.

#### 1. Inhalte und Besprechungen

| Funktion | Leser*in | Teilnehmer*in | Moderator*in | Admin |
|---|:---:|:---:|:---:|:---:|
| Zugewiesene Reihen, Themen und Termine ansehen | Ja | Ja | Ja | Ja, nur bei eigener Zuweisung |
| Protokolle abgeschlossener Termine ansehen und exportieren | Ja | Ja | Ja | Ja, nur bei eigener Zuweisung |
| Tagesordnungstexte bearbeiten und Punkte sortieren | Nein | Ja | Ja | Ja, bei Teilnehmer- oder Moderatorzuweisung |
| Tagesordnungspunkte in offenen Terminen ergänzen oder aus der Themenübersicht entfernen | Nein | Ja | Ja | Ja, bei Teilnehmer- oder Moderatorzuweisung |
| Zuständigkeiten für Tagesordnungspunkte pflegen | Nein | Ja | Ja | Ja, bei Teilnehmer- oder Moderatorzuweisung |
| Teilnehmerliste eines offenen Termins bearbeiten | Nein | Ja | Ja | Ja, bei Teilnehmer- oder Moderatorzuweisung |
| Besprechung abschließen und Protokollstand sichern | Nein | Ja | Ja | Ja, bei Teilnehmer- oder Moderatorzuweisung |
| Abgeschlossene Besprechung wieder öffnen | Nein | Nein | Ja | Ja, bei Moderatorzuweisung |
| Einzelne Besprechungstermine verschieben oder löschen | Nein | Nein | Ja | Ja, bei Moderatorzuweisung |

#### 2. Themen und Zusammenarbeit

| Funktion | Leser*in | Teilnehmer*in | Moderator*in | Admin |
|---|:---:|:---:|:---:|:---:|
| Themenübersicht und Themenhistorie ansehen | Ja | Ja | Ja | Ja, nur bei eigener Zuweisung |
| Themen anlegen und Titel bearbeiten | Nein | Ja | Ja | Ja, bei Teilnehmer- oder Moderatorzuweisung |
| Themen zwischen zugänglichen, beschreibbaren Reihen übertragen | Nein | Ja | Ja | Ja, bei Teilnehmer- oder Moderatorzuweisung |
| Kommentare hinzufügen | Nein | Ja | Ja | Ja, bei Teilnehmer- oder Moderatorzuweisung |
| Anlagen und Verweise hinzufügen | Nein | Ja | Ja | Ja, bei Teilnehmer- oder Moderatorzuweisung |
| Themen archivieren oder wieder öffnen | Nein | Nein | Ja | Ja, bei Moderatorzuweisung |

**Themenarchiv:** Archivieren und Wiederöffnen ist ausschließlich Moderator*innen der jeweiligen Reihe vorbehalten. Die Archivierung blendet das Thema aus den aktiven Übersichten aus, löscht aber weder Thema noch Protokollhistorie. Beim Wiederöffnen wird der vorherige Status wiederhergestellt.

#### 3. Besprechungsreihen verwalten

| Funktion | Leser*in | Teilnehmer*in | Moderator*in | Admin |
|---|:---:|:---:|:---:|:---:|
| Eigene zugewiesene Reihen verwalten | Nein | Nein | Ja | Ja, wenn Moderator*in |
| Reihen anlegen und Termine erzeugen | Nein | Nein | Ja | Ja |
| Reihen ändern und verlängern | Nein | Nein | Ja | Ja, wenn Moderator*in |
| Zukünftige Entwurfstermine einer Reihe neu aufsetzen | Nein | Nein | Ja | Ja, wenn Moderator*in |
| Reihen löschen | Nein | Nein | Ja | Ja, wenn Moderator*in |
| Fremde, nicht zugewiesene Reihen verwalten | Nein | Nein | Nein | Nein |

Moderator*innen können ausschließlich Reihen verwalten, in denen sie ausdrücklich die Rolle Moderator*in besitzen. Eine von ihnen neu angelegte Reihe wird automatisch der erstellenden Person als Moderator*in zugewiesen.

#### 4. Änderungsverlauf

| Funktion | Leser*in | Teilnehmer*in | Moderator*in | Admin |
|---|:---:|:---:|:---:|:---:|
| Änderungsverlauf ansehen | Nein | Nein | Ja, eigene moderierte Reihen | Systemereignisse und eigene moderierte Reihen |

Der serienbezogene Änderungsverlauf ist ausschließlich für Moderator*innen der jeweiligen Reihe sichtbar. Admins sehen Systemereignisse sowie Serienereignisse nur für Reihen, in denen sie selbst Moderator*innenrechte besitzen. Auditoren sehen ausschließlich den System-Änderungsverlauf und können ihn exportieren. Eine Teilnehmer- oder Leserzuweisung allein berechtigt nicht zur Einsicht. Ereignisse gelöschter Reihen, die keiner Reihe mehr zugeordnet werden können, sind globalen Admins zugänglich.

#### 5. Benutzer- und Systemverwaltung

| Funktion | Leser*in | Teilnehmer*in | Moderator*in | Admin |
|---|:---:|:---:|:---:|:---:|
| Benutzerkonten anlegen und bearbeiten | Nein | Nein | Nein | Ja |
| Globale Benutzerrolle vergeben oder entziehen | Nein | Nein | Nein | Ja |
| Serienzuweisungen und Rollen anderer Benutzer verwalten | Nein | Nein | Nein | Ja |
| Benutzer-CSV importieren und exportieren | Nein | Nein | Nein | Ja |
| Themen- und Tagesordnungspunkt-CSV importieren und exportieren | Nein | Nein | Nein | Ja |
| Globale Organisationseinstellungen ändern | Nein | Nein | Nein | Ja |
| Django-Administration öffnen | Nein | Nein | Nein | Ja |

Auch in der Django-Administration bleiben Serieninhalte auf ausdrücklich zugewiesene Reihen begrenzt. Serienbezogene Änderungen und CSV-Importe/-Exporte setzen eigene Moderatorrechte voraus; globale Adminrechte allein reichen dafür nicht.

### Was die Rollen im Alltag bedeuten

**Leser*in**

- Sieht Inhalte und Protokolle der ausdrücklich zugewiesenen Besprechungsreihen.
- Hat ausschließlich Leserechte. Änderungen, Kommentare, Anlagen, Tagesordnungsaktionen und Verwaltungsfunktionen sind nicht möglich.
- Kann den Änderungsverlauf nicht einsehen.

**Teilnehmer*in**

- Kann innerhalb der ausdrücklich zugewiesenen Reihen an der fachlichen Arbeit teilnehmen: Themen und Tagesordnung bearbeiten, Kommentare und Anlagen ergänzen, Teilnehmende verwalten und Besprechungen abschließen.
- Kann abgeschlossene Besprechungen nicht wieder öffnen und keine Besprechungsreihen verwalten.
- Kann den Änderungsverlauf nicht einsehen.

**Moderator*in**

- Hat innerhalb der jeweils moderierten Reihen die fachlichen Rechte einer Teilnehmerin bzw. eines Teilnehmers.
- Kann zusätzlich abgeschlossene Besprechungen wieder öffnen sowie die eigenen moderierten Reihen und deren Termine verwalten.
- Kann den Änderungsverlauf der eigenen moderierten Reihen einsehen.
- Kann weder fremde Reihen noch Benutzerkonten und globale Serienzuweisungen verwalten.

**Admin**

- Hat Zugriff auf alle Besprechungsreihen und deren Inhalte.
- Kann Besprechungsreihen, Benutzerkonten, Gruppen, Serienzuweisungen und globale Organisationseinstellungen verwalten.
- Kann alle Besprechungen abschließen und wieder öffnen sowie alle Änderungsverläufe einsehen.
- Die Admin-Rolle wird über die Gruppe **Admin** vergeben. Django-Superuser haben ebenfalls globalen Zugriff.

### Rollen gelten je Besprechungsreihe

Ein Konto kann in einer Reihe Leser*in, in einer zweiten Teilnehmer*in und in einer dritten Moderator*in sein. Die jeweilige Rolle gilt ausschließlich für die zugeordnete Reihe. **Admin** bleibt eine globale Berechtigung.

Bei der Einführung der Serienberechtigungen werden bestehende Konten automatisch zugeordnet:

- Bisherige Staff-Konten erhalten die Gruppe **Admin**.
- Bestehende Rollen werden bei der Migration auf die jeweiligen Serienzuordnungen übertragen. Konten ohne bisherige Moderator- oder Leserrolle erhalten dort **Teilnehmer*in**.
- Bestehende Nicht-Admin-Konten erhalten zunächst Zugriff auf alle zu diesem Zeitpunkt vorhandenen Besprechungsreihen. So bleibt der bisherige Zugriff nach dem Update erhalten. Diese Zuweisungen können anschließend auf die tatsächlich benötigten Reihen eingeschränkt werden.

Neue Benutzerkonten erhalten zunächst die globale Rolle Nutzer. Ihre Serienzuweisungen legen fest, auf welche Reihen sie zugreifen können. Auditoren benötigen keine Serienzuweisung, da sie ausschließlich administrative Prüfdaten lesen dürfen.

## Benutzer und Serienzuweisungen verwalten

Die integrierte Verwaltungsoberfläche ist über **Verwaltung** in der Seitenleiste bzw. unter `/verwaltung/` erreichbar. Sie steht ausschließlich globalen Administrator*innen und Django-Superusern zur Verfügung. Die Django-Administration unter `/django-admin/` bleibt als technische Rückfalloption vorhanden.

### Nutzerverwaltung

Unter **Verwaltung → Nutzerverwaltung** können Benutzerkonten angelegt und bearbeitet werden. Die Übersicht zeigt Aktivstatus, globale Benutzerrolle, letzte Anmeldung und Erstellungsdatum. Im Nutzerprofil stehen unter anderem folgende Funktionen bereit:

- Persönliche Angaben und Aktivstatus bearbeiten.
- Globale Administratorrechte vergeben oder entziehen.
- Besprechungsreihen-Zuordnungen direkt am Nutzerprofil öffnen und Rollen je Reihe festlegen.
- Ein Passwort-Reset per E-Mail auslösen. Das bestehende Passwort wird nicht angezeigt oder direkt geändert; die betroffene Person erhält einen zeitlich begrenzten Link zum selbstständigen Zurücksetzen.

### Serienzuweisungen und Rollen

Im Bereich **Gruppenverwaltung** können Benutzer und Besprechungsreihen gesucht und gefiltert sowie Rollen zugewiesen werden. Alternativ können die Zuordnungen direkt aus dem jeweiligen Nutzerprofil bearbeitet werden. Beide Ansichten verwalten dieselben Serienberechtigungen.

Die Rollen **Leser*in**, **Teilnehmer*in** und **Moderator*in** gelten jeweils nur innerhalb der zugewiesenen Besprechungsreihe. Die globale Gruppe **Admin** gewährt Zugriff auf alle Reihen und Verwaltungsfunktionen.

### CSV-Import und -Export

Unter **Verwaltung → Datenimport und -export** stehen die CSV-Funktionen direkt in der Anwendung zur Verfügung:

- **Nutzer:** Benutzerkonten einschließlich persönlicher Angaben, Aktivstatus, Administratorstatus und Serienzuordnungen exportieren bzw. importieren.
- **Themen und Tagesordnungspunkte:** Themen, Termine, Tagesordnungspunkte, Zuständigkeiten, Status und Wiedervorlage-Verknüpfungen exportieren bzw. importieren.
- Für Themen und Tagesordnungspunkte kann eine Muster-CSV heruntergeladen werden. Der Import bietet eine Vorschau und berücksichtigt den Schutz abgeschlossener Protokolle.

Für Themen- und Tagesordnungspunktdaten gilt: `record_type=topic` exportiert Themen ohne Tagesordnungspunkt; `record_type=agenda` enthält einen Terminbezug. Die Spalten `followup_series` und `followup_meeting_date` erhalten Wiedervorlage-Verknüpfungen.

### Organisationseinstellungen

Unter **Verwaltung → Organisationseinstellungen** werden Organisationsname, Kurzname, Zeitzone, maximale Anlagengröße und die Farben der Benutzeroberfläche gepflegt. Für die Farbwerte stehen Farbwähler und HEX-Validierung zur Verfügung. Der zentrale Organisationseinstellungs-Datensatz ist gegen versehentliches Löschen geschützt.

**Empfehlung:** Admin-Rechte nur an wenige verantwortliche Personen vergeben. Für alle anderen Konten die Rolle je Besprechungsreihe passend festlegen und nur die benötigten Reihen zuweisen.

## Updates und Betrieb

### Anwendung aktualisieren

Auf der VM wird die Anwendung im Verzeichnis `/opt/meeting-manager` aktualisiert. Vorher sollte ein aktuelles Backup vorhanden sein.

```bash
sudo bash /opt/meeting-manager/deploy/update.sh
```

Das Skript:

1. Sichert die lokale `.env`, holt Änderungen des aktuell ausgecheckten Git-Branches mit `git pull --ff-only` und stellt die `.env` anschließend wieder her. So funktioniert das Update auch beim Übergang von älteren Versionen, in denen `.env` noch versioniert war.
2. Installiert bzw. aktualisiert Python-Abhängigkeiten.
3. Führt ausstehende Datenbankmigrationen aus.
4. Sammelt statische Dateien für Nginx.
5. Deaktiviert in der aktiven Nginx-Konfiguration das Browser-Caching für HTML-Seiten und statische Assets (`Cache-Control: no-store`) und prüft/lädt Nginx neu. Bestehende Reverse-Proxy-Freigaben bleiben erhalten.
6. Startet den Dienst `meeting-manager` neu und zeigt dessen Status an.

Nach dem Update laden Browser und iOS-Web-Apps beim nächsten Seitenaufruf HTML und Assets erneut vom Server, statt alte Dateien aus dem HTTP-Cache zu verwenden. Bereits geöffnete Seiten werden nicht aktiv ferngesteuert neu geladen; sie beziehen die aktuelle Version beim nächsten Aufruf bzw. Neuladen. Betriebssystemseitig gespeicherte Home-Bildschirm-Symbole können davon unabhängig weiterhin separat zwischengespeichert bleiben.

Das Skript aktualisiert den Branch, der auf dem Server ausgecheckt ist. Für den regulären Betrieb sollte das der freigegebene Hauptbranch sein. Auf Debian-Installationen schaltet `sudo bash /opt/meeting-manager/deploy/update.sh -testing` den Testing-Modus ein. Nur in diesem Modus werden neben `main` und `beta` weitere Remote-Branches angeboten. Wird `update.sh` ohne `-testing` ausgeführt, wird der Modus beendet. Web-Updates übernehmen den aktiven Modus automatisch; in der Weboberfläche lässt er sich über **Testing-Modus beenden** ausschalten. Docker-Installationen verwenden diesen Modus nicht und behalten ihre bisherige Auswahl aller verfügbaren Branches bei.

### Updates über die Weboberfläche

Globale Administrator*innen öffnen in der Seitenleiste **Software aktualisieren**. Dort werden Installationsart, installierter Branch und Commit angezeigt. Auf Debian stehen standardmäßig `main` und `beta` zur Auswahl. Weitere Remote-Branches werden nur im aktivierten Testing-Modus angeboten. Docker zeigt weiterhin alle verfügbaren Remote-Branches. Status und Protokoll des letzten Laufs werden auf diesem Server angezeigt; die Ausführung läuft unabhängig von der Browseranfrage.

- **Debian/systemd:** Die Webanwendung startet ausschließlich den fest installierten Wrapper `meeting-manager-update` über eine eng begrenzte sudoers-Regel. Dieser startet den eigentlichen Lauf als eigenständigen transienten systemd-Dienst. Dadurch überlebt das Update den Neustart des Django-Dienstes. Der Runner prüft den ausgewählten Branch erneut gegen das Git-Remote, verhindert parallele Läufe und protokolliert Status und Ausgabe. Scheitert ein Update nach dem Git-Wechsel, aber noch vor der Installation von Abhängigkeiten, wird der vorherige Branch samt Commit wiederhergestellt und der Anwendungsdienst neu gestartet. Sobald Abhängigkeiten oder Datenbankmigrationen begonnen haben, erfolgt bewusst kein automatischer Code-Rollback, da der vorherige Stand sonst mit einer bereits veränderten Laufzeitumgebung oder Datenbank inkompatibel sein könnte; in diesem Fall bleibt der Fehler im Update-Protokoll sichtbar und eine Wiederherstellung muss anhand eines Backups erfolgen.
- **Docker Compose:** Die Webanwendung spricht den bereits eingerichteten Host-Updater ausschließlich über den lokalen Unix-Socket an. Der App-Container erhält weiterhin keinen Docker-Socket.
- Beide Varianten aktualisieren nur die jeweilige lokale Installation. Die Server beeinflussen sich nicht gegenseitig.

**Einmalige Aktivierung auf bestehenden Debian-Installationen:** Nach dem Einspielen des aktuellen Anwendungsstands den sicheren Updater-Installer einmalig ausführen:

```bash
sudo bash /opt/meeting-manager/deploy/install-debian-updater.sh
```

Das Skript aktualisiert die systemd-Dienstdefinition, richtet den eingeschränkten Wrapper samt Runner ein und startet den Anwendungsdienst bei Bedarf einmal neu. Datenbank, `.env` und Python-Umgebung bleiben unverändert. Danach sind reguläre Updates über die Weboberfläche möglich. Bei bestehenden Docker-Installationen muss der Host-Updater nach dem Aktualisieren des Repository-Checkouts einmalig mit `sudo bash deploy/install-docker-updater.sh` aktualisiert werden. Das installiert den aktuellen eingeschränkten Agenten und startet ihn neu. Der Agent merkt sich anschließend den ausgewählten Image-Branch in der lokalen `.env`; andere Einstellungen in dieser Datei bleiben unverändert. Die App-Images enthalten Commit- und Branch-Metadaten.

Vor Updates sollten weiterhin regelmäßige Backups von Datenbank und hochgeladenen Dateien vorhanden sein. Ein Docker-Rollback stellt das vorherige App-Image wieder her; bereits erfolgreich ausgeführte Datenbankmigrationen werden dabei nicht automatisch zurückgesetzt.

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
sudo -u meetingapp bash -c 'set -a; source /opt/meeting-manager/.env; set +a; exec /opt/meeting-manager/.venv/bin/python /opt/meeting-manager/manage.py showmigrations'
```

Dasselbe Muster gilt für weitere `manage.py`-Befehle, zum Beispiel `check` oder `test`. So werden dieselben Umgebungsvariablen und Dateiberechtigungen wie beim Anwendungsdienst verwendet. Keine Zugangsdaten direkt in Befehlszeilen oder Tickets schreiben.

## Arbeitsabläufe in der Anwendung

### 1. Besprechungsreihe anlegen

Moderator*innen öffnen **Besprechungsreihen** in der Navigation. Dort werden Name, Beschreibung, Wiederholungsrhythmus, Wochentag sowie Start- und optionales Enddatum festgelegt. Beim Speichern erzeugt die Anwendung die zugehörigen Termine. Die neu angelegte Reihe wird der erstellenden Moderatorin bzw. dem erstellenden Moderator automatisch zugewiesen.

### 2. Themen pflegen

Über **Neues Thema** wird ein Titel angelegt und ein erster Termin aus den vorhandenen zukünftigen Terminen einer Besprechungsreihe ausgewählt. Das Thema wird direkt auf dessen Tagesordnung gesetzt. In der Themenbearbeitung lassen sich Titel, Status, Hauptverantwortung und Besprechungsreihe pflegen. Kommentare, Anlagen und Netzwerkpfade werden direkt am Thema gesammelt.

### 3. Besprechung vorbereiten und durchführen

In der Übersicht einen Termin öffnen. Dort können Teilnehmende ausgewählt und Tagesordnungstexte bearbeitet werden. Tagesordnungspunkte lassen sich per Ziehen oder über die Pfeiltasten sortieren. Die Änderungen werden gespeichert, solange die Besprechung noch nicht abgeschlossen ist.

### 4. Besprechung abschließen

Mit **Besprechung abschließen & Protokollstand sichern** wird ein Snapshot des aktuellen Protokollstands erstellt. Danach sind Teilnehmerliste und Tagesordnungstexte gesperrt. Das Protokoll kann angezeigt, gedruckt oder als PDF exportiert werden.

Nur Moderator*innen und Admins können eine abgeschlossene Besprechung wieder öffnen. Nach dem Wiederöffnen kann sie erneut bearbeitet und abgeschlossen werden.

### 5. Aufgaben nachverfolgen

Die Seite **Meine Aufgaben** zeigt in einem eigenen Abschnitt die offenen Themen mit eigener Hauptzuständigkeit und optisch getrennt darunter die eigenen Tagesordnungspunkte heutiger und zukünftiger Termine. Die Themenübersicht und der Änderungsverlauf berücksichtigen stets die eigenen Serienberechtigungen.

## Netzwerkfreigaben und Anlagen

Netzwerkfreigaben werden auf der **VM selbst** eingebunden, nicht auf dem Arbeitsplatz des Benutzers. Beispiel: Eine NAS-Freigabe nach `/mnt/meeting-share` mounten und diesen Pfad am Thema hinterlegen.

SMB-Pfade (`smb://server/freigabe/...`) werden als anklickbare Referenz gespeichert, sofern Host und Schema gültig sind. Ob der Browser bzw. das Betriebssystem den Link öffnet, hängt von der Client-Konfiguration und einem registrierten SMB-Handler ab. UNC-Pfade werden, soweit eindeutig erkennbar, in SMB-URLs überführt; nicht unterstützte oder ungültige Pfade bleiben reiner Text. Die Anwendung greift nicht selbst auf SMB-Freigaben zu. Hochgeladene Dateien liegen unter `/opt/meeting-manager/media`.

Für hochgeladene Themenanlagen gilt serverseitig eine Dateiendungs-Allowlist: **PDF, DOCX, XLSX, PPTX, TXT, PNG, JPG und JPEG**. Andere Dateiendungen, insbesondere ausführbare Dateien, Skripte und Archive, werden beim Upload abgewiesen. Die Prüfung wertet die Dateiendung aus; sie verifiziert nicht die tatsächliche Dateisignatur oder den Dateiinhalt. Ein integrierter Malware-Scanner ist derzeit nicht vorhanden. Das organisationsweite Uploadlimit liegt standardmäßig bei 20 MB und kann in den Organisationseinstellungen auf 1 bis 24 MB gesetzt werden. Downloads sind weiterhin an Anmeldung und Serienberechtigung gebunden.

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

Eine ausführliche, am aktuellen Quellcode ausgerichtete Funktions-, Rollen-, Datenschutz- und Sicherheitsbeschreibung mit validierter Risikobewertung und konkreten Maßnahmen liegt unter [`docs/Funktions-und-Sicherheitsbeschreibung.md`](docs/Funktions-und-Sicherheitsbeschreibung.md). In der angemeldeten Anwendung ist sie zusätzlich unter **Hilfe → IT, Informationssicherheit und Datenschutz** als PDF verfügbar.

**Die Anwendung ist ein internes MVP und sollte vor einem produktiven Einsatz weiter gehärtet werden.**

- Zugriff auf das interne Netzwerk begrenzen und eine Firewall einsetzen.
- Für Zugriffe über nicht vertrauenswürdige Netze HTTPS mit gültigem Zertifikat konfigurieren. HSTS-Subdomain-Schutz darf nur aktiviert werden, wenn sämtliche Subdomains dauerhaft HTTPS verwenden. HSTS Preload ist zusätzlich nur mit HTTPS-Weiterleitung, mindestens einem Jahr HSTS-Laufzeit und vollständiger HTTPS-Abdeckung aller Subdomains zulässig; die Anwendung prüft diese Voraussetzungen beim Start. Die Installationsskripte erzwingen HTTPS hinter einem vorgeschalteten Reverse Proxy. Debian beschränkt den lokalen Nginx-Zugriff auf die beim Setup angegebene Proxy-IP/CIDR; Docker bindet den Web-Port standardmäßig ausschließlich an Loopback. Sichere Cookies, HTTPS-Weiterleitung und CSRF-Origin werden automatisch aktiviert.
- Regelmäßige, getestete Backups von Datenbank und Media-Verzeichnis einrichten.
- Admin-Rechte nur gezielt vergeben und Serienzuweisungen regelmäßig überprüfen.
- Hochgeladene Dateien werden ausschließlich über eine angemeldete, berechtigungsgeprüfte Download-Route ausgeliefert. Der Media-Ordner darf nicht direkt durch Nginx veröffentlicht werden.
- Passwörter werden durch Django gehasht gespeichert. Zugangsdaten und `SECRET_KEY` gehören ausschließlich in die geschützte Umgebungsdatei.
- Vor produktivem Einsatz automatisierte Tests und die Berechtigungen mit separaten Testkonten aller drei Rollen prüfen.

Screenshots sind derzeit nicht eingebettet: Die Anwendung wird in einem geschützten internen Netz betrieben und für diese Dokumentationsänderung stand keine authentifizierte Browser-Sitzung zur Verfügung. Es werden deshalb keine nachgebildeten Bilder als echte Anwendungsansichten ausgegeben. Sinnvolle spätere Screenshots wären die Übersicht, eine Besprechung mit Tagesordnung, die Themenbearbeitung und die Benutzer-/Serienzuweisung in der Verwaltung. Vor dem Einchecken sollten Namen, Kommentare und andere personenbezogene bzw. vertrauliche Daten unkenntlich gemacht werden.

## Entwicklung und Tests

### Lokale Umgebung

Die Anwendung benötigt Python-Abhängigkeiten aus `requirements.txt` sowie eine konfigurierte Datenbank. Für die produktive Installation werden PostgreSQL und die Umgebungsvariablen aus `/opt/meeting-manager/.env` verwendet.

### Django-Prüfungen und Tests

Im aktivierten Virtualenv und mit geladener Konfiguration:

```bash
sudo -u meetingapp bash -c 'set -a; source /opt/meeting-manager/.env; set +a; exec /opt/meeting-manager/.venv/bin/python /opt/meeting-manager/manage.py check'
sudo -u meetingapp bash -c 'set -a; source /opt/meeting-manager/.env; set +a; exec /opt/meeting-manager/.venv/bin/python /opt/meeting-manager/manage.py test'
```

Die Berechtigungstests liegen in `meetings/test_permissions.py`; weitere Anwendungstests liegen in `meetings/tests.py`.

## Datenbankmigrationen

Das Datenbankschema wird mit versionierten Django-Migrationen verwaltet. Neue Migrationen liegen unter `meetings/migrations/` und werden beim regulären Update automatisch mit `manage.py migrate` angewendet.

Die Migration `0006_series_access_and_roles` ergänzt die Serienzuweisungen. Die Migration `0009_series_roles` überführt die bisherigen globalen Rollen in Rollen je Serienzuordnung und entfernt die nicht mehr benötigten globalen Gruppen. Admin bleibt global.

Migrationen nicht manuell aus der Datenbank löschen und nicht mit `migrate --fake` überspringen, außer wenn ein bewusst geplanter und geprüfter Reparaturvorgang dies erfordert.

<!-- Harmloser PR-Test: keine funktionalen Änderungen. -->
