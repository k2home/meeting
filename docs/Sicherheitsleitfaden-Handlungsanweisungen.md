# Sicherheitsleitfaden – Handlungsanweisungen zur Risikominimierung

**Zielgruppen:** Hosting-/IT-Betrieb, Nutzer\*innen, globale Administrator\*innen und Auditor\*innen  
**Geltungsbereich:** Meeting Manager gemäß der Funktions- und Sicherheitsbeschreibung in PR #498  
**Zweck und Verbindlichkeit:** Dieses Dokument ist eine praktische Betriebs- und Nutzungsanweisung. Es legt fest, wie die vier Personengruppen den Meeting Manager einrichten, bedienen, verwalten und prüfen müssen, damit IT-Sicherheit und Datenschutz bestmöglich gewährleistet werden. Die Anweisungen sind vor der jeweiligen Handlung und anschließend fortlaufend einzuhalten. Wo eine Voraussetzung nicht erfüllt ist, darf der betreffende Vorgang bzw. die Produktivfreigabe nicht erfolgen; die zuständige Stelle ist einzuschalten.

Die Anweisungen unterscheiden zwischen technisch durch die Anwendung erzwungenen Schutzmaßnahmen und organisatorischen bzw. betrieblichen Pflichten. Eine Empfehlung ersetzt keine fehlende technische Funktion: Insbesondere sind Dateiendungsprüfung und Malware-Prüfung nicht gleichzusetzen, und ein Anwendungs-Audit ersetzt keine Infrastrukturüberwachung. Organisationsspezifische Zuständigkeiten und Meldewege müssen vor Produktivbetrieb namentlich festgelegt werden.

## 1. Technik und Hosting – verbindlicher Einrichtungs- und Betriebsablauf

Dieses Kapitel richtet sich an Personen, die Server, Reverse Proxy, Container, Datenbank, Netzwerk, Updates und Sicherungen betreiben.

### 1.1 Installation und HTTPS-Zugang absichern

- Den vorgesehenen Installer für Debian/Ubuntu oder Docker verwenden und die Installation vollständig abschließen. Die Installer setzen die Django-Sicherheitsoptionen für HTTPS, Session-Cookies und CSRF-Cookies sowie die Proxy-Vertrauenskonfiguration.
- Vor der Freigabe einen HTTPS-Reverse-Proxy mit gültigem Zertifikat auf demselben Host einrichten. Die Installer richten nicht automatisch den TLS-Proxy und das Zertifikat ein.
- Den öffentlichen Zugriff ausschließlich über HTTPS zulassen. HTTP muss auf HTTPS umleiten; die Anwendung darf nicht direkt über einen unverschlüsselten, aus nicht vertrauenswürdigen Netzen erreichbaren Port angeboten werden.
- Bei Docker den veröffentlichten Web-Port standardmäßig nur an `127.0.0.1:8080` binden. Den Reverse Proxy auf demselben Host betreiben und auf `http://127.0.0.1:8080` weiterleiten. Den App-Port 8000 und PostgreSQL niemals öffentlich veröffentlichen.
- Bei Debian den internen Nginx-Zugang auf die tatsächlich verwendete Proxy-IP bzw. das erforderliche CIDR begrenzen. Die beim Installer angegebene Proxy-Adresse muss stimmen und darf nicht unnötig weit gefasst sein.
- Am Proxy `X-Forwarded-Proto: https` setzen und vom Client angelieferte Forwarded-Header überschreiben. Nur dem bekannten Proxy vertrauen. Keine beliebigen Proxy-Adressen oder unkontrollierten Netze als vertrauenswürdig konfigurieren.
- Den öffentlichen Hostnamen in `ALLOWED_HOSTS` und die korrekte HTTPS-Origin in `CSRF_TRUSTED_ORIGINS` verwenden. Keine Wildcards als bequeme Dauerlösung eintragen.
- Nach Einrichtung HTTP-Weiterleitung, Login/Logout, Session- und CSRF-Cookies, Passwort-Reset, Datei-Upload/-Download und PDF-Ausgabe über den HTTPS-Zugang testen.
- HSTS zunächst mit einer kurzen Laufzeit testen. `includeSubDomains` und Preload nur aktivieren, wenn sämtliche betroffenen Subdomains dauerhaft HTTPS unterstützen und die Voraussetzungen geprüft sind.

**Freigabekriterium:** Kein Produktivzugriff, bevor Zertifikat, Proxy-Vertrauen, Portbindung und HTTPS-Tests dokumentiert erfolgreich geprüft wurden.

### 1.2 Netzwerk und Serverzugänge begrenzen

- Nur erforderliche Ports öffnen. Verwaltungszugänge wie SSH auf Admin-Netze bzw. definierte Administrationssysteme beschränken.
- Datenbank und interne App-Kommunikation ausschließlich im internen Netz bzw. Docker-Netz erreichbar machen. PostgreSQL nicht mit einem öffentlichen Host-Port versehen.
- Firewall-Regeln so gestalten, dass der Webdienst nur über den vorgesehenen Reverse Proxy erreichbar ist.
- Betriebssystem, Docker Engine, Docker Compose, PostgreSQL, Nginx und Python-Laufzeit zeitnah mit Sicherheitsupdates versorgen.
- Keine Secrets in Git, Tickets, Chatnachrichten, Shell-Historien oder allgemein lesbaren Dateien ablegen. `.env`, Datenbankpasswort und `SECRET_KEY` mit restriktiven Dateirechten schützen; Zugriffsrechte regelmäßig prüfen.
- Für administrative Tätigkeiten persönliche Konten verwenden. Gemeinsame Root-, SSH- oder Datenbankkonten vermeiden bzw. deren Nutzung auf technisch unvermeidbare Fälle begrenzen und nachvollziehbar kontrollieren.

