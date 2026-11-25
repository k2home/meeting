**Adressaten:** IT-Abteilung, Informationssicherheit und Datenschutzbeauftragte  
**Prüfstand:** Branch `main`  
**Stand:** 25. November 2026  
**Geltungsbereich:** Anwendungscode und Repository-Konfiguration. Die konkrete Server-, Proxy-, Netzwerk- und Backup-Konfiguration ist vor Ort gesondert zu prüfen.

> **Einordnung:** Diese Beschreibung ist eine nachvollziehbare technische Bestandsaufnahme und Risikoeinschätzung. Sie ist weder Penetrationstestbericht noch Datenschutz-Folgenabschätzung, TOM-Nachweis oder rechtsverbindliche DSGVO-Konformitätsbestätigung. Aussagen über die reale Betriebsumgebung gelten nur, wenn sie dort verifiziert wurden.

## 1. Kurzbeschreibung und Zweck

Meeting Manager ist eine deutschsprachige Webanwendung zur Organisation wiederkehrender Besprechungen und zur fortlaufenden Bearbeitung von Themen. Sie verbindet Besprechungsreihen und Termine mit Tagesordnungspunkten, Zuständigkeiten, Kommentaren, Anlagen und Protokollen.

Ein Thema beschreibt einen fortlaufenden Vorgang. Ein Tagesordnungspunkt ist die Behandlung dieses Themas in einem konkreten Termin. Der zu einem Termin gehörende Text und Status werden getrennt geführt. Beim Abschluss einer Besprechung speichert die Anwendung einen Protokoll-Snapshot. Spätere Änderungen am Thema verändern diesen historischen Snapshot nicht.

Die Anwendung ist laut Repository für interne Netze vorgesehen. Sie wird entweder auf Debian/Ubuntu mit PostgreSQL, Gunicorn und Nginx oder containerisiert mit Docker Compose betrieben.

## 2. Funktionsumfang und Datenverarbeitung

### 2.1 Fachliche Funktionen

- Wiederkehrende Besprechungsreihen mit wählbarem wöchentlichem oder monatlichem Rhythmus und Intervall (1–52 Wochen bzw. 1–52 Monate); Termine werden anhand der konfigurierten Daten erzeugt.
- Themen mit Status, Hauptzuständigkeit und Zuordnung zu einer Besprechungsreihe.
- Tagesordnungspunkte mit eigenem Text, Bearbeitungsstatus, Reihenfolge und optional abweichender Zuständigkeit je Termin.
- Kommentare, nächste Schritte, Datei-Anlagen und Verweise auf Netzwerkpfade bzw. Webadressen.
- Wiedervorlagen und Übernahme offener Punkte in Folgetermine.
- Abschluss einer Sitzung mit gesichertem Protokollstand; Anzeige, Druck und PDF-Export.
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
| Änderungsdaten | handelnde Person, Zeitpunkt, Aktion, Zusammenfassung, ausgewählte Änderungen | Nachvollziehbarkeit; mögliche Beschäftigtenbezüge |
| Betriebsdaten | Webserver-, Betriebssystem-, Datenbank- und Proxy-Logs, Backups | Abhängig von Hosting und Betriebsüberwachung |

Die Anwendung kann nicht verhindern, dass Nutzer*innen in Freitexten oder Anlagen unzulässige oder besonders schützenswerte Informationen hinterlegen. Dafür sind verbindliche Nutzungsregeln, Schulung und eine fachliche Freigabe der vorgesehenen Datenkategorien erforderlich.

## 3. Rollen- und Berechtigungskonzept

Das Modell kombiniert eine globale Rolle und unabhängige Berechtigungen je Besprechungsreihe. Eine globale Rolle ersetzt keine Serienzuweisung.

### 3.1 Globale Rollen

| Rolle | Umfang |
|---|---|
| **Nutzer*innen** | Standardrolle. Fachlicher Zugriff ausschließlich auf ausdrücklich zugewiesene Besprechungsreihen und gemäß der dortigen Serienrolle. |
| **Admin** | Globale Verwaltungsrechte für Benutzerkonten, globale Rollen, Serienzuweisungen und Organisationseinstellungen sowie administrative Funktionen. Kein automatischer Zugriff auf fachliche Reiheninhalte. Fachliche Aktionen und Reiheninhalte setzen eine passende Serienzuweisung voraus. |
| **Auditor*in** | Lesender Zugriff auf administrative Prüfdaten: System-Änderungsverlauf, Benutzerkonten und Rollen-/Serienzuordnungen sowie Organisationseinstellungen. Kein Zugriff auf Besprechungsreihen oder fachliche Besprechungsinhalte und keine Änderungsrechte. |

