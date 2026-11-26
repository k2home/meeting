# Prüfung des Verfahrens – Manuelle Testdokumentation

**Grundlage:** Branch `beta`  
**Zweck:** Vollständige manuelle Funktionsprüfung des Meeting Managers  
**Art der Dokumentation:** Ablauf- und Ergebnischeckliste mit serverlokal gespeichertem Prüfstatus, Live-Aktualisierung und Markdown-Export im TESTING-Modus

**Verwendung**

- Die Testfälle in einer geeigneten Testinstallation mit vorbereiteten Testkonten durchführen.
- Testblöcke mit **PR-Test erforderlich** sind durch die Änderungen des aktuellen Pull Requests betroffen und müssen in diesem PR erneut ausgeführt werden.
- Ein PR-Test-Marker ist kein Erfolgsnachweis. Die zugehörigen Kästchen bleiben bis zur tatsächlichen erfolgreichen Prüfung leer.
- Für jeden Testfall die einzelnen Aktionen der Reihe nach ausführen und im aktivierten TESTING-Modus die Kästchen auf der Hilfeseite abhaken. Jeder Klick wird unmittelbar in der lokalen Datei `docs/Pruefung-des-Verfahrens-Testdokumentation.md` auf dem Anwendungsserver gespeichert. Andere Nutzer derselben Installation sehen Änderungen automatisch spätestens nach zwei Sekunden. Der vollständige Prüfstand kann über **Aktuellen Test als .md herunterladen** exportiert und anschließend manuell in GitHub hochgeladen oder in den gewünschten Branch übernommen werden. Außerhalb des TESTING-Modus ist die Checkliste schreibgeschützt. Die Speicherung erfolgt weder in einer Datenbank noch automatisch in GitHub. Mehrere Serverinstallationen führen unabhängige lokale Checklisten ohne Synchronisierung.
- Am Ende jedes Testfalls den angezeigten Systemstand mit den erwarteten Ergebnissen vergleichen.
- Den Erfolgs-Haken nur setzen, wenn alle Prüfpunkte erfüllt sind. Bei Abweichungen den Test nicht als erfolgreich markieren und die Abweichung separat dokumentieren.
- Rollenprüfungen mit getrennten Konten durchführen. Eine globale Administratorrolle ersetzt keine Serienzuweisung und gewährt nicht automatisch Zugriff auf fachliche Reiheninhalte.
- Wo ein Test eine bestimmte Serienrolle voraussetzt, muss das Testkonto der betreffenden Besprechungsreihe ausdrücklich mit dieser Rolle zugewiesen sein.
- Testdaten und Testdateien verwenden. Keine produktiven Daten verändern oder löschen.

**Rollen**

- **Globale Nutzer*in:** Standardkonto ohne globale Verwaltungsrechte; fachlicher Zugriff nur auf ausdrücklich zugewiesene Reihen.
- **Admin:** Globale Benutzer-, Rollen-, Organisations- und Verwaltungsfunktionen; fachliche Reiheninhalte nur mit passender Serienzuweisung.
- **Auditor*in:** Lesender Zugriff auf administrative Prüfdaten; kein fachlicher Zugriff auf Besprechungsreihen.
- **Moderator*in:** Serienverwaltung und fachliche Moderationsfunktionen innerhalb der ausdrücklich zugewiesenen Reihe.
- **Teilnehmer*in:** Fachliche Bearbeitung innerhalb der ausdrücklich zugewiesenen Reihe, ohne Reihenverwaltung und ohne Wiederöffnung abgeschlossener Besprechungen.
- **Leser*in:** Lesender Zugriff innerhalb der ausdrücklich zugewiesenen Reihe.

**Einheitlicher Ergebnisvermerk**

Für jeden Testfall gilt: Prüfen, ob die genannten Datensätze, Statuswerte, Zuordnungen, Ansichten und Aktionen nach dem Speichern bzw. Neuladen dem erwarteten Stand entsprechen. Bei Berechtigungstests zusätzlich den direkten Aufruf der betreffenden Seite oder Aktion prüfen, nicht nur das Vorhandensein oder Fehlen einer Schaltfläche.

---

## Installation

Prüfungen zur Installation, Aktualisierung sowie Sicherung und Wiederherstellung der Anwendung.

### 16. Datenverwaltung und Sicherung

#### 16.1 Datenverwaltungsbereich aufrufen – Rolle: Admin

- [ ] **Verwaltung** öffnen.
- [ ] **Daten** öffnen.
- [ ] Verfügbare Datenverwaltungsfunktionen prüfen.
- [ ] Zur Verwaltungsübersicht zurückkehren.

**Ergebnisprüfung**
- [ ] Datenverwaltungsbereich wird angezeigt.
- [ ] Nur berechtigte Admin-Konten können die Funktionen aufrufen.
- [ ] Andere Rollen erhalten keinen Zugriff.

**Test erfolgreich:** [ ]

#### 16.2 Vollständigen Datenexport durchführen – Rolle: Admin

- [ ] Datenverwaltungsbereich öffnen.
- [ ] Funktion zum vollständigen Backup-Export aufrufen.
- [ ] Export starten.
- [ ] Exportdatei speichern.
- [ ] Datei und Ergebnisanzeige prüfen.

**Ergebnisprüfung**
- [ ] Export wird ohne Fehlermeldung abgeschlossen.
- [ ] Exportdatei ist vorhanden und im vorgesehenen Format lesbar bzw. weiterverarbeitbar.
- [ ] Export enthält keine Zugangsdaten oder Geheimnisse, die nicht Bestandteil des vorgesehenen Sicherungsformats sein dürfen.

**Test erfolgreich:** [ ]

#### 16.3 Datenimport in isolierter Testinstallation prüfen – Rolle: Admin

- [ ] Ausschließlich eine isolierte Testinstallation verwenden.
- [ ] Vorhandenen Testdatenbestand sichern.
- [ ] Datenimport öffnen.
- [ ] Geeignete Test-Sicherungsdatei auswählen.
- [ ] Import starten.
- [ ] Ergebnisanzeige prüfen.
- [ ] Betroffene Testdatenbereiche öffnen.

**Ergebnisprüfung**
- [ ] Import wird entsprechend dem vorgesehenen Format verarbeitet.
- [ ] Fehlerhafte oder ungeeignete Dateien werden nachvollziehbar abgewiesen.
- [ ] Datenbestand entspricht nach dem Import dem vorgesehenen Sicherungsstand.
- [ ] Keine produktiven Daten werden berührt.

**Test erfolgreich:** [ ]

---


### 21. Administration und Software-Updates

#### 21.1 Updatebereich aufrufen – Rolle: Admin

- [ ] Administrationsbereich für Software-Updates öffnen.
- [ ] Angezeigte Versions- und Branchinformationen prüfen.
- [ ] Verfügbare Updateinformationen aufrufen.
- [ ] Ohne Ausführung eines Updates zur Übersicht zurückkehren.

**Ergebnisprüfung**
- [ ] Updatebereich ist für Admins erreichbar.
- [ ] Versions- und Statusinformationen werden angezeigt.
- [ ] Nicht berechtigte Rollen erhalten keinen Zugriff.

**Test erfolgreich:** [ ]

#### 21.2 Update auf einer isolierten Testinstallation ausführen – Rolle: Admin bzw. Betrieb

- [ ] Vor dem Update Datenbank und Medienbestand sichern.
- [ ] Updatebereich öffnen.
- [ ] Gewünschten freigegebenen Branch auswählen.
- [ ] Update starten.
- [ ] Status und Protokoll des Updatevorgangs abwarten.
- [ ] Nach Abschluss die Anwendung neu laden.
- [ ] Anmeldung durchführen.
- [ ] Besprechungsübersicht, Themen, Protokoll und Anlagen öffnen.

**Ergebnisprüfung**
- [ ] Updatevorgang wird mit nachvollziehbarem Status beendet.
- [ ] Angezeigter Branch und Commit entsprechen der Auswahl.
- [ ] Anwendung ist erreichbar.
- [ ] Vorhandene Testdaten und Serienberechtigungen bleiben erhalten.
- [ ] Login, fachliche Ansichten und Dateizugriffe funktionieren.

**Test erfolgreich:** [ ]

---


## Ersteinrichtung

Prüfungen zur ersten Konfiguration, zu Konten, Organisation und initialen Berechtigungen.

### 1. Anmeldung und Sitzung

#### 1.1 Anmeldung mit gültigem Konto – Rolle: alle Rollen

- [ ] Anmeldeseite öffnen.
- [ ] Gültigen Benutzernamen eingeben.
- [ ] Gültiges Passwort eingeben.
- [ ] Anmelden anklicken.

**Ergebnisprüfung**
- [ ] Angemeldete Startseite wird angezeigt.
- [ ] Angezeigter Benutzer entspricht dem angemeldeten Konto.
- [ ] Navigation und verfügbare Bereiche entsprechen der Rolle und den Serienzuweisungen.

**Test erfolgreich:** [ ]

#### 1.2 Anmeldung mit ungültigen Zugangsdaten – Rolle: alle Rollen

- [ ] Anmeldeseite öffnen.
- [ ] Einen nicht vorhandenen Benutzernamen eingeben.
- [ ] Ein beliebiges Passwort eingeben.
- [ ] Anmelden anklicken.
- [ ] Den Versuch mit einem gültigen Benutzernamen und falschem Passwort wiederholen.

**Ergebnisprüfung**
- [ ] Anmeldung wird in beiden Fällen abgewiesen.
- [ ] Es wird keine geschützte Seite angezeigt.
- [ ] Die Fehlermeldung gibt nicht preis, ob ein Benutzerkonto existiert.

**Test erfolgreich:** [ ]

#### 1.3 Erzwungener Passwortwechsel – Rolle: Nutzer*in, Admin

- [ ] Mit einem Konto anmelden, für das ein Passwortwechsel erforderlich ist.
- [ ] Angezeigtes Formular zum Passwortwechsel öffnen.
- [ ] Neues Passwort eingeben.
- [ ] Neues Passwort wiederholen.
- [ ] Speichern bzw. Passwort ändern anklicken.
- [ ] Abmelden und erneut mit dem neuen Passwort anmelden.

**Ergebnisprüfung**
- [ ] Passwortwechsel wird vor dem Zugriff auf die übrige Anwendung verlangt.
- [ ] Nach erfolgreicher Änderung ist die Anmeldung mit dem neuen Passwort möglich.
- [ ] Das Konto wird nicht erneut zum Passwortwechsel aufgefordert, sofern keine neue Frist oder Rücksetzung gesetzt wurde.