### 1.3 Nutzerkonten und Berechtigungen organisatorisch absichern

- Für jede Person ein eigenes Konto verwenden; keine Konten oder Passwörter teilen.
- Globale Adminrechte auf wenige benannte Personen begrenzen. Adminrechte nicht für die tägliche fachliche Arbeit verwenden.
- Für jede Besprechungsreihe einen fachlichen Verantwortlichen festlegen, der Mitglieder und Serienrollen regelmäßig überprüft.
- Bei Eintritt, Rollenwechsel und Austritt von Mitarbeitenden Konten und Serienzuweisungen zeitnah anpassen. Nicht mehr benötigte Konten deaktivieren.
- Prüfen, ob ein vorgeschalteter Identity Provider mit MFA eingesetzt werden kann. Falls MFA nicht vorhanden ist, den Zugriff auf vertrauenswürdige Netze bzw. einen abgesicherten VPN-Zugang beschränken und zusätzliche Anmeldekontrollen am Proxy vorsehen.
- Anmeldeversuche und ungewöhnliche Zugriffsmuster auf Infrastruktur-Ebene überwachen. Ein anwendungsinterner Login-Rate-Limiter bzw. MFA darf nicht allein aufgrund der vorhandenen Passwortregeln angenommen werden.

### 1.4 Datei-Uploads und Downloads schützen

Für Themenanlagen gilt serverseitig eine Dateiendungs-Allowlist. Zugelassen sind **PDF, DOCX, XLSX, PPTX, TXT, PNG, JPG und JPEG**. Andere Dateiendungen werden abgewiesen.

- Die Allowlist nur nach fachlicher Prüfung und kontrollierter Änderung erweitern. Nicht benötigte ausführbare Dateien, Skripte und Archive nicht zulassen.
- Beachten, dass die Anwendung die Dateiendung prüft, nicht aber die tatsächliche Dateisignatur oder den Dateiinhalt. Die Endungsprüfung ist kein vollständiger Malware-Schutz.
- Wenn Dateien aus nicht vollständig vertrauenswürdigen Quellen hochgeladen werden, einen Malware-Scanner auf dem Host bzw. in einem vorgeschalteten Quarantäneprozess einsetzen. Ungeprüfte Dateien nicht automatisch als sicher einstufen.
- Das organisationsweite Uploadlimit auf den tatsächlichen Bedarf begrenzen. Standardmäßig sind 20 MB eingestellt; konfigurierbar sind 1 bis 24 MB. Proxy-, Nginx- und Anwendungslimits aufeinander abstimmen.
- Das Medienverzeichnis nicht als öffentliches Webverzeichnis freigeben. Uploads ausschließlich über die authentifizierte Anwendungsroute bereitstellen; keine zusätzliche statische Direkt-Auslieferung konfigurieren.
- Dateispeicher und Medien-Volume mit restriktiven Dateirechten betreiben und in Backups einbeziehen. Zugriff auf Host- und Backup-Ebene nur den zuständigen Betriebsadmins gewähren.

### 1.5 Backups, Wiederherstellung und Verfügbarkeit

- Datenbank und Medienverzeichnis gemeinsam und zeitlich konsistent sichern. Ein Datenbankbackup allein enthält nicht die hochgeladenen Anlagen.
- Mindestens eine verschlüsselte Sicherungskopie getrennt vom Produktivhost aufbewahren. Schreibrechte des Produktivsystems auf die getrennte Sicherung so weit wie möglich vermeiden.
- Aufbewahrungsfristen, Sicherungsintervalle, Verantwortliche sowie Wiederherstellungsziele (RPO/RTO) schriftlich festlegen.
- Vor Updates und Datenbankmigrationen einen überprüften Sicherungsstand erstellen.
- Wiederherstellung regelmäßig in einer isolierten Testumgebung durchführen. Dabei Datenbank, Medien, Logos und die Funktionsfähigkeit der Anwendung prüfen.
- Vollbackup- und Restore-Funktionen nur globalen Admin-Konten zugänglich machen. Vollbackups wie besonders schützenswerte Daten behandeln; sie können Konten, Inhalte und Anlagen umfassen.
- Benutzer-CSV-Import/-Export und Vollbackup/Restore sind globale Admin-Funktionen. Themen-CSV-Import/-Export steht Moderator\*innen nur für ihre ausdrücklich moderierten Reihen zur Verfügung; globale Adminrechte allein gewähren dafür keinen zusätzlichen Zugriff.
- Exportdateien verschlüsselt und zugriffsbeschränkt ablegen, nur an benannte Empfänger\*innen übermitteln und nicht mehr benötigte lokale Kopien sicher löschen.