Django-Superuser werden als globale Admins behandelt. Die Admin-Gruppe wird mit dem Django-Staff-Status synchronisiert. Die Auditor*innen-Rolle ist gegenüber Admin nachrangig: Ein Konto mit Admin- oder Superuser-Rechten wird nicht als Auditor behandelt.

### 3.2 Serienrollen

| Serienrolle | Rechte innerhalb der ausdrücklich zugewiesenen Reihe |
|---|---|
| **Leser*in** | Inhalte, Tagesordnungen, Themen, Anlagen und Protokolle ansehen und Protokolle exportieren; keine fachlichen Änderungen. |
| **Teilnehmer*in** | Zusätzlich Themen und Tagesordnungspunkte bearbeiten, Zuständigkeiten setzen, kommentieren, Anlagen ergänzen, Wiedervorlagen verwalten, Teilnehmerlisten bearbeiten und Besprechungen abschließen. Keine Reihenverwaltung und kein Wiederöffnen abgeschlossener Besprechungen. |
| **Moderator*in** | Zusätzlich Besprechungsreihe und Termine verwalten, Themen archivieren/wieder öffnen, abgeschlossene Besprechungen wieder öffnen und den Änderungsverlauf der eigenen moderierten Reihe einsehen. |

Nutzer*innen können in verschiedenen Reihen unterschiedliche Rollen besitzen. Eine Moderator*innenrolle in einer Reihe verleiht keine Rechte in einer anderen Reihe.

### 3.3 Historische Zugriffe und Änderungsverlauf

Wird eine Besprechungsreihe gelöscht, bleiben historische Termine und Protokolle standardmäßig erhalten. Die früheren Reihenmitglieder erhalten für diese erhaltenen Inhalte einen gesonderten Lesezugriff. Eine ausdrücklich gewählte endgültige Löschung kann abgeschlossene Besprechungen und Protokolle zusätzlich entfernen.

Der Änderungsverlauf ist in zwei Bereiche getrennt:

- Serienereignisse sind ausschließlich für Moderator*innen der jeweiligen Reihe sichtbar. Admins sehen Serienereignisse ebenfalls nur für Reihen, in denen sie selbst ausdrücklich Moderator*innenrechte besitzen.
- Systemereignisse sind für globale Admins und Auditor*innen sichtbar. Auditor*innen haben ausschließlich lesenden Zugriff auf Systemereignisse und keinen Zugriff auf Serienereignisse oder fachliche Reiheninhalte.
- Die CSV-Exportansichten wenden dieselbe Bereichstrennung an: Admins/Auditor*innen exportieren Systemereignisse; Moderator*innen exportieren Ereignisse ihrer eigenen moderierten Reihen.

Das Modell ist damit auf das Need-to-know-Prinzip ausgerichtet. Kritisch bleibt die konsequente Prüfung jedes neuen Endpunkts, Exports und administrativen Sonderwegs gegen diese Regeln.

## 4. Technische Architektur

- **Anwendungsframework:** Django (Python 3.13 im Docker-Image).
- **Datenbank:** PostgreSQL 16 im Docker-Betrieb; PostgreSQL auch für die Debian-Installation.
- **Webserver / Prozess:** Nginx und Gunicorn.
- **Dateien:** separates Medienverzeichnis bzw. Docker-Volume; statische Dateien werden separat bereitgestellt.
- **Container:** App-Prozess läuft als nicht privilegierter Benutzer. PostgreSQL ist im Compose-Netz erreichbar und erhält keinen veröffentlichten Host-Port. Der App-Container veröffentlicht Port 8000 nur intern; der Nginx-Container veröffentlicht den konfigurierten Web-Port.
- **Konfiguration:** Umgebungsvariablen und lokale `.env`-Datei. `SECRET_KEY` und Datenbankzugangsdaten sind vertraulich zu behandeln.

Die Installationsskripte erzwingen HTTPS auf Anwendungsebene: SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE und CSRF_COOKIE_SECURE werden aktiviert; CSRF_TRUSTED_ORIGINS wird auf die öffentliche HTTPS-Adresse gesetzt. Django vertraut X-Forwarded-Proto nur im vorgesehenen Reverse-Proxy-Betrieb. Bei Debian nimmt die lokale Nginx-Konfiguration HTTP auf Port 8080 entgegen und begrenzt den Zugriff auf die beim Setup angegebene Proxy-IP/CIDR. Bei Docker wird der veröffentlichte Nginx-Port standardmäßig ausschließlich an 127.0.0.1 gebunden. In beiden Varianten muss vor dem produktiven Zugriff ein TLS-Reverse-Proxy mit gültigem Zertifikat eingerichtet sein, der X-Forwarded-Proto: https setzt und eingehende Client-Header überschreibt. Ohne diesen Proxy ist die Anwendung absichtlich nicht regulär erreichbar.