**Test erfolgreich:** [ ]

#### 1.4 Abmeldung und Sitzungsschutz – Rolle: alle Rollen

- [ ] Mit einem Testkonto anmelden.
- [ ] Eine geschützte Seite öffnen.
- [ ] Abmelden anklicken.
- [ ] Die zuvor geöffnete geschützte URL erneut aufrufen.
- [ ] Im Browser zurück navigieren und die Seite neu laden.

**Ergebnisprüfung**
- [ ] Abmeldung führt zur Anmeldeseite bzw. zum nicht angemeldeten Zustand.
- [ ] Geschützte Inhalte sind nach der Abmeldung nicht erneut abrufbar.
- [ ] Eine erneute Anmeldung ist erforderlich.

**Test erfolgreich:** [ ]

#### 1.5 Passwort-Zurücksetzen über den bereitgestellten Link – Rolle: Nutzer*in, Admin

- [ ] Einen gültigen Passwort-Zurücksetzen-Link für ein Testkonto öffnen.
- [ ] Neues Passwort eingeben.
- [ ] Passwort wiederholen.
- [ ] Änderung bestätigen.
- [ ] Den Link erneut öffnen.
- [ ] Mit dem neuen Passwort anmelden.

**Ergebnisprüfung**
- [ ] Das neue Passwort wird akzeptiert.
- [ ] Ein bereits verwendeter bzw. ungültiger Link kann nicht erneut zum Zurücksetzen verwendet werden.
- [ ] Die Anmeldung mit dem neuen Passwort ist möglich.

**Test erfolgreich:** [ ]

---


### 12. Benutzerverwaltung

#### 12.1 Benutzerkonto anlegen – Rolle: Admin

- [ ] **Verwaltung** öffnen.
- [ ] **Nutzer** öffnen.
- [ ] **Neu** anklicken.
- [ ] Benutzernamen eintragen.
- [ ] Vorname und Nachname eintragen.
- [ ] E-Mail-Adresse eintragen.
- [ ] Organisationskennzeichen eintragen.
- [ ] Aktivstatus festlegen.
- [ ] Angezeigte Rollen- bzw. Kontoeinstellungen prüfen.
- [ ] Speichern anklicken.
- [ ] Benutzerübersicht neu laden.

**Ergebnisprüfung**
- [ ] Neues Konto erscheint in der Benutzerübersicht.
- [ ] Stammdaten und Aktivstatus entsprechen den Eingaben.
- [ ] Konto erhält keine unbeabsichtigten Serienberechtigungen.
- [ ] Passwortbereitstellung bzw. erforderlicher Passwortwechsel entspricht der vorgesehenen Einrichtung.

**Test erfolgreich:** [ ]

#### 12.2 Benutzerkonto bearbeiten – Rolle: Admin

- [ ] Benutzerverwaltung öffnen.
- [ ] Ein Testkonto auswählen.
- [ ] Bearbeiten öffnen.
- [ ] Name oder E-Mail-Adresse ändern.
- [ ] Organisationskennzeichen ändern.
- [ ] Aktivstatus ändern, soweit für den Test vorgesehen.
- [ ] Speichern.
- [ ] Konto erneut öffnen.

**Ergebnisprüfung**
- [ ] Geänderte Kontodaten werden korrekt angezeigt.
- [ ] Nicht geänderte Daten bleiben erhalten.
- [ ] Bestehende Serienzuweisungen bleiben erhalten, sofern sie nicht ausdrücklich geändert wurden.

**Test erfolgreich:** [ ]

#### 12.3 Benutzerkonto deaktivieren und aktivieren – Rolle: Admin

- [ ] Ein entbehrliches Testkonto auswählen.
- [ ] Aktivstatus deaktivieren.
- [ ] Speichern.
- [ ] Anmeldeversuch mit dem Testkonto durchführen.
- [ ] Konto erneut in der Benutzerverwaltung öffnen.
- [ ] Aktivstatus wieder aktivieren.
- [ ] Speichern.
- [ ] Anmeldung erneut versuchen.

**Ergebnisprüfung**
- [ ] Deaktiviertes Konto kann sich nicht anmelden.
- [ ] Reaktiviertes Konto kann sich gemäß Passwortstatus anmelden.
- [ ] Serienzuweisungen werden durch die Statusänderung nicht unbeabsichtigt gelöscht.

**Test erfolgreich:** [ ]

#### 12.4 Benutzerkonto löschen – Rolle: Admin

- [ ] Ausschließlich ein entbehrliches Testkonto auswählen.
- [ ] Löschfunktion öffnen.
- [ ] Angezeigte Folgen prüfen.
- [ ] Löschung bestätigen.
- [ ] Benutzerübersicht und betroffene Serienzuweisungen prüfen.

**Ergebnisprüfung**
- [ ] Testkonto wird entsprechend der vorgesehenen Regeln entfernt.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.
- [ ] Historische Einträge werden entsprechend der vorgesehenen Aufbewahrung behandelt.

**Test erfolgreich:** [ ]

#### 12.5 Serienzuweisungen eines Benutzers verwalten – Rolle: Admin

- [ ] Benutzerverwaltung öffnen.
- [ ] Testkonto auswählen.
- [ ] Serienzuweisungen öffnen.
- [ ] Eine Reihe zuweisen.
- [ ] Serienrolle auswählen.
- [ ] Speichern.
- [ ] Weitere Reihe mit abweichender Rolle zuweisen.
- [ ] Speichern.
- [ ] Benutzeransicht erneut öffnen.

**Ergebnisprüfung**
- [ ] Jede Zuweisung ist der richtigen Reihe zugeordnet.
- [ ] Unterschiedliche Rollen je Reihe bleiben getrennt.
- [ ] Bestehende Zuweisungen werden bei Änderungen an einer anderen Reihe nicht überschrieben.
- [ ] Ein globaler Admin erhält durch die Zuweisungsbearbeitung keine unbeabsichtigte fachliche Rolle.

**Test erfolgreich:** [ ]

#### 12.6 Passwort für Benutzer zurücksetzen – Rolle: Admin

- [ ] Benutzerverwaltung öffnen.
- [ ] Ein Testkonto auswählen.
- [ ] Passwort-Zurücksetzen-Funktion anklicken.
- [ ] Vorgang bestätigen.
- [ ] Mit dem Testkonto anmelden.
- [ ] Passwortwechsel durchführen.

**Ergebnisprüfung**
- [ ] Passwort wird gemäß dem vorgesehenen Rücksetzverfahren zurückgesetzt.
- [ ] Erforderlicher Passwortwechsel wird durchgesetzt.
- [ ] Andere Konten bleiben unverändert.

**Test erfolgreich:** [ ]

---


### 15. Organisationsverwaltung

#### 15.1 Organisationseinstellungen bearbeiten – Rolle: Admin

- [ ] **Verwaltung** öffnen.
- [ ] **Organisation** bzw. Organisationseinstellungen öffnen.
- [ ] Organisationsbezeichnung ändern.
- [ ] Kurzbezeichnung ändern.
- [ ] Zeitzone auswählen.
- [ ] Änderungen speichern.
- [ ] Seite neu laden.

**Ergebnisprüfung**
- [ ] Organisationsbezeichnung und Kurzbezeichnung werden korrekt angezeigt.
- [ ] Datums- und Uhrzeitanzeigen verwenden die eingestellte Zeitzone.
- [ ] Einstellungen bleiben nach dem Neuladen erhalten.

**Test erfolgreich:** [ ]

#### 15.2 Organisationslogo ändern – Rolle: Admin

- [ ] Organisationseinstellungen öffnen.
- [ ] Ein zulässiges Testlogo auswählen.
- [ ] Logo hochladen bzw. speichern.
- [ ] Dashboard und Protokoll-PDF öffnen.
- [ ] Falls vorgesehen, Logo entfernen bzw. durch ein anderes Testlogo ersetzen.

**Ergebnisprüfung**
- [ ] Logo wird in den vorgesehenen Bereichen angezeigt.
- [ ] Protokoll-PDF verwendet die vorgesehene Logo-Darstellung.
- [ ] Nicht unterstützte Dateien werden abgewiesen.
- [ ] Andere Organisationseinstellungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 15.3 Farben und Darstellung konfigurieren – Rolle: Admin

- [ ] Organisationseinstellungen öffnen.
- [ ] Primärfarbe ändern.
- [ ] Sekundärfarbe ändern.
- [ ] Tertiärfarbe ändern.
- [ ] Optionale Hell- und Dunkelmodus-Farbwerte ändern, sofern angeboten.
- [ ] Speichern.
- [ ] Anwendung in Hell- und Dunkelmodus neu laden.

**Ergebnisprüfung**
- [ ] Farben werden in den vorgesehenen Bereichen verwendet.
- [ ] Ungültige Farbwerte werden abgewiesen.
- [ ] Nicht gesetzte optionale Farbwerte verwenden den vorgesehenen Basiswert.
- [ ] Lesbarkeit und Bedienbarkeit bleiben erhalten.

**Test erfolgreich:** [ ]

#### 15.4 Aufbewahrungsfrist und Uploadlimit einstellen – Rolle: Admin

- [ ] Organisationseinstellungen öffnen.
- [ ] Zentrale Aufbewahrungsfrist ändern.
- [ ] Maximale Dateigröße für Anlagen ändern.
- [ ] Speichern.
- [ ] Einstellungen erneut öffnen.
- [ ] Upload mit einer Datei innerhalb und außerhalb des eingestellten Limits testen.

**Ergebnisprüfung**
- [ ] Aufbewahrungsfrist wird korrekt gespeichert und angezeigt.
- [ ] Uploadlimit wird korrekt gespeichert und durchgesetzt.
- [ ] Ungültige Werte werden abgewiesen.
- [ ] Bestehende Themen- bzw. Terminfristen werden nicht unbeabsichtigt überschrieben.

**Test erfolgreich:** [ ]

---


### 22. Rollenübergreifende Zugriffsmatrix

Die folgenden Kurzprüfungen ergänzen die fachlichen Testfälle. Sie sind mit getrennten Konten und direkten URL-Aufrufen auszuführen.

#### 22.1 Leser*in – nur lesender Zugriff in zugewiesener Reihe

- [ ] Zugewiesene Reihe öffnen.
- [ ] Termin und Protokoll öffnen.
- [ ] Thema und Tagesordnung öffnen.
- [ ] Kommentar-, Bearbeitungs-, Lösch- und Abschlussaktionen versuchen.
- [ ] Direkte schreibende URLs der Testreihe aufrufen.