### 1.6 Updates, Protokollierung und Notfallvorsorge

- Produktionsupdates nur aus freigegebenen Branches bzw. Releases übernehmen. Version und Commit des laufenden Systems dokumentieren.
- Abhängigkeiten und Container-Images regelmäßig auf bekannte Sicherheitslücken prüfen. Kritische Befunde priorisiert beheben und Ausnahmen mit Begründung, Verantwortlichem und Frist dokumentieren.
- Updates zunächst in einer Testumgebung prüfen. Nach Updates Login, Berechtigungen, Upload/Download, CSV-Funktionen, Protokollabschluss und Wiederherstellung testen.
- Systemlogs auf ungewöhnliche Login-Fehler, Änderungen globaler Rollen, fehlgeschlagene Downloads, unerwartete Dienstneustarts und Speicherengpässe überwachen.
- Audit-Daten und Systemlogs als vertrauliche Informationen behandeln. Die Anwendung gibt nach erfolgreichem Datenbank-Commit zusätzlich metadatenarme JSON-Audit-Ereignisse an stdout/stderr aus (Event-ID, Zeit, Bereich, Akteur-ID, Aktion und Objekt-IDs; keine Freitexte oder Änderungswerte). Diese Ausgabe an einen getrennt administrierten zentralen Logdienst weiterleiten. Bei zentraler Logsammlung Zugriffe und Aufbewahrungsfristen begrenzen; besonders schützenswerte Protokolle möglichst getrennt vom Produktivsystem speichern. Ohne externe Weiterleitung ist die Datenbank-Auditspur nicht manipulationsgeschützt.
- Verfahren für kompromittierte Konten, Datenpannen, Ransomware, Systemausfall und Wiederherstellung festlegen. Zuständigkeiten und Eskalationskontakte aktuell halten.

### Verbindlicher Ablauf vor, während und nach jeder Nutzung

1. **Vor der Anmeldung:** Öffnen Sie den Meeting Manager ausschließlich über die freigegebene HTTPS-Adresse. Verwenden Sie Ihr persönliches Konto. Nutzen Sie keine fremden oder gemeinsam verwendeten Zugangsdaten.
2. **Vor dem Öffnen einer Reihe:** Prüfen Sie, ob Sie für genau diese Besprechungsreihe berechtigt sind. Bei fehlender Berechtigung beantragen Sie die Zuweisung bei der zuständigen Moderation; umgehen Sie die Sperre nicht.
3. **Vor dem Erfassen von Inhalten:** Prüfen Sie den fachlichen Zweck und beschränken Sie Einträge auf erforderliche Informationen. Zugangsdaten und nicht freigegebene sensible Angaben gehören niemals in Besprechungsinhalte oder Anlagen.
4. **Vor dem Upload:** Prüfen Sie Empfänger\*innenkreis, Dateiendung und Herkunft. Laden Sie nur die freigegebenen Formate hoch. Öffnen Sie verdächtige Dateien nicht; melden Sie sie dem IT-Support. Eine erlaubte Endung ist kein Sicherheitsnachweis für den Dateiinhalt.
5. **Vor dem Teilen oder Exportieren:** Prüfen Sie jede empfangende Person und jeden Zielort. Geben Sie Inhalte nur an Personen weiter, die sie für ihre Aufgabe benötigen und berechtigt sind.
6. **Vor dem Abschluss einer Besprechung:** Prüfen Sie Tagesordnung, Zuständigkeiten und Protokoll auf Richtigkeit und Datenminimierung. Bedenken Sie, dass ein historischer Protokoll-Snapshot erhalten bleibt.
7. **Nach der Nutzung:** Melden Sie sich an gemeinsam genutzten Geräten ab und sperren Sie den Bildschirm. Melden Sie verdächtige Aktivitäten unverzüglich über den festgelegten Meldeweg.

**Abbruchregel:** Wenn Berechtigung, Empfänger\*innenkreis, Dateisicherheit oder Zulässigkeit eines Inhalts unklar ist, führen Sie die Handlung nicht aus. Fragen Sie die zuständige Moderation oder Administration.

## 2. Nutzer\*innen – verbindlicher Ablauf bei jeder Nutzung

Dieses Kapitel richtet sich an alle Personen, die Besprechungsreihen, Themen, Tagesordnungspunkte, Kommentare, Anlagen oder Protokolle verwenden.

### 2.1 Nur erforderliche Informationen erfassen

- Nur Informationen eintragen, die für Zweck und Durchführung der Besprechung erforderlich sind.
- Keine Passwörter, Zugangstoken, privaten Schlüssel oder sonstigen Zugangsdaten in Themen, Kommentaren, Tagesordnungstexten oder Anlagen hinterlegen.
- Keine besonders sensiblen personenbezogenen Angaben (z. B. Gesundheitsdaten oder private Personalangelegenheiten) eintragen, sofern dies nicht ausdrücklich freigegeben, erforderlich und datenschutzrechtlich geklärt ist.
- Bei Unsicherheit vor dem Eintragen die zuständige Führungskraft bzw. der fachlich verantwortlichen Person fragen.
- Sachlich, knapp und aufgabenbezogen formulieren. Wertende oder private Kommentare vermeiden.

