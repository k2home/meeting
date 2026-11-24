# Meeting Manager – Funktions- und Sicherheitsbeschreibung

**Adressaten:** IT-Abteilung, Informationssicherheit und Datenschutzbeauftragte  
**Prüfstand:** Branch `main`, Commit `8000875ec761e15358de1a5a3a1c45bef62de565`  
**Stand:** 24. November 2026  
**Geltungsbereich:** Anwendungscode und Repository-Konfiguration. Die konkrete Server-, Proxy-, Netzwerk- und Backup-Konfiguration ist vor Ort gesondert zu prüfen.

> **Einordnung:** Diese Beschreibung ist eine nachvollziehbare technische Bestandsaufnahme und Risikoeinschätzung. Sie ist weder Penetrationstestbericht noch Datenschutz-Folgenabschätzung, TOM-Nachweis oder rechtsverbindliche DSGVO-Konformitätsbestätigung. Aussagen über die reale Betriebsumgebung gelten nur, wenn sie dort verifiziert wurden.

## 1. Kurzbeschreibung und Zweck

Meeting Manager ist eine deutschsprachige Webanwendung zur Organisation wiederkehrender Besprechungen und zur fortlaufenden Bearbeitung von Themen. Sie verbindet Besprechungsreihen und Termine mit Tagesordnungspunkten, Zuständigkeiten, Kommentaren, Anlagen und Protokollen.

Ein Thema beschreibt einen fortlaufenden Vorgang. Ein Tagesordnungspunkt ist die Behandlung dieses Themas in einem konkreten Termin. Der zu einem Termin gehörende Text und Status werden getrennt geführt. Beim Abschluss einer Besprechung speichert die Anwendung einen Protokoll-Snapshot. Spätere Änderungen am Thema verändern diesen historischen Snapshot nicht.

Die Anwendung ist laut Repository für interne Netze vorgesehen. Sie wird entweder auf Debian/Ubuntu mit PostgreSQL, Gunicorn und Nginx oder containerisiert mit Docker Compose betrieben.

## 2. Funktionsumfang und Datenverarbeitung

### 2.1 Fachliche Funktionen

- Wiederkehrende Besprechungsreihen mit wöchentlichem, 14-tägigem oder monatlichem Rhythmus; Termine werden anhand der konfigurierten Daten erzeugt.
- Themen mit Status, Hauptzuständigkeit und Zuordnung zu einer Besprechungsreihe.
- Tagesordnungspunkte mit eigenem Text, Bearbeitungsstatus, Reihenfolge und optional abweichender Zuständigkeit je Termin.
- Kommentare, nächste Schritte, Datei-Anlagen und Verweise auf Netzwerkpfade bzw. Webadressen.
- Wiedervorlagen und Übernahme offener Punkte in Folgetermine.
- Abschluss einer Sitzung mit gesichertem Protokollstand; Anzeige, Druck sowie PDF- und Word-Export.
- Archivierung von Themen und Erhalt historischer Besprechungen nach dem Löschen einer Reihe. Bisherige Reihenmitglieder können erhaltene Protokolle weiterhin lesend aufrufen.
- Benutzer-, Serienrollen- und Organisationsverwaltung sowie CSV-Import/-Export.
- Änderungsverläufe für fachliche Vorgänge und administrative Systemereignisse.

### 2.2 Datenkategorien

| Datenkategorie | Beispiele | Datenschutzbezug |
|---|---|---|
| Kontodaten | Benutzername, Vor- und Nachname, E-Mail, Aktivstatus, letzte Anmeldung | Personenbezogene Stammdaten |
| Berechtigungen | globale Rolle, Serienzuordnung und Serienrolle | Organisations- und Aufgabenbezug |
| Besprechungsdaten | Reihe, Termine, Teilnehmerlisten, Protokoll-Snapshots | Anwesenheit und interne Zusammenarbeit |
| Inhaltsdaten | Themen, Tagesordnungstexte, Kommentare, Zuständigkeiten | Freitext kann vertrauliche oder sensible Angaben enthalten |
| Anlagen | hochgeladene Dokumente, Netzwerkpfade, URLs | Können eigenständige personenbezogene oder vertrauliche Inhalte enthalten |
| Änderungsdaten | Akteur, Zeitpunkt, Aktion, Zusammenfassung, ausgewählte Änderungen | Nachvollziehbarkeit; mögliche Beschäftigtenbezüge |
| Betriebsdaten | Webserver-, Betriebssystem-, Datenbank- und Proxy-Logs, Backups | Abhängig von Hosting und Betriebsüberwachung |

Die Anwendung kann nicht verhindern, dass Benutzer in Freitexten oder Anlagen unzulässige oder besonders schützenswerte Informationen hinterlegen. Dafür sind verbindliche Nutzungsregeln, Schulung und eine fachliche Freigabe der vorgesehenen Datenkategorien erforderlich.

## 3. Rollen- und Berechtigungskonzept

Das Modell kombiniert eine globale Rolle und unabhängige Berechtigungen je Besprechungsreihe. Eine globale Rolle ersetzt keine Serienzuweisung.

### 3.1 Globale Rollen