**Ergebnisprüfung**
- [ ] Lesen und Protokoll-Export sind im zugewiesenen Bereich möglich.
- [ ] Fachliche Änderungen und schreibende Aktionen werden verweigert.
- [ ] Nicht zugewiesene Reihen bleiben unzugänglich.

**Test erfolgreich:** [ ]

#### 22.2 Teilnehmer*in – fachliche Bearbeitung ohne Reihenverwaltung

- [ ] Zugewiesene Reihe öffnen.
- [ ] Thema und Tagesordnung bearbeiten.
- [ ] Zuständigkeit setzen.
- [ ] Kommentar und Anlage hinzufügen.
- [ ] Wiedervorlage anlegen.
- [ ] Teilnehmerliste bearbeiten.
- [ ] Besprechung abschließen.
- [ ] Serienverwaltung und Wiederöffnung eines abgeschlossenen Termins versuchen.

**Ergebnisprüfung**
- [ ] Erlaubte fachliche Aktionen sind möglich.
- [ ] Reihenverwaltung und Wiederöffnung bleiben gesperrt.
- [ ] Andere Reihen sind nicht zugänglich.

**Test erfolgreich:** [ ]

#### 22.3 Moderator*in – Verwaltung nur der eigenen Reihe

- [ ] Eigene Reihe öffnen.
- [ ] Reihe bearbeiten.
- [ ] Termine verwalten.
- [ ] Themen archivieren und wieder öffnen.
- [ ] Abgeschlossenen Termin wieder öffnen.
- [ ] Serienmitglieder verwalten.
- [ ] Fremde Reihe direkt aufrufen.
- [ ] Eigene Moderatorzuweisung zu ändern oder zu entfernen versuchen.

**Ergebnisprüfung**
- [ ] Moderationsfunktionen sind nur in der ausdrücklich zugewiesenen Reihe verfügbar.
- [ ] Fremde Reihen bleiben unzugänglich.
- [ ] Eigene Moderatorzuweisung ist gegen unzulässige Selbständerung geschützt.

**Test erfolgreich:** [ ]

#### 22.4 Admin – globale Verwaltung ohne automatische Fachberechtigung

- [ ] Benutzerverwaltung öffnen.
- [ ] Organisationseinstellungen öffnen.
- [ ] Serienzuweisungen verwalten.
- [ ] Eine fachliche Reihe ohne eigene Serienzuweisung direkt aufrufen.
- [ ] Ein Thema dieser Reihe direkt aufrufen.
- [ ] Einen fachlichen Schreibvorgang versuchen.

**Ergebnisprüfung**
- [ ] Globale Verwaltungsfunktionen sind verfügbar.
- [ ] Fachliche Reiheninhalte bleiben ohne passende Serienzuweisung unzugänglich.
- [ ] Eine ausdrückliche Serienzuweisung ermöglicht nur die zugewiesene Rolle und Reihe.

**Test erfolgreich:** [ ]

#### 22.5 Auditor*in – ausschließlich administrative Leserechte

- [ ] Auditor*innenübersicht öffnen.
- [ ] Benutzer- und Rolleninformationen lesen.
- [ ] Organisationseinstellungen lesen.
- [ ] Systemänderungsverlauf lesen.
- [ ] Fachliche Reihe und Thema direkt aufrufen.
- [ ] Administrative Schreibaktionen versuchen.

**Ergebnisprüfung**
- [ ] Administrative Prüfdaten sind lesbar.
- [ ] Fachliche Inhalte bleiben unzugänglich.
- [ ] Schreibende Aktionen sind gesperrt.
- [ ] Geheimnisse wie Startpasswörter werden nicht angezeigt.

**Test erfolgreich:** [ ]

---


## Testing

Prüfungen der isolierten Testumgebung, Testdaten, Hilfedokumentation und des abschließenden Testlaufs.

### 19. TESTING-Modus und Beispielkonfiguration

#### 19.1 TESTING-Kennzeichnung prüfen – Rolle: Admin auf isolierter Testinstallation

- [ ] TESTING-Modus in der Testinstallation aktivieren.
- [ ] Dashboard öffnen.
- [ ] Browser-Tab bzw. Seitentitel prüfen.
- [ ] Django-Administrationspfad aufrufen.
- [ ] TESTING-Modus deaktivieren.
- [ ] Dieselben Bereiche erneut aufrufen.

**Ergebnisprüfung**
- [ ] Bei aktivem TESTING-Modus ist die Testkennzeichnung sichtbar.
- [ ] Zusätzliche Testfunktionen sind nur im aktivierten Modus verfügbar.
- [ ] Nach Deaktivierung sind die zusätzlichen Testfunktionen nicht mehr erreichbar.

**Test erfolgreich:** [ ]

#### 19.2 Testnutzer erzeugen – Rolle: globale Adminrolle im TESTING-Modus

- [ ] **Verwaltung** öffnen.
- [ ] **Beispielkonfiguration** öffnen.
- [ ] Bereich zum Erzeugen zufälliger Testnutzer aufrufen.
- [ ] Eine kleine Anzahl Testnutzer auswählen.
- [ ] Erzeugung starten.
- [ ] Benutzerübersicht öffnen.

**Ergebnisprüfung**
- [ ] Testkonten werden mit der vorgesehenen Kennzeichnung angelegt.
- [ ] Benutzernamen und E-Mail-Adressen entsprechen dem Testdatenformat.
- [ ] Passwortwechsel wird entsprechend der Testdatenregel erzwungen.
- [ ] Reguläre Benutzerkonten bleiben unverändert.

**Test erfolgreich:** [ ]

#### 19.3 Testbesprechungsreihen erzeugen – Rolle: globale Adminrolle im TESTING-Modus

- [ ] Beispielkonfiguration öffnen.
- [ ] Bereich zum Erzeugen von Testbesprechungsreihen aufrufen.
- [ ] Eine kleine Anzahl Reihen auswählen.
- [ ] Erzeugung starten.
- [ ] Serienübersicht öffnen.

**Ergebnisprüfung**
- [ ] Testreihen werden mit der vorgesehenen TEST-Kennzeichnung angelegt.
- [ ] Wiederholungsrhythmus und Wochentag sind gesetzt.
- [ ] Reguläre Besprechungsreihen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 19.4 Termine für Testreihen generieren – Rolle: globale Adminrolle im TESTING-Modus

- [ ] Beispielkonfiguration öffnen.
- [ ] Eine Testreihe auswählen.
- [ ] Funktion zum Generieren der Termine öffnen.
- [ ] Generierung starten.
- [ ] Terminübersicht der Testreihe öffnen.

**Ergebnisprüfung**
- [ ] Termine entsprechen dem Rhythmus der ausgewählten Testreihe.
- [ ] Vergangene und zukünftige Termine werden entsprechend dem Generator berücksichtigt.
- [ ] Bestehende Serienrollen werden nicht überschrieben.
- [ ] Es entstehen keine doppelten Termine.

**Test erfolgreich:** [ ]

#### 19.5 Testthemen erzeugen – Rolle: globale Adminrolle im TESTING-Modus

- [ ] Beispielkonfiguration öffnen.
- [ ] Eine Testreihe auswählen.
- [ ] Bereich zum Erzeugen von Testthemen öffnen.
- [ ] Eine kleine Anzahl Themen festlegen.
- [ ] Erzeugung starten.
- [ ] Themenübersicht der Testreihe öffnen.

**Ergebnisprüfung**
- [ ] Themen sind eindeutig als Testdaten gekennzeichnet.
- [ ] Status und Hauptzuständigkeit sind gesetzt.
- [ ] Reguläre Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 19.6 Tagesordnungspunkte und Wiedervorlagen erzeugen – Rolle: globale Adminrolle im TESTING-Modus

- [ ] Beispielkonfiguration öffnen.
- [ ] Ein Testthema auswählen.
- [ ] Bereich zum Erzeugen von Tagesordnungspunkten öffnen.
- [ ] Eine kleine Anzahl Punkte festlegen.
- [ ] Erzeugung starten.
- [ ] Zugehörige Testtermine öffnen.

**Ergebnisprüfung**
- [ ] Tagesordnungspunkte werden den vorgesehenen Terminen zugeordnet.
- [ ] Status und Zuständigkeiten sind gesetzt.
- [ ] Wiedervorlagekette ist chronologisch verknüpft.
- [ ] Reguläre Themen und Termine bleiben unverändert.

**Test erfolgreich:** [ ]

#### 19.7 Testdaten zurücksetzen – Rolle: globale Adminrolle im TESTING-Modus

- [ ] Vorhandene Testdaten in der Testinstallation prüfen.
- [ ] Funktion **TEST-Daten zurücksetzen** öffnen.
- [ ] Angezeigte Auswahl und Folgen prüfen.
- [ ] Zurücksetzen bestätigen.
- [ ] Benutzer-, Reihen-, Termin- und Themenübersichten öffnen.

**Ergebnisprüfung**
- [ ] Gekennzeichnete Testdaten werden entsprechend der Reset-Regeln entfernt.
- [ ] Reguläre Reihen, Themen und Benutzer bleiben erhalten.
- [ ] Testkonten mit regulären Verwendungen bleiben entsprechend der Schutzregeln bestehen.
- [ ] Es verbleiben keine unbeabsichtigten Testdatenreste.

**Test erfolgreich:** [ ]

---

### 20. Hilfe und Dokumentation

#### 20.1 Benutzerhilfe aufrufen – Rolle: alle Rollen – **PR-Test erforderlich (#531)**

- [ ] Menüpunkt **Hilfe** öffnen.
- [ ] Benutzerhilfe aufrufen.
- [ ] Inhaltsübersicht und Verweise prüfen.
- [ ] Zur Anwendung zurückkehren.

**Ergebnisprüfung**
- [ ] Hilfe wird ohne Fehler angezeigt.
- [ ] Verlinkte Abschnitte sind erreichbar.
- [ ] Inhalte sind lesbar und der Navigation zugeordnet.

**Test erfolgreich:** [ ]

#### 20.2 IT-Sicherheits- und Funktionsbeschreibung aufrufen – Rolle: alle Rollen gemäß Sichtbarkeit

- [ ] Bereich **Hilfe → IT, Informationssicherheit und Datenschutz** öffnen.
- [ ] Dokument in der Anwendung anzeigen.
- [ ] PDF-Version öffnen.
- [ ] PDF-Datei speichern und öffnen.