### 2.2 Konten und Sitzungen schützen

- Das persönliche Konto ausschließlich selbst verwenden. Zugangsdaten nicht weitergeben und nicht in gemeinsam genutzten Dokumenten speichern.
- Ein individuelles, nicht anderweitig verwendetes Passwort nutzen und die Passwortregeln der Anwendung einhalten. Ein Passwortmanager wird empfohlen.
- Bei Verdacht auf Kenntnisnahme des Passworts unverzüglich den vorgesehenen Passwort-Reset durchführen und die Administrator\*innen informieren.
- An gemeinsam genutzten Arbeitsplätzen nach der Arbeit abmelden und den Bildschirm sperren. Die Anwendungssitzung kann bis zu acht Stunden bestehen.
- Verdächtige Login-Benachrichtigungen, unerwartete Änderungen oder nicht selbst ausgelöste Aktionen unverzüglich melden.

### 2.3 Serienberechtigungen beachten

- Nur Besprechungsreihen öffnen und verwenden, für die eine ausdrückliche Serienzuweisung besteht.
- Vor dem Teilen von Inhalten prüfen, ob die Empfänger\*innen tatsächlich Mitglied der betreffenden Reihe sind und die passende Serienrolle besitzen.
- Keine Protokolle, CSV-Dateien, Screenshots oder Anlagen außerhalb des vorgesehenen Empfänger\*innenkreises weitergeben.
- Netzwerkpfade und externe Links sind nur Verweise. Die Zugriffsberechtigung auf dem Zielsystem muss separat bestehen und darf nicht aus der Meeting-Manager-Berechtigung abgeleitet werden.
- Bei fehlendem oder unerwartetem Zugriff nicht versuchen, Berechtigungen durch erratene URLs oder fremde Konten zu umgehen, sondern Moderator\*in oder Administrator\*in kontaktieren.

### 2.4 Anlagen sicher verwenden

- Nur fachlich erforderliche Dateien hochladen. Zulässige Dateiendungen sind PDF, DOCX, XLSX, PPTX, TXT, PNG, JPG und JPEG.
- Keine Dateien durch Umbenennen einer Endung vermeintlich sicher machen. Die Anwendung prüft die Dateiendung, nicht den tatsächlichen Dateiinhalt.
- Dateien aus E-Mails oder externen Quellen vor dem Öffnen mit dem bereitgestellten Virenschutz prüfen. Bei unerwarteten oder verdächtigen Dateien nicht öffnen und den IT-Support informieren.
- Keine ausführbaren Dateien, Skripte oder Archive als Umweg über Netzwerkpfade oder externe Links bereitstellen.
- Vor dem Hochladen prüfen, ob die Datei vertrauliche Informationen enthält und ob alle Mitglieder der Reihe diese sehen dürfen.

### 2.5 Protokolle und Änderungsverlauf richtig einordnen

- Vor Abschluss einer Besprechung Tagesordnung, Zuständigkeiten und Protokolltext auf Richtigkeit und erforderlichen Inhalt prüfen.
- Beachten, dass beim Abschluss ein Protokoll-Snapshot entsteht. Spätere Änderungen am Thema ändern diesen historischen Protokollstand nicht.
- Änderungsdetails können zunächst eingeklappt sein. Nicht davon ausgehen, dass ein nicht sofort sichtbares Detail nicht gespeichert wurde.
- Der Audit-Verlauf ist rollenabhängig eingeschränkt. Nutzer\*innen erhalten dadurch nicht automatisch Einsicht in alle Änderungen oder in Systemereignisse.
- Fehlerhafte oder versehentlich eingetragene Informationen zeitnah an Moderator\*in oder Administrator\*in melden; historische Protokoll- und Audit-Daten können gesonderten Regeln unterliegen.

### Verbindlicher Ablauf für Konten- und Rechteverwaltung

1. **Antrag entgegennehmen:** Verlangen Sie einen nachvollziehbaren fachlichen Grund, die betroffene Person, den benötigten Zugriff und – soweit möglich – eine Befristung.
2. **Identität und Bedarf prüfen:** Vergewissern Sie sich, dass das Konto zur richtigen Person gehört und der beantragte Umfang erforderlich ist. Erteilen Sie keine globale Adminrolle, wenn eine Serienrolle genügt.
3. **Berechtigung setzen:** Vergeben Sie globale Rollen und Serienrollen getrennt. Globale Adminrechte gewähren nicht automatisch Einsicht in fachliche Reihen. Für fachliche Mitarbeit ist die ausdrückliche Serienzuweisung erforderlich.
4. **Änderung kontrollieren:** Prüfen Sie nach dem Speichern die resultierende Rolle und Serienzuordnung. Dokumentieren Sie Antrag, Entscheidung, Umfang und Zeitpunkt außerhalb des vertraulichen Inhaltsbereichs nach dem organisationsinternen Verfahren.
5. **Regelmäßig rezertifizieren:** Lassen Sie mindestens quartalsweise bestätigen, dass globale Admin-Konten und Serienmitgliedschaften weiterhin benötigt werden. Entziehen Sie nicht mehr erforderliche Rechte unverzüglich.
6. **Austritt oder Sicherheitsverdacht:** Deaktivieren Sie das betroffene Konto bzw. entziehen Sie die betroffenen Rechte unverzüglich nach dem internen Prozess. Bei kompromittierten Zugangsdaten veranlassen Sie zusätzlich Passwortzurücksetzung und Vorfallprüfung.

