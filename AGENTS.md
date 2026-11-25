# Arbeitsanweisungen für KI-Agenten

Diese Datei enthält verbindliche Arbeitsregeln für KI-Agenten (insbesondere ChatGPT und Codex), die dieses Repository bearbeiten.

## Repository- und Branch-Regeln

- Arbeite grundsätzlich auf dem vom Nutzer ausdrücklich genannten Feature-Branch bzw. dem Branch des zugehörigen Pull Requests.
- Für die laufende Arbeit an PR #528 ist dies `feat/testing-mode-fixtures`.
- Ändere oder merge `beta` oder andere Ziel-/Produktionsbranches niemals direkt, sofern der Nutzer dies nicht ausdrücklich beauftragt.
- Bewahre bestehende Funktionen, Daten, Berechtigungen und insbesondere die bestehenden Serienberechtigungen. Ändere Berechtigungsregeln nicht beiläufig.
- Kläre Rückfragen und Unklarheiten vor der Umsetzung. Triff bei fachlich mehrdeutigen Anforderungen keine stillschweigenden Annahmen.
- Führe passende Tests und Prüfungen aus, soweit möglich. Behaupte niemals, Tests oder CI-Prüfungen seien erfolgreich, wenn sie nicht tatsächlich ausgeführt wurden und erfolgreich waren. Weise offen auf nicht ausgeführte oder noch laufende Prüfungen hin.

## Verbindliche Prüfungen bei jeder relevanten Codeänderung

Die folgenden Prüfungen sind bei **jeder relevanten Codeänderung** durchzuführen. Relevant ist eine Änderung, sobald sie den jeweiligen Codepfad, dessen Daten, Berechtigungen, Schnittstellen, Konfiguration oder Benutzerabläufe berührt. Bei Änderungen mit Auswirkungen auf mehrere Bereiche sind alle betroffenen Prüfpunkte abzuarbeiten. Die Prüfung ist nicht auf Änderungen an sichtbaren Funktionen beschränkt.

### 1. Sicherheit

Bei jeder Änderung an Views, Formularen, APIs, Uploads/Downloads, Templates oder sonstigen Ein-/Ausgabepfaden:

- Prüfe alle schreibenden HTTP-Aktionen darauf, dass CSRF-Schutz aktiv ist und nicht durch Ausnahmen, alternative Endpunkte oder clientseitige Umgehungen ausgehebelt wird.
- Prüfe Ausgaben nutzergesteuerter oder externer Inhalte in HTML, JavaScript, Attributen und URLs auf kontextgerechtes Escaping. Verwende keine ungeprüfte HTML-Ausgabe und keine unsicheren DOM-/Template-Konstruktionen.
- Prüfe Datenbankzugriffe mit externen oder nutzergesteuerten Werten auf parametrisierte Abfragen bzw. sichere ORM-Nutzung; baue keine SQL-Anweisungen durch ungeprüfte String-Verkettung.
- Prüfe Datei-Uploads und -Downloads auf serverseitige Berechtigungsprüfung, zulässige Dateitypen und Größen, sichere Dateinamen und Pfade sowie Schutz vor Zugriff auf beliebige Dateien. Verlasse dich bei sicherheitsrelevanten Entscheidungen nicht allein auf clientseitige Prüfungen oder Dateiendungen.
- Stelle sicher, dass Fehlermeldungen und Logs keine Passwörter, Tokens, Sitzungsschlüssel oder unnötigen personenbezogenen bzw. vertraulichen Inhalte offenlegen.
- Prüfe Weiterleitungen und externe URLs auf erlaubte Ziele; nutzergesteuerte Redirect-Ziele dürfen keine unkontrollierten Weiterleitungen auf fremde Seiten ermöglichen.
- Dokumentiere im Abschlussbericht konkret, welche der genannten Angriffsflächen geprüft wurden und welche Tests oder manuellen Prüfungen dies belegen.

### 2. Berechtigungen und Zugriffsschutz

Bei jeder Änderung an Berechtigungen, Rollen, Views, URLs, APIs, Dateioperationen, Exporten oder Hintergrundaufgaben:

- Prüfe die Berechtigung serverseitig in jedem betroffenen Zugriffspfad. Eine ausgeblendete Schaltfläche oder ein clientseitiger Check gilt nicht als Zugriffsschutz.
- Prüfe sowohl lesende als auch schreibende Aktionen sowie direkte URL-Aufrufe, AJAX-Endpunkte, PDF-/CSV-Exporte, Downloads und Hintergrundprozesse.
- Stelle sicher, dass Nutzer nur auf Besprechungsreihen, Termine, Themen, Tagesordnungspunkte und Dateien zugreifen können, für die sie gemäß ihrer Rolle und Zuweisung berechtigt sind.
- Prüfe insbesondere die Trennung zwischen globalen Administratoren, Moderator*innen, Leser*innen und sonstigen Nutzerrollen. Leser*innen dürfen über alternative Endpunkte keine Schreibaktionen ausführen.
- Bewahre die bestehenden Serienberechtigungen und deren Reichweite. Eine neue Funktion darf weder unbeabsichtigt Rechte auf weitere Reihen ausweiten noch bestehende Zugriffe entziehen.
- Ergänze oder aktualisiere Tests für erlaubte und verweigerte Zugriffe, einschließlich direkter Aufrufe der betroffenen Endpunkte.

### 3. Datenschutz und Datenminimierung

Bei Änderungen an personenbezogenen Daten, Protokollen, Kommentaren, Anlagen, Exporten, Logs, Snapshots, Aufbewahrung oder Löschung:

- Prüfe, ob nur die für den jeweiligen Zweck erforderlichen personenbezogenen Daten gespeichert, angezeigt, exportiert und protokolliert werden.
- Vermeide personenbezogene oder vertrauliche Daten in URLs, unnötigen Logeinträgen und Fehlermeldungen.
- Prüfe Aufbewahrungsfristen anhand der maßgeblichen Organisations- oder Themenkonfiguration sowie der fachlich festgelegten Startzeitpunkte. Berücksichtige Datumsgrenzen, Zeitzonen und den Zeitpunkt der tatsächlichen Ausführung.
- Prüfe nicht nur den Hauptdatensatz, sondern auch abhängige Datensätze und Dateiinhalte: insbesondere Protokoll-Snapshots, historische Einträge, Audit-Daten, Exporte, Anlagen und gespeicherte Dateien.
- Stelle sicher, dass eine Löschung alle laut Fachregel zu löschenden Daten tatsächlich entfernt und keine unbeabsichtigten Kopien oder verwaisten Dateien zurücklässt. Daten, die ausdrücklich erhalten bleiben müssen, dürfen nicht mitgelöscht werden.
- Prüfe, ob archivierte und historische Inhalte nach Ablauf ihrer Frist weder über normale Ansichten noch über direkte URLs, Exporte oder Downloads weiterhin zugänglich sind.
- Ergänze Tests für Fristablauf, Datenzugriff vor und nach Ablauf sowie das gezielte Erhalten von Daten, die laut Fachregel bestehen bleiben sollen.

### 6. Automatisierte Tests

Bei jeder Änderung an bestehendem oder neuem Verhalten:

- Ergänze Tests für neue Funktionen und für geänderte fachliche Regeln. Ändere bestehende Tests nur, wenn sich das erwartete Verhalten fachlich begründet ändert.
- Entferne keine Tests und schwäche keine Assertions, Berechtigungsprüfungen oder Testdatenbedingungen ab, nur um eine Änderung grün zu bekommen.
- Führe mindestens die unmittelbar betroffenen Tests aus; führe zusätzlich die passende übergeordnete Testsuite aus, wenn Umfang und Laufzeit dies zulassen.
- Prüfe bei Änderungen an Django-Modellen und Formularen auch die einschlägigen Validierungs-, View- und Berechtigungstests.
- Nenne im Abschlussbericht die tatsächlich ausgeführten Testbefehle und deren Ergebnis. Nicht ausgeführte Tests sind ausdrücklich als nicht ausgeführt zu kennzeichnen.

### 7. Regressionen und bestehende Abläufe

Bei jeder Änderung an einem vorhandenen Ablauf oder an gemeinsam genutzten Komponenten:

- Identifiziere die bestehenden Benutzerabläufe und Funktionen, die denselben Code, dieselben Modelle oder dieselben Endpunkte verwenden.
- Prüfe, ob diese Abläufe nach der Änderung weiterhin funktionieren, insbesondere Anlegen, Anzeigen, Bearbeiten, Zuordnen, Verschieben, Abschließen, Wiederöffnen, Archivieren und Löschen, soweit sie vom Änderungsbereich berührt werden.
- Prüfe bestehende Rollen- und Seriengrenzen sowie die Behandlung bereits vorhandener Daten.
- Ergänze Regressionstests für zuvor unterstützte Fälle, die durch die Änderung beeinflusst werden könnten.
- Entferne oder ändere keine bestehende Funktionalität ohne ausdrücklichen fachlichen Auftrag. Falls eine Änderung ein bisheriges Verhalten absichtlich ersetzt, müssen betroffene Folgeabläufe und Dokumentation angepasst werden.

### 8. Datenbankänderungen und Migrationen

Bei Änderungen an Modellen, Feldern, Constraints, Indizes oder Datenbankzugriffen:

- Prüfe, ob eine Migration erforderlich ist, und erstelle sie mit den vorgesehenen Django-Werkzeugen. Änderungen am Modell dürfen nicht ohne passende Migration zurückbleiben.
- Prüfe Migrationen auf Datenverlust, sichere Standardwerte, Nullbarkeit, Eindeutigkeit, Fremdschlüsselverhalten und die korrekte Reihenfolge der Abhängigkeiten.
- Stelle sicher, dass Migrationen mit dem bestehenden Datenbestand und den unterstützten Updatepfaden funktionieren; vermeide destruktive oder nicht rückwärts nachvollziehbare Datenänderungen ohne ausdrückliche fachliche Notwendigkeit.
- Prüfe Datenmigrationen auf vollständige und idempotente Verarbeitung sowie auf eine sichere Behandlung leerer, ungültiger oder historischer Datensätze.
- Führe, soweit die Umgebung es ermöglicht, mindestens `makemigrations --check` und die relevanten Migrationstests bzw. einen Migrationslauf aus. Berichte Einschränkungen ausdrücklich.

### 10. Fehlerbehandlung und Datenkonsistenz

Bei jeder Änderung an schreibenden Abläufen, Hintergrundaufgaben, Integrationen oder mehrstufigen Operationen:

- Prüfe, welche Fehler während der einzelnen Verarbeitungsschritte auftreten können und ob sie für Nutzer und Betrieb nachvollziehbar behandelt werden.
- Verhindere, dass Fehler unbemerkt verschluckt werden oder die Anwendung einen irreführenden Erfolg meldet.
- Stelle sicher, dass zusammengehörige Datenänderungen atomar erfolgen oder bei Fehlern kontrolliert zurückgerollt bzw. bereinigt werden.
- Prüfe, dass Wiederholungen nach Fehlern keine doppelten Datensätze, doppelten Zuordnungen oder widersprüchlichen Status erzeugen.
- Gib Nutzern verständliche und nicht vertrauliche Fehlermeldungen; technische Details gehören in geeignete Logs, ohne Geheimnisse oder unnötige personenbezogene Daten zu protokollieren.
- Ergänze Tests für relevante Fehlerfälle und verifiziere, dass nach einem Fehler keine inkonsistenten Teilzustände zurückbleiben.

### 13. Besprechungsreihen, Rollen und Serienberechtigungen

Bei Änderungen an Besprechungsreihen, Zuweisungen, Rollen, Teilnehmern oder reihenbezogenen Ansichten:

- Prüfe die Berechtigungsregeln für globale Administratoren, Moderator*innen, Leser*innen und sonstige Nutzer getrennt.
- Stelle sicher, dass Moderator*innen nur die Reihen verwalten können, für die sie ausdrücklich berechtigt sind, und dass Leser*innen keine Schreibrechte erhalten.
- Prüfe Auswirkungen auf alle reihenbezogenen Funktionen: Termine, Themen, Tagesordnungspunkte, Zuständigkeiten, Anlagen, Protokolle, Historie und Exporte.
- Bewahre bestehende Serienzuweisungen und Serienberechtigungen bei Anlegen, Bearbeiten, Löschen, Übertragen und erneuter Erzeugung von Terminen. Keine automatische Ausweitung oder stille Neuvergabe von Berechtigungen.
- Ergänze Tests für mindestens einen berechtigten und einen unberechtigten Nutzer je betroffenem Rollen-/Reihenzugriff sowie für bestehende Zuweisungen.

### 14. Aufbewahrung und endgültige Löschung

Bei jeder Änderung an Aufbewahrungsfristen, Archivierung, Retention-Aufgaben oder Löschroutinen:

- Ermittle und prüfe die fachlich maßgebliche Frist und ihren Startzeitpunkt. Unterscheide insbesondere die globale Organisationsfrist für Besprechungstermine und Protokolle von einer gegebenenfalls abweichenden Themenfrist.
- Prüfe Grenzfälle unmittelbar vor, am und nach dem Ablaufdatum sowie Datums-/Zeitzonenwechsel. Berechnete Löschdaten müssen reproduzierbar und konsistent sein.
- Prüfe alle betroffenen Datensätze und Speicherorte: Termine, Protokoll-Snapshots, Themen, Tagesordnungstexte, Kommentare, Audit-/Historieneinträge, Anlagenmetadaten und physische Dateien.
- Stelle sicher, dass Termine und Protokolle gemäß der globalen Organisationsfrist unabhängig von den darin enthaltenen Themen gelöscht werden.
- Stelle sicher, dass Tagesordnungstexte oder andere historische Inhalte, die laut Fachregel am Thema erhalten bleiben müssen, bei der Terminlöschung erhalten bleiben und den gelöschten Termin korrekt kennzeichnen.
- Stelle sicher, dass ein abgelaufenes archiviertes Thema einschließlich aller laut Fachregel zugehörigen Inhalte endgültig gelöscht wird und nicht über direkte URLs, Exporte oder verwaiste Dateien weiter verfügbar ist.
- Prüfe, dass die automatische Retention-Ausführung wiederholbar ist, keine nicht abgelaufenen Daten löscht und Fehler einzelner Datensätze nicht unbemerkt die gesamte Verarbeitung verfälschen.
- Ergänze Tests für Fristberechnung, Grenzfälle, abhängige Daten und die Trennung zwischen zu löschenden und zu erhaltenden Inhalten.

### 15. Besprechungsserien und Wiedervorlagen

Bei Änderungen an Serienrhythmen, Terminerzeugung, Verschiebungen, Wiedervorlagen oder Zuordnungen:

- Prüfe die Berechnung von Folgeterminen für alle unterstützten Rhythmen und insbesondere Wochen-/Monatswechsel, Jahreswechsel und Schaltjahre.
- Stelle sicher, dass Folgetermine den fachlich vorgesehenen Wochentag und Rhythmus einhalten und dass Verschiebungen die Folgekette nicht unbeabsichtigt verändern.
- Prüfe, dass wiederholte Ausführung oder erneutes Anstoßen keine doppelten Termine, Tagesordnungspunkte oder Wiedervorlageketten erzeugt.
- Stelle sicher, dass eine Wiedervorlage die korrekte Zielreihe und den korrekten Zieltermin verwendet und bestehende Berechtigungen sowie Zuständigkeiten angemessen erhält.
- Prüfe das Verhalten beim Löschen, Verschieben oder Abschließen eines Termins sowie bei bereits vorhandenen oder parallelen Zuordnungen.
- Ergänze Tests für die betroffenen Rhythmen, Grenztermine, Wiederholung und das Verhindern doppelter bzw. getrennter Wiedervorlageketten.

### 16. Audit und Änderungsverlauf

Bei Änderungen an fachlich relevanten Schreibaktionen, Rollen, Historien oder Audit-Ereignissen:

- Prüfe, ob die Aktion einen erforderlichen Audit-Eintrag erzeugt und ob dieser Akteur, Zeitpunkt, betroffenen Datensatz und die fachlich notwendigen Änderungsinformationen korrekt abbildet.
- Stelle sicher, dass Audit-Einträge nicht über normale Benutzeroberflächen oder Endpunkte unberechtigt verändert oder gelöscht werden können.
- Prüfe die Sichtbarkeit und Filterung nach Rolle und Besprechungsreihe. Nutzer dürfen keine Ereignisse außerhalb ihres Berechtigungsbereichs einsehen oder exportieren.
- Prüfe CSV- und sonstige Audit-Exporte auf dieselben Zugriffsbeschränkungen wie die Anzeige.
- Berücksichtige Lösch- und Aufbewahrungsregeln: Audit-Daten dürfen weder unbeabsichtigt zu lange personenbezogene Inhalte behalten noch entgegen der Fachregel vorzeitig gelöscht werden.
- Ergänze Tests für die Erzeugung, Unveränderbarkeit, rollenabhängige Sichtbarkeit und Exportberechtigungen der betroffenen Ereignisse.