| Rolle | Umfang |
|---|---|
| **Nutzer** | Standardrolle. Fachlicher Zugriff ausschließlich auf ausdrücklich zugewiesene Besprechungsreihen und gemäß der dortigen Serienrolle. |
| **Admin** | Globale Verwaltungsrechte für Benutzer, globale Rollen, Serienzuweisungen und Organisationseinstellungen sowie administrative Funktionen. Kein automatischer Zugriff auf fachliche Reiheninhalte. Fachliche Aktionen und Reiheninhalte setzen eine passende Serienzuweisung voraus. |
| **Auditor** | Lesender Zugriff auf administrative Prüfdaten: System-Änderungsverlauf, Benutzerkonten und Rollen-/Serienzuordnungen sowie Organisationseinstellungen. Kein Zugriff auf Besprechungsreihen oder fachliche Besprechungsinhalte und keine Änderungsrechte. |

Django-Superuser werden als globale Admins behandelt. Die Admin-Gruppe wird mit dem Django-Staff-Status synchronisiert. Die Auditor-Rolle ist gegenüber Admin nachrangig: Ein Konto mit Admin- oder Superuser-Rechten wird nicht als Auditor behandelt.

### 3.2 Serienrollen

| Serienrolle | Rechte innerhalb der ausdrücklich zugewiesenen Reihe |
|---|---|
| **Leser*in** | Inhalte, Tagesordnungen, Themen, Anlagen und Protokolle ansehen und Protokolle exportieren; keine fachlichen Änderungen. |
| **Teilnehmer*in** | Zusätzlich Themen und Tagesordnungspunkte bearbeiten, Zuständigkeiten setzen, kommentieren, Anlagen ergänzen, Wiedervorlagen verwalten, Teilnehmerlisten bearbeiten und Besprechungen abschließen. Keine Reihenverwaltung und kein Wiederöffnen abgeschlossener Besprechungen. |
| **Moderator*in** | Zusätzlich Besprechungsreihe und Termine verwalten, Themen archivieren/wieder öffnen, abgeschlossene Besprechungen wieder öffnen und den Änderungsverlauf der eigenen moderierten Reihe einsehen. |

Ein Benutzer kann in verschiedenen Reihen unterschiedliche Rollen besitzen. Eine Moderatorrolle in einer Reihe verleiht keine Rechte in einer anderen Reihe.

### 3.3 Historische Zugriffe und Änderungsverlauf

Wird eine Besprechungsreihe gelöscht, bleiben historische Termine und Protokolle standardmäßig erhalten. Die früheren Reihenmitglieder erhalten für diese erhaltenen Inhalte einen gesonderten Lesezugriff. Eine ausdrücklich gewählte endgültige Löschung kann abgeschlossene Besprechungen und Protokolle zusätzlich entfernen.

Der Änderungsverlauf ist in zwei Bereiche getrennt:

- Serienereignisse sind für Moderator*innen der jeweiligen Reihe sichtbar. Admins sehen Serienereignisse nur für Reihen, in denen sie selbst Moderatorrechte besitzen.
- Systemereignisse sind für Admins und Auditoren sichtbar. Auditoren können diese Daten nur lesen und den Systemverlauf exportieren.

Das Modell ist damit auf das Need-to-know-Prinzip ausgerichtet. Kritisch bleibt die konsequente Prüfung jedes neuen Endpunkts, Exports und administrativen Sonderwegs gegen diese Regeln.

## 4. Technische Architektur

- **Anwendungsframework:** Django (Python 3.13 im Docker-Image).
- **Datenbank:** PostgreSQL 16 im Docker-Betrieb; PostgreSQL auch für die Debian-Installation.
- **Webserver / Prozess:** Nginx und Gunicorn.
- **Dateien:** separates Medienverzeichnis bzw. Docker-Volume; statische Dateien werden separat bereitgestellt.
- **Container:** App-Prozess läuft als nicht privilegierter Benutzer. PostgreSQL ist im Compose-Netz erreichbar und erhält keinen veröffentlichten Host-Port. Der App-Container veröffentlicht Port 8000 nur intern; der Nginx-Container veröffentlicht den konfigurierten Web-Port.
- **Konfiguration:** Umgebungsvariablen und lokale `.env`-Datei. `SECRET_KEY` und Datenbankzugangsdaten sind vertraulich zu behandeln.

Bei Docker ist Port 8080 standardmäßig für den Nginx-Container vorgesehen. Das ist zunächst HTTP und kein Ersatz für TLS. Bei Debian lauscht Gunicorn laut Installationskonfiguration lokal auf 127.0.0.1:8000; Nginx nimmt HTTP auf Port 80 entgegen. TLS muss durch eine bewusst eingerichtete Proxy-/Webserver-Konfiguration bereitgestellt werden.

## 5. Bereits vorhandene Sicherheitskontrollen

Die folgenden Kontrollen sind im geprüften Quellcode bzw. in den Installationsdateien erkennbar. Sie ersetzen nicht die Prüfung der tatsächlich betriebenen Instanz.