### Verbindlicher Ablauf für CSV-Importe und -Exporte

1. Führen Sie Benutzer-CSV-Funktionen nur mit dem globalen Admin-Konto und für einen konkreten administrativen Vorgang aus.
2. Prüfen Sie vor dem Import Dateiherkunft, UTF-8-Kodierung, Pflichtfelder, betroffene Konten und Serienzuordnungen. Kontrollieren Sie die Vorschau vollständig.
3. Brechen Sie den Import ab, wenn unerwartete Konten, Rollen oder Serienzuordnungen angezeigt werden. Klären Sie die Ursache vor einem erneuten Versuch.
4. Sichern Sie Exporte nur in freigegebenen, zugriffsbeschränkten Speicherorten. Übermitteln Sie sie ausschließlich an benannte berechtigte Empfänger\*innen und löschen Sie Arbeitskopien nach Ablauf des festgelegten Zwecks.
5. Themen-CSV-Funktionen verwenden Moderator\*innen ausschließlich für Reihen, für die sie ausdrücklich Moderator\*innenrechte besitzen. Globale Adminrechte ersetzen diese Serienberechtigung nicht.

### Verbindlicher Ablauf für Vollbackup und Restore

1. Erstellen Sie ein Vollbackup nur bei dokumentiertem Betriebsbedarf und speichern Sie es verschlüsselt an einem freigegebenen Ort.
2. Vor einem Restore prüfen Sie Freigabe, Zielsystem, Sicherungszeitpunkt und Zusammengehörigkeit von Datenbank und Medien.
3. Erstellen Sie unmittelbar vor dem Restore einen zusätzlichen Sicherungsstand, sofern der Zustand des Zielsystems dies zulässt.
4. Führen Sie den Restore im angekündigten Wartungsfenster aus und begrenzen Sie den Zugriff auf die beteiligten Betriebsadmins.
5. Prüfen Sie anschließend Anmeldung, Konten, Serienberechtigungen, Protokolle und Anlagen. Dokumentieren Sie Ergebnis und Abweichungen.

### Verbindlicher Ablauf bei Audit-Einsicht

Öffnen Sie Audit-Daten nur bei einem konkreten administrativen oder prüfenden Anlass. Berücksichtigen Sie die rollenabhängige Sichtbarkeit: Systemereignisse sind für Administrator*innen sichtbar; Serienereignisse nur für Reihen, in denen die betreffende Person ausdrücklich Moderator\*in ist. Öffnen Sie eingeklappte Details nur soweit erforderlich. Behandeln Sie Protokoll-Snapshots beim Wiederöffnen abgeschlossener Besprechungen und Audit-CSV-Dateien als vertrauliche Inhalte.

## 3. Globale Administrator\*innen – verbindlicher Verwaltungsablauf

Dieses Kapitel richtet sich an Personen mit globalen Adminrechten. Adminrechte sind weitreichend und sollen nur für administrative Aufgaben genutzt werden. Sie verleihen nicht automatisch Zugriff auf fachliche Inhalte jeder Besprechungsreihe; dafür ist eine eigene Serienzuweisung erforderlich.

### 3.1 Admin-Konten und Rechtevergabe

- Nur namentlich benannten Personen globale Adminrechte erteilen. Anzahl der Admin-Konten so klein wie betrieblich möglich halten.
- Für fachliche Mitarbeit ein separates persönliches Konto verwenden, statt dauerhaft mit dem Admin-Konto zu arbeiten.
- Adminrechte bei Aufgabenwechsel oder Austritt unverzüglich entziehen und das Konto deaktivieren, falls es nicht mehr benötigt wird.
- Vor jeder Rechtevergabe Zweck, Umfang und Dauer prüfen. Serienrollen unabhängig von der globalen Rolle vergeben.
- Mindestens quartalsweise globale Admin-Konten und Serienzuweisungen prüfen und das Ergebnis dokumentieren.
- Auditor\*innen-Konten nicht mit Adminrechten kombinieren. Die Auditor\*innen-Rolle ist für einen lesenden, fachlich eingeschränkten Prüfzugriff vorgesehen.

### 3.2 Serienberechtigungen verantwortungsvoll verwalten

- Für jede Reihe einen fachlichen Verantwortlichen benennen und die Mitgliederliste regelmäßig durch diesen bestätigen lassen.
- Nur die erforderliche Serienrolle vergeben: Leser\*in für Lesezugriff, Teilnehmer\*in für laufende Mitarbeit, Moderator\*in nur für tatsächliche Reihenverwaltung.
- Bei Änderungen der Organisation oder Aufgabenverteilung Serienzuweisungen sofort aktualisieren.
- Beachten, dass globale Adminrechte allein keinen fachlichen Zugriff auf eine Reihe gewähren. Für die eigene Einsichtnahme ist eine explizite Serienzuweisung erforderlich.
- Bei Supportfällen keine Serienzuweisung nur aus Bequemlichkeit vergeben. Stattdessen die betroffene Person bzw. die zuständige Moderator\*in um Prüfung bitten.
- Berechtigungsanträge und ihre Begründungen sorgfältig prüfen; nur den tatsächlich benötigten Umfang genehmigen.