## 5. Bereits vorhandene Sicherheitskontrollen

Die folgenden Kontrollen sind im geprüften Quellcode bzw. in den Installationsdateien erkennbar. Sie ersetzen nicht die Prüfung der tatsächlich betriebenen Instanz.

| Bereich | Vorhandene Kontrolle | Einordnung |
|---|---|---|
| Anmeldung | Django-Authentifizierung; geschützte Anwendungsbereiche verlangen Anmeldung. | Keine Aussage über externe Identitätsverwaltung. |
| Passwörter | Django-Passworthashing; Mindestlänge 8, Komplexitätsvalidator, Ähnlichkeits- und häufige-Passwort-Prüfung. | MFA und ein anwendungsinterner Login-Rate-Limiter sind im geprüften Kern nicht belegt. |
| Sessions | Session-Laufzeit 8 Stunden; Session wird bei Requests gespeichert/erneuert. | Bei langen aktiven Sitzungen erhöht dies die Bedeutung von Geräteschutz und Logout. |
| Autorisierung | Zentrale Serienzugriffsabfragen; Auditor*innen werden aus fachlichen Reihenabfragen ausgeschlossen; Admin ist keine Serienrolle. | Endpunkt- und Exporttests müssen die Regeln vollständig abdecken. |
| CSRF / Browser-Header | Django-CSRF-Middleware; nosniff, Referrer-Policy same-origin und X-Frame-Options DENY. | Eine umfassende Content-Security-Policy für alle Seiten ist nicht belegt. |
| TLS / Cookies / CSRF | Die Installer erzwingen HTTPS-Redirect und Secure-Cookies, setzen die HTTPS-CSRF-Origin und aktivieren Proxy-Vertrauen. Debian begrenzt den Zugriff auf die angegebene Proxy-IP/CIDR; Docker bindet den Web-Port an Loopback. | Ein gültiges TLS-Zertifikat und ein korrekt konfigurierter Reverse Proxy bleiben erforderlich. HSTS-Preload wird validiert und muss bewusst separat aktiviert werden. |
| Uploads | Anlagenlimit wird organisationsweit konfiguriert (1–24 MB, Standard 20 MB). Für Themenanlagen gilt serverseitig eine Dateiendungs-Allowlist: PDF, DOCX, XLSX, PPTX, TXT, PNG und JPEG. Download erfordert Anmeldung und Serienzugriff; Pfad wird auf MEDIA_ROOT begrenzt; Download als Attachment, nosniff und private/no-store. | Die Allowlist prüft die Dateiendung, nicht die tatsächliche Dateisignatur oder den Dateiinhalt. Malware-Scanning ist nicht integriert. |
| Logos / SVG | Logo-Auslieferung ist angemeldet, auf MEDIA_ROOT begrenzt und privat/no-store. SVG erhält eine restriktive CSP-Sandbox. | Upload- und Konvertierungspfad weiter beobachten. |
| Audit | Protokolliert werden handelnde Person, Zeitpunkt, Aktion, eine begrenzte Zusammenfassung und gezielt ausgewählte Änderungsmetadaten. Passwortwerte und hochgeladene Datei-Inhalte werden nicht gespeichert; bei Passwortänderungen wird nur der Status der Änderung festgehalten. Dateinamen können als Metadaten erscheinen. Eine fachliche Ausnahme ist das Wiederöffnen einer abgeschlossenen Besprechung: Der vorherige gesicherte Protokollstand wird als Audit-Detail aufbewahrt. Systemereignisse sehen globale Admins und Auditor*innen. Serienereignisse sehen Moderator*innen ausschließlich für ihre moderierten Reihen; globale Admins sehen sie ebenfalls nur, wenn sie in der jeweiligen Reihe ausdrücklich als Moderator*in zugewiesen sind. | Die Datenbankablage ist nicht manipulationsgeschützt. Die Oberfläche zeigt nur freigegebene Ereignisse und aufklappbare, ausgewählte Änderungsdetails; sie ist kein vollständiges Aktivitäts- oder Inhaltsprotokoll. |
| CSV | Import mit Vorschau/Bestätigung; Exportwerte werden gegen Tabellenformel-Präfixe abgesichert. Benutzer-CSV und Vollbackup/Restore sind Admin-Funktionen; Themen-CSV ist auf Moderator*innen und ihre moderierten Reihen begrenzt. | Import-/Exportdateien bleiben sensible Datenkopien. |
| Betrieb | Docker-App läuft als nicht-root; DB nicht nach außen veröffentlicht; Updater nutzt lokalen Socket statt Docker-Socket im App-Container. | Host, Socket-Berechtigungen, Images, Volumes und Updater bleiben Teil der Vertrauensgrenze. |
| Backups | Integrierter Datenbank-Vollbackup-Export/-Import und dokumentierte Backup-Wege für Datenbank und Medien. | Ein belastbarer externer Backup-, Verschlüsselungs- und Restore-Prozess muss von den Betreiber*innen eingerichtet werden. |