### 18. TESTING-Modus und Beispieldaten

Bei Änderungen am TESTING-Modus, an Testdaten, Testnutzern, Fixtures oder Administrationsfunktionen:

- Prüfe, dass TESTING-Funktionen ausschließlich bei aktivem TESTING-Merkmal verfügbar sind und im normalen Produktivbetrieb weder über Navigation noch durch direkte URL-/API-Aufrufe erreichbar sind.
- Prüfe, dass Aktivieren und Deaktivieren des Modus über alle unterstützten Installations- und Updatepfade konsistent wirkt und der deaktivierte Zustand keine Testfunktionen offenlässt.
- Stelle sicher, dass Erzeugen, Zurücksetzen oder Löschen von Testdaten ausschließlich eindeutig als Testdaten gekennzeichnete Datensätze betrifft.
- Prüfe, dass Testdatenoperationen keine produktiven Besprechungsreihen, Nutzer, Termine, Themen, Tagesordnungspunkte, Anlagen oder Berechtigungen verändern oder löschen können.
- Prüfe die Behandlung wiederholter Ausführung, Teilfehler und bereits vorhandener Testdaten; es dürfen keine unkontrollierten Duplikate oder verwaisten Datensätze entstehen.
- Stelle sicher, dass Testnutzer und Testpasswörter keine produktiven Konten oder regulären Authentifizierungs-/Berechtigungsregeln unbeabsichtigt beeinflussen.
- Ergänze Tests für aktivierten und deaktivierten Modus, direkte Zugriffe ohne Berechtigung sowie die Isolation zwischen Test- und Produktivdaten.

## Verbindliche Dokumentationsprüfung bei KI-gestützten Pull Requests

**Jeder Pull Request, den ein KI-Agent für dieses Repository erstellt oder bearbeitet, muss vor Abschluss der KI-Arbeit auf Dokumentationsaktualität geprüft werden.** Diese Pflicht gilt für die Arbeit des KI-Agenten und ist keine allgemeine Vorgabe, nach der jeder von Menschen erstellte Pull Request zwingend eine Dokumentationsprüfung durchlaufen muss.

Der KI-Agent muss:

1. die aktuelle `README.md` vollständig prüfen;
2. jedes Dokument im Verzeichnis `docs/` prüfen (nicht nur die vermeintlich betroffenen Dokumente);
3. README und Dokumente mit dem tatsächlich geänderten Code, den Modellen, Migrationen, Views, Templates, Konfigurationen, Berechtigungen, Betriebsabläufen und Tests abgleichen;
4. veraltete, unvollständige oder widersprüchliche Aussagen sowie fehlende notwendige Dokumentation identifizieren;
5. erforderliche Korrekturen direkt im PR-Branch vornehmen;
6. die geänderten Dokumentationsdateien anschließend erneut gegen den Code prüfen;
7. im abschließenden Bericht zum PR ausdrücklich nennen:
   - dass `README.md` geprüft wurde;
   - welche Dateien in `docs/` geprüft wurden;
   - welche Dokumentationsdateien geändert wurden und warum;
   - ob keine Dokumentationsänderung erforderlich war, falls dies das Ergebnis der Prüfung ist.

Die Prüfung darf nicht allein deshalb entfallen, weil eine Änderung zunächst rein technisch oder intern erscheint. Auch Änderungen an Sicherheitsverhalten, Berechtigungen, Aufbewahrung, Installation, Updates, Konfiguration, Administration und Benutzerabläufen können Dokumentationsfolgen haben.

Wenn ein Dokumentationsbestand sehr umfangreich ist, darf die Prüfung schrittweise erfolgen; am Ende müssen dennoch alle Dateien in `docs/` berücksichtigt worden sein. Nicht zugängliche oder nicht lesbare Dateien sind im Abschlussbericht ausdrücklich zu nennen und dürfen nicht als geprüft ausgegeben werden.

## Abschlussbericht

Der Abschlussbericht muss die tatsächlich vorgenommenen Änderungen knapp zusammenfassen und den Status der Tests/CI-Prüfungen korrekt wiedergeben. Die oben beschriebene Dokumentationsprüfung ist darin gesondert auszuweisen. Bei jeder relevanten Codeänderung ist außerdem anzugeben, welche der einschlägigen Prüfbereiche durchgeführt wurden und welche Tests bzw. manuellen Kontrollen das Ergebnis belegen.