| Bereich | Vorhandene Kontrolle | Einordnung |
|---|---|---|
| Anmeldung | Django-Authentifizierung; geschützte Anwendungsbereiche verlangen Anmeldung. | Keine Aussage über externe Identitätsverwaltung. |
| Passwörter | Django-Passworthashing; Mindestlänge 8, Komplexitätsvalidator, Ähnlichkeits- und häufige-Passwort-Prüfung. | MFA und ein anwendungsinterner Login-Rate-Limiter sind im geprüften Kern nicht belegt. |
| Sessions | Session-Laufzeit 8 Stunden; Session wird bei Requests gespeichert/erneuert. | Bei langen aktiven Sitzungen erhöht dies die Bedeutung von Geräteschutz und Logout. |
| Autorisierung | Zentrale Serienzugriffsabfragen; Auditoren werden aus fachlichen Reihenabfragen ausgeschlossen; Admin ist keine Serienrolle. | Endpunkt- und Exporttests müssen die Regeln vollständig abdecken. |
| CSRF / Browser-Header | Django-CSRF-Middleware; nosniff, Referrer-Policy same-origin und X-Frame-Options DENY. | Eine umfassende Content-Security-Policy für alle Seiten ist nicht belegt. |
| TLS / Cookies | SSL-Redirect, HSTS, sichere Session-/CSRF-Cookies und Proxy-Vertrauen sind konfigurierbar; HSTS-Preload-Konfiguration wird validiert. | Standardwerte der Installer sind HTTP bzw. sichere Cookie-/Redirect-Schalter aus. Konfiguration ist Betreiberaufgabe. |
| Uploads | Anlagenlimit wird organisationsweit konfiguriert (1–24 MB, Standard 20 MB). Download erfordert Anmeldung und Serienzugriff; Pfad wird auf MEDIA_ROOT begrenzt; Download als Attachment, nosniff und private/no-store. | Eine Malware-Prüfung und eine generelle inhaltliche Dateityp-Allowlist sind im geprüften Uploadpfad nicht belegt. |
| Logos / SVG | Logo-Auslieferung ist angemeldet, auf MEDIA_ROOT begrenzt und privat/no-store. SVG erhält eine restriktive CSP-Sandbox. | Upload- und Konvertierungspfad weiter beobachten. |
| Audit | Fachliche und administrative Ereignisse werden über Anwendungsvorgänge erfasst; Passwörter und Datei-Inhalte sollen nicht protokolliert werden. | Kein Nachweis einer manipulationsgeschützten externen oder WORM-Protokollablage. |
| CSV | Import mit Vorschau/Bestätigung; Exportwerte werden gegen Tabellenformel-Präfixe abgesichert. | Import-/Exportdateien bleiben sensible Datenkopien. |
| Betrieb | Docker-App läuft als nicht-root; DB nicht nach außen veröffentlicht; Updater nutzt lokalen Socket statt Docker-Socket im App-Container. | Host, Socket-Berechtigungen, Images, Volumes und Updater bleiben Teil der Vertrauensgrenze. |
| Backups | Integrierter Datenbank-Vollbackup-Export/-Import und dokumentierte Backup-Wege für Datenbank und Medien. | Ein belastbarer externer Backup-, Verschlüsselungs- und Restore-Prozess muss vom Betreiber eingerichtet werden. |

## 6. Validierte Sicherheitsrisiken

Die Einstufung unterscheidet zwischen einem im Code erkennbaren Befund und einem bedingten Betriebs- bzw. Restrisiko. Ein Risiko wird nicht allein deshalb als Schwachstelle bezeichnet, weil eine zusätzliche Sicherheitsfunktion nicht im Anwendungscode enthalten ist.