**Ergebnisprüfung**
- [ ] Dokument wird angezeigt.
- [ ] PDF lässt sich öffnen.
- [ ] Angezeigtes Dokument und PDF beziehen sich auf die vorgesehene Fassung.
- [ ] Es werden keine unberechtigten internen Daten offengelegt.

**Test erfolgreich:** [ ]

#### 20.3 Testcheckliste aus Hilfe & Anleitung öffnen – Rolle: alle angemeldeten Rollen – **PR-Test erforderlich (#531)**

- [ ] Mit einem angemeldeten Testkonto anmelden.
- [ ] **Hilfe & Anleitung** öffnen.
- [ ] Den Link **Prüfung des Verfahrens – Testcheckliste** im Inhaltsbereich anklicken.
- [ ] Prüfen, ob die Testdokumentation vollständig angezeigt wird.
- [ ] TESTING-Modus aktivieren und einen Testblock aufrufen.
- [ ] Ein Kontrollkästchen anklicken und die unmittelbare Speicherbestätigung abwarten.
- [ ] Prüfen, ob der entsprechende Marker in der lokalen Datei `docs/Pruefung-des-Verfahrens-Testdokumentation.md` auf dem Anwendungsserver geändert wurde.
- [ ] Dieselbe Checkliste in einem zweiten Browserfenster mit einem weiteren angemeldeten Nutzer öffnen.
- [ ] Im ersten Fenster einen weiteren Haken setzen und prüfen, ob das zweite Fenster spätestens nach zwei Sekunden aktualisiert wird, ohne die Seite neu zu laden.
- [ ] In beiden Fenstern gleichzeitig unterschiedliche Haken ändern und prüfen, ob beide Änderungen erhalten bleiben.
- [ ] Einen Haken wieder entfernen und prüfen, ob auch das Entfernen unmittelbar gespeichert und live übertragen wird.
- [ ] **Aktuellen Test als .md herunterladen** auswählen und die heruntergeladene vollständige Markdown-Datei öffnen.
- [ ] Prüfen, ob sämtliche gesetzten und entfernten Haken im Download enthalten sind.
- [ ] TESTING-Modus deaktivieren und Bearbeitbarkeit sowie Download erneut prüfen.
- [ ] Die Testcheckliste ohne Anmeldung direkt aufrufen.
- [ ] Über den Rücklink wieder **Hilfe & Anleitung** öffnen.

**Ergebnisprüfung**
- [ ] Der Link ist in **Hilfe & Anleitung** sichtbar und führt zur richtigen Testdokumentation.
- [ ] Die Checkliste wird vollständig und ohne Darstellungsfehler angezeigt.
- [ ] Bearbeitung und Download sind ausschließlich im TESTING-Modus verfügbar.
- [ ] Jeder Klick wird direkt in der lokalen Markdown-Datei auf dem Anwendungsserver gespeichert.
- [ ] Andere Nutzer derselben Serverinstallation sehen Änderungen spätestens nach zwei Sekunden ohne Neuladen.
- [ ] Gleichzeitige Änderungen überschreiben einander nicht unbemerkt.
- [ ] Die Datei wird atomar geschrieben und bleibt auch bei parallelen Zugriffen vollständig lesbar.
- [ ] Der Download enthält den vollständigen aktuellen Stand als `.md`-Datei.
- [ ] Die Übernahme nach GitHub erfolgt ausschließlich manuell über den heruntergeladenen Stand.
- [ ] Der Prüfstand wird nicht in der Anwendungsdatenbank gespeichert.
- [ ] Andere Serverinstallationen führen unabhängige Checklisten ohne Synchronisierung.
- [ ] Nicht angemeldete Konten erhalten keinen Zugriff.
- [ ] Rücknavigation zu **Hilfe & Anleitung** funktioniert.

**Test erfolgreich:** [ ]

---


### 23. Abschluss der Gesamtprüfung

#### 23.1 Vollständigkeit und Nachprüfung

- [ ] Alle für die Installation relevanten Testblöcke wurden durchgeführt.
- [ ] Alle Rollen wurden mit getrennten Testkonten geprüft.
- [ ] Direkte URL-Aufrufe wurden bei den Berechtigungstests berücksichtigt.
- [ ] Abweichungen wurden dokumentiert und nicht als erfolgreich abgehakt.
- [ ] Kritische Fehler wurden nach Korrektur erneut geprüft.
- [ ] Testdaten wurden nach Abschluss entsprechend den Testumgebungsregeln zurückgesetzt.

#### Ergebnis der Gesamtprüfung

- [ ] Alle durchgeführten und relevanten Testfälle erfolgreich.
- [ ] Keine offenen kritischen oder hohen Fehler.
- [ ] Abweichungen und nicht durchgeführte Tests sind separat dokumentiert.

**Prüfdatum:** ____________________  
**Geprüfte Version / Commit:** ____________________  
**Testumgebung:** ____________________  
**Prüfende Person:** ____________________  
**Offene Abweichungen / Bemerkungen:**  

____________________________________________________________________

____________________________________________________________________

____________________________________________________________________


## Produktiv

Prüfungen der regulären fachlichen Nutzung und der laufenden Verwaltungs- und Betriebsfunktionen.

### 2. Dashboard und Navigation

#### 2.1 Dashboard aufrufen – Rolle: alle Rollen

- [ ] Nach der Anmeldung das Dashboard öffnen.
- [ ] Angezeigte Kacheln und Übersichten prüfen.
- [ ] Jede für die Rolle sichtbare Kachel einmal anklicken.
- [ ] Über die Navigation zum Dashboard zurückkehren.

**Ergebnisprüfung**
- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 2.2 Navigation und Darstellungsvarianten – Rolle: alle Rollen

- [ ] Seitenmenü öffnen und schließen.
- [ ] Jede für die Rolle sichtbare Navigation aufrufen.
- [ ] Browserfenster auf eine schmale und eine breite Ansicht stellen.
- [ ] Hell- und Dunkelmodus wechseln, sofern die Auswahl angeboten wird.
- [ ] Seite neu laden.

**Ergebnisprüfung**
- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Die gewählte Darstellungsvariante bleibt entsprechend der Anwendungseinstellung erhalten.

**Test erfolgreich:** [ ]

---

### 3. Persönliches Konto und eigene Aufgaben

#### 3.1 Persönliche Kontodaten bearbeiten – Rolle: alle Rollen

- [ ] Persönliche Kontoseite über die Navigation öffnen.
- [ ] Vorname ändern.
- [ ] Nachname ändern.
- [ ] E-Mail-Adresse ändern.
- [ ] Organisationskennzeichen ändern.
- [ ] Änderungen speichern.
- [ ] Seite neu laden.

**Ergebnisprüfung**
- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 3.2 Eigene Aufgaben aufrufen – Rolle: Nutzer*in, Teilnehmer*in, Moderator*in

- [ ] Menüpunkt **Meine Aufgaben** öffnen.
- [ ] Bereich der offenen Themen prüfen.
- [ ] Bereich der Tagesordnungspunkte heutiger und zukünftiger Termine prüfen.
- [ ] Ein aufgeführtes Thema öffnen.
- [ ] Über die Navigation zu **Meine Aufgaben** zurückkehren.
- [ ] Den Test mit einem Konto ohne eigene Zuständigkeiten wiederholen.

**Ergebnisprüfung**
- [ ] Eigene offene Themen werden im vorgesehenen Abschnitt angezeigt.
- [ ] Eigene Tagesordnungspunkte werden getrennt davon angezeigt.
- [ ] Nicht zugewiesene oder nicht berechtigte Inhalte werden nicht zusätzlich eingeblendet.
- [ ] Bei fehlenden Aufgaben wird ein geeigneter Leerzustand angezeigt.

**Test erfolgreich:** [ ]

---

### 4. Besprechungsreihen verwalten

#### 4.1 Besprechungsreihe anlegen – Rolle: Admin oder Moderator*in

- [ ] **Besprechungsreihen** bzw. die Serienverwaltung öffnen.
- [ ] **+ Neu** bzw. die Schaltfläche zum Anlegen anklicken.
- [ ] Bezeichnung eintragen.
- [ ] Beschreibung eintragen.
- [ ] Wiederholungsrhythmus auswählen.
- [ ] Intervall eintragen.
- [ ] Wochentag auswählen.
- [ ] Startdatum festlegen.
- [ ] Optional ein Enddatum festlegen.
- [ ] Speichern anklicken.
- [ ] Neu angelegte Reihe öffnen.

**Ergebnisprüfung**
- [ ] Die neue Besprechungsreihe erscheint in der Übersicht.
- [ ] Bezeichnung, Beschreibung und Wiederholungseinstellungen entsprechen den Eingaben.
- [ ] Zugehörige Termine werden entsprechend Startdatum, Rhythmus, Intervall und Enddatum erzeugt.
- [ ] Die erstellende Moderatorin bzw. der erstellende Moderator besitzt die vorgesehene Serienzuweisung.
- [ ] Andere Serienzuweisungen wurden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 4.2 Besprechungsreihe bearbeiten – Rolle: Admin oder Moderator*in der Reihe

- [ ] Serienverwaltung öffnen.
- [ ] Vorhandene Reihe auswählen.
- [ ] Bearbeiten anklicken.
- [ ] Bezeichnung ändern.
- [ ] Beschreibung ändern.
- [ ] Wiederholungsrhythmus oder Intervall ändern.
- [ ] Änderungen speichern.
- [ ] Reihe erneut öffnen.

**Ergebnisprüfung**
- [ ] Geänderte Werte werden angezeigt.
- [ ] Nicht geänderte Werte bleiben erhalten.
- [ ] Bestehende Serienberechtigungen bleiben erhalten.
- [ ] Bereits vorhandene Termine und Themen sind weiterhin dem richtigen fachlichen Kontext zugeordnet.

**Test erfolgreich:** [ ]

#### 4.3 Besprechungsreihe verlängern – Rolle: Admin oder Moderator*in der Reihe

- [ ] Serienverwaltung öffnen.
- [ ] Eine Reihe mit begrenztem Enddatum auswählen.
- [ ] Funktion zum Verlängern öffnen.
- [ ] Neues Enddatum festlegen.
- [ ] Verlängerung bestätigen.
- [ ] Terminübersicht der Reihe öffnen.

**Ergebnisprüfung**
- [ ] Zusätzliche Termine werden bis zum neuen Enddatum erzeugt.
- [ ] Bereits vorhandene Termine bleiben erhalten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 4.4 Termine einer Reihe neu aufsetzen – Rolle: Admin oder Moderator*in der Reihe