### 3.3 CSV-Importe und -Exporte kontrollieren

- Benutzer-CSV-Importe und -Exporte nur für einen konkreten administrativen Zweck ausführen.
- Vor dem Benutzerimport UTF-8-Datei, Pflichtfelder, Benutzerkonten, Rollen und Serienzuordnungen prüfen. Die Importvorschau vollständig kontrollieren, bevor die Übernahme bestätigt wird.
- Beachten, dass CSV-Angaben zu Serienzuordnungen bestehende Zuordnungen aktualisieren können. Vor Änderungen einen nachvollziehbaren Ausgangsstand sichern.
- Benutzer-CSV-Dateien enthalten personenbezogene Kontodaten und Berechtigungsinformationen. Sie nur in zugriffsbeschränkten Verzeichnissen speichern und über sichere Wege übertragen.
- Themen-CSV-Import/-Export ist Moderator\*innen für ihre ausdrücklich moderierten Reihen vorbehalten. Globale Adminrechte allein berechtigen nicht zu diesem fachlichen CSV-Zugriff.
- Bei Importproblemen nicht durch direkte Datenbankänderungen oder manuelle Dateimanipulationen ausweichen, sondern den vorgesehenen Prozess bzw. einen kontrollierten Supportweg verwenden.
- Exportdateien nach Erfüllung des Zwecks sicher löschen und keine unkontrollierten Kopien in persönlichen Cloudspeichern oder E-Mail-Postfächern belassen.

### 3.4 Vollbackup und Restore schützen

- Vollbackups nur bei betrieblicher Notwendigkeit und durch autorisierte Administrator*innen erstellen.
- Backups als vollständige Datenkopien mit möglicherweise vertraulichen Inhalten und personenbezogenen Daten behandeln.
- Sicherungsdateien verschlüsselt und mit minimalem Empfänger\*innenkreis speichern bzw. übertragen. Keine Backups an private E-Mail-Adressen oder unfreigegebene Cloud-Dienste senden.
- Vor einem Restore Anlass, Zielsystem, Datenstand und Auswirkungen prüfen. Restore nur in einem kontrollierten Wartungsfenster durchführen.
- Vor dem Restore einen zusätzlichen aktuellen Sicherungsstand erstellen und sicherstellen, dass Datenbank und Medienstand zusammenpassen.
- Nach der Wiederherstellung Login, Benutzer-/Serienberechtigungen, Protokolle und Anlagen stichprobenartig prüfen und das Ergebnis dokumentieren.
- Regelmäßige Restore-Tests mit dem IT-Betrieb abstimmen; ein erfolgreich erzeugtes Backup ist noch kein Nachweis erfolgreicher Wiederherstellbarkeit.

### 3.5 Audit, Systemverwaltung und Datenschutz

- Systemereignisse nur für legitime administrative oder prüfende Zwecke einsehen. Die Einsichtnahme nicht zur anlasslosen Verhaltens- oder Leistungskontrolle verwenden.
- Beachten, dass Administrator*innen Systemereignisse sehen und Serienereignisse nur für Reihen, in denen sie selbst Moderator\*innenrechte besitzen. Eine globale Adminrolle allein öffnet keine fachlichen Serienverläufe.
- Passwörter und hochgeladene Datei-Inhalte werden nicht als Audit-Werte gespeichert. Bei Passwortänderungen wird nur der Änderungsstatus protokolliert; Dateinamen können als Metadaten erscheinen.
- Beim Wiederöffnen einer abgeschlossenen Besprechung bleibt der vorherige gesicherte Protokollstand als Audit-Detail erhalten. Diesen Snapshot als vertraulichen fachlichen Inhalt behandeln.
- Audit-Details sind in der Oberfläche zunächst eingeklappt. Das ist eine Darstellungsform und keine zusätzliche Zugriffsschranke.
- Audit-CSV-Exporte enthalten strukturierte Details und sind entsprechend der eigenen Berechtigung eingeschränkt. Exportdateien vertraulich behandeln und nicht unnötig vervielfältigen.
- Bei Verdacht auf unberechtigte Einsicht, fehlerhafte Rechte oder ungewöhnliche Systemereignisse den Vorfall dokumentieren und an IT-Sicherheit bzw. Datenschutzverantwortliche eskalieren.

### Verbindlicher Ablauf eines Audit-Prüfvorgangs