| Risiko / Befund | Validität | Mögliche Auswirkung | Priorität |
|---|---|---|---|
| HTTP-Standardbetrieb bzw. nicht aktivierte TLS-Schalter | **Bestätigt als Installationsstandard.** Beide Installer und `.env.example` starten mit SSL-Redirect und sicheren Cookies aus. Das ist nur dann kritisch, wenn der veröffentlichte Zugriff nicht durch einen korrekt abgesicherten HTTPS-Reverse-Proxy terminiert wird. | Mitlesen/Manipulieren von Zugangsdaten und Sessions im unverschlüsselten Übertragungsweg. | Hoch, falls extern oder über nicht vertrauenswürdige Netze; sonst abhängig von Netzsegmentierung. |
| Fehlkonfiguration von Rollen oder Endpunkten | **Plausibles Restrisiko, kein konkreter Bypass in dieser Prüfung nachgewiesen.** Zentrale Serienfilter und Rollenprüfungen sind vorhanden. Neue Views, Exporte und Sonderpfade können trotzdem fehlerhaft abgesichert werden. | Einsicht oder Änderung nicht zugewiesener Besprechungsinhalte. | Hoch wegen Vertraulichkeit, mit Regressionstests beherrschbar. |
| Kompromittiertes Benutzerkonto | **Allgemeines, gültiges Risiko.** Passwortregeln sind vorhanden; MFA und anwendungsinterne Login-Drosselung sind im geprüften Kern nicht belegt. | Unberechtigter Zugriff entsprechend der kompromittierten Serienrollen. | Hoch bei vertraulichen Inhalten. |
| Missbrauch globaler Adminrechte | **Gültiges Insider-/Kontenrisiko.** Admins können globale Benutzer- und Systemverwaltung durchführen; fachliche Reiheninhalte bleiben jedoch an Serienzuweisungen gebunden. | Rechteausweitung, Benutzerverwaltung, Datenexport/-import und Systemänderungen. | Hoch, aber durch Rollenbegrenzung und Kontrollen reduzierbar. |
| Schadsoftware oder aktive Inhalte in Uploads | **Teilweise bestätigt.** Größenlimit, geschützter Download, Attachment-Disposition, nosniff und Pfadbegrenzung sind vorhanden. Eine Malware-Prüfung und umfassende Typ-Allowlist sind nicht belegt. | Schadsoftware kann in gespeicherten Dateien weitergegeben werden; Empfänger können sie lokal öffnen. | Mittel bis hoch, abhängig von erlaubten Dateitypen und Nutzerkreis. |
| Unbefugter Zugriff auf Datei-Anlagen | **Im normalen Downloadpfad bereits adressiert.** Die Downloadansicht prüft den angemeldeten Benutzer und die Zugänglichkeit des Themas; der Medienpfad ist nicht zur öffentlichen Direkt-Auslieferung bestimmt. | Restrisiko bei Fehlkonfiguration des Webservers, Backup-Leaks oder fehlerhaften neuen Downloadpfaden. | Mittel; Infrastruktur und Regressionstests entscheidend. |
| Unbeabsichtigte sensible Inhalte in Freitext/Anlagen | **Gültiges organisatorisches Risiko.** Freitext und Dokumente sind bewusst flexibel; der Code kann den Inhalt nicht fachlich klassifizieren. | Unnötige Verarbeitung sensibler oder vertraulicher personenbezogener Daten. | Hoch bei unklaren Nutzungsregeln. |
| CSV- und Vollbackup-Exporte | **Gültiges Datenkopien-Risiko.** Export-/Importfunktionen sind Admin-Funktionen; CSV-Formelprävention und Importvorschau sind implementiert. | Datenabfluss über lokale Exportdateien oder unkontrollierte Sicherungskopien; fehlerhafter Import kann Daten verändern. | Hoch bei großen Datenmengen. |
| Manipulation oder zu breite Einsicht in Audit-Daten | **Teilweise bestätigt.** App-seitige Ereigniserfassung und getrennte Sichtrechte bestehen. Die Datenbank selbst ist nicht als unveränderbarer Speicher nachgewiesen. | Nachträgliche Manipulation durch privilegierte DB-/Host-Zugriffe oder übermäßige Einsicht in Beschäftigtenaktivitäten. | Mittel bis hoch. |
| Fehlende Wiederherstellbarkeit | **Betriebsrisiko, nicht aus dem Code allein bewertbar.** Backup-Funktionen und Anleitung sind vorhanden; regelmäßige, getrennte Sicherung und Restore-Tests sind nicht durch Code garantiert. | Datenverlust oder lange Ausfallzeit. | Hoch. |
| Veraltete Abhängigkeiten / Images | **Allgemeines Lieferkettenrisiko.** Abhängigkeiten sind in Requirements begrenzt; tatsächlicher Patchstand und laufende Scans sind Betriebs-/CI-Fragen. | Ausnutzung bekannter Schwachstellen. | Hoch, abhängig vom Patchprozess. |
| Netzwerkpfade und externe URLs | **Kein SSRF-Befund aus der Linkfunktion.** Die Anwendung validiert bestimmte URL-Schemata und stellt den Verweis als Link dar; sie ruft den Link nicht serverseitig ab. | Benutzer können auf externe oder falsch berechtigte Ziele verwiesen werden; dort gelten fremde Zugriffsrechte. | Niedrig bis mittel. |
| Denial of Service / Ressourcenerschöpfung | **Generisches Betriebsrisiko.** Keine konkrete Schwachstelle nachgewiesen. Uploadgrößen sind begrenzt, aber Nutzer-/Request-/Proxy-Limits sind Infrastrukturthemen. | Verlangsamung oder Ausfall durch hohe Last. | Mittel. |

### 6.1 Nicht als bestätigte Schwachstelle bewertet

- **Admin-Zugriff auf alle Besprechungsinhalte:** Die README und der aktuelle Code stimmen darin überein, dass Admins fachliche Inhalte nur mit eigener Serienzuweisung sehen und bearbeiten. Die frühere Beta-Abweichung besteht im geprüften `main`-Stand nicht mehr.
- **Öffentlich zugängliche Anlagen:** Der vorgesehene Downloadpfad verlangt Anmeldung und prüft Serienzugriff. Ein direkt öffentlich ausgelieferter MEDIA-Ordner wäre eine abweichende, unsichere Serverkonfiguration und ist zu vermeiden.
- **Server-Side Request Forgery durch Netzwerklinks:** Die Linkfunktion stellt gespeicherte Links dar; sie führt keine serverseitigen HTTP-Aufrufe zu diesen Zielen aus. Deshalb ist SSRF hier kein aus dem geprüften Linkpfad abgeleitetes Risiko.
- **CSV-Formelinjektion:** Der Export schützt Werte mit gefährlichen Formelpräfixen; ein Regressionstest deckt die Präfixe `=`, `+`, `-`, `@`, Tab und CR ab. Die Schutzmaßnahme sollte erhalten bleiben.
- **Auditor kann Änderungen vornehmen:** Auditoren sind im Anwendungsmodell als lesende Rolle vorgesehen. Die Freigabe sollte dennoch alle schreibenden Routen und Methoden automatisiert abdecken.