## 6. Häufige Sicherheitsrisiken und Bewertung der Schutzmaßnahmen

Die folgende Bewertung orientiert sich an typischen Risiken von Webanwendungen. Sie unterscheidet zwischen Schutzmaßnahmen, die im geprüften Quellcode bzw. in der Installationskonfiguration erkennbar sind, und verbleibenden Aufgaben für den Betrieb. Eine vorhandene Kontrolle reduziert ein Risiko, beseitigt es aber nicht automatisch.

| Häufiges Risiko | Bereits vorhandene Schutzmaßnahmen im Meeting Manager | Bewertung und verbleibender Handlungsbedarf |
|---|---|---|
| **Unberechtigter Zugriff / Broken Access Control** | Zentrale Serienzugriffsabfragen; globale Admin-Rechte ersetzen keine Serienzuweisung; Auditor*innen sind von fachlichen Reiheninhalten ausgeschlossen; Leser*innen-, Teilnehmer*innen- und Moderator*innenrechte werden getrennt geprüft. | **Im Anwendungscode wesentlich adressiert.** Neue Views, APIs, Exporte und direkte Objekt-IDs müssen weiterhin mit Positiv- und Negativtests für alle Rollen abgesichert werden. |
| **SQL-Injection und sonstige Eingabe-Injection** | Standard-Datenbankzugriffe über das Django-ORM mit parametrisierten Abfragen; Formulare und Modellvalidierungen prüfen Eingaben. | **Durch Framework-Schutzmaßnahmen adressiert.** Raw-SQL, dynamische Filter und neue Importpfade müssen separat geprüft werden; keine ungeprüfte SQL-Stringverkettung einführen. |
| **Cross-Site Request Forgery (CSRF)** | Django-CSRF-Middleware und CSRF-Tokens in Formularen. Die Installer aktivieren sichere CSRF-Cookies und setzen die öffentliche HTTPS-Origin. | **Im Code und Installationsstandard adressiert.** Der Reverse Proxy muss die korrekte HTTPS-Origin weitergeben; CSRF-Schutz darf für neue schreibende Views nicht umgangen werden. |
| **Abhören oder Übernehmen von Sitzungen** | Die Installer erzwingen HTTPS-Redirect sowie Secure-Attribute für Session- und CSRF-Cookies. Django verwaltet die Sitzungen; die Laufzeit ist auf acht Stunden begrenzt. | **Mit korrekt eingerichtetem TLS-Reverse-Proxy adressiert.** Zertifikatserneuerung, Proxy-Isolation, Geräteschutz und Logout bleiben Betriebsaufgaben. Eine Sitzung kann bei kompromittiertem Endgerät weiterhin missbraucht werden. |
| **Passwortdiebstahl und Brute Force** | Django-Passworthashing, Mindestlänge 8 sowie Komplexitäts-, Ähnlichkeits- und Häufige-Passwort-Prüfung. | **Teilweise adressiert.** MFA und anwendungsinterne Login-Drosselung sind im geprüften Kern nicht belegt. MFA über Identity Provider bzw. vorgeschaltete Zugangskontrolle und Rate-Limiting am Proxy ergänzen. |
| **Cross-Site Scripting (XSS)** | Django-Templates escapen gewöhnliche Ausgaben standardmäßig; nosniff, Referrer-Policy same-origin und X-Frame-Options DENY sind gesetzt. | **Teilweise adressiert.** Eine umfassende Content-Security-Policy ist nicht belegt. Bei neuen HTML-Ausgaben keine ungeprüften Safe-Ausgaben oder dynamisch eingebetteten Skripte verwenden; CSP prüfen und schrittweise einführen. |
| **Schadsoftware und aktive Inhalte in Datei-Uploads** | Uploadgrößen sind begrenzt. Themenanlagen akzeptieren serverseitig nur die Dateiendungen PDF, DOCX, XLSX, PPTX, TXT, PNG, JPG und JPEG. Downloads erfordern Anmeldung und Serienzugriff, erfolgen als Attachment und mit nosniff; Pfade werden auf MEDIA_ROOT begrenzt. | **Teilweise adressiert.** Die Endungs-Allowlist verhindert nicht, dass andersartige Inhalte mit erlaubter Endung hochgeladen werden. Dateisignaturprüfung und Malware-Scanning fehlen weiterhin und sollten vor einer Freigabe ergänzt werden. |
| **Datenabfluss über Anlagen, CSV und Backups** | Anlagen werden über eine geschützte Download-Route ausgeliefert. CSV-Import hat eine Vorschau; Exportwerte werden gegen Tabellenformeln abgesichert. Benutzer-CSV und Vollbackup/Restore sind Admin-Funktionen; Themen-CSV ist auf Moderator*innen und ihre moderierten Reihen begrenzt. | **Im normalen Anwendungspfad adressiert, Betrieb bleibt kritisch.** MEDIA-Verzeichnis nicht öffentlich ausliefern; Exportdateien und Backups verschlüsseln, Zugriff beschränken, Aufbewahrung und Löschung regeln. |
| **Missbrauch privilegierter Konten / Insider-Risiko** | Admin- und Auditor*innen-Rollen sind getrennt; Auditor*innen haben ausschließlich Leserechte. Admins erhalten fachlichen Reihen-Zugriff nicht allein durch ihre globale Rolle. Administrative und fachliche Ereignisse werden protokolliert. | **Teilweise adressiert.** Admin-Konten minimieren, MFA einsetzen, Admin-Aktionen überwachen und regelmäßige Rechteprüfungen durchführen. Privilegierte Host-/DB-Zugriffe bleiben außerhalb der Anwendungsautorisierung. |
| **Manipulation oder Verlust von Audit-Daten** | Serienereignisse sind für Moderator*innen ihrer jeweils moderierten Reihen sichtbar; globale Admins sehen sie nur mit eigener Moderator*innen-Zuweisung. Systemereignisse sind für globale Admins und Auditor*innen sichtbar. Die Erfassung beschränkt sich auf Ereignismetadaten und ausgewählte Änderungen. Passwortwerte und hochgeladene Datei-Inhalte werden nicht protokolliert. Beim Wiederöffnen einer abgeschlossenen Besprechung wird jedoch der vorherige Protokoll-Snapshot als fachliches Audit-Detail gespeichert. | **Zugriff und Darstellung sind eng begrenzt.** In der Weboberfläche sind Änderungsdetails zunächst eingeklappt; der CSV-Export enthält die strukturierten Änderungsdetails im Exportumfang der jeweiligen Rolle. Beim Wiederöffnen einer abgeschlossenen Besprechung bleibt der vorherige Protokoll-Snapshot im Audit erhalten. Die Datenbank selbst ist kein manipulationsgeschützter/WORM-Speicher. |
| **Veraltete Abhängigkeiten und Container-Images** | Python-Abhängigkeiten sind in Requirements/Constraints festgelegt; Images werden über den Build-/Release-Prozess bereitgestellt. | **Nur organisatorisch/über CI beherrschbar.** Regelmäßige Dependency- und Image-Scans, zeitnahe Sicherheitsupdates und Freigabe nur geprüfter Releases sicherstellen. |
| **Denial of Service und Ressourcenerschöpfung** | Uploadgrößen sind begrenzt; Datenbank und App sind in getrennten Diensten organisiert. | **Nur teilweise adressiert.** Request-Größen, Verbindungen, Rate-Limits, Timeouts, CPU, RAM und Speicherplatz am Proxy und Host begrenzen und überwachen. |
| **Datenverlust / fehlende Wiederherstellbarkeit** | Datenbank- und Medien-Backups sowie Import-/Restore-Funktionen sind vorhanden und dokumentiert. | **Nicht durch den Code garantiert.** Getrennte, verschlüsselte Backups, definierte RPO/RTO und regelmäßige Restore-Tests sind zwingend durch den Betreiber einzurichten. |
| **Fehlkonfiguration von HTTPS und Proxy-Vertrauen** | Die Installer setzen HTTPS-Redirect, Secure-Cookies, CSRF-Origin und Proxy-Vertrauen verbindlich. Debian beschränkt den internen Nginx-Zugriff auf die angegebene Proxy-IP/CIDR; Docker bindet den Web-Port nur an Loopback. | **Im Installationsstandard deutlich reduziert.** Ein gültiger TLS-Reverse-Proxy muss tatsächlich eingerichtet sein, Forwarded-Header überschreiben und darf nicht umgangen werden. HSTS bleibt eine bewusst zu prüfende Zusatzmaßnahme. |