1. **Prüfauftrag prüfen:** Beginnen Sie nur mit einem autorisierten Prüfauftrag. Halten Sie Prüfziel, Zeitraum, Umfang und zuständige auftraggebende Stelle fest.
2. **Zugriff begrenzen:** Verwenden Sie Ihr persönliches Auditor\*innen-Konto. Nutzen Sie keine Admin- oder fremden Konten. Der Auditor\*innen-Zugriff ist auf Systemereignisse und lesbare administrative Stammdaten beschränkt; er eröffnet keinen Zugriff auf Besprechungsinhalte.
3. **Gezielt filtern:** Begrenzen Sie Zeitraum und Ereignisauswahl auf das Prüfziel. Öffnen Sie eingeklappte Änderungsdetails nur, wenn sie für die Prüfung erforderlich sind.
4. **Inhalte richtig einordnen:** Passwortwerte und hochgeladene Datei-Inhalte werden nicht als Audit-Werte gespeichert. Passwortänderungen erscheinen als Statusereignis; Dateinamen können Metadaten sein. Beim Wiederöffnen einer abgeschlossenen Besprechung kann ein vorheriger Protokoll-Snapshot als Detail erscheinen. Behandeln Sie diesen wie vertrauliche Besprechungsdaten und greifen Sie nur bei geklärter Berechtigung darauf zu.
5. **Ergebnisse sichern:** Exportieren Sie Audit-CSV nur, wenn sie für den Prüfauftrag erforderlich ist. Speichern Sie Exporte verschlüsselt bzw. zugriffsbeschränkt, geben Sie sie nur an den autorisierten Empfänger\*innenkreis und löschen Sie Arbeitskopien nach Abschluss gemäß Aufbewahrungsregel.
6. **Feststellungen berichten:** Dokumentieren Sie Tatsachen, Zeitraum und relevante Ereignisse getrennt von Bewertungen. Ziehen Sie aus fehlenden Ereignissen nicht den Schluss, dass eine Handlung unmöglich stattgefunden hat.
7. **Auffälligkeiten eskalieren:** Melden Sie Hinweise auf unberechtigte Rollenänderungen, Kontoübernahmen oder Datenschutzverletzungen über den festgelegten Sicherheits- bzw. Datenschutzprozess. Für Host-, Proxy- und Datenbankereignisse fordern Sie die zuständigen Infrastrukturprotokolle an.

**Abbruchregel:** Wenn ein Prüfauftrag keinen ausreichenden Umfang oder keine Berechtigung für ein sichtbares fachliches Detail umfasst, öffnen, exportieren oder verbreiten Sie dieses Detail nicht. Klären Sie den Auftrag vor der Fortsetzung.

## 4. Auditor\*innen – verbindlicher Prüfablauf

Dieses Kapitel richtet sich an Personen mit der globalen Rolle Auditor\*in. Auditor\*innen haben einen lesenden Zugriff auf administrative Prüfdaten, nicht auf fachliche Besprechungsinhalte.

### 4.1 Umfang und Grenzen des Zugriffs verstehen

- Den Audit-Zugriff ausschließlich für festgelegte Prüfaufträge und nachvollziehbare Kontrollzwecke verwenden.
- Beachten, dass Auditor\*innen ausschließlich Systemereignisse einsehen und exportieren können. Besprechungsreihen, Tagesordnungspunkte, Kommentare und Anlagen gehören nicht zum Auditor\*innen-Zugriff.
- Auditor\*innen können Benutzerkonten, globale Rollen, Serienzuordnungen und Organisationseinstellungen lesend prüfen. Änderungen müssen durch die zuständigen Administrator*innen erfolgen.
- Keine fachlichen Serienberechtigungen anfordern, um den eingeschränkten Prüfzugriff zu umgehen. Wenn eine fachliche Prüfung erforderlich ist, muss sie gesondert legitimiert und über einen geeigneten Prozess organisiert werden.
- Die Auditor\*innen-Rolle nicht mit globalen Adminrechten kombinieren. Admin- und Superuser-Rechte sind keine Auditor\*innen-Rechte und erweitern den Zugriff erheblich.

### 4.2 System-Audit sorgfältig auswerten

- Bei jeder Prüfung Zeitraum, Prüfziel, betrachtete Ereignistypen und verwendete Filter dokumentieren.
- Ereignisse anhand von handelnder Person, Zeitpunkt, Aktion und verfügbaren Änderungsdetails einordnen. Einzelne Ereignisse nicht ohne Kontext als Fehlverhalten bewerten.
- Beachten, dass die Oberfläche Änderungsdetails zunächst eingeklappt darstellt. Details nur bei konkretem Prüfbedarf öffnen.
- Keine Passwörter oder Datei-Inhalte im Audit erwarten: Passwortwerte werden nicht protokolliert; bei Passwortänderungen wird nur der Änderungsstatus festgehalten. Hochgeladene Datei-Inhalte werden nicht gespeichert; Dateinamen können als Metadaten vorkommen.
- Wird eine abgeschlossene Besprechung wieder geöffnet, kann der vorherige Protokoll-Snapshot als Audit-Detail enthalten sein. Solche Inhalte nur einsehen, wenn der konkrete Prüfauftrag dies erfordert und die Berechtigung dafür geklärt ist.
- Die Audit-Ansicht als begrenzte Nachvollziehbarkeit verstehen, nicht als vollständiges, manipulationsgeschütztes Sicherheitsprotokoll der gesamten Hosting-Infrastruktur.

### 4.3 Audit-Exporte und Prüfergebnisse schützen