## 7. Konkrete Maßnahmen und empfohlene Vorgehensweisen

Die folgenden Schritte sind bewusst als umsetzbare Arbeitsanweisungen formuliert. Die Reihenfolge priorisiert die größten Auswirkungen.

### 7.1 HTTPS und sichere Proxy-Konfiguration – vor Produktivfreigabe

1. Einen zentralen Reverse Proxy mit gültigem TLS-Zertifikat vor die Anwendung setzen. TLS 1.2 oder höher aktivieren; veraltete Protokolle und schwache Cipher Suites deaktivieren.
2. Den Anwendungsport nur aus dem internen Netz bzw. ausschließlich vom Reverse Proxy erreichbar machen. Bei Docker den veröffentlichten Web-Port per Firewall auf Proxy-IP und erforderliche Admin-Netze beschränken; bei Debian Gunicorn nicht extern binden und den lokalen Nginx-Zugriff auf die Proxy-IP/CIDR begrenzen.
3. Am Proxy `X-Forwarded-Proto: https` setzen und eingehende, vom Client gelieferte Forwarded-Header überschreiben. Nur diesem bekannten Proxy vertrauen; `TRUST_PROXY_SSL=1` nicht aktivieren, solange der Proxy nicht zuverlässig isoliert ist.
4. In `.env` die tatsächliche HTTPS-Origin in `CSRF_TRUSTED_ORIGINS` eintragen und `TRUST_PROXY_SSL=1`, `USE_X_FORWARDED_HOST=1`, `SECURE_SSL_REDIRECT=1`, `SESSION_COOKIE_SECURE=1` und `CSRF_COOKIE_SECURE=1` aktivieren. Bei direkter TLS-Terminierung durch Django/den lokalen Webserver die Proxy-Header-Optionen nicht setzen.
5. Dienst neu starten und praktisch prüfen: HTTP wird auf HTTPS umgeleitet; Login und Logout funktionieren; Session- und CSRF-Cookies tragen das Secure-Attribut; Upload, Download, Passwortänderung und PDF-Export funktionieren hinter dem Proxy.
6. HSTS zunächst mit kurzer Testphase aktivieren. `includeSubDomains` nur setzen, wenn ausnahmslos alle Subdomains dauerhaft HTTPS unterstützen. Preload nur nach vollständiger Prüfung, mindestens 365 Tagen HSTS, HTTPS-Redirect und Subdomain-Abdeckung aktivieren. Die App validiert diese Kombination, die organisatorische Domainprüfung bleibt Aufgabe des Betreibers.

**Nachweis:** Proxy-Konfiguration, Firewall-Regeln, TLS-Scan und dokumentierte Browserprüfung zur Freigabe ablegen.

### 7.2 Rollen und Serienberechtigungen – laufender Kontrollprozess

1. Globale Admin-Konten auf einen kleinen, namentlich festgelegten Personenkreis begrenzen. Für normale Arbeit persönliche Nutzerkonten verwenden, nicht das Admin-Konto.
2. Für jede Besprechungsreihe einen fachlichen Eigentümer benennen. Dieser bestätigt bei Anlage und mindestens quartalsweise die Mitglieder und deren Rolle.
3. Bei Eintritt, Rollenwechsel und Austritt eines Mitarbeiters die Serienzuweisungen unmittelbar anpassen. Deaktivierte Konten und nicht mehr benötigte Serienzuweisungen in einem dokumentierten Offboarding-Prozess berücksichtigen.
4. Bei jeder Änderung an Views, Exporten, Downloads oder APIs eine Berechtigungsmatrix mit Positiv- und Negativtests ergänzen: Leser, Teilnehmer, Moderator, Admin ohne Serienzuweisung, Admin mit Serienzuweisung und Auditor.
5. Für jede Ressource sowohl Listenansichten als auch direkte Objekt-IDs testen. Ein nicht berechtigter Benutzer muss auch durch Erraten einer URL/ID keinen Inhalt erhalten oder ändern können.
6. Auditor-Tests müssen mindestens GET-Lesezugriffe auf die freigegebenen Prüfdaten sowie Ablehnung aller schreibenden HTTP-Methoden und sämtlicher fachlicher Reihen-/Anlagenzugriffe nachweisen.
7. Admin-Sonderfunktionen (CSV, Vollbackup, Restore, Organisationseinstellungen, globale Rollen) nur über die vorgesehenen Verwaltungsansichten erlauben und ihre Zugriffe protokollieren.

**Nachweis:** Quartalsweise Berechtigungsliste mit Freigabe durch den fachlichen Reihenverantwortlichen; CI-Testresultate für alle Rollen.