Die Einstufung beschreibt Schutzmechanismen im Repository, nicht den Sicherheitszustand eines konkreten Servers. Insbesondere TLS-Zertifikat, Reverse-Proxy-Konfiguration, Firewall, MFA, Malware-Scanner, zentrale Protokollierung und Backups müssen in der Zielumgebung überprüft werden.

## 7. Konkrete Maßnahmen und empfohlene Vorgehensweisen

Die folgenden Schritte sind bewusst als umsetzbare Arbeitsanweisungen formuliert. Die Reihenfolge priorisiert die größten Auswirkungen.

### 7.1 Rollen und Serienberechtigungen – laufender Kontrollprozess

1. Globale Admin-Konten auf einen kleinen, namentlich festgelegten Personenkreis begrenzen. Für normale Arbeit persönliche Konten verwenden, nicht das Admin-Konto.
2. Für jede Besprechungsreihe einen fachlichen Eigentümer benennen. Dieser bestätigt bei Anlage und mindestens quartalsweise die Mitglieder und deren Rolle.
3. Bei Eintritt, Rollenwechsel und Austritt von Mitarbeitenden die Serienzuweisungen unmittelbar anpassen. Deaktivierte Konten und nicht mehr benötigte Serienzuweisungen in einem dokumentierten Offboarding-Prozess berücksichtigen.
4. Bei jeder Änderung an Views, Exporten, Downloads oder APIs eine Berechtigungsmatrix mit Positiv- und Negativtests ergänzen: Leser*innen, Teilnehmer*innen, Moderator*innen, Admin ohne Serienzuweisung, Admin mit Serienzuweisung und Auditor*innen.
5. Für jede Ressource sowohl Listenansichten als auch direkte Objekt-IDs testen. Eine nicht berechtigte Person muss auch durch Erraten einer URL/ID keinen Inhalt erhalten oder ändern können.
6. Auditor*innen-Tests müssen mindestens GET-Lesezugriffe auf die freigegebenen Prüfdaten sowie Ablehnung aller schreibenden HTTP-Methoden und sämtlicher fachlicher Reihen-/Anlagenzugriffe nachweisen.
7. Admin-Sonderfunktionen (CSV, Vollbackup, Restore, Organisationseinstellungen, globale Rollen) nur über die vorgesehenen Verwaltungsansichten erlauben und ihre Zugriffe protokollieren.