- [ ] Serienverwaltung öffnen.
- [ ] Eine geeignete Testreihe auswählen.
- [ ] Funktion zum Zurücksetzen bzw. Neuaufsetzen der Termine öffnen.
- [ ] Angezeigte Auswahl und Bestätigung prüfen.
- [ ] Vorgang nur mit einer eigens dafür angelegten Testreihe bestätigen.
- [ ] Terminübersicht erneut öffnen.

**Ergebnisprüfung**
- [ ] Die Terminfolge entspricht den eingestellten Seriendaten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Bestehende Themen, Tagesordnungspunkte und Serienberechtigungen entsprechen den vorgesehenen Regeln.
- [ ] Nicht ausgewählte Reihen sind unverändert.

**Test erfolgreich:** [ ]

#### 4.5 Besprechungsreihe löschen – Rolle: Admin oder Moderator*in der Reihe

- [ ] Ausschließlich eine entbehrliche Testreihe auswählen.
- [ ] Löschfunktion öffnen.
- [ ] Angezeigte Löschvarianten prüfen.
- [ ] Löschung der Testreihe bestätigen.
- [ ] Reihenübersicht und Archiv öffnen.
- [ ] Historische Termine bzw. Protokolle prüfen.

**Ergebnisprüfung**
- [ ] Die Reihe wird nicht mehr als aktive Reihe angeboten.
- [ ] Historische Inhalte werden entsprechend der gewählten Löschvariante behandelt.
- [ ] Vorgesehene historische Lesezugriffe bleiben erhalten.
- [ ] Andere Reihen und deren Berechtigungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 4.6 Berechtigungen einer Reihe verwalten – Rolle: Admin oder Moderator*in der Reihe

- [ ] Eine Besprechungsreihe öffnen.
- [ ] Serienmitglieder bzw. Berechtigungsverwaltung öffnen.
- [ ] Ein Testkonto hinzufügen.
- [ ] Rolle **Leser*in** zuweisen.
- [ ] Speichern.
- [ ] Dasselbe Konto anschließend auf **Teilnehmer*in** ändern.
- [ ] Speichern.
- [ ] Dasselbe Konto anschließend auf **Moderator*in** ändern.
- [ ] Speichern.
- [ ] Berechtigungsübersicht erneut öffnen.

**Ergebnisprüfung**
- [ ] Das Testkonto ist der richtigen Reihe zugeordnet.
- [ ] Die jeweils ausgewählte Serienrolle wird korrekt angezeigt.
- [ ] Änderungen betreffen nur die ausgewählte Reihe.
- [ ] Die eigene Moderatorzuweisung lässt sich nicht unzulässig selbst entfernen oder herabstufen.
- [ ] Zuweisungen in anderen Reihen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 4.7 Fehlende Serienberechtigung prüfen – Rolle: Nutzer*in, Admin ohne Serienzuweisung

- [ ] Ein Konto ohne Zuweisung zu einer Testreihe anmelden.
- [ ] Reihenübersicht öffnen.
- [ ] Versuchen, die Testreihe über die Navigation aufzurufen.
- [ ] Die URL eines bekannten Termins der Testreihe direkt aufrufen.
- [ ] Eine bekannte Themen-URL der Testreihe direkt aufrufen.

**Ergebnisprüfung**
- [ ] Fachliche Inhalte der nicht zugewiesenen Reihe werden nicht offengelegt.
- [ ] Direkte URL-Aufrufe gewähren keinen unberechtigten Zugriff.
- [ ] Eine globale Adminrolle allein gewährt keinen automatischen fachlichen Reihen-Zugriff.

**Test erfolgreich:** [ ]

---

### 5. Termine und Besprechungsübersicht

#### 5.1 Terminübersicht aufrufen – Rolle: Leser*in, Teilnehmer*in, Moderator*in

- [ ] **Besprechungen** öffnen.
- [ ] Eine zugewiesene Besprechungsreihe auswählen.
- [ ] Vergangene Termine anzeigen.
- [ ] Zukünftige Termine anzeigen.
- [ ] Einen Termin öffnen.
- [ ] Zur Terminübersicht zurückkehren.

**Ergebnisprüfung**
- [ ] Termine der berechtigten Reihen werden angezeigt.
- [ ] Datum und Reihenbezeichnung stimmen.
- [ ] Vergangene und zukünftige Termine sind entsprechend gekennzeichnet bzw. erreichbar.
- [ ] Termine nicht zugewiesener Reihen werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 5.2 Einzelnen Termin verschieben – Rolle: Moderator*in der Reihe

- [ ] Terminübersicht öffnen.
- [ ] Einen noch nicht abgeschlossenen Testtermin auswählen.
- [ ] Bearbeitungsfunktion des Termins öffnen.
- [ ] Neues Datum eingeben.
- [ ] Speichern anklicken.
- [ ] Terminübersicht neu laden.

**Ergebnisprüfung**
- [ ] Der Termin wird am neuen Datum angezeigt.
- [ ] Der bisherige Termin wird nicht zusätzlich als Duplikat angezeigt.
- [ ] Zugehörige Tagesordnungspunkte und Zuständigkeiten bleiben dem Termin zugeordnet.
- [ ] Die übrigen Termine der Reihe entsprechen weiterhin dem vorgesehenen Rhythmus.

**Test erfolgreich:** [ ]

#### 5.3 Einzelnen Termin löschen – Rolle: Moderator*in der Reihe

- [ ] Einen entbehrlichen, nicht abgeschlossenen Testtermin auswählen.
- [ ] Löschfunktion öffnen.
- [ ] Angezeigte Folgen prüfen.
- [ ] Löschung bestätigen.
- [ ] Terminübersicht und betroffene Themen öffnen.

**Ergebnisprüfung**
- [ ] Der ausgewählte Termin wird entsprechend der Löschfunktion entfernt.
- [ ] Nicht ausgewählte Termine bleiben erhalten.
- [ ] Themen und historische Inhalte werden entsprechend den vorgesehenen Regeln behandelt.
- [ ] Es bleiben keine ungewollten Zuordnungen oder doppelten Einträge zurück.

**Test erfolgreich:** [ ]

#### 5.4 Teilnehmerliste bearbeiten – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Einen nicht abgeschlossenen Termin öffnen.
- [ ] Teilnehmerauswahl öffnen.
- [ ] Ein aktives Testkonto auswählen.
- [ ] Ein weiteres Testkonto abwählen.
- [ ] Änderungen speichern.
- [ ] Termin erneut öffnen.

**Ergebnisprüfung**
- [ ] Die ausgewählten Konten werden in der Teilnehmerliste angezeigt.
- [ ] Abgewählte Konten werden nicht mehr angezeigt.
- [ ] Die Änderung betrifft nur den ausgewählten Termin.
- [ ] Die Serienberechtigungen der Konten bleiben unverändert.

**Test erfolgreich:** [ ]

#### 5.5 Schreibschutz abgeschlossener Termine – Rolle: Leser*in, Teilnehmer*in

- [ ] Einen abgeschlossenen Testtermin öffnen.
- [ ] Teilnehmerliste bzw. Bearbeitungsfunktionen aufrufen.
- [ ] Eine direkte Bearbeitungs-URL bzw. Schreibaktion versuchen.
- [ ] Den Termin erneut laden.

**Ergebnisprüfung**
- [ ] Abgeschlossene Inhalte sind nicht durch Teilnehmer*innen oder Leser*innen veränderbar.
- [ ] Der gespeicherte Protokollstand bleibt unverändert.
- [ ] Die Anzeige des abgeschlossenen Termins bleibt möglich, sofern die Serienberechtigung dies erlaubt.

**Test erfolgreich:** [ ]

---

### 6. Themen anlegen und bearbeiten

#### 6.1 Thema aus dem Dashboard anlegen – Rolle: Teilnehmer*in oder Moderator*in der Zielreihe

- [ ] Dashboard öffnen.
- [ ] **Thema +Neu** bzw. den Einstieg zum Anlegen eines Themas anklicken.
- [ ] Titel eintragen.
- [ ] Hauptzuständigkeit auswählen.
- [ ] Besprechungsreihe auswählen, sofern im Formular vorgesehen.
- [ ] Zieltermin auswählen.
- [ ] Weitere angezeigte Pflicht- und Auswahlfelder ausfüllen.
- [ ] Speichern anklicken.
- [ ] Angelegtes Thema öffnen.

**Ergebnisprüfung**
- [ ] Das Thema erscheint in der Themenübersicht.
- [ ] Titel und Hauptzuständigkeit entsprechen den Eingaben.
- [ ] Das Thema ist der ausgewählten Besprechungsreihe zugeordnet.
- [ ] Für den ausgewählten Termin ist der zugehörige Tagesordnungspunkt vorhanden.
- [ ] Das Thema ist nicht versehentlich in einer anderen Reihe angelegt worden.

**Test erfolgreich:** [ ]

#### 6.2 Thema über einen Termin anlegen – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Einen nicht abgeschlossenen Termin öffnen.
- [ ] Funktion zum Hinzufügen eines Themas bzw. Tagesordnungspunkts öffnen.
- [ ] Titel des neuen Themas eingeben.
- [ ] Hauptzuständigkeit auswählen.
- [ ] Abweichende Zuständigkeit für den Tagesordnungspunkt optional auswählen.
- [ ] Speichern bzw. Hinzufügen anklicken.
- [ ] Termin und Themenansicht erneut öffnen.

**Ergebnisprüfung**
- [ ] Das neue Thema ist angelegt.
- [ ] Der Tagesordnungspunkt ist dem geöffneten Termin zugeordnet.
- [ ] Hauptzuständigkeit und abweichende Zuständigkeit werden getrennt und korrekt angezeigt.
- [ ] Das Thema ist in der Themenübersicht auffindbar.

**Test erfolgreich:** [ ]

#### 6.3 Thema bearbeiten – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Themenübersicht öffnen.
- [ ] Ein vorhandenes, nicht archiviertes Testthema auswählen.
- [ ] Bearbeiten öffnen.
- [ ] Titel ändern.
- [ ] Status ändern.
- [ ] Hauptzuständigkeit ändern.
- [ ] Änderungen speichern.
- [ ] Thema erneut öffnen.