### 7.3 Benutzerkonten und Anmeldung

1. Wo organisatorisch möglich, Anmeldung über einen zentralen Identity Provider mit MFA erzwingen. Falls lokale Konten verbleiben, MFA als vorgeschaltete Zugangskontrolle oder über eine geprüfte Django-Erweiterung ergänzen.
2. Login-Rate-Limiting am Reverse Proxy oder durch eine gepflegte Django-Komponente einrichten. Als Startwert z. B. nach 5 fehlgeschlagenen Anmeldungen pro Konto/IP eine zeitlich begrenzte Verzögerung bzw. Sperre auslösen; legitime Nutzer müssen kontrolliert entsperrt werden können.
3. Fehlermeldungen bei Login nicht verraten, ob Benutzername oder Passwort falsch ist. Fehlversuche und ungewöhnliche Anmeldehäufungen zentral überwachen.
4. Passwortregeln der Anwendung beibehalten; Benutzer zu individuellen Passphrasen und Passwortmanagern anhalten. Gemeinsame Startpasswörter nur über einen geschützten Einmalprozess übermitteln und beim ersten Zugriff ändern lassen.
5. Bei Rollenwechsel, Austritt oder Sicherheitsvorfall Konten deaktivieren, Sessions invalidieren und bei Verdacht Passwörter sowie relevante Secrets rotieren.
6. Die 8-Stunden-Session-Laufzeit mit dem Schutzbedarf abstimmen. Für gemeinsam genutzte Arbeitsplätze automatische Bildschirmsperre und explizites Abmelden verbindlich machen.

**Nachweis:** Konfiguration des IdP/Rate-Limiters, Testprotokoll für Fehlversuche und dokumentierter Offboarding-Prozess.

### 7.4 Datei-Uploads und Downloads

1. Eine fachlich begründete Allowlist zulässiger Formate festlegen (z. B. PDF, DOCX, XLSX, PPTX, TXT, PNG/JPEG). Nicht benötigte ausführbare, Skript- und Archivformate ablehnen. Dateiendung und tatsächlichen Dateityp prüfen; der vom Browser gelieferte MIME-Typ allein ist nicht vertrauenswürdig.
2. Malware-Scanning vor Freigabe zum Download einführen. Dateien zunächst in Quarantäne speichern und erst nach erfolgreicher Prüfung für berechtigte Nutzer bereitstellen. Bei Scanner-Ausfall Uploads nicht ungeprüft freigeben.
3. Upload-Grenze in der Organisationseinstellung auf den tatsächlichen Bedarf begrenzen und mit Nginx-/Proxy-/Django-Limits abstimmen. Auch Anzahl und Gesamtvolumen je Benutzer/Reihe überwachen.
4. MEDIA_ROOT außerhalb des öffentlich durch Nginx ausgelieferten Document Roots halten. Für Docker ausschließlich das vorgesehene private Media-Volume nutzen. Keine zusätzliche Nginx-Alias- oder Static-Media-Regel für Uploads einrichten.
5. Downloads ausschließlich über die authentifizierte Anwendungsroute ausliefern. Für neue Datei-Endpunkte Tests ergänzen, die fehlende Anmeldung, falsche Serienzuweisung, Auditorzugriff und manipulierte Datei-IDs zurückweisen.
6. Medien-Volume verschlüsselt sichern, Dateiberechtigungen auf das Dienstkonto begrenzen und Zugriff auf Host-/Backup-Ebene auf Administratoren beschränken.

**Nachweis:** dokumentierte Dateityp-Allowlist, Scanner-Konfiguration, Upload-/Download-Negativtests und Prüfung der Nginx-/Volume-Konfiguration.

### 7.5 Datenschutz und Inhalte

1. Für den Einsatz schriftlich festlegen, welche Themen und personenbezogenen Angaben in Protokollen zulässig sind. Besondere Kategorien personenbezogener Daten und private/medizinische Personalinformationen grundsätzlich nicht in Freitext oder Anlagen aufnehmen, sofern keine gesonderte Rechtsgrundlage und Erforderlichkeit festgestellt wurde.
2. In der Hilfe und in einer Nutzungsrichtlinie einen kurzen Hinweis ergänzen: nur besprechungsnotwendige Informationen erfassen, keine Zugangsdaten oder besonders schützenswerten Inhalte in Kommentare/Anlagen einstellen.
3. Protokoll- und Themenverantwortliche benennen. Diese prüfen bei Abschluss, ob Inhalte sachlich erforderlich und für den vorgesehenen Empfängerkreis geeignet sind.
4. Zweck, Rechtsgrundlage, Empfänger, Speicherorte und Aufbewahrungsfrist für Kontodaten, Protokolle, Snapshots, Kommentare, Anlagen, Audit-Logs, CSV-Exporte und Backups dokumentieren.
5. Einen Prozess für Auskunft, Berichtigung, Löschung und Einschränkung einrichten. Dabei auch Snapshot-Daten, Audit-Logs, Exportdateien und Backup-Rotation berücksichtigen.
6. Vor Einführung mit Datenschutzbeauftragten und ggf. Personalvertretung prüfen, ob eine Datenschutz-Folgenabschätzung erforderlich ist und ob die Nutzung als Leistungs-/Verhaltenskontrolle ausgeschlossen bzw. geregelt werden muss.