**Nachweis:** Quartalsweise Berechtigungsliste mit Freigabe durch den fachlichen Reihenverantwortlichen; CI-Testresultate für alle Rollen.

### 7.2 Benutzerkonten und Anmeldung

1. Wo organisatorisch möglich, Anmeldung über einen zentralen Identity Provider mit MFA erzwingen. Falls lokale Konten verbleiben, MFA als vorgeschaltete Zugangskontrolle oder über eine geprüfte Django-Erweiterung ergänzen.
2. Login-Rate-Limiting am Reverse Proxy oder durch eine gepflegte Django-Komponente einrichten. Als Startwert z. B. nach 5 fehlgeschlagenen Anmeldungen pro Konto/IP eine zeitlich begrenzte Verzögerung bzw. Sperre auslösen; legitime Nutzer*innen müssen kontrolliert entsperrt werden können.
3. Fehlermeldungen bei Login nicht verraten, ob Benutzername oder Passwort falsch ist. Fehlversuche und ungewöhnliche Anmeldehäufungen zentral überwachen.
4. Passwortregeln der Anwendung beibehalten; Nutzer*innen zu individuellen Passphrasen und Passwortmanagern anhalten. Gemeinsame Startpasswörter nur über einen geschützten Einmalprozess übermitteln und beim ersten Zugriff ändern lassen.
5. Bei Rollenwechsel, Austritt oder Sicherheitsvorfall Konten deaktivieren, Sessions invalidieren und bei Verdacht Passwörter sowie relevante Secrets rotieren.
6. Die 8-Stunden-Session-Laufzeit mit dem Schutzbedarf abstimmen. Für gemeinsam genutzte Arbeitsplätze automatische Bildschirmsperre und explizites Abmelden verbindlich machen.

**Nachweis:** Konfiguration des IdP/Rate-Limiters, Testprotokoll für Fehlversuche und dokumentierter Offboarding-Prozess.

### 7.3 Datei-Uploads und Downloads

