**Adressaten:** IT-Abteilung, Informationssicherheit und Datenschutzbeauftragte  
**Prüfstand:** Branch `beta`, einschließlich der Sicherheitsbewertung auf Basis von `main` (Commit `ed6fdd73e5fbe78569ff2112d88294fb6fe229d2`, Merge PR #511); die Python-3.12-Laufzeit und der Updater aus PR #524 sind Bestandteil des geprüften Beta-Stands.  
**Stand:** 25. November 2026  
**Geltungsbereich:** Anwendungscode und Repository-Konfiguration. Die konkrete Server-, Proxy-, Netzwerk- und Backup-Konfiguration ist vor Ort gesondert zu prüfen.

> **Einordnung:** Diese Beschreibung ist eine nachvollziehbare technische Bestandsaufnahme und Risikoeinschätzung. Sie ist weder Penetrationstestbericht noch Datenschutz-Folgenabschätzung, TOM-Nachweis oder rechtsverbindliche DSGVO-Konformitätsbestätigung. Aussagen über die reale Betriebsumgebung gelten nur, wenn sie dort verifiziert wurden.

## 1. Kurzbeschreibung und Zweck

Meeting Manager ist eine deutschsprachige Webanwendung zur Organisation wiederkehrender Besprechungen und zur fortlaufenden Bearbeitung von Themen. Sie verbindet Besprechungsreihen und Termine mit Tagesordnungspunkten, Zuständigkeiten, Kommentaren, Anlagen und Protokollen.

Ein Thema beschreibt einen fortlaufenden Vorgang. Ein Tagesordnungspunkt ist die Behandlung dieses Themas in einem konkreten Termin. Der zu einem Termin gehörende Text und Status werden getrennt geführt. Beim Abschluss einer Besprechung speichert die Anwendung einen Protokoll-Snapshot. Spätere Änderungen am Thema verändern diesen historischen Snapshot nicht.

Die Anwendung ist für den Betrieb in internen Netzen vorgesehen. Der verbindliche Produktivbetrieb dieser Installation erfolgt ausschließlich im Intranet; die Produktivinstanz besitzt keine direkte Internetverbindung. Zusätzlich ist eine optionale Online-Betriebsvariante für Betreiber möglich, die ihre Anwendung bewusst mit Internetzugriff betreiben. Beide Betriebsvarianten verwenden dieselbe Anwendung, unterscheiden sich aber bei Netzfreigaben, Release- und Updatewegen sowie bei der Aktualisierung von Betriebssystempaketen und Malware-Signaturen. Die Anwendung wird entweder auf Debian/Ubuntu mit PostgreSQL, Gunicorn und Nginx oder containerisiert mit Docker Compose betrieben.

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
| Besprechungsdaten | Reihe, Termine, Teilnehmer\*innenlisten, Protokoll-Snapshots | Anwesenheit und interne Zusammenarbeit |
| Inhaltsdaten | Themen, Tagesordnungstexte, Kommentare, Zuständigkeiten | Freitext kann vertrauliche oder sensible Angaben enthalten |
| Anlagen | hochgeladene Dokumente, Netzwerkpfade, URLs | Können eigenständige personenbezogene oder vertrauliche Inhalte enthalten |
| Änderungsdaten | handelnde Person, Zeitpunkt, Aktion, Zusammenfassung, ausgewählte Änderungen | Nachvollziehbarkeit; mögliche Beschäftigtenbezüge |
| Betriebsdaten | Webserver-, Betriebssystem-, Datenbank- und Proxy-Logs, Backups | Abhängig von Hosting und Betriebsüberwachung |

Die Anwendung kann nicht verhindern, dass Nutzer\*innen in Freitexten oder Anlagen unzulässige oder besonders schützenswerte Informationen hinterlegen. Dafür sind verbindliche Nutzungsregeln, Schulung und eine fachliche Freigabe der vorgesehenen Datenkategorien erforderlich.

## 3. Rollen- und Berechtigungskonzept

Das Modell kombiniert eine globale Rolle und unabhängige Berechtigungen je Besprechungsreihe. Eine globale Rolle ersetzt keine Serienzuweisung.

### 3.1 Globale Rollen

| Rolle | Umfang |
|---|---|
| **Nutzer\*innen** | Standardrolle. Fachlicher Zugriff ausschließlich auf ausdrücklich zugewiesene Besprechungsreihen und gemäß der dortigen Serienrolle. |
| **Admin** | Globale Verwaltungsrechte für Benutzerkonten, globale Rollen, Serienzuweisungen und Organisationseinstellungen sowie administrative Funktionen. Kein automatischer Zugriff auf fachliche Reiheninhalte. Fachliche Aktionen und Reiheninhalte setzen eine passende Serienzuweisung voraus. |
| **Auditor\*in** | Lesender Zugriff auf administrative Prüfdaten: System-Änderungsverlauf, Benutzerkonten und Rollen-/Serienzuordnungen sowie Organisationseinstellungen einschließlich Aufbewahrungsfrist und Markenfarben. Das Startpasswort ist ausgeschlossen. Kein Zugriff auf Besprechungsreihen oder fachliche Besprechungsinhalte und keine Änderungsrechte. |

Django-Superuser werden als globale Administrator\*innen behandelt. Die Admin-Gruppe wird mit dem Django-Staff-Status synchronisiert. Die Auditor\*innen-Rolle ist gegenüber Administrator\*in nachrangig: Ein Konto mit Administrator\*in- oder Superuser-Rechten wird nicht als Auditor\*in behandelt.

### 3.2 Serienrollen

| Serienrolle | Rechte innerhalb der ausdrücklich zugewiesenen Reihe |
|---|---|
| **Leser\*in** | Inhalte, Tagesordnungen, Themen, Anlagen und Protokolle ansehen und Protokolle exportieren; keine fachlichen Änderungen. |
| **Teilnehmer\*in** | Zusätzlich Themen und Tagesordnungspunkte bearbeiten, Zuständigkeiten setzen, kommentieren, Anlagen ergänzen, Wiedervorlagen verwalten, Teilnehmer\*innenlisten bearbeiten und Besprechungen abschließen. Keine Reihenverwaltung und kein Wiederöffnen abgeschlossener Besprechungen. |
| **Moderator\*in** | Zusätzlich Besprechungsreihe und Termine verwalten, Themen archivieren/wieder öffnen, abgeschlossene Besprechungen wieder öffnen und den Änderungsverlauf der eigenen moderierten Reihe einsehen. |

Nutzer\*innen können in verschiedenen Reihen unterschiedliche Rollen besitzen. Eine Moderator\*innenrolle in einer Reihe verleiht keine Rechte in einer anderen Reihe. Moderator\*innen können die Serienrollen anderer Benutzer\*innen in der eigenen Reihe verwalten; die eigene Moderatorzuweisung ist in der Serienverwaltung und den persönlichen Einstellungen gegen Änderung und Entzug gesperrt.

### 3.3 Historische Zugriffe und Änderungsverlauf

Wird eine Besprechungsreihe gelöscht, bleiben historische Termine und Protokolle zunächst erhalten. Die früheren Reihenmitglieder erhalten für noch vorhandene Inhalte einen gesonderten Lesezugriff. Abgeschlossene Besprechungstermine und Protokoll-Snapshots werden nach Ablauf der globalen Organisationsfrist automatisch gelöscht. Tagesordnungstexte bleiben bis zum Ablauf der unabhängigen Themenfrist erhalten; archivierte Themen werden zum berechneten Löschdatum vollständig entfernt. Eine ausdrücklich gewählte endgültige Löschung kann abgeschlossene Besprechungen und Protokolle zusätzlich entfernen.

Der Änderungsverlauf ist in zwei Bereiche getrennt:

- Serienereignisse sind ausschließlich für Moderator\*innen der jeweiligen Reihe sichtbar. Administrator\*innen sehen Serienereignisse ebenfalls nur für Reihen, in denen sie selbst ausdrücklich Moderator\*innenrechte besitzen.
- Systemereignisse sind für globale Administrator\*innen und Auditor\*innen sichtbar. Auditor\*innen haben ausschließlich lesenden Zugriff auf Systemereignisse und keinen Zugriff auf Serienereignisse oder fachliche Reiheninhalte.
- Die CSV-Exportansichten wenden dieselbe Bereichstrennung an: Administrator\*innen/Auditor\*innen exportieren Systemereignisse; Moderator\*innen exportieren Ereignisse ihrer eigenen moderierten Reihen.

Das Modell ist damit auf das Need-to-know-Prinzip ausgerichtet. Kritisch bleibt die konsequente Prüfung jedes neuen Endpunkts, Exports und administrativen Sonderwegs gegen diese Regeln.

## 4. Technische Architektur

- **Anwendungsframework:** Django (Python 3.13 im Docker-Image).
- **Datenbank:** PostgreSQL 16 im Docker-Betrieb; PostgreSQL auch für die Debian-Installation.
- **Webserver / Prozess:** Nginx und Gunicorn.
- **Dateien:** separates Medienverzeichnis bzw. Docker-Volume; statische Dateien werden separat bereitgestellt.
- **Container:** App-Prozess läuft als nicht privilegierter Benutzer. PostgreSQL ist im Compose-Netz erreichbar und erhält keinen veröffentlichten Host-Port. Der App-Container veröffentlicht Port 8000 nur intern; der Nginx-Container veröffentlicht den konfigurierten Web-Port.
- **Konfiguration:** Umgebungsvariablen und lokale `.env`-Datei. `SECRET_KEY` und Datenbankzugangsdaten sind vertraulich zu behandeln.

Die Installationsskripte konfigurieren HTTPS-Schutzmechanismen: SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE und CSRF_COOKIE_SECURE können durch die Installationskonfiguration aktiviert werden; CSRF_TRUSTED_ORIGINS enthält die konfigurierte Anwendungs-Origin. Django vertraut X-Forwarded-Proto nur bei ausdrücklich aktiviertem TRUST_PROXY_SSL. Bei Debian nimmt die lokale Nginx-Konfiguration HTTP auf Port 8080 entgegen und begrenzt den Zugriff auf die beim Setup angegebene Proxy-IP/CIDR. Bei Docker wird der veröffentlichte Nginx-Port standardmäßig ausschließlich an 127.0.0.1 gebunden. Vor dem produktiven Zugriff muss ein TLS-Reverse-Proxy mit einem von den Clients vertrauten Zertifikat eingerichtet sein, der X-Forwarded-Proto korrekt setzt und eingehende Client-Header überschreibt. Im Intranet kann dafür eine interne Zertifizierungsstelle verwendet werden; ein öffentliches Zertifikat ist nicht zwingend. Im verbindlichen Offline-Betrieb bleibt die Produktivinstanz ohne direkte Internetverbindung.

### 4.1 Betriebsvarianten und Netzwerkgrenzen

**Verbindliche Offline-Produktivvariante**

- Die Webanwendung ist ausschließlich aus dem vorgesehenen Intranet bzw. über den dafür freigegebenen internen Zugangsweg erreichbar.
- Die Produktivinstanz besitzt keine direkte ausgehende Internetverbindung. DNS, Zeitquelle, Identitätsdienst, SMTP, Monitoring und sonstige benötigte Infrastruktur müssen intern bereitgestellt oder ausdrücklich als Ausnahme freigegeben werden.
- Die Produktivinstanz darf zur Laufzeit keine Verbindung zu GitHub, Docker Hub, GHCR, öffentlichen Paket-Repositories, externen APIs oder Cloud-Telemetrie benötigen. Die erforderliche interne Kommunikation zwischen Reverse Proxy, Anwendung, Datenbank und administrativen Systemen bleibt zulässig.
- Die Netzwerksegmentierung begrenzt den Zugriff auf notwendige Clients, den Reverse Proxy, die Datenbank und administrative Systeme. Die Datenbank wird nicht für Benutzer-Netze veröffentlicht.
- „Offline“ bedeutet hier ohne Internetanbindung der Produktivinstanz, nicht ohne interne Netzkommunikation.

**Optionale Online-Betriebsvariante**

Betreiber können die Anwendung alternativ mit Internetanbindung betreiben. Dies ist eine eigenständige Betriebsentscheidung und keine Voraussetzung für die Anwendung. In dieser Variante sind eingehende Erreichbarkeit, ausgehende Verbindungen und externe Dienste ausdrücklich zu dokumentieren und auf das notwendige Minimum zu begrenzen. Insbesondere dürfen Datenbank und interne Verwaltungsports nicht öffentlich erreichbar sein.

Der aktuelle Docker-Installer bezieht Images aus Docker Hub. Der Docker-Web-Updater fragt verfügbare Branches bei GitHub ab und lädt das gewählte Anwendungsimage aus der GitHub Container Registry (GHCR). Der Debian-Updater bezieht den Quellcode über Git und aktualisiert Betriebssystem- sowie Python-Abhängigkeiten über APT- und Python-Paketquellen. Diese automatisierten Updatewege setzen daher eine funktionierende Internetverbindung bzw. Erreichbarkeit der jeweiligen externen Quellen voraus. Sie sind für eine vollständig vom Internet getrennte Produktivinstanz nicht geeignet.

**Kontrollierte Updates im Offline-Betrieb – erforderliche, noch nicht implementierte Betriebsfähigkeit**

Sicherheitsupdates müssen auch im Offline-Betrieb möglich sein. Die derzeitigen Installations- und Web-Updater enthalten jedoch keinen vollständigen Offline-Importmodus. Bis ein solcher Prozess implementiert und getestet ist, darf nicht behauptet werden, dass die Anwendung Updates in der Offline-Produktivinstanz automatisiert und ohne Internetzugang einspielen kann. Der Betreiber muss den folgenden kontrollierten Prozess technisch einrichten und vor dem Produktiveinsatz nachweisen:

1. **Bezug in einer getrennten Bereitstellungsumgebung:** Release-Quellcode bzw. Git-Repository-Stand, Container-Images, Debian-Pakete samt Abhängigkeiten, Python-Wheels sowie erforderliche Signatur- und Malware-Definitionsdateien werden aus festgelegten Quellen bezogen. Die Version, Herkunft, Bezugszeit und verantwortliche Person werden dokumentiert.
2. **Authentizität und Integrität:** Hersteller-/Repository-Signaturen werden gegen separat vertrauenswürdige Schlüssel geprüft. Für das freigegebene Update wird zusätzlich ein signiertes Manifest mit Versionsnummer, Quell-Commit, Artefaktbezeichnungen und SHA-256-Prüfsummen erstellt. Eine Prüfsumme aus derselben nicht vertrauenswürdigen Quelle authentifiziert das Artefakt nicht.
3. **Sicherheitsprüfung und Freigabe:** Artefakte werden auf bekannte Schwachstellen und Schadsoftware geprüft. Scanberichte, CI-Ergebnisse, Ausnahmen und Freigabeentscheidung werden dem konkreten Release zugeordnet. Ein CI-Scan mit nicht blockierendem Exit-Code gilt nicht allein als Freigabenachweis.
4. **Kontrollierte Übertragung:** Nur freigegebene Artefakte und das signierte Manifest werden über einen definierten, protokollierten Transferweg (z. B. geprüftes Transfermedium oder internes Übergabesystem) in die Offline-Umgebung eingebracht.
5. **Erneute Prüfung offline:** Signatur, Manifest und Prüfsummen werden in der Offline-Umgebung erneut geprüft. Bei Abweichungen, fehlender Signatur oder nicht nachvollziehbarer Herkunft wird der Import abgebrochen.
6. **Offline-Bereitstellung:** Für Debian müssen ein internes, signaturgeprüftes APT-Repository oder vollständige Paket-/Abhängigkeitsbestände bereitstehen; Python-Abhängigkeiten müssen als geprüfte Wheels lokal verfügbar sein. Für Docker müssen alle benötigten Images (Anwendung, Datenbank und Webserver) als Archive übertragen, lokal importiert und mit unveränderlichen Tags bzw. Digests referenziert werden. Der vorhandene Online-Updater darf dafür nicht verwendet werden, solange er GitHub-/GHCR-Zugriffe voraussetzt.
7. **Test, Sicherung und Einspielen:** Vor dem Update werden Datenbank und Medien gesichert. Das Update wird zunächst in einer geeigneten Test-/Abnahmeumgebung geprüft und anschließend im Wartungsfenster eingespielt. Datenbankmigrationen, Login, Berechtigungen, Upload/Download, PDF-Export und Protokollabschluss sind zu prüfen.
8. **Nachweis und Wiederherstellung:** Release-Version, Quell-Commit, Image-Digests, Prüfergebnisse, Freigabe, Installationszeitpunkt und verantwortliche Personen werden protokolliert. Ein getesteter Wiederherstellungsweg ist vorzuhalten. Ein Image-Rollback setzt Datenbankmigrationen nicht automatisch zurück; gegebenenfalls ist ein konsistenter Datenbank- und Medien-Restore erforderlich.

Die konkrete technische Umsetzung eines signierten Offline-Updatepakets bzw. eines lokalen Paket- und Image-Importers ist eine offene Betriebs-/Produktaufgabe. Bis zu deren Umsetzung ist der Offline-Updateprozess eine Anforderung an den Betreiber, keine bereits durch die Repository-Updater bereitgestellte Funktion.

## 5. Bereits vorhandene Sicherheitskontrollen

Die folgenden Kontrollen sind im geprüften Quellcode bzw. in den Installationsdateien erkennbar. Sie ersetzen nicht die Prüfung der tatsächlich betriebenen Instanz. Die Ersteinrichtung wird standardmäßig durch einen kryptografisch zufälligen Aktivierungstoken geschützt, den die Installer erzeugen und nur einmalig in der Installationskonsole ausgeben; die tokenfreie Variante ist eine bewusste Ausnahme über `-nocode` und muss durch eine entsprechend abgeschottete Erreichbarkeit kompensiert werden.

| Bereich | Vorhandene Kontrolle | Einordnung |
|---|---|---|
| Anmeldung | Django-Authentifizierung; geschützte Anwendungsbereiche verlangen Anmeldung. Debian- und Docker-Nginx begrenzen Login-Anfragen auf 10 Requests pro Minute mit Burst 10 (danach HTTP 429), sofern `X-Forwarded-For` gesetzt ist. Fehlt der Header oder ist er leer, wird kein Login-Rate-Limit angewendet. | Kein konto-/benutzerbezogenes Rate-Limit und keine MFA im Anwendungskern. Für eine wirksame IP-Zuordnung muss der vorgeschaltete Reverse Proxy `X-Forwarded-For` mit der tatsächlichen Client-IP überschreiben; ungeprüfte Client-Werte wären manipulierbar. |
| Passwörter | Django-Passworthashing; Mindestlänge 8, Komplexitätsvalidator, Ähnlichkeits- und häufige-Passwort-Prüfung. | MFA und ein anwendungsinterner Login-Rate-Limiter sind im geprüften Kern nicht belegt. |
| Sessions | Inaktivitäts-Timeout 8 Stunden; Sessions werden bei Requests gespeichert/erneuert. „Angemeldet bleiben“ hält das Cookie nach dem Schließen des Browsers, verlängert aber nicht das 8-Stunden-Inaktivitätsfenster. | Bei langen aktiven Sitzungen erhöht dies die Bedeutung von Geräteschutz und Logout. |
| Autorisierung | Zentrale Serienzugriffsabfragen; Auditor\*innen werden aus fachlichen Reihenabfragen ausgeschlossen; Administrator\*in ist keine Serienrolle. | Endpunkt- und Exporttests müssen die Regeln vollständig abdecken. |
| CSRF / Browser-Header | Django-CSRF-Middleware; nosniff, Referrer-Policy same-origin und X-Frame-Options DENY. | Eine umfassende Content-Security-Policy für alle Seiten ist nicht belegt. |
| TLS / Cookies / CSRF | Die Installer erzwingen HTTPS-Redirect und Secure-Cookies, setzen die HTTPS-CSRF-Origin und aktivieren Proxy-Vertrauen. Debian begrenzt den Zugriff auf die angegebene Proxy-IP/CIDR; Docker bindet den Web-Port an Loopback. | Ein gültiges TLS-Zertifikat und ein korrekt konfigurierter Reverse Proxy bleiben erforderlich. HSTS-Preload wird validiert und muss bewusst separat aktiviert werden. |
| Uploads | Anlagenlimit wird organisationsweit konfiguriert (1–24 MB, Standard 20 MB). Für Themenanlagen gilt serverseitig eine Dateiendungs-Allowlist: PDF, DOCX, XLSX, PPTX, TXT, PNG und JPEG. Download erfordert Anmeldung und Serienzugriff; Pfad wird auf MEDIA_ROOT begrenzt; Download als Attachment, nosniff und private/no-store. | Die Allowlist prüft die Dateiendung, nicht die tatsächliche Dateisignatur oder den Dateiinhalt. Malware-Scanning ist nicht integriert. |
| Logos / SVG | Logo-Auslieferung ist angemeldet, auf MEDIA_ROOT begrenzt und privat/no-store. SVG erhält eine restriktive CSP-Sandbox. | Upload- und Konvertierungspfad weiter beobachten. |
| Audit | Protokolliert werden handelnde Person, Zeitpunkt, Aktion, eine begrenzte Zusammenfassung und gezielt ausgewählte Änderungsmetadaten. Passwortwerte und hochgeladene Datei-Inhalte werden nicht gespeichert; bei Passwortänderungen wird nur der Status der Änderung festgehalten. Dateinamen können als Metadaten erscheinen. Eine fachliche Ausnahme ist das Wiederöffnen einer abgeschlossenen Besprechung: Der vorherige gesicherte Protokollstand wird als Audit-Detail aufbewahrt. Systemereignisse sehen globale Administrator\*innen und Auditor\*innen. Serienereignisse sehen Moderator\*innen ausschließlich für ihre moderierten Reihen; globale Administrator\*innen sehen sie ebenfalls nur, wenn sie in der jeweiligen Reihe ausdrücklich als Moderator\*in zugewiesen sind. | Die Datenbankablage ist nicht manipulationsgeschützt. Die Oberfläche zeigt nur freigegebene Ereignisse und aufklappbare, ausgewählte Änderungsdetails; sie ist kein vollständiges Aktivitäts- oder Inhaltsprotokoll. |
| CSV | Import mit Vorschau/Bestätigung; Exportwerte werden gegen Tabellenformel-Präfixe abgesichert. Benutzer-CSV und Vollbackup/Restore sind Administrator\*in-Funktionen; Themen-CSV ist auf Moderator\*innen und ihre moderierten Reihen begrenzt. | Import-/Exportdateien bleiben sensible Datenkopien. |
| Betrieb und Updates | Docker-App läuft als nicht-root; DB nicht nach außen veröffentlicht; Updater nutzt lokalen Unix-Socket statt Docker-Socket im App-Container. Der Docker-Updater fragt GitHub ab und lädt Images aus GHCR; der Debian-Updater nutzt Git, APT und Python-Paketquellen. | Host, Socket-Berechtigungen, Images, Volumes und Updater bleiben Teil der Vertrauensgrenze. Die derzeitigen Updater setzen externe Erreichbarkeit voraus und sind nicht offlinefähig. Für Offline-Betrieb ist ein geprüfter lokaler Artefaktimport erforderlich; dieser ist im Repository derzeit nicht implementiert. |
| Backups | Integrierter Datenbank-Vollbackup-Export/-Import und dokumentierte Backup-Wege für Datenbank und Medien. | Ein belastbarer externer Backup-, Verschlüsselungs- und Restore-Prozess muss von den Betreiber\*innen eingerichtet werden. |

## 6. Häufige Sicherheitsrisiken und Bewertung der Schutzmaßnahmen

Die folgende Bewertung orientiert sich an typischen Risiken von Webanwendungen. Sie unterscheidet zwischen Schutzmaßnahmen, die im geprüften Quellcode bzw. in der Installationskonfiguration erkennbar sind, und verbleibenden Aufgaben für den Betrieb. Eine vorhandene Kontrolle reduziert ein Risiko, beseitigt es aber nicht automatisch.

| Häufiges Risiko | Bereits vorhandene Schutzmaßnahmen im Meeting Manager | Bewertung und verbleibender Handlungsbedarf |
|---|---|---|
| **Unberechtigter Zugriff / Broken Access Control** | Zentrale Serienzugriffsabfragen; globale Administrator\*in-Rechte ersetzen keine Serienzuweisung; Auditor\*innen sind von fachlichen Reiheninhalten ausgeschlossen; Leser\*innen-, Teilnehmer\*innen- und Moderator\*innenrechte werden getrennt geprüft. | **Im Anwendungscode wesentlich adressiert.** Neue Views, APIs, Exporte und direkte Objekt-IDs müssen weiterhin mit Positiv- und Negativtests für alle Rollen abgesichert werden. |
| **SQL-Injection und sonstige Eingabe-Injection** | Standard-Datenbankzugriffe über das Django-ORM mit parametrisierten Abfragen; Formulare und Modellvalidierungen prüfen Eingaben. | **Durch Framework-Schutzmaßnahmen adressiert.** Raw-SQL, dynamische Filter und neue Importpfade müssen separat geprüft werden; keine ungeprüfte SQL-Stringverkettung einführen. |
| **Cross-Site Request Forgery (CSRF)** | Django-CSRF-Middleware und CSRF-Tokens in Formularen. Die Installer aktivieren sichere CSRF-Cookies und setzen die öffentliche HTTPS-Origin. | **Im Code und Installationsstandard adressiert.** Der Reverse Proxy muss die korrekte HTTPS-Origin weitergeben; CSRF-Schutz darf für neue schreibende Views nicht umgangen werden. |
| **Abhören oder Übernehmen von Sitzungen** | Die Installer erzwingen HTTPS-Redirect sowie Secure-Attribute für Session- und CSRF-Cookies. Django verwaltet die Sitzungen; die Laufzeit ist auf acht Stunden begrenzt. | **Mit korrekt eingerichtetem TLS-Reverse-Proxy adressiert.** Zertifikatserneuerung, Proxy-Isolation, Geräteschutz und Logout bleiben Betriebsaufgaben. Eine Sitzung kann bei kompromittiertem Endgerät weiterhin missbraucht werden. |
| **Passwortdiebstahl und Brute Force** | Django-Passworthashing, Mindestlänge 8 sowie Komplexitäts-, Ähnlichkeits- und Häufige-Passwort-Prüfung. Debian- und Docker-Nginx drosseln `/login/` auf 10 Requests pro Minute und über `X-Forwarded-For` identifizierter Client-IP (Burst 10, danach HTTP 429). Ist der Header nicht vorhanden oder leer, wird kein Rate-Limit angewendet. | **Teilweise adressiert.** Kein konto-/benutzerbezogenes Limit und keine MFA. Für eine korrekte IP-Zuordnung muss der vorgeschaltete Reverse Proxy `X-Forwarded-For` mit der tatsächlichen Client-IP überschreiben; gemeinsam genutzte IPs können legitime Personen gemeinsam begrenzen. |
| **Cross-Site Scripting (XSS)** | Django-Templates escapen gewöhnliche Ausgaben standardmäßig; nosniff, Referrer-Policy same-origin und X-Frame-Options DENY sind gesetzt. | **Teilweise adressiert.** Eine umfassende Content-Security-Policy ist nicht belegt. Bei neuen HTML-Ausgaben keine ungeprüften Safe-Ausgaben oder dynamisch eingebetteten Skripte verwenden; CSP prüfen und schrittweise einführen. |
| **Schadsoftware und aktive Inhalte in Datei-Uploads** | Uploadgrößen sind begrenzt. Themenanlagen akzeptieren serverseitig nur die Dateiendungen PDF, DOCX, XLSX, PPTX, TXT, PNG, JPG und JPEG. Downloads erfordern Anmeldung und Serienzugriff, erfolgen als Attachment und mit nosniff; Pfade werden auf MEDIA_ROOT begrenzt. | **Teilweise adressiert.** Die Endungs-Allowlist verhindert nicht, dass andersartige Inhalte mit erlaubter Endung hochgeladen werden. Dateisignaturprüfung und Malware-Scanning fehlen weiterhin und sollten vor einer Freigabe ergänzt werden. |
| **Datenabfluss über Anlagen, CSV und Backups** | Anlagen werden über eine geschützte Download-Route ausgeliefert. CSV-Import hat eine Vorschau; Exportwerte werden gegen Tabellenformeln abgesichert. Benutzer-CSV und Vollbackup/Restore sind Administrator\*in-Funktionen; Themen-CSV ist auf Moderator\*innen und ihre moderierten Reihen begrenzt. | **Im normalen Anwendungspfad adressiert, Betrieb bleibt kritisch.** MEDIA-Verzeichnis nicht öffentlich ausliefern; Exportdateien und Backups verschlüsseln, Zugriff beschränken, Aufbewahrung und Löschung regeln. |
| **Missbrauch privilegierter Konten / Insider-Risiko** | Administrator\*in- und Auditor\*innen-Rollen sind getrennt; Auditor\*innen haben ausschließlich Leserechte. Administrator\*innen erhalten fachlichen Reihen-Zugriff nicht allein durch ihre globale Rolle. Administrative und fachliche Ereignisse werden protokolliert. | **Teilweise adressiert.** Administrator\*in-Konten minimieren, MFA einsetzen, Administrator\*in-Aktionen überwachen und regelmäßige Rechteprüfungen durchführen. Privilegierte Host-/DB-Zugriffe bleiben außerhalb der Anwendungsautorisierung. |
| **Manipulation oder Verlust von Audit-Daten** | Serienereignisse sind für Moderator\*innen ihrer jeweils moderierten Reihen sichtbar; globale Administrator\*innen sehen sie nur mit eigener Moderator\*innen-Zuweisung. Systemereignisse sind für globale Administrator\*innen und Auditor\*innen sichtbar. Die Erfassung beschränkt sich auf Ereignismetadaten und ausgewählte Änderungen. Passwortwerte und hochgeladene Datei-Inhalte werden nicht protokolliert. Beim Wiederöffnen einer abgeschlossenen Besprechung wird jedoch der vorherige Protokoll-Snapshot als fachliches Audit-Detail gespeichert. | **Zugriff und Darstellung sind eng begrenzt.** In der Weboberfläche sind Änderungsdetails zunächst eingeklappt; der CSV-Export enthält die strukturierten Änderungsdetails im Exportumfang der jeweiligen Rolle. Beim Wiederöffnen einer abgeschlossenen Besprechung bleibt der vorherige Protokoll-Snapshot im Audit erhalten. Die Datenbank selbst ist kein manipulationsgeschützter/WORM-Speicher. |
| **Veraltete Abhängigkeiten und Container-Images** | Python-Abhängigkeiten werden bei Pull Requests sowie Pushes auf `main` und `beta` durch `pip-audit --strict` geprüft. CodeQL analysiert Python-Code bei Pull Requests, Pushes auf `main`/`beta` und wöchentlich. Das Anwendungsimage und das ClamAV-Image werden bei Pull Requests, Pushes auf `main`/`beta` und wöchentlich mit Trivy auf OS- und Bibliotheks-Schwachstellen geprüft. Beim Anwendungsimage erstellen die Trivy-Schritte JSON-/SARIF-Berichte mit `exit-code: 0`; ein nachgelagerter Prüfschritt lässt den Job jedoch fehlschlagen, wenn behebbare HIGH-/CRITICAL-Befunde (`FixedVersion` vorhanden) enthalten sind. Der ClamAV-Image-Scan verwendet `exit-code: 1` und kann den Job bei HIGH-/CRITICAL-Befunden fehlschlagen lassen. `ignore-unfixed: true` schließt nicht behebbare Befunde aus diesen Fehlerentscheidungen aus. Der Anwendungsbericht wird als Artifact sieben Tage aufbewahrt; SARIF-Berichte werden, sofern vorhanden, an GitHub Code Scanning übergeben. | **Die CI enthält damit ein blockierendes Gate für behebbare HIGH-/CRITICAL-Schwachstellen im Anwendungsimage und für HIGH-/CRITICAL-Befunde im ClamAV-Image.** Nicht behebbare Befunde werden nicht durch diese Exit-Code-Entscheidung blockiert und müssen vor einer Releasefreigabe anhand der Berichte bewertet und dokumentiert werden. Die Prüfungen schützen nicht die Laufzeit der Offline-Instanz. Der ClamAV-Image-Scan belegt keinen Malware-Scan hochgeladener Dateien; im geprüften `docker/compose.yaml` ist kein ClamAV-Dienst und kein Upload-Scanpfad eingebunden. |
| **Denial of Service und Ressourcenerschöpfung** | Uploadgrößen sind begrenzt; Datenbank und App sind in getrennten Diensten organisiert. | **Nur teilweise adressiert.** Request-Größen, Verbindungen, Rate-Limits, Timeouts, CPU, RAM und Speicherplatz am Proxy und Host begrenzen und überwachen. |
| **Datenverlust / fehlende Wiederherstellbarkeit** | Datenbank- und Medien-Backups sowie Import-/Restore-Funktionen sind vorhanden und dokumentiert. | **Nicht durch den Code garantiert.** Getrennte, verschlüsselte Backups, definierte RPO/RTO und regelmäßige Restore-Tests sind zwingend durch die Betreiber\*innen einzurichten. |
| **Fehlkonfiguration von HTTPS und Proxy-Vertrauen** | Die Installer setzen HTTPS-Redirect, Secure-Cookies, CSRF-Origin und Proxy-Vertrauen verbindlich. Debian beschränkt den internen Nginx-Zugriff auf die angegebene Proxy-IP/CIDR; Docker bindet den Web-Port nur an Loopback. | **Im Installationsstandard deutlich reduziert.** Ein gültiger TLS-Reverse-Proxy muss tatsächlich eingerichtet sein, Forwarded-Header überschreiben und darf nicht umgangen werden. HSTS bleibt eine bewusst zu prüfende Zusatzmaßnahme. |

Die Einstufung beschreibt Schutzmechanismen im Repository, nicht den Sicherheitszustand eines konkreten Servers. Insbesondere TLS-Zertifikat, Reverse-Proxy-Konfiguration, Firewall, MFA, Malware-Scanner, zentrale Protokollierung und Backups müssen in der Zielumgebung überprüft werden.

## 7. Konkrete Maßnahmen und empfohlene Vorgehensweisen

Die folgenden Schritte sind bewusst als umsetzbare Arbeitsanweisungen formuliert. Die Reihenfolge priorisiert die größten Auswirkungen.

### 7.1 Rollen und Serienberechtigungen – laufender Kontrollprozess

1. Globale Administrator\*in-Konten auf einen kleinen, namentlich festgelegten Personenkreis begrenzen. Für normale Arbeit persönliche Konten verwenden, nicht das Administrator\*in-Konto.
2. Für jede Besprechungsreihe eine fachlich verantwortliche Person benennen. Diese bestätigt bei Anlage und mindestens quartalsweise die Mitglieder und deren Rolle.
3. Bei Eintritt, Rollenwechsel und Austritt von Mitarbeitenden die Serienzuweisungen unmittelbar anpassen. Deaktivierte Konten und nicht mehr benötigte Serienzuweisungen in einem dokumentierten Offboarding-Prozess berücksichtigen.
4. Bei jeder Änderung an Views, Exporten, Downloads oder APIs eine Berechtigungsmatrix mit Positiv- und Negativtests ergänzen: Leser\*innen, Teilnehmer\*innen, Moderator\*innen, Administrator\*in ohne Serienzuweisung, Administrator\*in mit Serienzuweisung und Auditor\*innen.
5. Für jede Ressource sowohl Listenansichten als auch direkte Objekt-IDs testen. Eine nicht berechtigte Person muss auch durch Erraten einer URL/ID keinen Inhalt erhalten oder ändern können.
6. Auditor\*innen-Tests müssen mindestens GET-Lesezugriffe auf die freigegebenen Prüfdaten sowie Ablehnung aller schreibenden HTTP-Methoden und sämtlicher fachlicher Reihen-/Anlagenzugriffe nachweisen.
7. Administrator\*in-Sonderfunktionen (CSV, Vollbackup, Restore, Organisationseinstellungen, globale Rollen) nur über die vorgesehenen Verwaltungsansichten erlauben und ihre Zugriffe protokollieren.

**Nachweis:** Quartalsweise Berechtigungsliste mit Freigabe durch den fachlichen Reihenverantwortlichen; CI-Testresultate für alle Rollen.

### 7.2 Benutzerkonten und Anmeldung

1. Wo organisatorisch möglich, Anmeldung über einen zentralen Identity Provider mit MFA erzwingen. Falls lokale Konten verbleiben, MFA als vorgeschaltete Zugangskontrolle oder über eine geprüfte Django-Erweiterung ergänzen.
2. Login-Rate-Limiting am Reverse Proxy oder durch eine gepflegte Django-Komponente einrichten. Als Startwert z. B. nach 5 fehlgeschlagenen Anmeldungen pro Konto/IP eine zeitlich begrenzte Verzögerung bzw. Sperre auslösen; legitime Nutzer\*innen müssen kontrolliert entsperrt werden können.
3. Fehlermeldungen bei Login nicht verraten, ob Benutzername oder Passwort falsch ist. Fehlversuche und ungewöhnliche Anmeldehäufungen zentral überwachen.
4. Passwortregeln der Anwendung beibehalten; Nutzer\*innen zu individuellen Passphrasen und Passwortmanagern anhalten. Gemeinsame Startpasswörter nur über einen geschützten Einmalprozess übermitteln und beim ersten Zugriff ändern lassen.
5. Bei Rollenwechsel, Austritt oder Sicherheitsvorfall Konten deaktivieren, Sessions invalidieren und bei Verdacht Passwörter sowie relevante Secrets rotieren.
6. Die 8-Stunden-Session-Laufzeit mit dem Schutzbedarf abstimmen. Für gemeinsam genutzte Arbeitsplätze automatische Bildschirmsperre und explizites Abmelden verbindlich machen.

**Nachweis:** Konfiguration des IdP/Rate-Limiters, Testprotokoll für Fehlversuche und dokumentierter Offboarding-Prozess.

### 7.3 Datei-Uploads und Downloads

1. Für Themenanlagen gilt bereits eine serverseitige Dateiendungs-Allowlist: PDF, DOCX, XLSX, PPTX, TXT, PNG, JPG und JPEG. Andere Endungen – insbesondere ausführbare Dateien, Skripte und Archive – werden durch die Formularvalidierung abgewiesen. Die Allowlist prüft nur den Dateinamen, nicht die tatsächliche Dateisignatur oder den Dateiinhalt.
2. Als nächste Schutzstufe Dateisignaturen serverseitig prüfen und Malware-Scanning vor Freigabe zum Download einführen. Dateien bis zur erfolgreichen Prüfung in Quarantäne halten; bei Scanner-Ausfall keine ungeprüften Dateien freigeben.
3. Upload-Grenze in der Organisationseinstellung auf den tatsächlichen Bedarf begrenzen und mit Nginx-/Proxy-/Django-Limits abstimmen. Auch Anzahl und Gesamtvolumen je Nutzer\*in/Reihe überwachen.
4. MEDIA_ROOT außerhalb des öffentlich durch Nginx ausgelieferten Document Roots halten. Für Docker ausschließlich das vorgesehene private Media-Volume nutzen. Keine zusätzliche Nginx-Alias- oder Static-Media-Regel für Uploads einrichten.
5. Downloads ausschließlich über die authentifizierte Anwendungsroute ausliefern. Für neue Datei-Endpunkte Tests ergänzen, die fehlende Anmeldung, falsche Serienzuweisung, Auditor\*innen-Zugriff und manipulierte Datei-IDs zurückweisen.
6. Medien-Volume verschlüsselt sichern, Dateiberechtigungen auf das Dienstkonto begrenzen und Zugriff auf Host-/Backup-Ebene auf Administrator\*innen beschränken.

**Nachweis:** automatisierte Tests für erlaubte und abgewiesene Dateiendungen, dokumentierte Signaturprüfung und Scanner-Konfiguration (sobald ergänzt) sowie Upload-/Download-Negativtests und Prüfung der Nginx-/Volume-Konfiguration.

### 7.4 Datenschutz und Inhalte

1. Für den Einsatz schriftlich festlegen, welche Themen und personenbezogenen Angaben in Protokollen zulässig sind. Besondere Kategorien personenbezogener Daten und private/medizinische Personalinformationen grundsätzlich nicht in Freitext oder Anlagen aufnehmen, sofern keine gesonderte Rechtsgrundlage und Erforderlichkeit festgestellt wurde.
2. In der Hilfe und in einer Nutzungsrichtlinie einen kurzen Hinweis ergänzen: nur besprechungsnotwendige Informationen erfassen, keine Zugangsdaten oder besonders schützenswerten Inhalte in Kommentare/Anlagen einstellen.
3. Protokoll- und Themenverantwortliche benennen. Diese prüfen bei Abschluss, ob Inhalte sachlich erforderlich und für den vorgesehenen Empfänger\*innenkreis geeignet sind.
4. Zweck, Rechtsgrundlage, Empfänger\*innen, Speicherorte und Aufbewahrungsfrist für Kontodaten, Protokolle, Snapshots, Kommentare, Anlagen, Audit-Logs, CSV-Exporte und Backups dokumentieren.
5. Einen Prozess für Auskunft, Berichtigung, Löschung und Einschränkung einrichten. Dabei auch Snapshot-Daten, Audit-Logs, Exportdateien und Backup-Rotation berücksichtigen.
6. Vor Einführung mit Datenschutzbeauftragten und ggf. Personalvertretung prüfen, ob eine Datenschutz-Folgenabschätzung erforderlich ist und ob die Nutzung als Leistungs-/Verhaltenskontrolle ausgeschlossen bzw. geregelt werden muss.

**Nachweis:** freigegebene Nutzungsrichtlinie, Verzeichnis der Verarbeitungstätigkeiten, Löschkonzept und Betroffenenrechte-Prozess.

### 7.5 CSV, Vollbackup und Datenwiederherstellung

1. Die vorhandenen Rollenprüfungen beibehalten: Benutzer-CSV sowie Vollbackup-/Restore-Funktionen sind globalen Administrator\*in-Konten vorbehalten. Themen-CSV-Import und -Export sind dagegen Moderator\*innen vorbehalten und auf die Reihen begrenzt, in denen sie ausdrücklich Moderator\*innenrechte besitzen. Diese Unterscheidung bei neuen Import-/Export-Endpunkten mit Negativtests absichern.
2. Exportdateien ausschließlich in zugriffsbeschränkten, verschlüsselten Verzeichnissen ablegen und über einen sicheren Übertragungsweg weitergeben. Nach erfolgreicher Übergabe lokal löschen; Papierkorb und Synchronisationskopien berücksichtigen.
3. Vor Importen die Vorschau vollständig prüfen. Änderungen an Benutzerrollen, Serienzuweisungen und bestehenden Themen nur nach Vier-Augen-Kontrolle übernehmen.
4. Vor Datenbank-Restore immer einen aktuellen zusätzlichen Sicherungsstand erstellen und Restore nur in einem kontrollierten Wartungsfenster durch autorisierte Administrator\*innen durchführen.
5. Datenbank und Medienverzeichnis zeitlich passend und gemeinsam sichern. Mindestens eine verschlüsselte Kopie getrennt vom Produktivhost aufbewahren; Schreibzugriff des Produktivsystems auf diese Kopie vermeiden.
6. RPO/RTO festlegen und mindestens quartalsweise eine Wiederherstellung in einer isolierten Testumgebung durchführen. Prüfen, ob Datenbank, Anhänge, Logos und statische Betriebsdaten konsistent sind.

**Nachweis:** Backup-Protokolle, Zugriffsrechte, dokumentierte Aufbewahrung und quartalsweiser Restore-Test.

### 7.6 Patch- und Lieferkettenmanagement

1. Für Betriebssystem, PostgreSQL, Python-Abhängigkeiten, Docker-Basisimages und Nginx einen festen Patch-Rhythmus mit kurzfristigem Prozess für kritische Sicherheitsupdates definieren. Dies gilt für Offline- und Online-Betrieb.
2. Bei jedem Build Abhängigkeitsscans, Codeanalyse und Container-Image-Scans ausführen. Der aktuelle CI-Workflow blockiert behebbare HIGH-/CRITICAL-Befunde im Anwendungsimage sowie HIGH-/CRITICAL-Befunde im ClamAV-Image. Nicht behebbare Befunde werden durch `ignore-unfixed: true` nicht blockiert; sie müssen vor Freigabe anhand der Scanberichte bewertet und mit verantwortlicher Person, Begründung, kompensierenden Maßnahmen und Frist dokumentiert werden. Eine Ausnahme von einem blockierenden Gate darf nur bewusst, nachvollziehbar und nach Freigabe durch die zuständige Stelle erfolgen.
3. **Offline-Betrieb:** Die aktuelle Repository-Version bietet keinen automatisierten Offline-Updateimport. Der Debian-Updater führt `git fetch`, `apt-get update` und eine Installation von Python-Abhängigkeiten aus Paketquellen aus. Der Docker-Updater fragt verfügbare Branches über GitHub ab und lädt Anwendungsimages aus GHCR. Beide Wege benötigen externe Erreichbarkeit und sind in der Offline-Produktivumgebung nicht verwendbar. Bis ein Offline-Importer bereitsteht, muss der Betreiber einen getrennten Staging- und Transferprozess wie in Abschnitt 4.1 beschrieben technisch umsetzen: signierte Artefakte und Manifest, getrennte Schlüsselprüfung, erneute Hashprüfung offline, lokales APT-Repository bzw. Python-Wheelhouse oder Docker-Image-Archive sowie dokumentierte Freigabe.
4. **Optionale Online-Variante:** Der Docker-Installer bezieht Images initial aus Docker Hub; der Docker-Web-Updater fragt Branches bei GitHub ab und lädt Images aus GHCR. Der Debian-Updater aktualisiert Quellcode über Git und Abhängigkeiten über APT-/Python-Paketquellen. Diese Bezugswege sind bei der Netzfreigabe zu berücksichtigen. Quelle und Version sind festzulegen; Signaturen/Prüfsummen, Scanberichte und Freigaben müssen dokumentiert werden. Automatische ungeprüfte Updates in Produktion sind nicht vorgesehen.
5. Produktionsimages nur aus freigegebenen Releases beziehen. Version, Quell-Commit und unveränderliche Image-Digests des tatsächlich laufenden Builds dokumentieren. Die Branch-basierten Updater wählen bewegliche Tags; diese allein sind kein unveränderlicher Freigabenachweis.
6. Updates zunächst in einer Testumgebung mit Datenbankkopie prüfen. Vor Migrationen Backup erstellen und nach dem Update Login, Berechtigungen, Upload/Download, PDF-Export und Protokollabschluss testen.
7. Rollback nicht mit Datenbank-Rollback gleichsetzen: Bereits angewendete Migrationen können eine Wiederherstellung aus Backup erfordern. Vorgehen vorab testen.
8. Der aktuelle CI-Workflow scannt das ClamAV-Container-Image, nicht hochgeladene Dateien. Im geprüften Docker-Compose-Stack ist kein ClamAV-Dienst und kein Upload-Scanpfad eingebunden. Soll Malware-Scanning für Uploads eingeführt werden, sind Scannerintegration, Quarantäne, Fehlerverhalten (fail closed), Signaturaktualisierung und ein offlinefähiger, signaturgeprüfter Definitionsimport gesondert zu implementieren und zu testen.

**Nachweis:** Scanberichte, signiertes Release-Manifest, Prüfsummen- und Signaturprüfprotokoll, Patchprotokoll, Releasefreigabe und dokumentierter Rollback-/Restore-Ablauf.

### 7.7 Netzwerk- und Verfügbarkeitsbetrieb

1. Nur erforderliche Ports öffnen. PostgreSQL nicht veröffentlichen; Docker-App-Port 8000 nicht nach außen freigeben. SSH nur aus Administrator\*in-Netzen zulassen.
2. Reverse-Proxy-Limits für Request-Größe, Verbindungszahl und Zeitüberschreitungen setzen; Upload-Grenzen mit der Anwendung abstimmen.
3. CPU, RAM, Plattenplatz, PostgreSQL-Verbindungen, HTTP-Fehler und Dienstverfügbarkeit überwachen. Alarmgrenzen und Eskalationskontakte festlegen.
4. Netzwerkpfade und externe Links als Verweise behandeln: Die Berechtigung am Zielsystem muss separat geprüft werden. Keine Passwörter oder Zugriffstoken in URLs hinterlegen.
5. Notfallverfahren für Ausfall, Ransomware, kompromittiertes Konto und Datenpanne dokumentieren und regelmäßig durchspielen.

**Nachweis:** Firewall-Regeln, Monitoring-Dashboard, Alarmtest und Incident-Response-Runbook.

## 8. Datenschutzrechtliche und organisatorische Freigabepunkte

Vor produktiver Nutzung sind mit verantwortlicher Person, IT, Informationssicherheit und Datenschutzbeauftragten mindestens folgende Punkte zu klären:

- Zweck(e), Rechtsgrundlage(n) und Verantwortlichkeit für Besprechungsdokumentation und Beschäftigtendaten.
- Datenkategorien, Empfänger\*innen, Hostingstandort, Unterauftragnehmer\*innen und Supportzugriffe.
- Verzeichnis der Verarbeitungstätigkeiten und Transparenzinformation für Nutzer\*innen.
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
| Serienzuweisungen und fachliche Inhalte | Fachverantwortliche / Moderator\*innen | Anwendungsadministration |
| Regelmäßige Berechtigungsprüfung | Fachverantwortliche | IT / Informationssicherheit |
| Zwecke, Rechtsgrundlagen, Betroffenenrechte, Löschkonzept | Verantwortliche Organisationseinheit | Datenschutzbeauftragte |
| Sicherheitsvorfälle und Wiederherstellung | IT-Betrieb / Incident Response | Datenschutzbeauftragte bei Datenschutzverletzungen |

## 10. Prüfgrundlage und Grenzen

Geprüft wurden insbesondere:

- `README.md`: Funktionsumfang, Rollenmatrix, Installations- und Sicherheitshinweise.
- `deploy/install-debian.sh`, `deploy/install-docker.sh`, `deploy/nginx-meeting-manager.conf`, `docker/compose.yaml` und `docker/nginx.conf`: HTTPS-Vorgaben, Proxy-Vertrauen, Bindung des Web-Ports und IP-basiertes Login-Rate-Limiting.
- `meetings/access.py`, `meetings/user_roles.py`: globale Rollen und zentrale Serienzugriffslogik.
- `meetings/models.py`: Datenmodelle, Anlagen, Serienzuweisungen, Audit-Ereignisse und Protokoll-Snapshots.
- `meetings/secure_files.py`, `meetings/views.py`: geschützte Datei-Auslieferung und fachliche Zugriffspfade.
- `meetings/audit.py`, `meetings/audit_export.py`: Ereigniserfassung und Export.
- `config/settings.py`: Django-Sicherheitseinstellungen, Middleware, Sessions und Passwortvalidierung.
- `.github/workflows/codeql.yml`, `.github/workflows/dependency-security.yml`, `.github/workflows/container-image-security.yml`, `.github/workflows/tests.yml`: automatisierte Code-, Abhängigkeits-, Container- und Regressionstests.
- `meetings/management_views.py`, `meetings/setup_views.py`: Verwaltung, Import/Export und Ersteinrichtung.
- `meetings/guide_views.py`, `templates/meetings/user_guide.html`: Hilfe-Bereich.
- `docker/compose.yaml`, `docker/Dockerfile`, `.env.example`, Installationsskripte: Bereitstellung und Konfigurationsdefaults.
- Berechtigungs-, Audit-, CSV- und Sicherheitsregressionstests im Repository.

Nicht untersucht wurden eine laufende Instanz, tatsächliche Firewall-/Proxy-/DNS-Konfiguration, die technische Durchsetzung der fehlenden Internetverbindung, Betriebssystemhärtung, reale Datenbestände, Auftragsverarbeitungsverträge, organisatorische Prozesse, die konkrete Offline-Übertragungskette oder ein unabhängiger Penetrationstest. Die im Dokument beschriebene Offline-Updatekette ist derzeit nicht als automatisierter Prozess im Repository implementiert; sie muss durch den Betreiber technisch eingerichtet und nachgewiesen werden. Die vorhandenen Debian- und Docker-Updater benötigen externe Quellen und können in einer vollständig getrennten Offline-Umgebung nicht verwendet werden. Die Risikobewertung muss daher vor Ort bestätigt und nach wesentlichen Änderungen aktualisiert werden.

## 11. Freigabevermerk

Die Freigabe sollte erst erfolgen, wenn die priorisierten Maßnahmen aus Kapitel 7 umgesetzt oder mit einer dokumentierten Risikoakzeptanz versehen wurden.

| Stelle | Bewertung | Name / Datum / Auflagen |
|---|---|---|
| IT-Abteilung | ☐ freigegeben ☐ mit Auflagen ☐ nicht freigegeben | |
| Informationssicherheit | ☐ freigegeben ☐ mit Auflagen ☐ nicht freigegeben | |
| Datenschutzbeauftragte | ☐ Stellungnahme erfolgt ☐ Rückfragen offen | |
| Fachverantwortung | ☐ fachlich freigegeben ☐ Rückfragen offen | |