- System-Audit-CSV nur exportieren, wenn die Prüfung es erfordert. Die Exportfunktion erweitert nicht den fachlichen Zugriff auf Besprechungsreihen.
- Exportdateien wie vertrauliche personenbezogene Prüfdaten behandeln. Empfänger\*innenkreis, Speicherort und Aufbewahrungsfrist vorab festlegen.
- Dateien nur über freigegebene, zugriffsbeschränkte und möglichst verschlüsselte Speicher- und Übertragungswege verarbeiten.
- Keine Audit-Exporte in offene Tickets, allgemeine Teamablagen oder unverschlüsselte E-Mail-Anhänge kopieren.
- Nach Abschluss der Prüfung Arbeitskopien löschen und erforderliche Prüfunterlagen gemäß den geltenden Aufbewahrungsregeln ablegen.
- Feststellungen sachlich formulieren und nur die für den Prüfzweck erforderlichen personenbezogenen Angaben in Berichte übernehmen.

### 4.4 Auffälligkeiten und Grenzen eskalieren

- Ungewöhnliche Änderungen globaler Rollen, Benutzerkonten oder Organisationseinstellungen zeitnah mit IT-Betrieb bzw. Anwendungsadministration abgleichen.
- Fehlende oder unerwartete Ereignisse nicht automatisch als Beweis werten, dass eine Aktion nicht stattgefunden hat. Der Audit-Verlauf bildet die von der Anwendung erfassten Ereignisse ab.
- Für Fragen zu Host-, Proxy-, Datenbank- oder Betriebssystemereignissen die zuständigen IT-Betriebsprotokolle anfordern. Diese liegen außerhalb des fachlichen System-Audits der Anwendung.
- Hinweise auf Datenschutzverletzungen oder unberechtigte Zugriffe nach dem organisationsinternen Melde- und Eskalationsprozess weitergeben.

## 5. Verbindlicher Kontroll- und Freigabezyklus

Die folgenden Intervalle bilden den Mindeststandard für den Betrieb. Die verantwortliche Organisation benennt die ausführenden Personen und dokumentiert jede Prüfung. Kürzere Intervalle sind bei erhöhtem Schutzbedarf festzulegen.

| Intervall | Verantwortlich | Prüfpunkte |
|---|---|---|
| Bei jeder Installation / vor Produktivfreigabe | IT/Hosting | HTTPS, Proxy-Vertrauen, Firewall, Secrets, Medienpfad, initiales Admin-Konto |
| Bei Eintritt, Rollenwechsel und Austritt | Administrator*innen + Fachverantwortliche | Kontoaktivität, globale Rolle, Serienzuweisungen |
| Mindestens quartalsweise | Fachverantwortliche + Administrator*innen | Mitglieder und Serienrollen, Admin-Konten, unnötige Berechtigungen |
| Monatlich und bei Sicherheitsmeldungen | IT/Hosting | Betriebssystem-/Image-/Abhängigkeitsupdates, Sicherheitswarnungen, Speicherplatz |
| Nach jedem Update | IT/Hosting + Testverantwortliche | Login, Rollen, Upload/Download, CSV, Protokolle, Backup/Restore |
| Mindestens quartalsweise | IT/Hosting | Wiederherstellungstest für Datenbank und Medien |
| Nach Prüfauftrag bzw. anlassbezogen | Auditor\*innen | System-Audit, Rollen-/Kontrollprüfung, sichere Behandlung von Exporten |
| Jährlich und bei wesentlichen Änderungen | Verantwortliche, Datenschutz, IT-Sicherheit | Zwecke, Datenkategorien, Empfänger\*innen, Aufbewahrung, Löschung und Risikobewertung |

## 6. Vorfälle melden

Bei Verdacht auf kompromittierte Konten, versehentliche Offenlegung, schädliche Dateien, unberechtigte Zugriffe oder Datenverlust:

1. Keine verdächtigen Dateien öffnen und keine weiteren Datenkopien erzeugen.
2. Zeitpunkt, betroffene Besprechungsreihe bzw. Funktion und beobachtetes Verhalten sachlich festhalten. Keine Passwörter oder sonstigen Geheimnisse in die Meldung schreiben.
3. Unverzüglich den zuständigen IT-Support bzw. die benannte Sicherheitskontaktstelle informieren.
4. Bei möglichem Personenbezug zusätzlich den internen Datenschutz-Meldeweg nutzen. Die Bewertung und Meldung einer Datenschutzverletzung erfolgt durch die dafür zuständigen Stellen.
5. Betroffene Konten, Systeme oder Dateien nicht eigenmächtig löschen oder verändern, sofern dadurch Beweise oder Wiederherstellungsmöglichkeiten verloren gehen könnten.

---

**Verbindlichkeit:** Die vorstehenden Abläufe sind als Mindeststandard umzusetzen. Vor Produktivbetrieb müssen die Organisation und die Betreiber\*innen konkrete Verantwortliche, erreichbare Sicherheits- und Datenschutzkontakte, Freigabewege, Aufbewahrungsfristen und Löschverfahren schriftlich festlegen. Kann eine Anweisung nicht umgesetzt werden, ist dies vorab als Abweichung mit Risiko, kompensierender Maßnahme, verantwortlicher Freigabe und Überprüfungstermin zu dokumentieren. Eine nicht freigegebene Abweichung berechtigt nicht zur Produktivnutzung.