1. Für Themenanlagen gilt bereits eine serverseitige Dateiendungs-Allowlist: PDF, DOCX, XLSX, PPTX, TXT, PNG, JPG und JPEG. Andere Endungen – insbesondere ausführbare Dateien, Skripte und Archive – werden durch die Formularvalidierung abgewiesen. Die Allowlist prüft nur den Dateinamen, nicht die tatsächliche Dateisignatur oder den Dateiinhalt.
2. Als nächste Schutzstufe Dateisignaturen serverseitig prüfen und Malware-Scanning vor Freigabe zum Download einführen. Dateien bis zur erfolgreichen Prüfung in Quarantäne halten; bei Scanner-Ausfall keine ungeprüften Dateien freigeben.
3. Upload-Grenze in der Organisationseinstellung auf den tatsächlichen Bedarf begrenzen und mit Nginx-/Proxy-/Django-Limits abstimmen. Auch Anzahl und Gesamtvolumen je Nutzer*in/Reihe überwachen.
4. MEDIA_ROOT außerhalb des öffentlich durch Nginx ausgelieferten Document Roots halten. Für Docker ausschließlich das vorgesehene private Media-Volume nutzen. Keine zusätzliche Nginx-Alias- oder Static-Media-Regel für Uploads einrichten.
5. Downloads ausschließlich über die authentifizierte Anwendungsroute ausliefern. Für neue Datei-Endpunkte Tests ergänzen, die fehlende Anmeldung, falsche Serienzuweisung, Auditor*innen-Zugriff und manipulierte Datei-IDs zurückweisen.
6. Medien-Volume verschlüsselt sichern, Dateiberechtigungen auf das Dienstkonto begrenzen und Zugriff auf Host-/Backup-Ebene auf Administrator*innen beschränken.

**Nachweis:** automatisierte Tests für erlaubte und abgewiesene Dateiendungen, dokumentierte Signaturprüfung und Scanner-Konfiguration (sobald ergänzt) sowie Upload-/Download-Negativtests und Prüfung der Nginx-/Volume-Konfiguration.

### 7.4 Datenschutz und Inhalte

1. Für den Einsatz schriftlich festlegen, welche Themen und personenbezogenen Angaben in Protokollen zulässig sind. Besondere Kategorien personenbezogener Daten und private/medizinische Personalinformationen grundsätzlich nicht in Freitext oder Anlagen aufnehmen, sofern keine gesonderte Rechtsgrundlage und Erforderlichkeit festgestellt wurde.
2. In der Hilfe und in einer Nutzungsrichtlinie einen kurzen Hinweis ergänzen: nur besprechungsnotwendige Informationen erfassen, keine Zugangsdaten oder besonders schützenswerten Inhalte in Kommentare/Anlagen einstellen.
3. Protokoll- und Themenverantwortliche benennen. Diese prüfen bei Abschluss, ob Inhalte sachlich erforderlich und für den vorgesehenen Empfänger*innenkreis geeignet sind.
4. Zweck, Rechtsgrundlage, Empfänger*innen, Speicherorte und Aufbewahrungsfrist für Kontodaten, Protokolle, Snapshots, Kommentare, Anlagen, Audit-Logs, CSV-Exporte und Backups dokumentieren.
5. Einen Prozess für Auskunft, Berichtigung, Löschung und Einschränkung einrichten. Dabei auch Snapshot-Daten, Audit-Logs, Exportdateien und Backup-Rotation berücksichtigen.
6. Vor Einführung mit Datenschutzbeauftragten und ggf. Personalvertretung prüfen, ob eine Datenschutz-Folgenabschätzung erforderlich ist und ob die Nutzung als Leistungs-/Verhaltenskontrolle ausgeschlossen bzw. geregelt werden muss.

**Nachweis:** freigegebene Nutzungsrichtlinie, Verzeichnis der Verarbeitungstätigkeiten, Löschkonzept und Betroffenenrechte-Prozess.

### 7.5 CSV, Vollbackup und Datenwiederherstellung