**Ergebnisprüfung**
- [ ] Titel, Status und Hauptzuständigkeit entsprechen den gespeicherten Werten.
- [ ] Änderungen bleiben nach dem Neuladen erhalten.
- [ ] Zugehörige Tagesordnungspunkte und historische Protokollstände bleiben korrekt zugeordnet.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 6.4 Themenstatus ändern – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Ein Testthema öffnen.
- [ ] Status auf einen anderen verfügbaren Wert setzen.
- [ ] Speichern.
- [ ] Themenübersicht neu laden.
- [ ] Thema erneut öffnen.

**Ergebnisprüfung**
- [ ] Der neue Status wird in der Detailansicht angezeigt.
- [ ] Der Status wird in der Übersicht korrekt dargestellt.
- [ ] Der Status eines einzelnen Tagesordnungspunkts wird nicht unbeabsichtigt mitgeändert.

**Test erfolgreich:** [ ]

#### 6.5 Thema archivieren und wieder öffnen – Rolle: Moderator*in der Reihe

- [ ] Ein entbehrliches Testthema öffnen.
- [ ] Funktion **Archivieren** anklicken.
- [ ] Archiv öffnen.
- [ ] Archiviertes Thema auswählen.
- [ ] Funktion zum Wiederöffnen anklicken.
- [ ] Themenübersicht erneut öffnen.

**Ergebnisprüfung**
- [ ] Archivierte Themen erscheinen im Archiv und nicht mehr in der regulären offenen Themenliste.
- [ ] Wieder geöffnete Themen erscheinen wieder im vorgesehenen aktiven Bereich.
- [ ] Titel, Zuständigkeit, Kommentare und zugehörige historische Inhalte bleiben erhalten.
- [ ] Der Änderungsverlauf bildet die Aktion ab.

**Test erfolgreich:** [ ]

#### 6.6 Thema in eine andere Besprechungsreihe übertragen – Rolle: Teilnehmer*in oder Moderator*in mit den erforderlichen Rechten in Quell- und Zielreihe

- [ ] Ein übertragbares Testthema öffnen.
- [ ] Funktion zum Übertragen öffnen.
- [ ] Ziel-Besprechungsreihe auswählen.
- [ ] Zieltermin auswählen.
- [ ] Optionale Übertragungsnotiz eintragen.
- [ ] Übertragung bestätigen.
- [ ] Thema in der Zielreihe öffnen.
- [ ] Quell- und Zielreihe erneut prüfen.

**Ergebnisprüfung**
- [ ] Das Thema ist der vorgesehenen Zielreihe zugeordnet.
- [ ] Der vorgesehene Zieltermin enthält den Tagesordnungspunkt.
- [ ] Übertragungsnotiz und Übertragungsverlauf sind nachvollziehbar.
- [ ] Quell- und Zielberechtigungen werden nicht unbeabsichtigt ausgeweitet.
- [ ] Andere Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 6.7 Themenvorschläge verwenden – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Formular zum Anlegen eines Themas bzw. Tagesordnungspunkts öffnen.
- [ ] Themenvorschläge aufrufen.
- [ ] Einen Vorschlag auswählen.
- [ ] Vorgeschlagenen Titel übernehmen.
- [ ] Weitere Felder ausfüllen.
- [ ] Speichern.

**Ergebnisprüfung**
- [ ] Der ausgewählte Vorschlag wird korrekt übernommen.
- [ ] Das Thema bzw. der Tagesordnungspunkt wird mit den eingegebenen Daten angelegt.
- [ ] Es wird kein zusätzlicher oder doppelter Datensatz angelegt.

**Test erfolgreich:** [ ]

---

### 7. Tagesordnungspunkte und Wiedervorlagen

#### 7.1 Tagesordnungspunkt bearbeiten – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Einen nicht abgeschlossenen Termin öffnen.
- [ ] Einen vorhandenen Tagesordnungspunkt auswählen.
- [ ] Bearbeitungsfunktion öffnen.
- [ ] Text für diesen Termin ändern.
- [ ] Status des Tagesordnungspunkts ändern.
- [ ] Optional abweichende Zuständigkeit setzen.
- [ ] Speichern.
- [ ] Termin erneut öffnen.

**Ergebnisprüfung**
- [ ] Der terminbezogene Text wird korrekt angezeigt.
- [ ] Der Status des Tagesordnungspunkts entspricht der Auswahl.
- [ ] Eine abweichende Zuständigkeit wird korrekt angezeigt.
- [ ] Der allgemeine Themenstatus bleibt davon getrennt.

**Test erfolgreich:** [ ]

#### 7.2 Tagesordnungspunkte sortieren – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Einen Termin mit mindestens drei Tagesordnungspunkten öffnen.
- [ ] Einen Punkt per Ziehen an eine andere Position verschieben.
- [ ] Falls vorhanden, einen Punkt über die Pfeiltasten verschieben.
- [ ] Änderungen speichern bzw. Sortierung abwarten.
- [ ] Seite neu laden.

**Ergebnisprüfung**
- [ ] Die Reihenfolge entspricht der zuletzt vorgenommenen Sortierung.
- [ ] Jeder Tagesordnungspunkt ist weiterhin dem richtigen Thema zugeordnet.
- [ ] Es fehlen keine Punkte und es sind keine Duplikate entstanden.

**Test erfolgreich:** [ ]

#### 7.3 Tagesordnungspunkt entfernen – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Einen nicht abgeschlossenen Testtermin öffnen.
- [ ] Einen entbehrlichen Tagesordnungspunkt auswählen.
- [ ] Entfernen- bzw. Löschen-Funktion anklicken.
- [ ] Rückfrage bestätigen, falls vorhanden.
- [ ] Termin und zugehöriges Thema erneut öffnen.

**Ergebnisprüfung**
- [ ] Der Punkt ist aus dem ausgewählten Termin entfernt.
- [ ] Das Thema selbst bleibt entsprechend der vorgesehenen Datenregel erhalten.
- [ ] Andere Tagesordnungspunkte bleiben unverändert.

**Test erfolgreich:** [ ]

#### 7.4 Wiedervorlage anlegen – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Einen nicht abgeschlossenen Termin öffnen.
- [ ] Einen Tagesordnungspunkt mit weiterem Bearbeitungsbedarf auswählen.
- [ ] Wiedervorlage bzw. Folgetermin auswählen.
- [ ] Zieltermin festlegen.
- [ ] Abweichende Zuständigkeit bei Bedarf setzen.
- [ ] Vorgang speichern.
- [ ] Zieltermin öffnen.

**Ergebnisprüfung**
- [ ] Der Tagesordnungspunkt erscheint im vorgesehenen Zieltermin.
- [ ] Die Verbindung zum vorherigen Tagesordnungspunkt ist nachvollziehbar.
- [ ] Status und Zuständigkeit entsprechen den vorgesehenen Übernahmeregeln.
- [ ] Es ist keine doppelte Wiedervorlage entstanden.

**Test erfolgreich:** [ ]

#### 7.5 Wiedervorlage über mehrere Termine fortführen – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Eine vorhandene Wiedervorlagekette öffnen.
- [ ] Den nächsten Termin der Reihe öffnen.
- [ ] Wiedervorlage erneut für einen späteren Termin setzen.
- [ ] Speichern.
- [ ] Die vorherigen und nachfolgenden Tagesordnungspunkte öffnen.

**Ergebnisprüfung**
- [ ] Die Wiedervorlagekette ist chronologisch nachvollziehbar.
- [ ] Jeder Punkt ist dem richtigen Termin zugeordnet.
- [ ] Frühere Protokollstände bleiben unverändert.
- [ ] Es entstehen keine doppelten oder voneinander getrennten Ketten.

**Test erfolgreich:** [ ]

#### 7.6 Historische Tagesordnungseinträge aufrufen – Rolle: Leser*in, Teilnehmer*in oder Moderator*in mit historischem Lesezugriff

- [ ] Ein Thema mit historischen Tagesordnungseinträgen öffnen.
- [ ] Historie bzw. frühere Tagesordnungseinträge öffnen.
- [ ] Einen historischen Eintrag auswählen.
- [ ] Zugehörigen Termin bzw. Protokollbezug prüfen.

**Ergebnisprüfung**
- [ ] Datum, Reihenbezeichnung, Text, Status und Verantwortlichkeit werden dem historischen Eintrag entsprechend angezeigt.
- [ ] Historische Einträge lassen sich nicht unberechtigt verändern.
- [ ] Zugriff ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 8. Kommentare, Anlagen und Links

#### 8.1 Kommentar hinzufügen – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Ein Testthema öffnen.
- [ ] Kommentarbereich öffnen.
- [ ] Kommentartext eingeben.
- [ ] Kommentar absenden.
- [ ] Thema neu laden.

**Ergebnisprüfung**
- [ ] Der Kommentar wird beim richtigen Thema angezeigt.
- [ ] Autor und Erstellungszeitpunkt werden korrekt angezeigt.
- [ ] Der Kommentar bleibt nach dem Neuladen erhalten.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 8.2 Datei als Themenanlage hochladen – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Ein Testthema öffnen.
- [ ] Anlagenbereich öffnen.
- [ ] Bezeichnung der Anlage eingeben.
- [ ] Eine zulässige Testdatei auswählen.
- [ ] Upload starten.
- [ ] Thema neu laden.

**Ergebnisprüfung**
- [ ] Die Anlage wird beim richtigen Thema angezeigt.
- [ ] Bezeichnung und Datei sind korrekt zugeordnet.
- [ ] Die Datei lässt sich mit einem berechtigten Konto herunterladen.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 8.3 Netzwerkpfad oder Weblink hinterlegen – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Ein Testthema öffnen.
- [ ] Anlagenbereich öffnen.
- [ ] Bezeichnung eingeben.
- [ ] Einen zulässigen Netzwerkpfad oder Link eintragen.
- [ ] Speichern.
- [ ] Thema neu laden.
- [ ] Link bzw. Pfad anklicken, sofern als Link dargestellt.

**Ergebnisprüfung**
- [ ] Der eingetragene Pfad bzw. Link wird korrekt angezeigt.
- [ ] Unterstützte Pfade werden entsprechend der Anwendung als Link dargestellt.
- [ ] Nicht unterstützte oder ungültige Werte werden nicht als unsichere Links ausgegeben.
- [ ] Die Anwendung behauptet nicht, die Erreichbarkeit einer externen Freigabe zu garantieren.

**Test erfolgreich:** [ ]

#### 8.4 Anlage herunterladen – Rolle: Leser*in, Teilnehmer*in oder Moderator*in der Reihe