**Nachweis:** freigegebene Nutzungsrichtlinie, Verzeichnis der Verarbeitungstätigkeiten, Löschkonzept und Betroffenenrechte-Prozess.

### 7.6 CSV, Vollbackup und Datenwiederherstellung

1. CSV-Importe/-Exporte und Vollbackup-/Restore-Funktionen auf Admin-Konten beschränken. Für Exporte einen dokumentierten Zweck und Empfängerkreis verlangen.
2. Exportdateien ausschließlich in zugriffsbeschränkten, verschlüsselten Verzeichnissen ablegen und über einen sicheren Übertragungsweg weitergeben. Nach erfolgreicher Übergabe lokal löschen; Papierkorb und Synchronisationskopien berücksichtigen.
3. Vor Importen die Vorschau vollständig prüfen. Änderungen an Benutzerrollen, Serienzuweisungen und bestehenden Themen nur nach Vier-Augen-Kontrolle übernehmen.
4. Vor Datenbank-Restore immer einen aktuellen zusätzlichen Sicherungsstand erstellen und Restore nur in einem kontrollierten Wartungsfenster durch autorisierte Administratoren durchführen.
5. Datenbank und Medienverzeichnis zeitlich passend und gemeinsam sichern. Mindestens eine verschlüsselte Kopie getrennt vom Produktivhost aufbewahren; Schreibzugriff des Produktivsystems auf diese Kopie vermeiden.
6. RPO/RTO festlegen und mindestens quartalsweise eine Wiederherstellung in einer isolierten Testumgebung durchführen. Prüfen, ob Datenbank, Anhänge, Logos und statische Betriebsdaten konsistent sind.

**Nachweis:** Backup-Protokolle, Zugriffsrechte, dokumentierte Aufbewahrung und quartalsweiser Restore-Test.

### 7.7 Änderungsverlauf und Überwachung

1. Audit-Ereignisse auf das notwendige Maß beschränken. Keine Passwörter, Authentifizierungs-Tokens, Datei-Inhalte oder unnötigen Freitext in Audit-Details aufnehmen.
2. Zugriff auf System- und Serienverläufe entsprechend der Rollen begrenzen. CSV-Exporte des Systemverlaufs wie vertrauliche Personaldaten behandeln.
3. Sicherheitsrelevante Systemereignisse zusätzlich an einen zentralen Logserver/SIEM übertragen. Schreibrechte auf der zentralen Ablage vom App- und DB-Administrationskonto trennen; soweit verfügbar manipulationsgeschützte Aufbewahrung nutzen.
4. Auf ungewöhnliche Häufungen von Login-Fehlern, Änderungen globaler Rollen, CSV-/Vollbackup-Exporte, Datenbank-Restores und wiederholte Downloadfehler Alarmregeln einrichten.
5. Aufbewahrungsdauer und Zugriff auf Logs festlegen. Logdaten nicht unbegrenzt speichern; Zugriff auf die zentrale Logplattform selbst protokollieren.

**Nachweis:** Logging-Konzept, SIEM-Regeln, Rollen für Logzugriff und dokumentierte Löschfristen.

### 7.8 Patch- und Lieferkettenmanagement

1. Für Betriebssystem, PostgreSQL, Python-Abhängigkeiten, Docker-Basisimages und Nginx einen festen Patch-Rhythmus mit kurzfristigem Prozess für kritische Sicherheitsupdates definieren.
2. Bei jedem Build Abhängigkeitsscans und Container-Image-Scans ausführen. Kritische und hohe Befunde vor Freigabe beheben oder mit Verantwortlichem, Begründung und Frist dokumentiert akzeptieren.
3. Produktionsimages nur aus freigegebenen Branches/Tags beziehen. Version und Commit des laufenden Builds dokumentieren; keine ungeprüften Branches im Produktivsystem verwenden.
4. Updates zunächst in einer Testumgebung mit Datenbankkopie prüfen. Vor Migrationen Backup erstellen und nach dem Update Login, Berechtigungen, Upload/Download, PDF-Export und Protokollabschluss testen.
5. Rollback nicht mit Datenbank-Rollback gleichsetzen: Bereits angewendete Migrationen können eine Wiederherstellung aus Backup erfordern. Vorgehen vorab testen.

**Nachweis:** Scanberichte, Patchprotokoll, Releasefreigabe und dokumentierter Rollback-/Restore-Ablauf.

### 7.9 Netzwerk- und Verfügbarkeitsbetrieb

1. Nur erforderliche Ports öffnen. PostgreSQL nicht veröffentlichen; Docker-App-Port 8000 nicht nach außen freigeben. SSH nur aus Admin-Netzen zulassen.
2. Reverse-Proxy-Limits für Request-Größe, Verbindungszahl und Zeitüberschreitungen setzen; Upload-Grenzen mit der Anwendung abstimmen.
3. CPU, RAM, Plattenplatz, PostgreSQL-Verbindungen, HTTP-Fehler und Dienstverfügbarkeit überwachen. Alarmgrenzen und Eskalationskontakte festlegen.
4. Netzwerkpfade und externe Links als Verweise behandeln: Die Berechtigung am Zielsystem muss separat geprüft werden. Keine Passwörter oder Zugriffstoken in URLs hinterlegen.
5. Notfallverfahren für Ausfall, Ransomware, kompromittiertes Konto und Datenpanne dokumentieren und regelmäßig durchspielen.