1. Die vorhandenen Rollenprüfungen beibehalten: Benutzer-CSV sowie Vollbackup-/Restore-Funktionen sind globalen Admin-Konten vorbehalten. Themen-CSV-Import und -Export sind dagegen Moderator*innen vorbehalten und auf die Reihen begrenzt, in denen sie ausdrücklich Moderator*innenrechte besitzen. Diese Unterscheidung bei neuen Import-/Export-Endpunkten mit Negativtests absichern.
2. Exportdateien ausschließlich in zugriffsbeschränkten, verschlüsselten Verzeichnissen ablegen und über einen sicheren Übertragungsweg weitergeben. Nach erfolgreicher Übergabe lokal löschen; Papierkorb und Synchronisationskopien berücksichtigen.
3. Vor Importen die Vorschau vollständig prüfen. Änderungen an Benutzerrollen, Serienzuweisungen und bestehenden Themen nur nach Vier-Augen-Kontrolle übernehmen.
4. Vor Datenbank-Restore immer einen aktuellen zusätzlichen Sicherungsstand erstellen und Restore nur in einem kontrollierten Wartungsfenster durch autorisierte Administratoren durchführen.
5. Datenbank und Medienverzeichnis zeitlich passend und gemeinsam sichern. Mindestens eine verschlüsselte Kopie getrennt vom Produktivhost aufbewahren; Schreibzugriff des Produktivsystems auf diese Kopie vermeiden.
6. RPO/RTO festlegen und mindestens quartalsweise eine Wiederherstellung in einer isolierten Testumgebung durchführen. Prüfen, ob Datenbank, Anhänge, Logos und statische Betriebsdaten konsistent sind.

**Nachweis:** Backup-Protokolle, Zugriffsrechte, dokumentierte Aufbewahrung und quartalsweiser Restore-Test.

### 7.6 Patch- und Lieferkettenmanagement

1. Für Betriebssystem, PostgreSQL, Python-Abhängigkeiten, Docker-Basisimages und Nginx einen festen Patch-Rhythmus mit kurzfristigem Prozess für kritische Sicherheitsupdates definieren.
2. Bei jedem Build Abhängigkeitsscans und Container-Image-Scans ausführen. Kritische und hohe Befunde vor Freigabe beheben oder mit Verantwortlichem, Begründung und Frist dokumentiert akzeptieren.
3. Produktionsimages nur aus freigegebenen Branches/Tags beziehen. Version und Commit des laufenden Builds dokumentieren; keine ungeprüften Branches im Produktivsystem verwenden.
4. Updates zunächst in einer Testumgebung mit Datenbankkopie prüfen. Vor Migrationen Backup erstellen und nach dem Update Login, Berechtigungen, Upload/Download, PDF-Export und Protokollabschluss testen.
5. Rollback nicht mit Datenbank-Rollback gleichsetzen: Bereits angewendete Migrationen können eine Wiederherstellung aus Backup erfordern. Vorgehen vorab testen.

**Nachweis:** Scanberichte, Patchprotokoll, Releasefreigabe und dokumentierter Rollback-/Restore-Ablauf.

### 7.7 Netzwerk- und Verfügbarkeitsbetrieb

1. Nur erforderliche Ports öffnen. PostgreSQL nicht veröffentlichen; Docker-App-Port 8000 nicht nach außen freigeben. SSH nur aus Admin-Netzen zulassen.
2. Reverse-Proxy-Limits für Request-Größe, Verbindungszahl und Zeitüberschreitungen setzen; Upload-Grenzen mit der Anwendung abstimmen.
3. CPU, RAM, Plattenplatz, PostgreSQL-Verbindungen, HTTP-Fehler und Dienstverfügbarkeit überwachen. Alarmgrenzen und Eskalationskontakte festlegen.
4. Netzwerkpfade und externe Links als Verweise behandeln: Die Berechtigung am Zielsystem muss separat geprüft werden. Keine Passwörter oder Zugriffstoken in URLs hinterlegen.
5. Notfallverfahren für Ausfall, Ransomware, kompromittiertes Konto und Datenpanne dokumentieren und regelmäßig durchspielen.

**Nachweis:** Firewall-Regeln, Monitoring-Dashboard, Alarmtest und Incident-Response-Runbook.

## 8. Datenschutzrechtliche und organisatorische Freigabepunkte

Vor produktiver Nutzung sind mit Verantwortlichem, IT, Informationssicherheit und Datenschutzbeauftragten mindestens folgende Punkte zu klären:

- Zweck(e), Rechtsgrundlage(n) und Verantwortlichkeit für Besprechungsdokumentation und Beschäftigtendaten.
- Datenkategorien, Empfänger*innen, Hostingstandort, Unterauftragnehmer und Supportzugriffe.
- Verzeichnis der Verarbeitungstätigkeiten und Transparenzinformation für Nutzer*innen.
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
- `deploy/install-debian.sh`, `deploy/install-docker.sh`, `deploy/nginx-meeting-manager.conf`, `docker/compose.yaml` und `docker/nginx.conf`: HTTPS-Vorgaben, Proxy-Vertrauen und Bindung des Web-Ports.
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