- [ ] Ein Thema mit vorhandener Testanlage öffnen.
- [ ] Download der Anlage anklicken.
- [ ] Heruntergeladene Datei öffnen bzw. Dateiname und Inhalt prüfen.
- [ ] Den Download mit einem Konto ohne Serienberechtigung wiederholen.

**Ergebnisprüfung**
- [ ] Berechtigte Konten können die zugehörige Datei herunterladen.
- [ ] Dateiinhalt und Dateiname entsprechen der hochgeladenen Datei.
- [ ] Nicht berechtigte Konten erhalten keinen Dateizugriff.

**Test erfolgreich:** [ ]

#### 8.5 Anlage löschen – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Ein Thema mit einer entbehrlichen Testanlage öffnen.
- [ ] Löschfunktion der Anlage anklicken.
- [ ] Rückfrage bestätigen, falls vorhanden.
- [ ] Thema neu laden.
- [ ] Download-URL der entfernten Anlage direkt aufrufen.

**Ergebnisprüfung**
- [ ] Die Anlage wird nicht mehr in der Themenansicht angezeigt.
- [ ] Der direkte Download der entfernten Anlage ist nicht mehr möglich.
- [ ] Andere Anlagen und Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 8.6 Upload-Grenzen prüfen – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Upload einer zulässigen Datei innerhalb des konfigurierten Größenlimits durchführen.
- [ ] Upload einer Datei oberhalb des konfigurierten Größenlimits versuchen.
- [ ] Upload einer Datei mit nicht erlaubter Dateiendung versuchen.
- [ ] Themenansicht nach den Versuchen neu laden.

**Ergebnisprüfung**
- [ ] Zulässige Dateien innerhalb des Limits werden angenommen.
- [ ] Zu große Dateien werden abgewiesen.
- [ ] Nicht erlaubte Dateiendungen werden abgewiesen.
- [ ] Abgewiesene Uploads erzeugen keine ungewollten Anlagen-Datensätze.

**Test erfolgreich:** [ ]

---

### 9. Besprechung abschließen und Protokoll

#### 9.1 Besprechung abschließen – Rolle: Teilnehmer*in oder Moderator*in der Reihe

- [ ] Einen nicht abgeschlossenen Testtermin öffnen.
- [ ] Teilnehmerliste prüfen.
- [ ] Tagesordnungstexte und Statuswerte prüfen.
- [ ] Schaltfläche **Besprechung abschließen & Protokollstand sichern** anklicken.
- [ ] Bestätigung durchführen, falls vorhanden.
- [ ] Termin erneut öffnen.

**Ergebnisprüfung**
- [ ] Der Termin ist als abgeschlossen gekennzeichnet.
- [ ] Ein Protokoll-Snapshot wurde erstellt.
- [ ] Teilnehmerliste und Tagesordnungstexte sind gegen weitere Bearbeitung gesperrt.
- [ ] Der Abschluss wird im Änderungsverlauf dokumentiert.

**Test erfolgreich:** [ ]

#### 9.2 Protokoll anzeigen – Rolle: Leser*in, Teilnehmer*in oder Moderator*in der Reihe

- [ ] Einen abgeschlossenen Termin öffnen.
- [ ] Protokollansicht aufrufen.
- [ ] Teilnehmerliste prüfen.
- [ ] Tagesordnungspunkte und Texte prüfen.
- [ ] Statuswerte und Verantwortlichkeiten prüfen.

**Ergebnisprüfung**
- [ ] Protokoll zeigt den beim Abschluss gesicherten Stand.
- [ ] Historische Werte werden nicht durch spätere Änderungen am Thema überschrieben.
- [ ] Protokoll ist für berechtigte Leser*innen sichtbar.

**Test erfolgreich:** [ ]

#### 9.3 Protokoll drucken und als PDF exportieren – Rolle: Leser*in, Teilnehmer*in oder Moderator*in der Reihe

- [ ] Protokollansicht öffnen.
- [ ] Druckfunktion auslösen.
- [ ] Druckvorschau prüfen.
- [ ] PDF-Export anklicken.
- [ ] Exportierte PDF-Datei öffnen.

**Ergebnisprüfung**
- [ ] Druckansicht enthält den richtigen Termin und Protokollstand.
- [ ] PDF lässt sich öffnen.
- [ ] PDF enthält die vorgesehenen Protokolldaten.
- [ ] Organisationsbezeichnung und Logo erscheinen entsprechend der Konfiguration.
- [ ] Unberechtigte Konten können den Export nicht abrufen.

**Test erfolgreich:** [ ]

#### 9.4 Abgeschlossene Besprechung wieder öffnen – Rolle: Moderator*in der Reihe oder Admin mit entsprechender Berechtigung

- [ ] Einen abgeschlossenen Testtermin öffnen.
- [ ] Funktion **Wieder öffnen** anklicken.
- [ ] Bestätigung durchführen, falls vorhanden.
- [ ] Termin erneut öffnen.
- [ ] Einen Tagesordnungstext testweise ändern.
- [ ] Änderung speichern.
- [ ] Besprechung erneut abschließen.

**Ergebnisprüfung**
- [ ] Der Termin ist nach dem Wiederöffnen bearbeitbar.
- [ ] Der vorherige Protokollstand bleibt als historischer Stand nachvollziehbar.
- [ ] Die erneute Bearbeitung und der erneute Abschluss funktionieren.
- [ ] Teilnehmer*innen ohne Moderatorrechte können den Termin nicht wieder öffnen.

**Test erfolgreich:** [ ]

#### 9.5 Themenprotokoll als PDF exportieren – Rolle: Leser*in, Teilnehmer*in oder Moderator*in mit Themenzugriff

- [ ] Ein Thema mit mehreren historischen Tagesordnungseinträgen öffnen.
- [ ] Themenprotokoll-PDF aufrufen.
- [ ] PDF-Datei öffnen.
- [ ] Chronologie und Einträge prüfen.

**Ergebnisprüfung**
- [ ] PDF enthält die dem Thema zugeordneten historischen Einträge.
- [ ] Datum, Reihe, Texte und Statuswerte sind korrekt.
- [ ] Der Export ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 10. Offene Themen und Archiv

#### 10.1 Offene Themen aufrufen – Rolle: Leser*in, Teilnehmer*in oder Moderator*in

- [ ] **Offene Themen** öffnen.
- [ ] Themenliste prüfen.
- [ ] Filter bzw. Suchfunktion verwenden, sofern vorhanden.
- [ ] Ein Thema öffnen.
- [ ] Zur Themenliste zurückkehren.

**Ergebnisprüfung**
- [ ] Nur fachlich zugängliche Themen werden angezeigt.
- [ ] Status, Zuständigkeit und Besprechungsreihe werden korrekt angezeigt.
- [ ] Auswahl und Filter führen zu passenden Ergebnissen.

**Test erfolgreich:** [ ]

#### 10.2 Archiv aufrufen – Rolle: Leser*in, Teilnehmer*in oder Moderator*in mit historischem Zugriff

- [ ] **Archiv** öffnen.
- [ ] Archivierte Testthemen suchen.
- [ ] Ein archiviertes Thema öffnen.
- [ ] Historische Einträge aufrufen.

**Ergebnisprüfung**
- [ ] Archivierte Themen sind im Archiv auffindbar.
- [ ] Historische Inhalte werden entsprechend der Berechtigung angezeigt.
- [ ] Nicht archivierte Themen werden nicht fälschlich als archiviert dargestellt.

**Test erfolgreich:** [ ]

#### 10.3 Zugriff auf historische Inhalte nach Reihenlöschung – Rolle: früheres Reihenmitglied

- [ ] Eine eigens dafür vorbereitete Testreihe mit mindestens einem weiteren Testkonto verwenden.
- [ ] Das Testkonto als Reihenmitglied zuweisen.
- [ ] Historischen Termin abschließen.
- [ ] Testreihe mit der vorgesehenen Löschvariante entfernen.
- [ ] Mit dem früheren Reihenmitglied anmelden.
- [ ] Historischen Termin und Protokoll aufrufen.
- [ ] Mit einem unbeteiligten Konto denselben Direktaufruf versuchen.

**Ergebnisprüfung**
- [ ] Der vorgesehene historische Lesezugriff des früheren Reihenmitglieds bleibt bestehen.
- [ ] Das unbeteiligte Konto erhält keinen Zugriff.
- [ ] Gelöschte aktive Reihenfunktionen werden nicht unbeabsichtigt wieder verfügbar.

**Test erfolgreich:** [ ]

---

### 11. Berechtigungsanträge

#### 11.1 Serienberechtigung beantragen – Rolle: Nutzer*in ohne passende Serienzuweisung

- [ ] Eine Besprechungsreihe ohne eigene Zuweisung aufrufen, soweit der Antragseinstieg angeboten wird.
- [ ] Funktion zum Beantragen einer Berechtigung öffnen.
- [ ] Gewünschte Serienrolle auswählen.
- [ ] Antrag absenden.
- [ ] Antragstatus erneut aufrufen.

**Ergebnisprüfung**
- [ ] Der Antrag wird der richtigen Person und Besprechungsreihe zugeordnet.
- [ ] Gewünschte Rolle wird korrekt angezeigt.
- [ ] Der Antrag erscheint mit offenem Status.
- [ ] Durch den Antrag allein entstehen noch keine fachlichen Schreibrechte.

**Test erfolgreich:** [ ]

#### 11.2 Berechtigungsantrag entscheiden – Rolle: Admin oder entscheidungsberechtigte Moderator*in

- [ ] Verwaltungs- bzw. Antragsübersicht öffnen.
- [ ] Offenen Testantrag auswählen.
- [ ] Antrag genehmigen oder ablehnen.
- [ ] Optional eine Entscheidungsnotiz eintragen.
- [ ] Entscheidung speichern.
- [ ] Antragsübersicht erneut öffnen.
- [ ] Mit dem betroffenen Testkonto anmelden.

**Ergebnisprüfung**
- [ ] Antrag erhält den richtigen Entscheidungsstatus.
- [ ] Entscheidende Person und Entscheidungszeitpunkt werden korrekt erfasst.
- [ ] Bei Genehmigung wird die vorgesehene Serienrolle zugewiesen.
- [ ] Bei Ablehnung wird keine neue Serienberechtigung erteilt.

**Test erfolgreich:** [ ]

#### 11.3 Bereits vorhandenen Antrag erneut bearbeiten – Rolle: Nutzer*in, Admin oder entscheidungsberechtigte Moderator*in