**Nachweis:** Firewall-Regeln, Monitoring-Dashboard, Alarmtest und Incident-Response-Runbook.

## 8. Datenschutzrechtliche und organisatorische Freigabepunkte

Vor produktiver Nutzung sind mit Verantwortlichem, IT, Informationssicherheit und Datenschutzbeauftragten mindestens folgende Punkte zu klären:

- Zweck(e), Rechtsgrundlage(n) und Verantwortlichkeit für Besprechungsdokumentation und Beschäftigtendaten.
- Datenkategorien, Empfänger, Hostingstandort, Unterauftragnehmer und Supportzugriffe.
- Verzeichnis der Verarbeitungstätigkeiten und Transparenzinformation für Nutzer.
- Notwendigkeit einer Datenschutz-Folgenabschätzung; Beteiligung einer Personalvertretung, soweit erforderlich.
- Aufbewahrungs- und Löschfristen für aktive Inhalte, Protokoll-Snapshots, Kommentare, Audit-Daten, Exportdateien und Backups.
- Verfahren für Betroffenenrechte und Datenschutzverletzungen.
- Technische und organisatorische Maßnahmen anhand des tatsächlichen Schutzbedarfs.
- Klare Abgrenzung, dass die Anwendung nicht ohne gesonderte Prüfung zur Leistungs- oder Verhaltenskontrolle eingesetzt wird.

## 9. Betriebsverantwortung

| Aufgabe | Primär verantwortlich | Mitwirkung/Kontrolle |
|---|---|---|
| Hosting, TLS, Netzwerk, Datenbank, Updates, Backups | IT-Betrieb | Informationssicherheit |
| Benutzerkonten und globale Rollen | Anwendungsadministration | IT / Informationssicherheit |
| Serienzuweisungen und fachliche Inhalte | Fachverantwortliche / Moderator*innen | Anwendungsadministration |
| Regelmäßige Berechtigungsprüfung | Fachverantwortliche | IT / Informationssicherheit |
| Zwecke, Rechtsgrundlagen, Betroffenenrechte, Löschkonzept | Verantwortliche Organisationseinheit | Datenschutzbeauftragte |
| Sicherheitsvorfälle und Wiederherstellung | IT-Betrieb / Incident Response | Datenschutzbeauftragte bei Datenschutzverletzungen |

## 10. Prüfgrundlage und Grenzen

Geprüft wurden insbesondere:

- `README.md`: Funktionsumfang, Rollenmatrix, Installations- und Sicherheitshinweise.
- `meetings/access.py`, `meetings/user_roles.py`: globale Rollen und zentrale Serienzugriffslogik.
- `meetings/models.py`: Datenmodelle, Anlagen, Serienzuweisungen, Audit-Ereignisse und Protokoll-Snapshots.
- `meetings/secure_files.py`, `meetings/views.py`: geschützte Datei-Auslieferung und fachliche Zugriffspfade.
- `meetings/audit.py`, `meetings/audit_export.py`: Ereigniserfassung und Export.
- `config/settings.py`: Django-Sicherheitseinstellungen, Middleware, Sessions und Passwortvalidierung.
- `meetings/management_views.py`, `meetings/setup_views.py`: Verwaltung, Import/Export und Ersteinrichtung.
- `meetings/guide_views.py`, `templates/meetings/user_guide.html`: Hilfe-Bereich.
- `docker/compose.yaml`, `docker/Dockerfile`, `.env.example`, Installationsskripte: Bereitstellung und Konfigurationsdefaults.
- Berechtigungs-, Audit-, CSV- und Sicherheitsregressionstests im Repository.

Nicht untersucht wurden eine laufende Instanz, tatsächliche Firewall-/Proxy-/DNS-Konfiguration, Betriebssystemhärtung, reale Datenbestände, Auftragsverarbeitungsverträge, organisatorische Prozesse oder ein unabhängiger Penetrationstest. Die Risikobewertung muss daher vor Ort bestätigt und nach wesentlichen Änderungen aktualisiert werden.

## 11. Freigabevermerk

Die Freigabe sollte erst erfolgen, wenn die priorisierten Maßnahmen aus Kapitel 7 umgesetzt oder mit einer dokumentierten Risikoakzeptanz versehen wurden.

| Stelle | Bewertung | Name / Datum / Auflagen |
|---|---|---|
| IT-Abteilung | ☐ freigegeben ☐ mit Auflagen ☐ nicht freigegeben | |
| Informationssicherheit | ☐ freigegeben ☐ mit Auflagen ☐ nicht freigegeben | |
| Datenschutzbeauftragte | ☐ Stellungnahme erfolgt ☐ Rückfragen offen | |
| Fachverantwortung | ☐ fachlich freigegeben ☐ Rückfragen offen | |