- [ ] Einen bereits entschiedenen Testantrag öffnen.
- [ ] Erneute Antragstellung bzw. erneute Entscheidung versuchen, sofern die Oberfläche dies anbietet.
- [ ] Status und Serienzuweisung erneut prüfen.

**Ergebnisprüfung**
- [ ] Es entstehen keine unzulässigen doppelten offenen Anträge.
- [ ] Bereits entschiedene Anträge werden nicht irrtümlich als offen behandelt.
- [ ] Die bestehende Serienzuweisung wird nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

---


### 13. Benutzer- und Themenimport/-export

#### 13.1 Benutzer als CSV exportieren – Rolle: Admin

- [ ] Benutzerverwaltung öffnen.
- [ ] CSV-Export anklicken.
- [ ] Exportdatei speichern.
- [ ] CSV-Datei öffnen.
- [ ] Spalten und Datensätze prüfen.

**Ergebnisprüfung**
- [ ] Exportdatei ist lesbar.
- [ ] Enthaltene Konten und Felder entsprechen dem vorgesehenen Exportumfang.
- [ ] Passwörter oder andere nicht exportierbare Geheimnisse sind nicht enthalten.

**Test erfolgreich:** [ ]

#### 13.2 Benutzer per CSV importieren – Rolle: Admin

- [ ] CSV-Mustervorlage herunterladen.
- [ ] Vorlage mit eindeutig gekennzeichneten Testkonten befüllen.
- [ ] CSV-Import öffnen.
- [ ] Testdatei auswählen.
- [ ] Import starten.
- [ ] Ergebnisanzeige prüfen.
- [ ] Benutzerübersicht öffnen.

**Ergebnisprüfung**
- [ ] Gültige Testkonten werden angelegt bzw. entsprechend der Importregel verarbeitet.
- [ ] Fehlerhafte Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Vorhandene Konten werden nicht ungewollt überschrieben.
- [ ] Serienzuweisungen werden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 13.3 Themen als CSV exportieren – Rolle: Admin

- [ ] Themenverwaltung bzw. Themenexport öffnen.
- [ ] CSV-Export anklicken.
- [ ] Exportdatei speichern.
- [ ] CSV-Datei öffnen.
- [ ] Datensätze und Spalten prüfen.

**Ergebnisprüfung**
- [ ] Export ist lesbar und enthält die vorgesehenen Themen.
- [ ] Zuständigkeiten, Status und Reihenbezüge sind korrekt.
- [ ] Inhalte außerhalb des zulässigen Berechtigungs- bzw. Exportumfangs werden nicht offengelegt.

**Test erfolgreich:** [ ]

#### 13.4 Themen per CSV importieren – Rolle: Admin

- [ ] CSV-Mustervorlage für Themen herunterladen.
- [ ] Vorlage mit Testthemen befüllen.
- [ ] Themen-CSV-Import öffnen.
- [ ] Testdatei auswählen.
- [ ] Import starten.
- [ ] Ergebnisanzeige prüfen.
- [ ] Themenübersicht öffnen.

**Ergebnisprüfung**
- [ ] Gültige Testthemen werden entsprechend der Importregeln angelegt bzw. verarbeitet.
- [ ] Ungültige Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Reihenbezüge und Zuständigkeiten sind korrekt.
- [ ] Es entstehen keine unbeabsichtigten Duplikate.

**Test erfolgreich:** [ ]

---

### 14. Änderungsverlauf und Audit

#### 14.1 Serienbezogenen Änderungsverlauf anzeigen – Rolle: Moderator*in der jeweiligen Reihe

- [ ] Eine moderierte Besprechungsreihe öffnen.
- [ ] Änderungsverlauf der Reihe aufrufen.
- [ ] Ein zuvor bearbeitetes Testthema auswählen.
- [ ] Ein Ereignis öffnen bzw. dessen Details prüfen.
- [ ] Mit einem Moderator-Konto einer anderen Reihe denselben Bereich aufrufen.

**Ergebnisprüfung**
- [ ] Moderator*in sieht die Ereignisse der eigenen moderierten Reihe.
- [ ] Ereignisse anderer Reihen werden nicht offengelegt.
- [ ] Akteur, Zeitpunkt und Aktion sind nachvollziehbar.
- [ ] Unberechtigte Konten erhalten keinen Zugriff.

**Test erfolgreich:** [ ]

#### 14.2 Systembezogenen Änderungsverlauf anzeigen – Rolle: Admin oder Auditor*in

- [ ] **Änderungsverlauf** bzw. Systemhistorie öffnen.
- [ ] Ein administratives Testereignis suchen.
- [ ] Filter bzw. Detailansicht verwenden, sofern vorhanden.
- [ ] Mit einem normalen Nutzerkonto denselben Bereich aufrufen.

**Ergebnisprüfung**
- [ ] Admin und Auditor*in können die vorgesehenen Systemereignisse einsehen.
- [ ] Auditor*in kann keine Änderungsaktionen ausführen.
- [ ] Normale Nutzerkonten erhalten keinen unberechtigten Systemzugriff.
- [ ] Fachliche Reihenereignisse werden nicht unberechtigt in der Systemhistorie offengelegt.

**Test erfolgreich:** [ ]

#### 14.3 Änderungsverlauf als CSV exportieren – Rolle: Admin, Auditor*in oder Moderator*in im jeweiligen Geltungsbereich

- [ ] Den für die Rolle vorgesehenen Änderungsverlauf öffnen.
- [ ] CSV-Export anklicken.
- [ ] Exportdatei speichern.
- [ ] CSV-Datei öffnen.
- [ ] Mit einem Konto außerhalb des jeweiligen Berechtigungsbereichs den Export direkt aufrufen.

**Ergebnisprüfung**
- [ ] CSV-Datei ist lesbar.
- [ ] Export enthält nur die für die Rolle zulässigen Ereignisse.
- [ ] Direkter Exportaufruf ohne passende Berechtigung wird abgewiesen.
- [ ] Nicht erforderliche vertrauliche Daten werden nicht exportiert.

**Test erfolgreich:** [ ]

---


### 17. Aufbewahrung und automatische Löschung

#### 17.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Rolle: Admin

- [ ] Eine isolierte Testreihe mit abgeschlossenen Testterminen vorbereiten.
- [ ] Zentrale Aufbewahrungsfrist für die Testinstallation festlegen.
- [ ] Einen Termin innerhalb der Frist prüfen.
- [ ] Einen Termin mit überschrittenem Löschdatum vorbereiten.
- [ ] Retention-Funktion in der Testumgebung ausführen.
- [ ] Terminübersicht und Protokollzugriffe erneut prüfen.

**Ergebnisprüfung**
- [ ] Nicht abgelaufene Termine und Protokolle bleiben erhalten.
- [ ] Abgelaufene abgeschlossene Termine und Protokolle werden gemäß der Frist entfernt.
- [ ] Tagesordnungshistorie, die laut Fachregel am Thema erhalten bleiben muss, bleibt korrekt erhalten.
- [ ] Nicht abgeschlossene bzw. wieder geöffnete Termine werden nicht unberechtigt gelöscht.

**Test erfolgreich:** [ ]

#### 17.2 Aufbewahrungsfrist archivierter Themen prüfen – Rolle: Moderator*in und Admin

- [ ] Ein entbehrliches Testthema archivieren.
- [ ] Für das Thema eine geeignete Test-Aufbewahrungsfrist festlegen.
- [ ] Thema vor Ablauf der Frist prüfen.
- [ ] Thema nach Ablauf der Frist in der isolierten Testumgebung verarbeiten lassen.
- [ ] Themenübersicht, Archiv, Historie und Anlagenzugriffe prüfen.

**Ergebnisprüfung**
- [ ] Thema bleibt vor Fristablauf erhalten.
- [ ] Abgelaufenes archiviertes Thema wird gemäß der Fachregel endgültig entfernt.
- [ ] Zugehörige Inhalte und Dateien werden entsprechend der Löschregel behandelt.
- [ ] Nicht abgelaufene oder nicht archivierte Themen bleiben erhalten.

**Test erfolgreich:** [ ]

#### 17.3 Retention wiederholt ausführen – Rolle: Admin bzw. Betrieb

- [ ] Retention-Funktion in der isolierten Testumgebung ausführen.
- [ ] Ergebnis und Datenbestand prüfen.
- [ ] Retention-Funktion erneut ausführen.
- [ ] Datenbestand erneut prüfen.

**Ergebnisprüfung**
- [ ] Wiederholte Ausführung erzeugt keine doppelten Löschvorgänge oder inkonsistenten Datensätze.
- [ ] Nicht abgelaufene Daten bleiben erhalten.
- [ ] Fehler einzelner Datensätze führen nicht zu unbemerkter Fehlbehandlung des gesamten Bestands.

**Test erfolgreich:** [ ]

---

### 18. Auditor*innenbereich

#### 18.1 Auditor*innenübersicht aufrufen – Rolle: Auditor*in

- [ ] Mit einem Auditor*innenkonto anmelden.
- [ ] Auditor*innenübersicht öffnen.
- [ ] Benutzerübersicht öffnen.
- [ ] Gruppen- bzw. Rollenübersicht öffnen.
- [ ] Organisationseinstellungen lesend öffnen.

**Ergebnisprüfung**
- [ ] Die vorgesehenen administrativen Prüfdaten sind lesbar.
- [ ] Startpasswort und andere Geheimnisse werden nicht angezeigt.
- [ ] Es bestehen keine Änderungsfunktionen für Auditor*innen.
- [ ] Fachliche Besprechungsreihen und Themeninhalte sind nicht zugänglich.

**Test erfolgreich:** [ ]

#### 18.2 Auditor*innenzugriff gegen direkte URLs prüfen – Rolle: Auditor*in

- [ ] Eine URL zur Benutzerverwaltung direkt aufrufen.
- [ ] Eine URL zur Systemhistorie direkt aufrufen.
- [ ] Eine URL zu einer fachlichen Besprechungsreihe direkt aufrufen.
- [ ] Eine URL zu einem Thema direkt aufrufen.
- [ ] Eine schreibende Verwaltungsaktion direkt aufrufen, soweit für den Test bekannt.

**Ergebnisprüfung**
- [ ] Lesender Zugriff auf ausdrücklich freigegebene administrative Prüfdaten ist möglich.
- [ ] Fachliche Inhalte sind nicht zugänglich.
- [ ] Schreibende Aktionen sind nicht möglich.
- [ ] Direkte URLs umgehen die Rollenbegrenzung nicht.

**Test erfolgreich:** [ ]

---

