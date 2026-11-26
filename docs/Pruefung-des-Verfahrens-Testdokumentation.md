# Prüfung des Verfahrens – Manuelle Testdokumentation

**Grundlage:** Branch `beta`  
**Zweck:** Vollständige manuelle Funktionsprüfung des Meeting Managers  
**Art der Dokumentation:** Ablauf- und Ergebnischeckliste mit serverlokal gespeichertem Prüfstatus, Live-Aktualisierung und Markdown-Export im TESTING-Modus

**Verwendung**

- Die Testfälle in einer geeigneten Testinstallation mit vorbereiteten Testkonten durchführen.
- Testblöcke mit **PR-Test erforderlich** sind durch die Änderungen des aktuellen Pull Requests betroffen und müssen in diesem PR erneut ausgeführt werden.
- Ein PR-Test-Marker ist kein Erfolgsnachweis. Die zugehörigen Kästchen bleiben bis zur tatsächlichen erfolgreichen Prüfung leer.
- Für jeden Testfall die einzelnen Aktionen der Reihe nach ausführen und im aktivierten TESTING-Modus die Kästchen auf der Hilfeseite abhaken. Jeder Klick wird unmittelbar in der lokalen Datei `docs/Pruefung-des-Verfahrens-Testdokumentation.md` auf dem Anwendungsserver gespeichert. Andere Nutzer derselben Installation sehen Änderungen automatisch spätestens nach 15 Sekunden. Der vollständige Prüfstand kann über **Aktuellen Test als .md herunterladen** exportiert und anschließend manuell in GitHub hochgeladen oder in den gewünschten Branch übernommen werden. Außerhalb des TESTING-Modus ist die Checkliste schreibgeschützt. Die Speicherung erfolgt weder in einer Datenbank noch automatisch in GitHub. Mehrere Serverinstallationen führen unabhängige lokale Checklisten ohne Synchronisierung.
- Am Ende jedes Testfalls den angezeigten Systemstand mit den erwarteten Ergebnissen vergleichen.
- Den Erfolgs-Haken nur setzen, wenn alle Prüfpunkte erfüllt sind. Bei Abweichungen den Test nicht als erfolgreich markieren und die Abweichung separat dokumentieren.
- Rollenprüfungen mit getrennten Konten durchführen. Eine globale Administratorrolle ersetzt keine Serienzuweisung und gewährt nicht automatisch Zugriff auf fachliche Reiheninhalte.
- Wo ein Test eine bestimmte Serienrolle voraussetzt, muss das Testkonto der betreffenden Besprechungsreihe ausdrücklich mit dieser Rolle zugewiesen sein.
- Testdaten und Testdateien verwenden. Keine produktiven Daten verändern oder löschen.

**Rollen und Berechtigungsbereiche**

Die Anwendung unterscheidet zwischen einer **globalen Benutzerrolle** und einer **Serienrolle**. Die globale Rolle gilt anwendungsweit; die Serienrolle gilt ausschließlich für die jeweils ausdrücklich zugewiesene Besprechungsreihe. Eine globale Adminrolle verleiht insbesondere **keine automatische Moderator- oder Leseberechtigung** für bestehende Reihen.

- **Globale Nutzer*in (Nutzer):** Keine globalen Verwaltungsrechte. Zugriff auf fachliche Inhalte nur über eine ausdrückliche Serienzuweisung als Teilnehmer*in, Moderator*in oder Leser*in. Ohne Serienzuweisung besteht kein Zugriff auf die betreffende Reihe.
- **Globaler Admin:** Darf Benutzerkonten, globale Rollen, Organisationseinstellungen, globale Serienzuweisungen und administrative Funktionen verwalten. Darf neue Besprechungsreihen anlegen und dabei die erste Moderatorin bzw. den ersten Moderator bestimmen sowie Berechtigungsanträge entscheiden. Ein Admin erhält dadurch **keinen automatischen Zugriff auf bestehende Reiheninhalte** und kann eine bestehende Reihe, ihre Termine oder ihre reihenbezogenen Berechtigungen nur verwalten, wenn er für genau diese Reihe zusätzlich als **Moderator*in** zugewiesen ist. Die globale Benutzerverwaltung kann Serienzuweisungen administrativ vergeben; sie ersetzt nicht die eigene Serienberechtigung des Admin-Kontos.
- **Auditor*in (globale Rolle):** Ausschließlich lesender Zugriff auf administrative Prüfdaten wie Benutzer-, Rollen- und Organisationseinstellungen sowie den systemweiten Änderungsverlauf. Kein Zugriff auf fachliche Besprechungsreihen, Termine oder Themen – auch nicht durch eine zusätzliche Serienzuweisung.
- **Moderator*in (Serienrolle):** Explizit für eine bestimmte Reihe zugewiesen. Darf diese Reihe und ihre Inhalte verwalten, Reihenparameter und Termine bearbeiten sowie die Serienrollen der Mitglieder dieser Reihe verwalten. Die Berechtigung gilt nicht automatisch für andere Reihen.
- **Teilnehmer*in (Serienrolle):** Explizit für eine bestimmte Reihe zugewiesen. Darf die fachlichen Inhalte dieser Reihe im vorgesehenen Umfang bearbeiten, hat aber keine Verwaltungsrechte für die Reihe oder deren Mitglieder.
- **Leser*in (Serienrolle):** Explizit für eine bestimmte Reihe zugewiesen. Hat dort ausschließlich lesenden Zugriff.
- **Keine automatische Vererbung:** Globale Rollen und Serienrollen sind getrennt. Insbesondere muss ein Admin, der eine Reihe fachlich verwalten, deren Inhalte sehen oder eine Besprechung wieder öffnen soll, zusätzlich als Moderator*in genau dieser Reihe zugewiesen sein.

**Einheitlicher Ergebnisvermerk**

Für jeden Testfall gilt: Prüfen, ob die genannten Datensätze, Statuswerte, Zuordnungen, Ansichten und Aktionen nach dem Speichern bzw. Neuladen dem erwarteten Stand entsprechen. Bei Berechtigungstests zusätzlich den direkten Aufruf der betreffenden Seite oder Aktion prüfen, nicht nur das Vorhandensein oder Fehlen einer Schaltfläche.

**Verbindliche Zugriffsprüfung je Funktionsbereich und Rolle**

Diese Regel gilt für **alle sieben Produktiv-Rollengruppen** – globale Nutzer*innen, Nutzer*innen ohne Berechtigung, Leser*innen, Teilnehmer*innen, Moderator*innen, globale Admins und globale Auditor*innen – und für jeden einzelnen Funktionsbereich (z. B. Serienverwaltung, Termine, Themen, Import/Export oder Auditor*innenbereich):

1. Zuerst ausschließlich den Zugang zur übergeordneten Seite des jeweiligen Funktionsbereichs prüfen. Dazu die Seite über die Navigation und – soweit sinnvoll – durch direkten URL-Aufruf aufrufen. Die Prüfung muss eindeutig feststellen, ob die Seite für diese Rolle erreichbar ist.
2. **Ist die Seite nicht erreichbar und ist die Zugriffsverweigerung nachgewiesen, ist die Prüfung dieses Funktionsbereichs für diese Rolle beendet.** Alle nachfolgenden Testfälle und Einzelfunktionen innerhalb dieses Funktionsbereichs werden für diese Rolle übersprungen. Die erfolgreiche Zugriffsverweigerung am Seitenzugang ist der dokumentierte Prüfnachweis; es werden keine zusätzlichen Versuche zum Anlegen, Bearbeiten, Löschen, Importieren oder Exportieren ausgeführt.
3. Ist die Seite erreichbar, werden die darunter aufgeführten Einzelfunktionen entsprechend den jeweiligen Berechtigungserwartungen geprüft. Auch dann können einzelne Aktionen gesperrt sein; diese konkreten Aktionsberechtigungen bleiben zu testen.
4. Die Regel gilt unabhängig davon, ob die Einschränkung aus einer globalen Rolle oder einer fehlenden bzw. abweichenden Serienrolle folgt. Bei rollenabhängigen Mischfällen (z. B. globaler Admin mit zusätzlicher Moderatorzuweisung) ist der Zugang mit genau der im Testfall beschriebenen Rollenkombination zu prüfen.

**Wichtig für die Durchführung:** Die nachfolgenden Einzelfälle eines Funktionsbereichs sind keine Aufforderung, trotz bereits nachgewiesener Seitensperre weitere Direktaufrufe oder Aktionen zu versuchen. Bei gesperrter übergeordneter Seite wird zum nächsten Funktionsbereich gewechselt.

---

## 1. Installation

Prüfungen zur Installation, Aktualisierung sowie Sicherung und Wiederherstellung der Anwendung.

### 1.1 Datenverwaltung und Sicherung

#### 1.1.1 Datenverwaltungsbereich aufrufen – Rolle: Admin

- [ ] **Verwaltung** öffnen.
- [ ] **Daten** öffnen.
- [ ] Verfügbare Datenverwaltungsfunktionen prüfen.
- [ ] Zur Verwaltungsübersicht zurückkehren.

**Ergebnisprüfung**

- [ ] Datenverwaltungsbereich wird angezeigt.
- [ ] Nur berechtigte Admin-Konten können die Funktionen aufrufen.
- [ ] Andere Rollen erhalten keinen Zugriff.

**Test erfolgreich:** [ ]

#### 1.1.2 Vollständigen Datenexport durchführen – Rolle: Admin

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

#### 1.1.3 Datenimport in isolierter Testinstallation prüfen – Rolle: Admin

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


### 1.2 Administration und Software-Updates

#### 1.2.1 Updatebereich aufrufen – Rolle: Admin

- [ ] Administrationsbereich für Software-Updates öffnen.
- [ ] Angezeigte Versions- und Branchinformationen prüfen.
- [ ] Verfügbare Updateinformationen aufrufen.
- [ ] Ohne Ausführung eines Updates zur Übersicht zurückkehren.

**Ergebnisprüfung**

- [ ] Updatebereich ist für Admins erreichbar.
- [ ] Versions- und Statusinformationen werden angezeigt.
- [ ] Nicht berechtigte Rollen erhalten keinen Zugriff.

**Test erfolgreich:** [ ]

#### 1.2.2 Update auf einer isolierten Testinstallation ausführen – Rolle: Admin bzw. Betrieb

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


## 2. Ersteinrichtung

Prüfungen zur ersten Konfiguration, zu Konten, Organisation und initialen Berechtigungen.

### 2.1 Anmeldung und Sitzung

#### 2.1.1 Anmeldung mit gültigem Konto – Rolle: alle Rollen

- [ ] Anmeldeseite öffnen.
- [ ] Gültigen Benutzernamen eingeben.
- [ ] Gültiges Passwort eingeben.
- [ ] Anmelden anklicken.

**Ergebnisprüfung**

- [ ] Angemeldete Startseite wird angezeigt.
- [ ] Angezeigter Benutzer entspricht dem angemeldeten Konto.
- [ ] Navigation und verfügbare Bereiche entsprechen der Rolle und den Serienzuweisungen.

**Test erfolgreich:** [ ]

#### 2.1.2 Anmeldung mit ungültigen Zugangsdaten – Rolle: alle Rollen

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

#### 2.1.3 Erzwungener Passwortwechsel – Rolle: Nutzer*in, Admin

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

#### 2.1.4 Abmeldung und Sitzungsschutz – Rolle: alle Rollen

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

#### 2.1.5 Passwort-Zurücksetzen über den bereitgestellten Link – Rolle: Nutzer*in, Admin

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


### 2.2 Benutzerverwaltung

#### 2.2.1 Benutzerkonto anlegen – Rolle: Admin

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

#### 2.2.2 Benutzerkonto bearbeiten – Rolle: Admin

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

#### 2.2.3 Benutzerkonto deaktivieren und aktivieren – Rolle: Admin

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

#### 2.2.4 Benutzerkonto löschen – Rolle: Admin

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

#### 2.2.5 Serienzuweisungen eines Benutzers verwalten – Rolle: Admin

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

#### 2.2.6 Passwort für Benutzer zurücksetzen – Rolle: Admin

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


### 2.3 Organisationsverwaltung

#### 2.3.1 Organisationseinstellungen bearbeiten – Rolle: Admin

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

#### 2.3.2 Organisationslogo ändern – Rolle: Admin

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

#### 2.3.3 Farben und Darstellung konfigurieren – Rolle: Admin

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

#### 2.3.4 Aufbewahrungsfrist und Uploadlimit einstellen – Rolle: Admin

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


### 2.4 Rollenübergreifende Zugriffsmatrix

Die folgenden Kurzprüfungen ergänzen die fachlichen Testfälle. Sie sind mit getrennten Konten und direkten URL-Aufrufen auszuführen.

#### 2.4.1 Leser*in – nur lesender Zugriff in zugewiesener Reihe

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

#### 2.4.2 Teilnehmer*in – fachliche Bearbeitung ohne Reihenverwaltung

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

#### 2.4.3 Moderator*in – Verwaltung nur der eigenen Reihe

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

#### 2.4.4 Admin – globale Verwaltung ohne automatische Fachberechtigung

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

#### 2.4.5 Auditor*in – ausschließlich administrative Leserechte

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


## 3. Testing

Prüfungen der isolierten Testumgebung, Testdaten, Hilfedokumentation und des abschließenden Testlaufs.

### 3.1 TESTING-Modus und Beispielkonfiguration

#### 3.1.1 TESTING-Kennzeichnung prüfen – Rolle: Admin auf isolierter Testinstallation

- [ ] TESTING-Modus in der Testinstallation aktivieren.- [ ] Dashboard öffnen.- [ ] Browser-Tab bzw. Seitentitel prüfen.- [ ] Django-Administrationspfad aufrufen.
- [ ] TESTING-Modus deaktivieren.
- [ ] Dieselben Bereiche erneut aufrufen.

**Ergebnisprüfung**

- [ ] Bei aktivem TESTING-Modus ist die Testkennzeichnung sichtbar.
- [ ] Zusätzliche Testfunktionen sind nur im aktivierten Modus verfügbar.
- [ ] Nach Deaktivierung sind die zusätzlichen Testfunktionen nicht mehr erreichbar.

**Test erfolgreich:** [ ]

#### 3.1.2 Testnutzer erzeugen – Rolle: globale Adminrolle im TESTING-Modus

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

#### 3.1.3 Testbesprechungsreihen erzeugen – Rolle: globale Adminrolle im TESTING-Modus

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

#### 3.1.4 Termine für Testreihen generieren – Rolle: globale Adminrolle im TESTING-Modus

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

#### 3.1.5 Testthemen erzeugen – Rolle: globale Adminrolle im TESTING-Modus

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

#### 3.1.6 Tagesordnungspunkte und Wiedervorlagen erzeugen – Rolle: globale Adminrolle im TESTING-Modus

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

#### 3.1.7 Testdaten zurücksetzen – Rolle: globale Adminrolle im TESTING-Modus

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

### 3.2 Hilfe und Dokumentation

#### 3.2.1 Benutzerhilfe aufrufen – Rolle: alle Rollen – **PR-Test erforderlich (#531)**

- [ ] Menüpunkt **Hilfe** öffnen.
- [ ] Benutzerhilfe aufrufen.
- [ ] Inhaltsübersicht und Verweise prüfen.
- [ ] Zur Anwendung zurückkehren.

**Ergebnisprüfung**

- [ ] Hilfe wird ohne Fehler angezeigt.
- [ ] Verlinkte Abschnitte sind erreichbar.
- [ ] Inhalte sind lesbar und der Navigation zugeordnet.

**Test erfolgreich:** [ ]

#### 3.2.2 IT-Sicherheits- und Funktionsbeschreibung aufrufen – Rolle: alle Rollen gemäß Sichtbarkeit

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

#### 3.2.3 Testcheckliste aus Hilfe & Anleitung öffnen – Rolle: alle angemeldeten Rollen – **PR-Test erforderlich (#531)**

- [ ] Mit einem angemeldeten Testkonto anmelden.
- [ ] **Hilfe & Anleitung** öffnen.
- [ ] Den Link **Prüfung des Verfahrens – Testcheckliste** im Inhaltsbereich anklicken.
- [ ] Prüfen, ob die Testdokumentation vollständig angezeigt wird.
- [ ] TESTING-Modus aktivieren und einen Testblock aufrufen.
- [ ] Ein Kontrollkästchen anklicken und die unmittelbare Speicherbestätigung abwarten.
- [ ] Prüfen, ob der entsprechende Marker in der lokalen Datei `docs/Pruefung-des-Verfahrens-Testdokumentation.md` auf dem Anwendungsserver geändert wurde.
- [ ] Dieselbe Checkliste in einem zweiten Browserfenster mit einem weiteren angemeldeten Nutzer öffnen.
- [ ] Im ersten Fenster einen weiteren Haken setzen und prüfen, ob das zweite Fenster spätestens nach 15 Sekunden aktualisiert wird, ohne die Seite neu zu laden.
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
- [ ] Andere Nutzer derselben Serverinstallation sehen Änderungen spätestens nach 15 Sekunden ohne Neuladen.
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


### 3.3 Abschluss der Gesamtprüfung

#### 3.3.1 Vollständigkeit und Nachprüfung

- [ ] Alle für die Installation relevanten Testblöcke wurden durchgeführt.
- [ ] Alle Rollen wurden mit getrennten Testkonten geprüft.
- [ ] Direkte URL-Aufrufe wurden bei den Berechtigungstests berücksichtigt.
- [ ] Abweichungen wurden dokumentiert und nicht als erfolgreich abgehakt.
- [ ] Kritische Fehler wurden nach Korrektur erneut geprüft.
- [ ] Testdaten wurden nach Abschluss entsprechend den Testumgebungsregeln zurückgesetzt.

#### 3.3.2 Ergebnis der Gesamtprüfung

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


## 4. Produktiv – Globale Rolle Nutzer

Ein normales Benutzerkonto ohne globale Admin- oder Auditorrolle verwenden. Für reine Funktionsprüfungen zusätzlich die in der jeweiligen Testbeschreibung ausdrücklich genannte Serienrolle zuweisen; globale Nutzerrechte allein verleihen keinen Serienzugriff.

**Verbindliche Durchführung für diese Rollengruppe**

- Alle folgenden Funktionsbereiche und Testfälle sind aus Sicht dieses Kontos durchzuführen.
- Bei erlaubten Aktionen muss die Funktion vollständig und mit korrektem Ergebnis funktionieren.
- Bei nicht erlaubten Aktionen den Aufruf über Navigation, direkte URL und – soweit möglich – direkte POST-Anfrage versuchen. Erwartet wird eine verweigerte Antwort (403/404 oder vorgesehene Umleitung), keine Datenänderung und keine Offenlegung geschützter Inhalte.
- Die nachfolgende Einzelprüfung nennt jeweils, ob die Rolle laut Berechtigungsmodell zugriffsberechtigt ist. Bei Serienfunktionen gilt die Berechtigung ausschließlich für die konkret zugewiesene Reihe.

### 4.1 Dashboard und Navigation

#### 4.1.1 Dashboard aufrufen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 4.1.2 Navigation und Darstellungsvarianten – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Die gewählte Darstellungsvariante bleibt entsprechend der Anwendungseinstellung erhalten.

**Test erfolgreich:** [ ]

---

### 4.2 Persönliches Konto und eigene Aufgaben

#### 4.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 4.2.2 Eigene Aufgaben aufrufen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Eigene offene Themen werden im vorgesehenen Abschnitt angezeigt.
- [ ] Eigene Tagesordnungspunkte werden getrennt davon angezeigt.
- [ ] Nicht zugewiesene oder nicht berechtigte Inhalte werden nicht zusätzlich eingeblendet.
- [ ] Bei fehlenden Aufgaben wird ein geeigneter Leerzustand angezeigt.

**Test erfolgreich:** [ ]

---

### 4.3 Besprechungsreihen verwalten

#### 4.3.1 Besprechungsreihe anlegen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die neue Besprechungsreihe erscheint in der Übersicht.
- [ ] Bezeichnung, Beschreibung und Wiederholungseinstellungen entsprechen den Eingaben.
- [ ] Zugehörige Termine werden entsprechend Startdatum, Rhythmus, Intervall und Enddatum erzeugt.
- [ ] Die erstellende Moderatorin bzw. der erstellende Moderator besitzt die vorgesehene Serienzuweisung.
- [ ] Andere Serienzuweisungen wurden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 4.3.2 Besprechungsreihe bearbeiten – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Geänderte Werte werden angezeigt.
- [ ] Nicht geänderte Werte bleiben erhalten.
- [ ] Bestehende Serienberechtigungen bleiben erhalten.
- [ ] Bereits vorhandene Termine und Themen sind weiterhin dem richtigen fachlichen Kontext zugeordnet.

**Test erfolgreich:** [ ]

#### 4.3.3 Besprechungsreihe verlängern – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Zusätzliche Termine werden bis zum neuen Enddatum erzeugt.
- [ ] Bereits vorhandene Termine bleiben erhalten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 4.3.4 Termine einer Reihe neu aufsetzen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Terminfolge entspricht den eingestellten Seriendaten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Bestehende Themen, Tagesordnungspunkte und Serienberechtigungen entsprechen den vorgesehenen Regeln.
- [ ] Nicht ausgewählte Reihen sind unverändert.

**Test erfolgreich:** [ ]

#### 4.3.5 Besprechungsreihe löschen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Reihe wird nicht mehr als aktive Reihe angeboten.
- [ ] Historische Inhalte werden entsprechend der gewählten Löschvariante behandelt.
- [ ] Vorgesehene historische Lesezugriffe bleiben erhalten.
- [ ] Andere Reihen und deren Berechtigungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 4.3.6 Berechtigungen einer Reihe verwalten – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Das Testkonto ist der richtigen Reihe zugeordnet.
- [ ] Die jeweils ausgewählte Serienrolle wird korrekt angezeigt.
- [ ] Änderungen betreffen nur die ausgewählte Reihe.
- [ ] Die eigene Moderatorzuweisung lässt sich nicht unzulässig selbst entfernen oder herabstufen.
- [ ] Zuweisungen in anderen Reihen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 4.3.7 Fehlende Serienberechtigung prüfen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Fachliche Inhalte der nicht zugewiesenen Reihe werden nicht offengelegt.
- [ ] Direkte URL-Aufrufe zu Terminen und Themen gewähren keinen unberechtigten Zugriff.
- [ ] Die globale Adminrolle und eine Moderatorzuweisung in einer anderen Reihe gewähren keine Rechte für die geprüfte Testreihe.
- [ ] Reihenbearbeitung und Verwaltung der Serienmitglieder werden ohne Moderatorzuweisung für genau diese Reihe verweigert.
- [ ] Die zugewiesene andere Testreihe bleibt für das Admin-Konto gemäß seiner dortigen Moderatorrolle erreichbar.

**Test erfolgreich:** [ ]

---

#### 4.3.8 Globaler Admin mit zusätzlicher Moderatorzuweisung – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

- [ ] Ein globales Admin-Konto verwenden und es für Testreihe A ausdrücklich als Moderator zuweisen.
- [ ] Für Testreihe B keine Serienzuweisung für dieses Konto vergeben.
- [ ] Testreihe A über die Serienverwaltung öffnen und eine zulässige Verwaltungsaktion ausführen.
- [ ] Dieselbe Verwaltungsseite für Testreihe B über die direkte URL aufrufen.
- [ ] Prüfen, ob die globale Adminrolle ohne Serienzuweisung den Zugriff auf Testreihe B erweitert.

**Ergebnisprüfung**

- [ ] In Testreihe A ist die Moderatorverwaltung aufgrund der ausdrücklichen Serienzuweisung möglich.
- [ ] In Testreihe B wird der Zugriff verweigert.
- [ ] Die globale Adminrolle erweitert die Moderatorberechtigung nicht auf andere Reihen.
- [ ] Änderungen an Testreihe A verändern die Berechtigungen von Testreihe B nicht.

**Test erfolgreich:** [ ]

#### 4.3.9 Moderatorzugriff auf eine fremde Reihe verweigern – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff auf die eigene Reihe erlaubt, auf fremde Reihen verweigert.** Mit dem Testkonto muss die eigene zugewiesene Reihe verwaltbar sein. Für die fremde Reihe müssen Navigation, direkte URLs und schreibende Aktionen gesperrt bleiben; Daten und Berechtigungen bleiben unverändert.

- [ ] Ein Moderator-Konto für Testreihe A verwenden.
- [ ] Sicherstellen, dass für Testreihe B keine Zuweisung besteht.
- [ ] Testreihe A über die Serienverwaltung öffnen.
- [ ] Die Verwaltungsübersicht und Bearbeitungsseite von Testreihe B über direkte URLs aufrufen.
- [ ] Eine schreibende Aktion für Testreihe B über die direkte URL bzw. POST-Anfrage versuchen.

**Ergebnisprüfung**

- [ ] Testreihe A kann verwaltet werden.
- [ ] Testreihe B ist weder über die Navigation noch über direkte URLs erreichbar.
- [ ] Schreibende Aktionen für Testreihe B werden verweigert.
- [ ] Daten und Berechtigungen von Testreihe B bleiben unverändert.

**Test erfolgreich:** [ ]

### 4.4 Termine und Besprechungsübersicht

#### 4.4.1 Terminübersicht aufrufen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Termine der berechtigten Reihen werden angezeigt.
- [ ] Datum und Reihenbezeichnung stimmen.
- [ ] Vergangene und zukünftige Termine sind entsprechend gekennzeichnet bzw. erreichbar.
- [ ] Termine nicht zugewiesener Reihen werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 4.4.2 Einzelnen Termin verschieben – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Termin wird am neuen Datum angezeigt.
- [ ] Der bisherige Termin wird nicht zusätzlich als Duplikat angezeigt.
- [ ] Zugehörige Tagesordnungspunkte und Zuständigkeiten bleiben dem Termin zugeordnet.
- [ ] Die übrigen Termine der Reihe entsprechen weiterhin dem vorgesehenen Rhythmus.

**Test erfolgreich:** [ ]

#### 4.4.3 Einzelnen Termin löschen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der ausgewählte Termin wird entsprechend der Löschfunktion entfernt.
- [ ] Nicht ausgewählte Termine bleiben erhalten.
- [ ] Themen und historische Inhalte werden entsprechend den vorgesehenen Regeln behandelt.
- [ ] Es bleiben keine ungewollten Zuordnungen oder doppelten Einträge zurück.

**Test erfolgreich:** [ ]

#### 4.4.4 Teilnehmerliste bearbeiten – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die ausgewählten Konten werden in der Teilnehmerliste angezeigt.
- [ ] Abgewählte Konten werden nicht mehr angezeigt.
- [ ] Die Änderung betrifft nur den ausgewählten Termin.
- [ ] Die Serienberechtigungen der Konten bleiben unverändert.

**Test erfolgreich:** [ ]

#### 4.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**- [ ] Abgeschlossene Inhalte sind nicht durch Teilnehmer*innen oder Leser*innen veränderbar.
- [ ] Der gespeicherte Protokollstand bleibt unverändert.- [ ] Die Anzeige des abgeschlossenen Termins bleibt möglich, sofern die Serienberechtigung dies erlaubt.
**Test erfolgreich:** [ ]

---

### 4.5 Themen anlegen und bearbeiten

#### 4.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Das Thema erscheint in der Themenübersicht.
- [ ] Titel und Hauptzuständigkeit entsprechen den Eingaben.
- [ ] Das Thema ist der ausgewählten Besprechungsreihe zugeordnet.
- [ ] Für den ausgewählten Termin ist der zugehörige Tagesordnungspunkt vorhanden.
- [ ] Das Thema ist nicht versehentlich in einer anderen Reihe angelegt worden.

**Test erfolgreich:** [ ]

#### 4.5.2 Thema über einen Termin anlegen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Das neue Thema ist angelegt.
- [ ] Der Tagesordnungspunkt ist dem geöffneten Termin zugeordnet.
- [ ] Hauptzuständigkeit und abweichende Zuständigkeit werden getrennt und korrekt angezeigt.
- [ ] Das Thema ist in der Themenübersicht auffindbar.

**Test erfolgreich:** [ ]

#### 4.5.3 Thema bearbeiten – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Titel, Status und Hauptzuständigkeit entsprechen den gespeicherten Werten.
- [ ] Änderungen bleiben nach dem Neuladen erhalten.
- [ ] Zugehörige Tagesordnungspunkte und historische Protokollstände bleiben korrekt zugeordnet.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 4.5.4 Themenstatus ändern – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der neue Status wird in der Detailansicht angezeigt.
- [ ] Der Status wird in der Übersicht korrekt dargestellt.
- [ ] Der Status eines einzelnen Tagesordnungspunkts wird nicht unbeabsichtigt mitgeändert.

**Test erfolgreich:** [ ]

#### 4.5.5 Thema archivieren und wieder öffnen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Archivierte Themen erscheinen im Archiv und nicht mehr in der regulären offenen Themenliste.
- [ ] Wieder geöffnete Themen erscheinen wieder im vorgesehenen aktiven Bereich.
- [ ] Titel, Zuständigkeit, Kommentare und zugehörige historische Inhalte bleiben erhalten.
- [ ] Der Änderungsverlauf bildet die Aktion ab.

**Test erfolgreich:** [ ]

#### 4.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Das Thema ist der vorgesehenen Zielreihe zugeordnet.
- [ ] Der vorgesehene Zieltermin enthält den Tagesordnungspunkt.
- [ ] Übertragungsnotiz und Übertragungsverlauf sind nachvollziehbar.
- [ ] Quell- und Zielberechtigungen werden nicht unbeabsichtigt ausgeweitet.
- [ ] Andere Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 4.5.7 Themenvorschläge verwenden – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der ausgewählte Vorschlag wird korrekt übernommen.
- [ ] Das Thema bzw. der Tagesordnungspunkt wird mit den eingegebenen Daten angelegt.
- [ ] Es wird kein zusätzlicher oder doppelter Datensatz angelegt.

**Test erfolgreich:** [ ]

---

### 4.6 Tagesordnungspunkte und Wiedervorlagen

#### 4.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der terminbezogene Text wird korrekt angezeigt.
- [ ] Der Status des Tagesordnungspunkts entspricht der Auswahl.
- [ ] Eine abweichende Zuständigkeit wird korrekt angezeigt.
- [ ] Der allgemeine Themenstatus bleibt davon getrennt.

**Test erfolgreich:** [ ]

#### 4.6.2 Tagesordnungspunkte sortieren – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Reihenfolge entspricht der zuletzt vorgenommenen Sortierung.
- [ ] Jeder Tagesordnungspunkt ist weiterhin dem richtigen Thema zugeordnet.
- [ ] Es fehlen keine Punkte und es sind keine Duplikate entstanden.

**Test erfolgreich:** [ ]

#### 4.6.3 Tagesordnungspunkt entfernen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Punkt ist aus dem ausgewählten Termin entfernt.
- [ ] Das Thema selbst bleibt entsprechend der vorgesehenen Datenregel erhalten.
- [ ] Andere Tagesordnungspunkte bleiben unverändert.

**Test erfolgreich:** [ ]

#### 4.6.4 Wiedervorlage anlegen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Tagesordnungspunkt erscheint im vorgesehenen Zieltermin.
- [ ] Die Verbindung zum vorherigen Tagesordnungspunkt ist nachvollziehbar.
- [ ] Status und Zuständigkeit entsprechen den vorgesehenen Übernahmeregeln.
- [ ] Es ist keine doppelte Wiedervorlage entstanden.

**Test erfolgreich:** [ ]

#### 4.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Wiedervorlagekette ist chronologisch nachvollziehbar.
- [ ] Jeder Punkt ist dem richtigen Termin zugeordnet.
- [ ] Frühere Protokollstände bleiben unverändert.
- [ ] Es entstehen keine doppelten oder voneinander getrennten Ketten.

**Test erfolgreich:** [ ]

#### 4.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Datum, Reihenbezeichnung, Text, Status und Verantwortlichkeit werden dem historischen Eintrag entsprechend angezeigt.
- [ ] Historische Einträge lassen sich nicht unberechtigt verändern.
- [ ] Zugriff ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 4.7 Kommentare, Anlagen und Links

#### 4.7.1 Kommentar hinzufügen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Kommentar wird beim richtigen Thema angezeigt.
- [ ] Autor und Erstellungszeitpunkt werden korrekt angezeigt.
- [ ] Der Kommentar bleibt nach dem Neuladen erhalten.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 4.7.2 Datei als Themenanlage hochladen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Anlage wird beim richtigen Thema angezeigt.
- [ ] Bezeichnung und Datei sind korrekt zugeordnet.
- [ ] Die Datei lässt sich mit einem berechtigten Konto herunterladen.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 4.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der eingetragene Pfad bzw. Link wird korrekt angezeigt.
- [ ] Unterstützte Pfade werden entsprechend der Anwendung als Link dargestellt.
- [ ] Nicht unterstützte oder ungültige Werte werden nicht als unsichere Links ausgegeben.
- [ ] Die Anwendung behauptet nicht, die Erreichbarkeit einer externen Freigabe zu garantieren.

**Test erfolgreich:** [ ]

#### 4.7.4 Anlage herunterladen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Berechtigte Konten können die zugehörige Datei herunterladen.
- [ ] Dateiinhalt und Dateiname entsprechen der hochgeladenen Datei.
- [ ] Nicht berechtigte Konten erhalten keinen Dateizugriff.

**Test erfolgreich:** [ ]

#### 4.7.5 Anlage löschen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Anlage wird nicht mehr in der Themenansicht angezeigt.
- [ ] Der direkte Download der entfernten Anlage ist nicht mehr möglich.
- [ ] Andere Anlagen und Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 4.7.6 Upload-Grenzen prüfen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Zulässige Dateien innerhalb des Limits werden angenommen.
- [ ] Zu große Dateien werden abgewiesen.
- [ ] Nicht erlaubte Dateiendungen werden abgewiesen.
- [ ] Abgewiesene Uploads erzeugen keine ungewollten Anlagen-Datensätze.

**Test erfolgreich:** [ ]

---

### 4.8 Besprechung abschließen und Protokoll

#### 4.8.1 Besprechung abschließen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Termin ist als abgeschlossen gekennzeichnet.
- [ ] Ein Protokoll-Snapshot wurde erstellt.
- [ ] Teilnehmerliste und Tagesordnungstexte sind gegen weitere Bearbeitung gesperrt.
- [ ] Der Abschluss wird im Änderungsverlauf dokumentiert.

**Test erfolgreich:** [ ]

#### 4.8.2 Protokoll anzeigen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Protokoll zeigt den beim Abschluss gesicherten Stand.
- [ ] Historische Werte werden nicht durch spätere Änderungen am Thema überschrieben.
- [ ] Protokoll ist für berechtigte Leser*innen sichtbar.

**Test erfolgreich:** [ ]

#### 4.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Druckansicht enthält den richtigen Termin und Protokollstand.
- [ ] PDF lässt sich öffnen.
- [ ] PDF enthält die vorgesehenen Protokolldaten.
- [ ] Organisationsbezeichnung und Logo erscheinen entsprechend der Konfiguration.
- [ ] Unberechtigte Konten können den Export nicht abrufen.

**Test erfolgreich:** [ ]

#### 4.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Termin ist nach dem Wiederöffnen bearbeitbar.
- [ ] Der vorherige Protokollstand bleibt als historischer Stand nachvollziehbar.
- [ ] Die erneute Bearbeitung und der erneute Abschluss funktionieren.
- [ ] Teilnehmer*innen ohne Moderatorrechte können den Termin nicht wieder öffnen.

**Test erfolgreich:** [ ]

#### 4.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] PDF enthält die dem Thema zugeordneten historischen Einträge.
- [ ] Datum, Reihe, Texte und Statuswerte sind korrekt.
- [ ] Der Export ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 4.9 Offene Themen und Archiv

#### 4.9.1 Offene Themen aufrufen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Nur fachlich zugängliche Themen werden angezeigt.
- [ ] Status, Zuständigkeit und Besprechungsreihe werden korrekt angezeigt.
- [ ] Auswahl und Filter führen zu passenden Ergebnissen.

**Test erfolgreich:** [ ]

#### 4.9.2 Archiv aufrufen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Archivierte Themen sind im Archiv auffindbar.
- [ ] Historische Inhalte werden entsprechend der Berechtigung angezeigt.
- [ ] Nicht archivierte Themen werden nicht fälschlich als archiviert dargestellt.

**Test erfolgreich:** [ ]

#### 4.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der vorgesehene historische Lesezugriff des früheren Reihenmitglieds bleibt bestehen.
- [ ] Das unbeteiligte Konto erhält keinen Zugriff.
- [ ] Gelöschte aktive Reihenfunktionen werden nicht unbeabsichtigt wieder verfügbar.

**Test erfolgreich:** [ ]

---

### 4.10 Berechtigungsanträge

#### 4.10.1 Serienberechtigung beantragen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Antrag wird der richtigen Person und Besprechungsreihe zugeordnet.
- [ ] Gewünschte Rolle wird korrekt angezeigt.
- [ ] Der Antrag erscheint mit offenem Status.
- [ ] Durch den Antrag allein entstehen noch keine fachlichen Schreibrechte.

**Test erfolgreich:** [ ]

#### 4.10.2 Berechtigungsantrag entscheiden – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

#### 4.10.3 Bereits vorhandenen Antrag erneut bearbeiten – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Es entstehen keine unzulässigen doppelten offenen Anträge.
- [ ] Bereits entschiedene Anträge werden nicht irrtümlich als offen behandelt.
- [ ] Die bestehende Serienzuweisung wird nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

---

### 4.11 Benutzer- und Themenimport/-export

#### 4.11.1 Benutzer als CSV exportieren – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Exportdatei ist lesbar.
- [ ] Enthaltene Konten und Felder entsprechen dem vorgesehenen Exportumfang.
- [ ] Passwörter oder andere nicht exportierbare Geheimnisse sind nicht enthalten.

**Test erfolgreich:** [ ]

#### 4.11.2 Benutzer per CSV importieren – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Gültige Testkonten werden angelegt bzw. entsprechend der Importregel verarbeitet.
- [ ] Fehlerhafte Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Vorhandene Konten werden nicht ungewollt überschrieben.
- [ ] Serienzuweisungen werden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 4.11.3 Themen als CSV exportieren – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Export ist lesbar und enthält die vorgesehenen Themen.
- [ ] Zuständigkeiten, Status und Reihenbezüge sind korrekt.
- [ ] Inhalte außerhalb des zulässigen Berechtigungs- bzw. Exportumfangs werden nicht offengelegt.

**Test erfolgreich:** [ ]

#### 4.11.4 Themen per CSV importieren – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Gültige Testthemen werden entsprechend der Importregeln angelegt bzw. verarbeitet.
- [ ] Ungültige Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Reihenbezüge und Zuständigkeiten sind korrekt.
- [ ] Es entstehen keine unbeabsichtigten Duplikate.

**Test erfolgreich:** [ ]

---

### 4.12 Änderungsverlauf und Audit

#### 4.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Moderator*in sieht die Ereignisse der eigenen moderierten Reihe.
- [ ] Ereignisse anderer Reihen werden nicht offengelegt.
- [ ] Akteur, Zeitpunkt und Aktion sind nachvollziehbar.
- [ ] Unberechtigte Konten erhalten keinen Zugriff.

**Test erfolgreich:** [ ]

#### 4.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Admin und Auditor*in können die vorgesehenen Systemereignisse einsehen.
- [ ] Auditor*in kann keine Änderungsaktionen ausführen.
- [ ] Normale Nutzerkonten erhalten keinen unberechtigten Systemzugriff.
- [ ] Fachliche Reihenereignisse werden nicht unberechtigt in der Systemhistorie offengelegt.

**Test erfolgreich:** [ ]

#### 4.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] CSV-Datei ist lesbar.
- [ ] Export enthält nur die für die Rolle zulässigen Ereignisse.
- [ ] Direkter Exportaufruf ohne passende Berechtigung wird abgewiesen.
- [ ] Nicht erforderliche vertrauliche Daten werden nicht exportiert.

**Test erfolgreich:** [ ]

---

### 4.13 Aufbewahrung und automatische Löschung

#### 4.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Nicht abgelaufene Termine und Protokolle bleiben erhalten.
- [ ] Abgelaufene abgeschlossene Termine und Protokolle werden gemäß der Frist entfernt.
- [ ] Tagesordnungshistorie, die laut Fachregel am Thema erhalten bleiben muss, bleibt korrekt erhalten.
- [ ] Nicht abgeschlossene bzw. wieder geöffnete Termine werden nicht unberechtigt gelöscht.

**Test erfolgreich:** [ ]

#### 4.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Thema bleibt vor Fristablauf erhalten.
- [ ] Abgelaufenes archiviertes Thema wird gemäß der Fachregel endgültig entfernt.
- [ ] Zugehörige Inhalte und Dateien werden entsprechend der Löschregel behandelt.
- [ ] Nicht abgelaufene oder nicht archivierte Themen bleiben erhalten.

**Test erfolgreich:** [ ]

#### 4.13.3 Retention wiederholt ausführen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Wiederholte Ausführung erzeugt keine doppelten Löschvorgänge oder inkonsistenten Datensätze.
- [ ] Nicht abgelaufene Daten bleiben erhalten.
- [ ] Fehler einzelner Datensätze führen nicht zu unbemerkter Fehlbehandlung des gesamten Bestands.

**Test erfolgreich:** [ ]

---

### 4.14 Auditor*innenbereich

#### 4.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die vorgesehenen administrativen Prüfdaten sind lesbar.
- [ ] Startpasswort und andere Geheimnisse werden nicht angezeigt.
- [ ] Es bestehen keine Änderungsfunktionen für Auditor*innen.
- [ ] Fachliche Besprechungsreihen und Themeninhalte sind nicht zugänglich.

**Test erfolgreich:** [ ]

#### 4.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: globale Nutzerrolle (Serienrolle gemäß Testfall)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Lesender Zugriff auf ausdrücklich freigegebene administrative Prüfdaten ist möglich.
- [ ] Fachliche Inhalte sind nicht zugänglich.
- [ ] Schreibende Aktionen sind nicht möglich.
- [ ] Direkte URLs umgehen die Rollenbegrenzung nicht.

**Test erfolgreich:** [ ]

---

---

## 5. Produktiv – Ohne Berechtigungen

Ein angemeldetes normales Benutzerkonto ohne Serienzuweisung verwenden. Es darf weder Serieninhalte lesen noch fachliche oder administrative Aktionen ausführen. Direkte URLs und POST-Aktionen ausdrücklich mitprüfen.

**Verbindliche Durchführung für diese Rollengruppe**

- Alle folgenden Funktionsbereiche und Testfälle sind aus Sicht dieses Kontos durchzuführen.
- Bei erlaubten Aktionen muss die Funktion vollständig und mit korrektem Ergebnis funktionieren.
- Bei nicht erlaubten Aktionen den Aufruf über Navigation, direkte URL und – soweit möglich – direkte POST-Anfrage versuchen. Erwartet wird eine verweigerte Antwort (403/404 oder vorgesehene Umleitung), keine Datenänderung und keine Offenlegung geschützter Inhalte.
- Die nachfolgende Einzelprüfung nennt jeweils, ob die Rolle laut Berechtigungsmodell zugriffsberechtigt ist. Bei Serienfunktionen gilt die Berechtigung ausschließlich für die konkret zugewiesene Reihe.

### 5.1 Dashboard und Navigation

#### 5.1.1 Dashboard aufrufen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 5.1.2 Navigation und Darstellungsvarianten – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Die gewählte Darstellungsvariante bleibt entsprechend der Anwendungseinstellung erhalten.

**Test erfolgreich:** [ ]

---

### 5.2 Persönliches Konto und eigene Aufgaben

#### 5.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 5.2.2 Eigene Aufgaben aufrufen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Eigene offene Themen werden im vorgesehenen Abschnitt angezeigt.
- [ ] Eigene Tagesordnungspunkte werden getrennt davon angezeigt.
- [ ] Nicht zugewiesene oder nicht berechtigte Inhalte werden nicht zusätzlich eingeblendet.
- [ ] Bei fehlenden Aufgaben wird ein geeigneter Leerzustand angezeigt.

**Test erfolgreich:** [ ]

---

### 5.3 Besprechungsreihen verwalten

#### 5.3.1 Besprechungsreihe anlegen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die neue Besprechungsreihe erscheint in der Übersicht.
- [ ] Bezeichnung, Beschreibung und Wiederholungseinstellungen entsprechen den Eingaben.
- [ ] Zugehörige Termine werden entsprechend Startdatum, Rhythmus, Intervall und Enddatum erzeugt.
- [ ] Die erstellende Moderatorin bzw. der erstellende Moderator besitzt die vorgesehene Serienzuweisung.
- [ ] Andere Serienzuweisungen wurden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 5.3.2 Besprechungsreihe bearbeiten – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Geänderte Werte werden angezeigt.
- [ ] Nicht geänderte Werte bleiben erhalten.
- [ ] Bestehende Serienberechtigungen bleiben erhalten.
- [ ] Bereits vorhandene Termine und Themen sind weiterhin dem richtigen fachlichen Kontext zugeordnet.

**Test erfolgreich:** [ ]

#### 5.3.3 Besprechungsreihe verlängern – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Zusätzliche Termine werden bis zum neuen Enddatum erzeugt.
- [ ] Bereits vorhandene Termine bleiben erhalten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 5.3.4 Termine einer Reihe neu aufsetzen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Terminfolge entspricht den eingestellten Seriendaten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Bestehende Themen, Tagesordnungspunkte und Serienberechtigungen entsprechen den vorgesehenen Regeln.
- [ ] Nicht ausgewählte Reihen sind unverändert.

**Test erfolgreich:** [ ]

#### 5.3.5 Besprechungsreihe löschen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Reihe wird nicht mehr als aktive Reihe angeboten.
- [ ] Historische Inhalte werden entsprechend der gewählten Löschvariante behandelt.
- [ ] Vorgesehene historische Lesezugriffe bleiben erhalten.
- [ ] Andere Reihen und deren Berechtigungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 5.3.6 Berechtigungen einer Reihe verwalten – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das Testkonto ist der richtigen Reihe zugeordnet.
- [ ] Die jeweils ausgewählte Serienrolle wird korrekt angezeigt.
- [ ] Änderungen betreffen nur die ausgewählte Reihe.
- [ ] Die eigene Moderatorzuweisung lässt sich nicht unzulässig selbst entfernen oder herabstufen.
- [ ] Zuweisungen in anderen Reihen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 5.3.7 Fehlende Serienberechtigung prüfen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Fachliche Inhalte der nicht zugewiesenen Reihe werden nicht offengelegt.
- [ ] Direkte URL-Aufrufe zu Terminen und Themen gewähren keinen unberechtigten Zugriff.
- [ ] Die globale Adminrolle und eine Moderatorzuweisung in einer anderen Reihe gewähren keine Rechte für die geprüfte Testreihe.
- [ ] Reihenbearbeitung und Verwaltung der Serienmitglieder werden ohne Moderatorzuweisung für genau diese Reihe verweigert.
- [ ] Die zugewiesene andere Testreihe bleibt für das Admin-Konto gemäß seiner dortigen Moderatorrolle erreichbar.

**Test erfolgreich:** [ ]

---

#### 5.3.8 Globaler Admin mit zusätzlicher Moderatorzuweisung – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

- [ ] Ein globales Admin-Konto verwenden und es für Testreihe A ausdrücklich als Moderator zuweisen.
- [ ] Für Testreihe B keine Serienzuweisung für dieses Konto vergeben.
- [ ] Testreihe A über die Serienverwaltung öffnen und eine zulässige Verwaltungsaktion ausführen.
- [ ] Dieselbe Verwaltungsseite für Testreihe B über die direkte URL aufrufen.
- [ ] Prüfen, ob die globale Adminrolle ohne Serienzuweisung den Zugriff auf Testreihe B erweitert.

**Ergebnisprüfung**

- [ ] In Testreihe A ist die Moderatorverwaltung aufgrund der ausdrücklichen Serienzuweisung möglich.
- [ ] In Testreihe B wird der Zugriff verweigert.
- [ ] Die globale Adminrolle erweitert die Moderatorberechtigung nicht auf andere Reihen.
- [ ] Änderungen an Testreihe A verändern die Berechtigungen von Testreihe B nicht.

**Test erfolgreich:** [ ]

#### 5.3.9 Moderatorzugriff auf eine fremde Reihe verweigern – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

- [ ] Ein Moderator-Konto für Testreihe A verwenden.
- [ ] Sicherstellen, dass für Testreihe B keine Zuweisung besteht.
- [ ] Testreihe A über die Serienverwaltung öffnen.
- [ ] Die Verwaltungsübersicht und Bearbeitungsseite von Testreihe B über direkte URLs aufrufen.
- [ ] Eine schreibende Aktion für Testreihe B über die direkte URL bzw. POST-Anfrage versuchen.

**Ergebnisprüfung**

- [ ] Testreihe A kann verwaltet werden.
- [ ] Testreihe B ist weder über die Navigation noch über direkte URLs erreichbar.
- [ ] Schreibende Aktionen für Testreihe B werden verweigert.
- [ ] Daten und Berechtigungen von Testreihe B bleiben unverändert.

**Test erfolgreich:** [ ]

### 5.4 Termine und Besprechungsübersicht

#### 5.4.1 Terminübersicht aufrufen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Termine der berechtigten Reihen werden angezeigt.
- [ ] Datum und Reihenbezeichnung stimmen.
- [ ] Vergangene und zukünftige Termine sind entsprechend gekennzeichnet bzw. erreichbar.
- [ ] Termine nicht zugewiesener Reihen werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 5.4.2 Einzelnen Termin verschieben – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Termin wird am neuen Datum angezeigt.
- [ ] Der bisherige Termin wird nicht zusätzlich als Duplikat angezeigt.
- [ ] Zugehörige Tagesordnungspunkte und Zuständigkeiten bleiben dem Termin zugeordnet.
- [ ] Die übrigen Termine der Reihe entsprechen weiterhin dem vorgesehenen Rhythmus.

**Test erfolgreich:** [ ]

#### 5.4.3 Einzelnen Termin löschen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der ausgewählte Termin wird entsprechend der Löschfunktion entfernt.
- [ ] Nicht ausgewählte Termine bleiben erhalten.
- [ ] Themen und historische Inhalte werden entsprechend den vorgesehenen Regeln behandelt.
- [ ] Es bleiben keine ungewollten Zuordnungen oder doppelten Einträge zurück.

**Test erfolgreich:** [ ]

#### 5.4.4 Teilnehmerliste bearbeiten – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die ausgewählten Konten werden in der Teilnehmerliste angezeigt.
- [ ] Abgewählte Konten werden nicht mehr angezeigt.
- [ ] Die Änderung betrifft nur den ausgewählten Termin.
- [ ] Die Serienberechtigungen der Konten bleiben unverändert.

**Test erfolgreich:** [ ]

#### 5.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**- [ ] Abgeschlossene Inhalte sind nicht durch Teilnehmer*innen oder Leser*innen veränderbar.
- [ ] Der gespeicherte Protokollstand bleibt unverändert.- [ ] Die Anzeige des abgeschlossenen Termins bleibt möglich, sofern die Serienberechtigung dies erlaubt.
**Test erfolgreich:** [ ]

---

### 5.5 Themen anlegen und bearbeiten

#### 5.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das Thema erscheint in der Themenübersicht.
- [ ] Titel und Hauptzuständigkeit entsprechen den Eingaben.
- [ ] Das Thema ist der ausgewählten Besprechungsreihe zugeordnet.
- [ ] Für den ausgewählten Termin ist der zugehörige Tagesordnungspunkt vorhanden.
- [ ] Das Thema ist nicht versehentlich in einer anderen Reihe angelegt worden.

**Test erfolgreich:** [ ]

#### 5.5.2 Thema über einen Termin anlegen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das neue Thema ist angelegt.
- [ ] Der Tagesordnungspunkt ist dem geöffneten Termin zugeordnet.
- [ ] Hauptzuständigkeit und abweichende Zuständigkeit werden getrennt und korrekt angezeigt.
- [ ] Das Thema ist in der Themenübersicht auffindbar.

**Test erfolgreich:** [ ]

#### 5.5.3 Thema bearbeiten – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Titel, Status und Hauptzuständigkeit entsprechen den gespeicherten Werten.
- [ ] Änderungen bleiben nach dem Neuladen erhalten.
- [ ] Zugehörige Tagesordnungspunkte und historische Protokollstände bleiben korrekt zugeordnet.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 5.5.4 Themenstatus ändern – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der neue Status wird in der Detailansicht angezeigt.
- [ ] Der Status wird in der Übersicht korrekt dargestellt.
- [ ] Der Status eines einzelnen Tagesordnungspunkts wird nicht unbeabsichtigt mitgeändert.

**Test erfolgreich:** [ ]

#### 5.5.5 Thema archivieren und wieder öffnen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Archivierte Themen erscheinen im Archiv und nicht mehr in der regulären offenen Themenliste.
- [ ] Wieder geöffnete Themen erscheinen wieder im vorgesehenen aktiven Bereich.
- [ ] Titel, Zuständigkeit, Kommentare und zugehörige historische Inhalte bleiben erhalten.
- [ ] Der Änderungsverlauf bildet die Aktion ab.

**Test erfolgreich:** [ ]

#### 5.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das Thema ist der vorgesehenen Zielreihe zugeordnet.
- [ ] Der vorgesehene Zieltermin enthält den Tagesordnungspunkt.
- [ ] Übertragungsnotiz und Übertragungsverlauf sind nachvollziehbar.
- [ ] Quell- und Zielberechtigungen werden nicht unbeabsichtigt ausgeweitet.
- [ ] Andere Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 5.5.7 Themenvorschläge verwenden – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der ausgewählte Vorschlag wird korrekt übernommen.
- [ ] Das Thema bzw. der Tagesordnungspunkt wird mit den eingegebenen Daten angelegt.
- [ ] Es wird kein zusätzlicher oder doppelter Datensatz angelegt.

**Test erfolgreich:** [ ]

---

### 5.6 Tagesordnungspunkte und Wiedervorlagen

#### 5.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der terminbezogene Text wird korrekt angezeigt.
- [ ] Der Status des Tagesordnungspunkts entspricht der Auswahl.
- [ ] Eine abweichende Zuständigkeit wird korrekt angezeigt.
- [ ] Der allgemeine Themenstatus bleibt davon getrennt.

**Test erfolgreich:** [ ]

#### 5.6.2 Tagesordnungspunkte sortieren – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Reihenfolge entspricht der zuletzt vorgenommenen Sortierung.
- [ ] Jeder Tagesordnungspunkt ist weiterhin dem richtigen Thema zugeordnet.
- [ ] Es fehlen keine Punkte und es sind keine Duplikate entstanden.

**Test erfolgreich:** [ ]

#### 5.6.3 Tagesordnungspunkt entfernen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Punkt ist aus dem ausgewählten Termin entfernt.
- [ ] Das Thema selbst bleibt entsprechend der vorgesehenen Datenregel erhalten.
- [ ] Andere Tagesordnungspunkte bleiben unverändert.

**Test erfolgreich:** [ ]

#### 5.6.4 Wiedervorlage anlegen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Tagesordnungspunkt erscheint im vorgesehenen Zieltermin.
- [ ] Die Verbindung zum vorherigen Tagesordnungspunkt ist nachvollziehbar.
- [ ] Status und Zuständigkeit entsprechen den vorgesehenen Übernahmeregeln.
- [ ] Es ist keine doppelte Wiedervorlage entstanden.

**Test erfolgreich:** [ ]

#### 5.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Wiedervorlagekette ist chronologisch nachvollziehbar.
- [ ] Jeder Punkt ist dem richtigen Termin zugeordnet.
- [ ] Frühere Protokollstände bleiben unverändert.
- [ ] Es entstehen keine doppelten oder voneinander getrennten Ketten.

**Test erfolgreich:** [ ]

#### 5.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Datum, Reihenbezeichnung, Text, Status und Verantwortlichkeit werden dem historischen Eintrag entsprechend angezeigt.
- [ ] Historische Einträge lassen sich nicht unberechtigt verändern.
- [ ] Zugriff ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 5.7 Kommentare, Anlagen und Links

#### 5.7.1 Kommentar hinzufügen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Kommentar wird beim richtigen Thema angezeigt.
- [ ] Autor und Erstellungszeitpunkt werden korrekt angezeigt.
- [ ] Der Kommentar bleibt nach dem Neuladen erhalten.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 5.7.2 Datei als Themenanlage hochladen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Anlage wird beim richtigen Thema angezeigt.
- [ ] Bezeichnung und Datei sind korrekt zugeordnet.
- [ ] Die Datei lässt sich mit einem berechtigten Konto herunterladen.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 5.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der eingetragene Pfad bzw. Link wird korrekt angezeigt.
- [ ] Unterstützte Pfade werden entsprechend der Anwendung als Link dargestellt.
- [ ] Nicht unterstützte oder ungültige Werte werden nicht als unsichere Links ausgegeben.
- [ ] Die Anwendung behauptet nicht, die Erreichbarkeit einer externen Freigabe zu garantieren.

**Test erfolgreich:** [ ]

#### 5.7.4 Anlage herunterladen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Berechtigte Konten können die zugehörige Datei herunterladen.
- [ ] Dateiinhalt und Dateiname entsprechen der hochgeladenen Datei.
- [ ] Nicht berechtigte Konten erhalten keinen Dateizugriff.

**Test erfolgreich:** [ ]

#### 5.7.5 Anlage löschen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Anlage wird nicht mehr in der Themenansicht angezeigt.
- [ ] Der direkte Download der entfernten Anlage ist nicht mehr möglich.
- [ ] Andere Anlagen und Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 5.7.6 Upload-Grenzen prüfen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Zulässige Dateien innerhalb des Limits werden angenommen.
- [ ] Zu große Dateien werden abgewiesen.
- [ ] Nicht erlaubte Dateiendungen werden abgewiesen.
- [ ] Abgewiesene Uploads erzeugen keine ungewollten Anlagen-Datensätze.

**Test erfolgreich:** [ ]

---

### 5.8 Besprechung abschließen und Protokoll

#### 5.8.1 Besprechung abschließen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Termin ist als abgeschlossen gekennzeichnet.
- [ ] Ein Protokoll-Snapshot wurde erstellt.
- [ ] Teilnehmerliste und Tagesordnungstexte sind gegen weitere Bearbeitung gesperrt.
- [ ] Der Abschluss wird im Änderungsverlauf dokumentiert.

**Test erfolgreich:** [ ]

#### 5.8.2 Protokoll anzeigen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Protokoll zeigt den beim Abschluss gesicherten Stand.
- [ ] Historische Werte werden nicht durch spätere Änderungen am Thema überschrieben.
- [ ] Protokoll ist für berechtigte Leser*innen sichtbar.

**Test erfolgreich:** [ ]

#### 5.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Druckansicht enthält den richtigen Termin und Protokollstand.
- [ ] PDF lässt sich öffnen.
- [ ] PDF enthält die vorgesehenen Protokolldaten.
- [ ] Organisationsbezeichnung und Logo erscheinen entsprechend der Konfiguration.
- [ ] Unberechtigte Konten können den Export nicht abrufen.

**Test erfolgreich:** [ ]

#### 5.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Termin ist nach dem Wiederöffnen bearbeitbar.
- [ ] Der vorherige Protokollstand bleibt als historischer Stand nachvollziehbar.
- [ ] Die erneute Bearbeitung und der erneute Abschluss funktionieren.
- [ ] Teilnehmer*innen ohne Moderatorrechte können den Termin nicht wieder öffnen.

**Test erfolgreich:** [ ]

#### 5.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] PDF enthält die dem Thema zugeordneten historischen Einträge.
- [ ] Datum, Reihe, Texte und Statuswerte sind korrekt.
- [ ] Der Export ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 5.9 Offene Themen und Archiv

#### 5.9.1 Offene Themen aufrufen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Nur fachlich zugängliche Themen werden angezeigt.
- [ ] Status, Zuständigkeit und Besprechungsreihe werden korrekt angezeigt.
- [ ] Auswahl und Filter führen zu passenden Ergebnissen.

**Test erfolgreich:** [ ]

#### 5.9.2 Archiv aufrufen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Archivierte Themen sind im Archiv auffindbar.
- [ ] Historische Inhalte werden entsprechend der Berechtigung angezeigt.
- [ ] Nicht archivierte Themen werden nicht fälschlich als archiviert dargestellt.

**Test erfolgreich:** [ ]

#### 5.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der vorgesehene historische Lesezugriff des früheren Reihenmitglieds bleibt bestehen.
- [ ] Das unbeteiligte Konto erhält keinen Zugriff.
- [ ] Gelöschte aktive Reihenfunktionen werden nicht unbeabsichtigt wieder verfügbar.

**Test erfolgreich:** [ ]

---

### 5.10 Berechtigungsanträge

#### 5.10.1 Serienberechtigung beantragen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Antrag wird der richtigen Person und Besprechungsreihe zugeordnet.
- [ ] Gewünschte Rolle wird korrekt angezeigt.
- [ ] Der Antrag erscheint mit offenem Status.
- [ ] Durch den Antrag allein entstehen noch keine fachlichen Schreibrechte.

**Test erfolgreich:** [ ]

#### 5.10.2 Berechtigungsantrag entscheiden – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

#### 5.10.3 Bereits vorhandenen Antrag erneut bearbeiten – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Es entstehen keine unzulässigen doppelten offenen Anträge.
- [ ] Bereits entschiedene Anträge werden nicht irrtümlich als offen behandelt.
- [ ] Die bestehende Serienzuweisung wird nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

---

### 5.11 Benutzer- und Themenimport/-export

#### 5.11.1 Benutzer als CSV exportieren – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Exportdatei ist lesbar.
- [ ] Enthaltene Konten und Felder entsprechen dem vorgesehenen Exportumfang.
- [ ] Passwörter oder andere nicht exportierbare Geheimnisse sind nicht enthalten.

**Test erfolgreich:** [ ]

#### 5.11.2 Benutzer per CSV importieren – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Gültige Testkonten werden angelegt bzw. entsprechend der Importregel verarbeitet.
- [ ] Fehlerhafte Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Vorhandene Konten werden nicht ungewollt überschrieben.
- [ ] Serienzuweisungen werden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 5.11.3 Themen als CSV exportieren – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Export ist lesbar und enthält die vorgesehenen Themen.
- [ ] Zuständigkeiten, Status und Reihenbezüge sind korrekt.
- [ ] Inhalte außerhalb des zulässigen Berechtigungs- bzw. Exportumfangs werden nicht offengelegt.

**Test erfolgreich:** [ ]

#### 5.11.4 Themen per CSV importieren – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Gültige Testthemen werden entsprechend der Importregeln angelegt bzw. verarbeitet.
- [ ] Ungültige Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Reihenbezüge und Zuständigkeiten sind korrekt.
- [ ] Es entstehen keine unbeabsichtigten Duplikate.

**Test erfolgreich:** [ ]

---

### 5.12 Änderungsverlauf und Audit

#### 5.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Moderator*in sieht die Ereignisse der eigenen moderierten Reihe.
- [ ] Ereignisse anderer Reihen werden nicht offengelegt.
- [ ] Akteur, Zeitpunkt und Aktion sind nachvollziehbar.
- [ ] Unberechtigte Konten erhalten keinen Zugriff.

**Test erfolgreich:** [ ]

#### 5.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Admin und Auditor*in können die vorgesehenen Systemereignisse einsehen.
- [ ] Auditor*in kann keine Änderungsaktionen ausführen.
- [ ] Normale Nutzerkonten erhalten keinen unberechtigten Systemzugriff.
- [ ] Fachliche Reihenereignisse werden nicht unberechtigt in der Systemhistorie offengelegt.

**Test erfolgreich:** [ ]

#### 5.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] CSV-Datei ist lesbar.
- [ ] Export enthält nur die für die Rolle zulässigen Ereignisse.
- [ ] Direkter Exportaufruf ohne passende Berechtigung wird abgewiesen.
- [ ] Nicht erforderliche vertrauliche Daten werden nicht exportiert.

**Test erfolgreich:** [ ]

---

### 5.13 Aufbewahrung und automatische Löschung

#### 5.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Nicht abgelaufene Termine und Protokolle bleiben erhalten.
- [ ] Abgelaufene abgeschlossene Termine und Protokolle werden gemäß der Frist entfernt.
- [ ] Tagesordnungshistorie, die laut Fachregel am Thema erhalten bleiben muss, bleibt korrekt erhalten.
- [ ] Nicht abgeschlossene bzw. wieder geöffnete Termine werden nicht unberechtigt gelöscht.

**Test erfolgreich:** [ ]

#### 5.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Thema bleibt vor Fristablauf erhalten.
- [ ] Abgelaufenes archiviertes Thema wird gemäß der Fachregel endgültig entfernt.
- [ ] Zugehörige Inhalte und Dateien werden entsprechend der Löschregel behandelt.
- [ ] Nicht abgelaufene oder nicht archivierte Themen bleiben erhalten.

**Test erfolgreich:** [ ]

#### 5.13.3 Retention wiederholt ausführen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Wiederholte Ausführung erzeugt keine doppelten Löschvorgänge oder inkonsistenten Datensätze.
- [ ] Nicht abgelaufene Daten bleiben erhalten.
- [ ] Fehler einzelner Datensätze führen nicht zu unbemerkter Fehlbehandlung des gesamten Bestands.

**Test erfolgreich:** [ ]

---

### 5.14 Auditor*innenbereich

#### 5.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die vorgesehenen administrativen Prüfdaten sind lesbar.
- [ ] Startpasswort und andere Geheimnisse werden nicht angezeigt.
- [ ] Es bestehen keine Änderungsfunktionen für Auditor*innen.
- [ ] Fachliche Besprechungsreihen und Themeninhalte sind nicht zugänglich.

**Test erfolgreich:** [ ]

#### 5.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Lesender Zugriff auf ausdrücklich freigegebene administrative Prüfdaten ist möglich.
- [ ] Fachliche Inhalte sind nicht zugänglich.
- [ ] Schreibende Aktionen sind nicht möglich.
- [ ] Direkte URLs umgehen die Rollenbegrenzung nicht.

**Test erfolgreich:** [ ]

---

---

## 6. Produktiv – Leser

Ein normales Benutzerkonto verwenden, das ausschließlich als Leser der jeweiligen Testreihe zugewiesen ist. Keine Teilnehmer- oder Moderatorrolle vergeben.

**Verbindliche Durchführung für diese Rollengruppe**

- Alle folgenden Funktionsbereiche und Testfälle sind aus Sicht dieses Kontos durchzuführen.
- Bei erlaubten Aktionen muss die Funktion vollständig und mit korrektem Ergebnis funktionieren.
- Bei nicht erlaubten Aktionen den Aufruf über Navigation, direkte URL und – soweit möglich – direkte POST-Anfrage versuchen. Erwartet wird eine verweigerte Antwort (403/404 oder vorgesehene Umleitung), keine Datenänderung und keine Offenlegung geschützter Inhalte.
- Die nachfolgende Einzelprüfung nennt jeweils, ob die Rolle laut Berechtigungsmodell zugriffsberechtigt ist. Bei Serienfunktionen gilt die Berechtigung ausschließlich für die konkret zugewiesene Reihe.

### 6.1 Dashboard und Navigation

#### 6.1.1 Dashboard aufrufen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 6.1.2 Navigation und Darstellungsvarianten – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Die gewählte Darstellungsvariante bleibt entsprechend der Anwendungseinstellung erhalten.

**Test erfolgreich:** [ ]

---

### 6.2 Persönliches Konto und eigene Aufgaben

#### 6.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 6.2.2 Eigene Aufgaben aufrufen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Eigene offene Themen werden im vorgesehenen Abschnitt angezeigt.
- [ ] Eigene Tagesordnungspunkte werden getrennt davon angezeigt.
- [ ] Nicht zugewiesene oder nicht berechtigte Inhalte werden nicht zusätzlich eingeblendet.
- [ ] Bei fehlenden Aufgaben wird ein geeigneter Leerzustand angezeigt.

**Test erfolgreich:** [ ]

---

### 6.3 Besprechungsreihen verwalten

#### 6.3.1 Besprechungsreihe anlegen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die neue Besprechungsreihe erscheint in der Übersicht.
- [ ] Bezeichnung, Beschreibung und Wiederholungseinstellungen entsprechen den Eingaben.
- [ ] Zugehörige Termine werden entsprechend Startdatum, Rhythmus, Intervall und Enddatum erzeugt.
- [ ] Die erstellende Moderatorin bzw. der erstellende Moderator besitzt die vorgesehene Serienzuweisung.
- [ ] Andere Serienzuweisungen wurden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 6.3.2 Besprechungsreihe bearbeiten – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Geänderte Werte werden angezeigt.
- [ ] Nicht geänderte Werte bleiben erhalten.
- [ ] Bestehende Serienberechtigungen bleiben erhalten.
- [ ] Bereits vorhandene Termine und Themen sind weiterhin dem richtigen fachlichen Kontext zugeordnet.

**Test erfolgreich:** [ ]

#### 6.3.3 Besprechungsreihe verlängern – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Zusätzliche Termine werden bis zum neuen Enddatum erzeugt.
- [ ] Bereits vorhandene Termine bleiben erhalten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 6.3.4 Termine einer Reihe neu aufsetzen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Terminfolge entspricht den eingestellten Seriendaten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Bestehende Themen, Tagesordnungspunkte und Serienberechtigungen entsprechen den vorgesehenen Regeln.
- [ ] Nicht ausgewählte Reihen sind unverändert.

**Test erfolgreich:** [ ]

#### 6.3.5 Besprechungsreihe löschen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Reihe wird nicht mehr als aktive Reihe angeboten.
- [ ] Historische Inhalte werden entsprechend der gewählten Löschvariante behandelt.
- [ ] Vorgesehene historische Lesezugriffe bleiben erhalten.
- [ ] Andere Reihen und deren Berechtigungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 6.3.6 Berechtigungen einer Reihe verwalten – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das Testkonto ist der richtigen Reihe zugeordnet.
- [ ] Die jeweils ausgewählte Serienrolle wird korrekt angezeigt.
- [ ] Änderungen betreffen nur die ausgewählte Reihe.
- [ ] Die eigene Moderatorzuweisung lässt sich nicht unzulässig selbst entfernen oder herabstufen.
- [ ] Zuweisungen in anderen Reihen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 6.3.7 Fehlende Serienberechtigung prüfen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Fachliche Inhalte der nicht zugewiesenen Reihe werden nicht offengelegt.
- [ ] Direkte URL-Aufrufe zu Terminen und Themen gewähren keinen unberechtigten Zugriff.
- [ ] Die globale Adminrolle und eine Moderatorzuweisung in einer anderen Reihe gewähren keine Rechte für die geprüfte Testreihe.
- [ ] Reihenbearbeitung und Verwaltung der Serienmitglieder werden ohne Moderatorzuweisung für genau diese Reihe verweigert.
- [ ] Die zugewiesene andere Testreihe bleibt für das Admin-Konto gemäß seiner dortigen Moderatorrolle erreichbar.

**Test erfolgreich:** [ ]

---

#### 6.3.8 Globaler Admin mit zusätzlicher Moderatorzuweisung – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

- [ ] Ein globales Admin-Konto verwenden und es für Testreihe A ausdrücklich als Moderator zuweisen.
- [ ] Für Testreihe B keine Serienzuweisung für dieses Konto vergeben.
- [ ] Testreihe A über die Serienverwaltung öffnen und eine zulässige Verwaltungsaktion ausführen.
- [ ] Dieselbe Verwaltungsseite für Testreihe B über die direkte URL aufrufen.
- [ ] Prüfen, ob die globale Adminrolle ohne Serienzuweisung den Zugriff auf Testreihe B erweitert.

**Ergebnisprüfung**

- [ ] In Testreihe A ist die Moderatorverwaltung aufgrund der ausdrücklichen Serienzuweisung möglich.
- [ ] In Testreihe B wird der Zugriff verweigert.
- [ ] Die globale Adminrolle erweitert die Moderatorberechtigung nicht auf andere Reihen.
- [ ] Änderungen an Testreihe A verändern die Berechtigungen von Testreihe B nicht.

**Test erfolgreich:** [ ]

#### 6.3.9 Moderatorzugriff auf eine fremde Reihe verweigern – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

- [ ] Ein Moderator-Konto für Testreihe A verwenden.
- [ ] Sicherstellen, dass für Testreihe B keine Zuweisung besteht.
- [ ] Testreihe A über die Serienverwaltung öffnen.
- [ ] Die Verwaltungsübersicht und Bearbeitungsseite von Testreihe B über direkte URLs aufrufen.
- [ ] Eine schreibende Aktion für Testreihe B über die direkte URL bzw. POST-Anfrage versuchen.

**Ergebnisprüfung**

- [ ] Testreihe A kann verwaltet werden.
- [ ] Testreihe B ist weder über die Navigation noch über direkte URLs erreichbar.
- [ ] Schreibende Aktionen für Testreihe B werden verweigert.
- [ ] Daten und Berechtigungen von Testreihe B bleiben unverändert.

**Test erfolgreich:** [ ]

### 6.4 Termine und Besprechungsübersicht

#### 6.4.1 Terminübersicht aufrufen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Termine der berechtigten Reihen werden angezeigt.
- [ ] Datum und Reihenbezeichnung stimmen.
- [ ] Vergangene und zukünftige Termine sind entsprechend gekennzeichnet bzw. erreichbar.
- [ ] Termine nicht zugewiesener Reihen werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 6.4.2 Einzelnen Termin verschieben – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Termin wird am neuen Datum angezeigt.
- [ ] Der bisherige Termin wird nicht zusätzlich als Duplikat angezeigt.
- [ ] Zugehörige Tagesordnungspunkte und Zuständigkeiten bleiben dem Termin zugeordnet.
- [ ] Die übrigen Termine der Reihe entsprechen weiterhin dem vorgesehenen Rhythmus.

**Test erfolgreich:** [ ]

#### 6.4.3 Einzelnen Termin löschen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der ausgewählte Termin wird entsprechend der Löschfunktion entfernt.
- [ ] Nicht ausgewählte Termine bleiben erhalten.
- [ ] Themen und historische Inhalte werden entsprechend den vorgesehenen Regeln behandelt.
- [ ] Es bleiben keine ungewollten Zuordnungen oder doppelten Einträge zurück.

**Test erfolgreich:** [ ]

#### 6.4.4 Teilnehmerliste bearbeiten – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die ausgewählten Konten werden in der Teilnehmerliste angezeigt.
- [ ] Abgewählte Konten werden nicht mehr angezeigt.
- [ ] Die Änderung betrifft nur den ausgewählten Termin.
- [ ] Die Serienberechtigungen der Konten bleiben unverändert.

**Test erfolgreich:** [ ]

#### 6.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**- [ ] Abgeschlossene Inhalte sind nicht durch Teilnehmer*innen oder Leser*innen veränderbar.
- [ ] Der gespeicherte Protokollstand bleibt unverändert.- [ ] Die Anzeige des abgeschlossenen Termins bleibt möglich, sofern die Serienberechtigung dies erlaubt.
**Test erfolgreich:** [ ]

---

### 6.5 Themen anlegen und bearbeiten

#### 6.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das Thema erscheint in der Themenübersicht.
- [ ] Titel und Hauptzuständigkeit entsprechen den Eingaben.
- [ ] Das Thema ist der ausgewählten Besprechungsreihe zugeordnet.
- [ ] Für den ausgewählten Termin ist der zugehörige Tagesordnungspunkt vorhanden.
- [ ] Das Thema ist nicht versehentlich in einer anderen Reihe angelegt worden.

**Test erfolgreich:** [ ]

#### 6.5.2 Thema über einen Termin anlegen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das neue Thema ist angelegt.
- [ ] Der Tagesordnungspunkt ist dem geöffneten Termin zugeordnet.
- [ ] Hauptzuständigkeit und abweichende Zuständigkeit werden getrennt und korrekt angezeigt.
- [ ] Das Thema ist in der Themenübersicht auffindbar.

**Test erfolgreich:** [ ]

#### 6.5.3 Thema bearbeiten – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Titel, Status und Hauptzuständigkeit entsprechen den gespeicherten Werten.
- [ ] Änderungen bleiben nach dem Neuladen erhalten.
- [ ] Zugehörige Tagesordnungspunkte und historische Protokollstände bleiben korrekt zugeordnet.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 6.5.4 Themenstatus ändern – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der neue Status wird in der Detailansicht angezeigt.
- [ ] Der Status wird in der Übersicht korrekt dargestellt.
- [ ] Der Status eines einzelnen Tagesordnungspunkts wird nicht unbeabsichtigt mitgeändert.

**Test erfolgreich:** [ ]

#### 6.5.5 Thema archivieren und wieder öffnen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Archivierte Themen erscheinen im Archiv und nicht mehr in der regulären offenen Themenliste.
- [ ] Wieder geöffnete Themen erscheinen wieder im vorgesehenen aktiven Bereich.
- [ ] Titel, Zuständigkeit, Kommentare und zugehörige historische Inhalte bleiben erhalten.
- [ ] Der Änderungsverlauf bildet die Aktion ab.

**Test erfolgreich:** [ ]

#### 6.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das Thema ist der vorgesehenen Zielreihe zugeordnet.
- [ ] Der vorgesehene Zieltermin enthält den Tagesordnungspunkt.
- [ ] Übertragungsnotiz und Übertragungsverlauf sind nachvollziehbar.
- [ ] Quell- und Zielberechtigungen werden nicht unbeabsichtigt ausgeweitet.
- [ ] Andere Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 6.5.7 Themenvorschläge verwenden – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der ausgewählte Vorschlag wird korrekt übernommen.
- [ ] Das Thema bzw. der Tagesordnungspunkt wird mit den eingegebenen Daten angelegt.
- [ ] Es wird kein zusätzlicher oder doppelter Datensatz angelegt.

**Test erfolgreich:** [ ]

---

### 6.6 Tagesordnungspunkte und Wiedervorlagen

#### 6.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der terminbezogene Text wird korrekt angezeigt.
- [ ] Der Status des Tagesordnungspunkts entspricht der Auswahl.
- [ ] Eine abweichende Zuständigkeit wird korrekt angezeigt.
- [ ] Der allgemeine Themenstatus bleibt davon getrennt.

**Test erfolgreich:** [ ]

#### 6.6.2 Tagesordnungspunkte sortieren – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Reihenfolge entspricht der zuletzt vorgenommenen Sortierung.
- [ ] Jeder Tagesordnungspunkt ist weiterhin dem richtigen Thema zugeordnet.
- [ ] Es fehlen keine Punkte und es sind keine Duplikate entstanden.

**Test erfolgreich:** [ ]

#### 6.6.3 Tagesordnungspunkt entfernen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Punkt ist aus dem ausgewählten Termin entfernt.
- [ ] Das Thema selbst bleibt entsprechend der vorgesehenen Datenregel erhalten.
- [ ] Andere Tagesordnungspunkte bleiben unverändert.

**Test erfolgreich:** [ ]

#### 6.6.4 Wiedervorlage anlegen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Tagesordnungspunkt erscheint im vorgesehenen Zieltermin.
- [ ] Die Verbindung zum vorherigen Tagesordnungspunkt ist nachvollziehbar.
- [ ] Status und Zuständigkeit entsprechen den vorgesehenen Übernahmeregeln.
- [ ] Es ist keine doppelte Wiedervorlage entstanden.

**Test erfolgreich:** [ ]

#### 6.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Wiedervorlagekette ist chronologisch nachvollziehbar.
- [ ] Jeder Punkt ist dem richtigen Termin zugeordnet.
- [ ] Frühere Protokollstände bleiben unverändert.
- [ ] Es entstehen keine doppelten oder voneinander getrennten Ketten.

**Test erfolgreich:** [ ]

#### 6.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Datum, Reihenbezeichnung, Text, Status und Verantwortlichkeit werden dem historischen Eintrag entsprechend angezeigt.
- [ ] Historische Einträge lassen sich nicht unberechtigt verändern.
- [ ] Zugriff ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 6.7 Kommentare, Anlagen und Links

#### 6.7.1 Kommentar hinzufügen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Kommentar wird beim richtigen Thema angezeigt.
- [ ] Autor und Erstellungszeitpunkt werden korrekt angezeigt.
- [ ] Der Kommentar bleibt nach dem Neuladen erhalten.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 6.7.2 Datei als Themenanlage hochladen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Anlage wird beim richtigen Thema angezeigt.
- [ ] Bezeichnung und Datei sind korrekt zugeordnet.
- [ ] Die Datei lässt sich mit einem berechtigten Konto herunterladen.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 6.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der eingetragene Pfad bzw. Link wird korrekt angezeigt.
- [ ] Unterstützte Pfade werden entsprechend der Anwendung als Link dargestellt.
- [ ] Nicht unterstützte oder ungültige Werte werden nicht als unsichere Links ausgegeben.
- [ ] Die Anwendung behauptet nicht, die Erreichbarkeit einer externen Freigabe zu garantieren.

**Test erfolgreich:** [ ]

#### 6.7.4 Anlage herunterladen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Berechtigte Konten können die zugehörige Datei herunterladen.
- [ ] Dateiinhalt und Dateiname entsprechen der hochgeladenen Datei.
- [ ] Nicht berechtigte Konten erhalten keinen Dateizugriff.

**Test erfolgreich:** [ ]

#### 6.7.5 Anlage löschen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Anlage wird nicht mehr in der Themenansicht angezeigt.
- [ ] Der direkte Download der entfernten Anlage ist nicht mehr möglich.
- [ ] Andere Anlagen und Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 6.7.6 Upload-Grenzen prüfen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Zulässige Dateien innerhalb des Limits werden angenommen.
- [ ] Zu große Dateien werden abgewiesen.
- [ ] Nicht erlaubte Dateiendungen werden abgewiesen.
- [ ] Abgewiesene Uploads erzeugen keine ungewollten Anlagen-Datensätze.

**Test erfolgreich:** [ ]

---

### 6.8 Besprechung abschließen und Protokoll

#### 6.8.1 Besprechung abschließen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Termin ist als abgeschlossen gekennzeichnet.
- [ ] Ein Protokoll-Snapshot wurde erstellt.
- [ ] Teilnehmerliste und Tagesordnungstexte sind gegen weitere Bearbeitung gesperrt.
- [ ] Der Abschluss wird im Änderungsverlauf dokumentiert.

**Test erfolgreich:** [ ]

#### 6.8.2 Protokoll anzeigen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Protokoll zeigt den beim Abschluss gesicherten Stand.
- [ ] Historische Werte werden nicht durch spätere Änderungen am Thema überschrieben.
- [ ] Protokoll ist für berechtigte Leser*innen sichtbar.

**Test erfolgreich:** [ ]

#### 6.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Druckansicht enthält den richtigen Termin und Protokollstand.
- [ ] PDF lässt sich öffnen.
- [ ] PDF enthält die vorgesehenen Protokolldaten.
- [ ] Organisationsbezeichnung und Logo erscheinen entsprechend der Konfiguration.
- [ ] Unberechtigte Konten können den Export nicht abrufen.

**Test erfolgreich:** [ ]

#### 6.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Termin ist nach dem Wiederöffnen bearbeitbar.
- [ ] Der vorherige Protokollstand bleibt als historischer Stand nachvollziehbar.
- [ ] Die erneute Bearbeitung und der erneute Abschluss funktionieren.
- [ ] Teilnehmer*innen ohne Moderatorrechte können den Termin nicht wieder öffnen.

**Test erfolgreich:** [ ]

#### 6.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] PDF enthält die dem Thema zugeordneten historischen Einträge.
- [ ] Datum, Reihe, Texte und Statuswerte sind korrekt.
- [ ] Der Export ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 6.9 Offene Themen und Archiv

#### 6.9.1 Offene Themen aufrufen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Nur fachlich zugängliche Themen werden angezeigt.
- [ ] Status, Zuständigkeit und Besprechungsreihe werden korrekt angezeigt.
- [ ] Auswahl und Filter führen zu passenden Ergebnissen.

**Test erfolgreich:** [ ]

#### 6.9.2 Archiv aufrufen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Archivierte Themen sind im Archiv auffindbar.
- [ ] Historische Inhalte werden entsprechend der Berechtigung angezeigt.
- [ ] Nicht archivierte Themen werden nicht fälschlich als archiviert dargestellt.

**Test erfolgreich:** [ ]

#### 6.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der vorgesehene historische Lesezugriff des früheren Reihenmitglieds bleibt bestehen.
- [ ] Das unbeteiligte Konto erhält keinen Zugriff.
- [ ] Gelöschte aktive Reihenfunktionen werden nicht unbeabsichtigt wieder verfügbar.

**Test erfolgreich:** [ ]

---

### 6.10 Berechtigungsanträge

#### 6.10.1 Serienberechtigung beantragen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Antrag wird der richtigen Person und Besprechungsreihe zugeordnet.
- [ ] Gewünschte Rolle wird korrekt angezeigt.
- [ ] Der Antrag erscheint mit offenem Status.
- [ ] Durch den Antrag allein entstehen noch keine fachlichen Schreibrechte.

**Test erfolgreich:** [ ]

#### 6.10.2 Berechtigungsantrag entscheiden – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

#### 6.10.3 Bereits vorhandenen Antrag erneut bearbeiten – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Es entstehen keine unzulässigen doppelten offenen Anträge.
- [ ] Bereits entschiedene Anträge werden nicht irrtümlich als offen behandelt.
- [ ] Die bestehende Serienzuweisung wird nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

---

### 6.11 Benutzer- und Themenimport/-export

#### 6.11.1 Benutzer als CSV exportieren – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Exportdatei ist lesbar.
- [ ] Enthaltene Konten und Felder entsprechen dem vorgesehenen Exportumfang.
- [ ] Passwörter oder andere nicht exportierbare Geheimnisse sind nicht enthalten.

**Test erfolgreich:** [ ]

#### 6.11.2 Benutzer per CSV importieren – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Gültige Testkonten werden angelegt bzw. entsprechend der Importregel verarbeitet.
- [ ] Fehlerhafte Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Vorhandene Konten werden nicht ungewollt überschrieben.
- [ ] Serienzuweisungen werden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 6.11.3 Themen als CSV exportieren – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Export ist lesbar und enthält die vorgesehenen Themen.
- [ ] Zuständigkeiten, Status und Reihenbezüge sind korrekt.
- [ ] Inhalte außerhalb des zulässigen Berechtigungs- bzw. Exportumfangs werden nicht offengelegt.

**Test erfolgreich:** [ ]

#### 6.11.4 Themen per CSV importieren – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Gültige Testthemen werden entsprechend der Importregeln angelegt bzw. verarbeitet.
- [ ] Ungültige Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Reihenbezüge und Zuständigkeiten sind korrekt.
- [ ] Es entstehen keine unbeabsichtigten Duplikate.

**Test erfolgreich:** [ ]

---

### 6.12 Änderungsverlauf und Audit

#### 6.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Moderator*in sieht die Ereignisse der eigenen moderierten Reihe.
- [ ] Ereignisse anderer Reihen werden nicht offengelegt.
- [ ] Akteur, Zeitpunkt und Aktion sind nachvollziehbar.
- [ ] Unberechtigte Konten erhalten keinen Zugriff.

**Test erfolgreich:** [ ]

#### 6.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Admin und Auditor*in können die vorgesehenen Systemereignisse einsehen.
- [ ] Auditor*in kann keine Änderungsaktionen ausführen.
- [ ] Normale Nutzerkonten erhalten keinen unberechtigten Systemzugriff.
- [ ] Fachliche Reihenereignisse werden nicht unberechtigt in der Systemhistorie offengelegt.

**Test erfolgreich:** [ ]

#### 6.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] CSV-Datei ist lesbar.
- [ ] Export enthält nur die für die Rolle zulässigen Ereignisse.
- [ ] Direkter Exportaufruf ohne passende Berechtigung wird abgewiesen.
- [ ] Nicht erforderliche vertrauliche Daten werden nicht exportiert.

**Test erfolgreich:** [ ]

---

### 6.13 Aufbewahrung und automatische Löschung

#### 6.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Nicht abgelaufene Termine und Protokolle bleiben erhalten.
- [ ] Abgelaufene abgeschlossene Termine und Protokolle werden gemäß der Frist entfernt.
- [ ] Tagesordnungshistorie, die laut Fachregel am Thema erhalten bleiben muss, bleibt korrekt erhalten.
- [ ] Nicht abgeschlossene bzw. wieder geöffnete Termine werden nicht unberechtigt gelöscht.

**Test erfolgreich:** [ ]

#### 6.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Thema bleibt vor Fristablauf erhalten.
- [ ] Abgelaufenes archiviertes Thema wird gemäß der Fachregel endgültig entfernt.
- [ ] Zugehörige Inhalte und Dateien werden entsprechend der Löschregel behandelt.
- [ ] Nicht abgelaufene oder nicht archivierte Themen bleiben erhalten.

**Test erfolgreich:** [ ]

#### 6.13.3 Retention wiederholt ausführen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Wiederholte Ausführung erzeugt keine doppelten Löschvorgänge oder inkonsistenten Datensätze.
- [ ] Nicht abgelaufene Daten bleiben erhalten.
- [ ] Fehler einzelner Datensätze führen nicht zu unbemerkter Fehlbehandlung des gesamten Bestands.

**Test erfolgreich:** [ ]

---

### 6.14 Auditor*innenbereich

#### 6.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die vorgesehenen administrativen Prüfdaten sind lesbar.
- [ ] Startpasswort und andere Geheimnisse werden nicht angezeigt.
- [ ] Es bestehen keine Änderungsfunktionen für Auditor*innen.
- [ ] Fachliche Besprechungsreihen und Themeninhalte sind nicht zugänglich.

**Test erfolgreich:** [ ]

#### 6.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Lesender Zugriff auf ausdrücklich freigegebene administrative Prüfdaten ist möglich.
- [ ] Fachliche Inhalte sind nicht zugänglich.
- [ ] Schreibende Aktionen sind nicht möglich.
- [ ] Direkte URLs umgehen die Rollenbegrenzung nicht.

**Test erfolgreich:** [ ]

---

---

## 7. Produktiv – Teilnehmer

Ein normales Benutzerkonto verwenden, das als Teilnehmer der jeweiligen Testreihe zugewiesen ist. Keine Moderatorrolle vergeben.

**Verbindliche Durchführung für diese Rollengruppe**

- Alle folgenden Funktionsbereiche und Testfälle sind aus Sicht dieses Kontos durchzuführen.
- Bei erlaubten Aktionen muss die Funktion vollständig und mit korrektem Ergebnis funktionieren.
- Bei nicht erlaubten Aktionen den Aufruf über Navigation, direkte URL und – soweit möglich – direkte POST-Anfrage versuchen. Erwartet wird eine verweigerte Antwort (403/404 oder vorgesehene Umleitung), keine Datenänderung und keine Offenlegung geschützter Inhalte.
- Die nachfolgende Einzelprüfung nennt jeweils, ob die Rolle laut Berechtigungsmodell zugriffsberechtigt ist. Bei Serienfunktionen gilt die Berechtigung ausschließlich für die konkret zugewiesene Reihe.

### 7.1 Dashboard und Navigation

#### 7.1.1 Dashboard aufrufen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 7.1.2 Navigation und Darstellungsvarianten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Die gewählte Darstellungsvariante bleibt entsprechend der Anwendungseinstellung erhalten.

**Test erfolgreich:** [ ]

---

### 7.2 Persönliches Konto und eigene Aufgaben

#### 7.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 7.2.2 Eigene Aufgaben aufrufen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Eigene offene Themen werden im vorgesehenen Abschnitt angezeigt.
- [ ] Eigene Tagesordnungspunkte werden getrennt davon angezeigt.
- [ ] Nicht zugewiesene oder nicht berechtigte Inhalte werden nicht zusätzlich eingeblendet.
- [ ] Bei fehlenden Aufgaben wird ein geeigneter Leerzustand angezeigt.

**Test erfolgreich:** [ ]

---

### 7.3 Besprechungsreihen verwalten

#### 7.3.1 Besprechungsreihe anlegen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die neue Besprechungsreihe erscheint in der Übersicht.
- [ ] Bezeichnung, Beschreibung und Wiederholungseinstellungen entsprechen den Eingaben.
- [ ] Zugehörige Termine werden entsprechend Startdatum, Rhythmus, Intervall und Enddatum erzeugt.
- [ ] Die erstellende Moderatorin bzw. der erstellende Moderator besitzt die vorgesehene Serienzuweisung.
- [ ] Andere Serienzuweisungen wurden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 7.3.2 Besprechungsreihe bearbeiten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Geänderte Werte werden angezeigt.
- [ ] Nicht geänderte Werte bleiben erhalten.
- [ ] Bestehende Serienberechtigungen bleiben erhalten.
- [ ] Bereits vorhandene Termine und Themen sind weiterhin dem richtigen fachlichen Kontext zugeordnet.

**Test erfolgreich:** [ ]

#### 7.3.3 Besprechungsreihe verlängern – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Zusätzliche Termine werden bis zum neuen Enddatum erzeugt.
- [ ] Bereits vorhandene Termine bleiben erhalten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 7.3.4 Termine einer Reihe neu aufsetzen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Terminfolge entspricht den eingestellten Seriendaten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Bestehende Themen, Tagesordnungspunkte und Serienberechtigungen entsprechen den vorgesehenen Regeln.
- [ ] Nicht ausgewählte Reihen sind unverändert.

**Test erfolgreich:** [ ]

#### 7.3.5 Besprechungsreihe löschen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Reihe wird nicht mehr als aktive Reihe angeboten.
- [ ] Historische Inhalte werden entsprechend der gewählten Löschvariante behandelt.
- [ ] Vorgesehene historische Lesezugriffe bleiben erhalten.
- [ ] Andere Reihen und deren Berechtigungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 7.3.6 Berechtigungen einer Reihe verwalten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das Testkonto ist der richtigen Reihe zugeordnet.
- [ ] Die jeweils ausgewählte Serienrolle wird korrekt angezeigt.
- [ ] Änderungen betreffen nur die ausgewählte Reihe.
- [ ] Die eigene Moderatorzuweisung lässt sich nicht unzulässig selbst entfernen oder herabstufen.
- [ ] Zuweisungen in anderen Reihen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 7.3.7 Fehlende Serienberechtigung prüfen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Fachliche Inhalte der nicht zugewiesenen Reihe werden nicht offengelegt.
- [ ] Direkte URL-Aufrufe zu Terminen und Themen gewähren keinen unberechtigten Zugriff.
- [ ] Die globale Adminrolle und eine Moderatorzuweisung in einer anderen Reihe gewähren keine Rechte für die geprüfte Testreihe.
- [ ] Reihenbearbeitung und Verwaltung der Serienmitglieder werden ohne Moderatorzuweisung für genau diese Reihe verweigert.
- [ ] Die zugewiesene andere Testreihe bleibt für das Admin-Konto gemäß seiner dortigen Moderatorrolle erreichbar.

**Test erfolgreich:** [ ]

---

#### 7.3.8 Globaler Admin mit zusätzlicher Moderatorzuweisung – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

- [ ] Ein globales Admin-Konto verwenden und es für Testreihe A ausdrücklich als Moderator zuweisen.
- [ ] Für Testreihe B keine Serienzuweisung für dieses Konto vergeben.
- [ ] Testreihe A über die Serienverwaltung öffnen und eine zulässige Verwaltungsaktion ausführen.
- [ ] Dieselbe Verwaltungsseite für Testreihe B über die direkte URL aufrufen.
- [ ] Prüfen, ob die globale Adminrolle ohne Serienzuweisung den Zugriff auf Testreihe B erweitert.

**Ergebnisprüfung**

- [ ] In Testreihe A ist die Moderatorverwaltung aufgrund der ausdrücklichen Serienzuweisung möglich.
- [ ] In Testreihe B wird der Zugriff verweigert.
- [ ] Die globale Adminrolle erweitert die Moderatorberechtigung nicht auf andere Reihen.
- [ ] Änderungen an Testreihe A verändern die Berechtigungen von Testreihe B nicht.

**Test erfolgreich:** [ ]

#### 7.3.9 Moderatorzugriff auf eine fremde Reihe verweigern – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

- [ ] Ein Moderator-Konto für Testreihe A verwenden.
- [ ] Sicherstellen, dass für Testreihe B keine Zuweisung besteht.
- [ ] Testreihe A über die Serienverwaltung öffnen.
- [ ] Die Verwaltungsübersicht und Bearbeitungsseite von Testreihe B über direkte URLs aufrufen.
- [ ] Eine schreibende Aktion für Testreihe B über die direkte URL bzw. POST-Anfrage versuchen.

**Ergebnisprüfung**

- [ ] Testreihe A kann verwaltet werden.
- [ ] Testreihe B ist weder über die Navigation noch über direkte URLs erreichbar.
- [ ] Schreibende Aktionen für Testreihe B werden verweigert.
- [ ] Daten und Berechtigungen von Testreihe B bleiben unverändert.

**Test erfolgreich:** [ ]

### 7.4 Termine und Besprechungsübersicht

#### 7.4.1 Terminübersicht aufrufen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Termine der berechtigten Reihen werden angezeigt.
- [ ] Datum und Reihenbezeichnung stimmen.
- [ ] Vergangene und zukünftige Termine sind entsprechend gekennzeichnet bzw. erreichbar.
- [ ] Termine nicht zugewiesener Reihen werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 7.4.2 Einzelnen Termin verschieben – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Termin wird am neuen Datum angezeigt.
- [ ] Der bisherige Termin wird nicht zusätzlich als Duplikat angezeigt.
- [ ] Zugehörige Tagesordnungspunkte und Zuständigkeiten bleiben dem Termin zugeordnet.
- [ ] Die übrigen Termine der Reihe entsprechen weiterhin dem vorgesehenen Rhythmus.

**Test erfolgreich:** [ ]

#### 7.4.3 Einzelnen Termin löschen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der ausgewählte Termin wird entsprechend der Löschfunktion entfernt.
- [ ] Nicht ausgewählte Termine bleiben erhalten.
- [ ] Themen und historische Inhalte werden entsprechend den vorgesehenen Regeln behandelt.
- [ ] Es bleiben keine ungewollten Zuordnungen oder doppelten Einträge zurück.

**Test erfolgreich:** [ ]

#### 7.4.4 Teilnehmerliste bearbeiten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die ausgewählten Konten werden in der Teilnehmerliste angezeigt.
- [ ] Abgewählte Konten werden nicht mehr angezeigt.
- [ ] Die Änderung betrifft nur den ausgewählten Termin.
- [ ] Die Serienberechtigungen der Konten bleiben unverändert.

**Test erfolgreich:** [ ]

#### 7.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**- [ ] Abgeschlossene Inhalte sind nicht durch Teilnehmer*innen oder Leser*innen veränderbar.
- [ ] Der gespeicherte Protokollstand bleibt unverändert.- [ ] Die Anzeige des abgeschlossenen Termins bleibt möglich, sofern die Serienberechtigung dies erlaubt.
**Test erfolgreich:** [ ]

---

### 7.5 Themen anlegen und bearbeiten

#### 7.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Das Thema erscheint in der Themenübersicht.
- [ ] Titel und Hauptzuständigkeit entsprechen den Eingaben.
- [ ] Das Thema ist der ausgewählten Besprechungsreihe zugeordnet.
- [ ] Für den ausgewählten Termin ist der zugehörige Tagesordnungspunkt vorhanden.
- [ ] Das Thema ist nicht versehentlich in einer anderen Reihe angelegt worden.

**Test erfolgreich:** [ ]

#### 7.5.2 Thema über einen Termin anlegen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Das neue Thema ist angelegt.
- [ ] Der Tagesordnungspunkt ist dem geöffneten Termin zugeordnet.
- [ ] Hauptzuständigkeit und abweichende Zuständigkeit werden getrennt und korrekt angezeigt.
- [ ] Das Thema ist in der Themenübersicht auffindbar.

**Test erfolgreich:** [ ]

#### 7.5.3 Thema bearbeiten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Titel, Status und Hauptzuständigkeit entsprechen den gespeicherten Werten.
- [ ] Änderungen bleiben nach dem Neuladen erhalten.
- [ ] Zugehörige Tagesordnungspunkte und historische Protokollstände bleiben korrekt zugeordnet.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 7.5.4 Themenstatus ändern – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der neue Status wird in der Detailansicht angezeigt.
- [ ] Der Status wird in der Übersicht korrekt dargestellt.
- [ ] Der Status eines einzelnen Tagesordnungspunkts wird nicht unbeabsichtigt mitgeändert.

**Test erfolgreich:** [ ]

#### 7.5.5 Thema archivieren und wieder öffnen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Archivierte Themen erscheinen im Archiv und nicht mehr in der regulären offenen Themenliste.
- [ ] Wieder geöffnete Themen erscheinen wieder im vorgesehenen aktiven Bereich.
- [ ] Titel, Zuständigkeit, Kommentare und zugehörige historische Inhalte bleiben erhalten.
- [ ] Der Änderungsverlauf bildet die Aktion ab.

**Test erfolgreich:** [ ]

#### 7.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Das Thema ist der vorgesehenen Zielreihe zugeordnet.
- [ ] Der vorgesehene Zieltermin enthält den Tagesordnungspunkt.
- [ ] Übertragungsnotiz und Übertragungsverlauf sind nachvollziehbar.
- [ ] Quell- und Zielberechtigungen werden nicht unbeabsichtigt ausgeweitet.
- [ ] Andere Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 7.5.7 Themenvorschläge verwenden – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der ausgewählte Vorschlag wird korrekt übernommen.
- [ ] Das Thema bzw. der Tagesordnungspunkt wird mit den eingegebenen Daten angelegt.
- [ ] Es wird kein zusätzlicher oder doppelter Datensatz angelegt.

**Test erfolgreich:** [ ]

---

### 7.6 Tagesordnungspunkte und Wiedervorlagen

#### 7.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der terminbezogene Text wird korrekt angezeigt.
- [ ] Der Status des Tagesordnungspunkts entspricht der Auswahl.
- [ ] Eine abweichende Zuständigkeit wird korrekt angezeigt.
- [ ] Der allgemeine Themenstatus bleibt davon getrennt.

**Test erfolgreich:** [ ]

#### 7.6.2 Tagesordnungspunkte sortieren – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Reihenfolge entspricht der zuletzt vorgenommenen Sortierung.
- [ ] Jeder Tagesordnungspunkt ist weiterhin dem richtigen Thema zugeordnet.
- [ ] Es fehlen keine Punkte und es sind keine Duplikate entstanden.

**Test erfolgreich:** [ ]

#### 7.6.3 Tagesordnungspunkt entfernen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Punkt ist aus dem ausgewählten Termin entfernt.
- [ ] Das Thema selbst bleibt entsprechend der vorgesehenen Datenregel erhalten.
- [ ] Andere Tagesordnungspunkte bleiben unverändert.

**Test erfolgreich:** [ ]

#### 7.6.4 Wiedervorlage anlegen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Tagesordnungspunkt erscheint im vorgesehenen Zieltermin.
- [ ] Die Verbindung zum vorherigen Tagesordnungspunkt ist nachvollziehbar.
- [ ] Status und Zuständigkeit entsprechen den vorgesehenen Übernahmeregeln.
- [ ] Es ist keine doppelte Wiedervorlage entstanden.

**Test erfolgreich:** [ ]

#### 7.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Wiedervorlagekette ist chronologisch nachvollziehbar.
- [ ] Jeder Punkt ist dem richtigen Termin zugeordnet.
- [ ] Frühere Protokollstände bleiben unverändert.
- [ ] Es entstehen keine doppelten oder voneinander getrennten Ketten.

**Test erfolgreich:** [ ]

#### 7.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Datum, Reihenbezeichnung, Text, Status und Verantwortlichkeit werden dem historischen Eintrag entsprechend angezeigt.
- [ ] Historische Einträge lassen sich nicht unberechtigt verändern.
- [ ] Zugriff ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 7.7 Kommentare, Anlagen und Links

#### 7.7.1 Kommentar hinzufügen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Kommentar wird beim richtigen Thema angezeigt.
- [ ] Autor und Erstellungszeitpunkt werden korrekt angezeigt.
- [ ] Der Kommentar bleibt nach dem Neuladen erhalten.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 7.7.2 Datei als Themenanlage hochladen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Anlage wird beim richtigen Thema angezeigt.
- [ ] Bezeichnung und Datei sind korrekt zugeordnet.
- [ ] Die Datei lässt sich mit einem berechtigten Konto herunterladen.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 7.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der eingetragene Pfad bzw. Link wird korrekt angezeigt.
- [ ] Unterstützte Pfade werden entsprechend der Anwendung als Link dargestellt.
- [ ] Nicht unterstützte oder ungültige Werte werden nicht als unsichere Links ausgegeben.
- [ ] Die Anwendung behauptet nicht, die Erreichbarkeit einer externen Freigabe zu garantieren.

**Test erfolgreich:** [ ]

#### 7.7.4 Anlage herunterladen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Berechtigte Konten können die zugehörige Datei herunterladen.
- [ ] Dateiinhalt und Dateiname entsprechen der hochgeladenen Datei.
- [ ] Nicht berechtigte Konten erhalten keinen Dateizugriff.

**Test erfolgreich:** [ ]

#### 7.7.5 Anlage löschen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Anlage wird nicht mehr in der Themenansicht angezeigt.
- [ ] Der direkte Download der entfernten Anlage ist nicht mehr möglich.
- [ ] Andere Anlagen und Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 7.7.6 Upload-Grenzen prüfen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Zulässige Dateien innerhalb des Limits werden angenommen.
- [ ] Zu große Dateien werden abgewiesen.
- [ ] Nicht erlaubte Dateiendungen werden abgewiesen.
- [ ] Abgewiesene Uploads erzeugen keine ungewollten Anlagen-Datensätze.

**Test erfolgreich:** [ ]

---

### 7.8 Besprechung abschließen und Protokoll

#### 7.8.1 Besprechung abschließen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Termin ist als abgeschlossen gekennzeichnet.
- [ ] Ein Protokoll-Snapshot wurde erstellt.
- [ ] Teilnehmerliste und Tagesordnungstexte sind gegen weitere Bearbeitung gesperrt.
- [ ] Der Abschluss wird im Änderungsverlauf dokumentiert.

**Test erfolgreich:** [ ]

#### 7.8.2 Protokoll anzeigen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Protokoll zeigt den beim Abschluss gesicherten Stand.
- [ ] Historische Werte werden nicht durch spätere Änderungen am Thema überschrieben.
- [ ] Protokoll ist für berechtigte Leser*innen sichtbar.

**Test erfolgreich:** [ ]

#### 7.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Druckansicht enthält den richtigen Termin und Protokollstand.
- [ ] PDF lässt sich öffnen.
- [ ] PDF enthält die vorgesehenen Protokolldaten.
- [ ] Organisationsbezeichnung und Logo erscheinen entsprechend der Konfiguration.
- [ ] Unberechtigte Konten können den Export nicht abrufen.

**Test erfolgreich:** [ ]

#### 7.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Termin ist nach dem Wiederöffnen bearbeitbar.
- [ ] Der vorherige Protokollstand bleibt als historischer Stand nachvollziehbar.
- [ ] Die erneute Bearbeitung und der erneute Abschluss funktionieren.
- [ ] Teilnehmer*innen ohne Moderatorrechte können den Termin nicht wieder öffnen.

**Test erfolgreich:** [ ]

#### 7.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] PDF enthält die dem Thema zugeordneten historischen Einträge.
- [ ] Datum, Reihe, Texte und Statuswerte sind korrekt.
- [ ] Der Export ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 7.9 Offene Themen und Archiv

#### 7.9.1 Offene Themen aufrufen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Nur fachlich zugängliche Themen werden angezeigt.
- [ ] Status, Zuständigkeit und Besprechungsreihe werden korrekt angezeigt.
- [ ] Auswahl und Filter führen zu passenden Ergebnissen.

**Test erfolgreich:** [ ]

#### 7.9.2 Archiv aufrufen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Archivierte Themen sind im Archiv auffindbar.
- [ ] Historische Inhalte werden entsprechend der Berechtigung angezeigt.
- [ ] Nicht archivierte Themen werden nicht fälschlich als archiviert dargestellt.

**Test erfolgreich:** [ ]

#### 7.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der vorgesehene historische Lesezugriff des früheren Reihenmitglieds bleibt bestehen.
- [ ] Das unbeteiligte Konto erhält keinen Zugriff.
- [ ] Gelöschte aktive Reihenfunktionen werden nicht unbeabsichtigt wieder verfügbar.

**Test erfolgreich:** [ ]

---

### 7.10 Berechtigungsanträge

#### 7.10.1 Serienberechtigung beantragen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Antrag wird der richtigen Person und Besprechungsreihe zugeordnet.
- [ ] Gewünschte Rolle wird korrekt angezeigt.
- [ ] Der Antrag erscheint mit offenem Status.
- [ ] Durch den Antrag allein entstehen noch keine fachlichen Schreibrechte.

**Test erfolgreich:** [ ]

#### 7.10.2 Berechtigungsantrag entscheiden – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

#### 7.10.3 Bereits vorhandenen Antrag erneut bearbeiten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Es entstehen keine unzulässigen doppelten offenen Anträge.
- [ ] Bereits entschiedene Anträge werden nicht irrtümlich als offen behandelt.
- [ ] Die bestehende Serienzuweisung wird nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

---

### 7.11 Benutzer- und Themenimport/-export

#### 7.11.1 Benutzer als CSV exportieren – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Exportdatei ist lesbar.
- [ ] Enthaltene Konten und Felder entsprechen dem vorgesehenen Exportumfang.
- [ ] Passwörter oder andere nicht exportierbare Geheimnisse sind nicht enthalten.

**Test erfolgreich:** [ ]

#### 7.11.2 Benutzer per CSV importieren – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Gültige Testkonten werden angelegt bzw. entsprechend der Importregel verarbeitet.
- [ ] Fehlerhafte Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Vorhandene Konten werden nicht ungewollt überschrieben.
- [ ] Serienzuweisungen werden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 7.11.3 Themen als CSV exportieren – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Export ist lesbar und enthält die vorgesehenen Themen.
- [ ] Zuständigkeiten, Status und Reihenbezüge sind korrekt.
- [ ] Inhalte außerhalb des zulässigen Berechtigungs- bzw. Exportumfangs werden nicht offengelegt.

**Test erfolgreich:** [ ]

#### 7.11.4 Themen per CSV importieren – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Gültige Testthemen werden entsprechend der Importregeln angelegt bzw. verarbeitet.
- [ ] Ungültige Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Reihenbezüge und Zuständigkeiten sind korrekt.
- [ ] Es entstehen keine unbeabsichtigten Duplikate.

**Test erfolgreich:** [ ]

---

### 7.12 Änderungsverlauf und Audit

#### 7.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Moderator*in sieht die Ereignisse der eigenen moderierten Reihe.
- [ ] Ereignisse anderer Reihen werden nicht offengelegt.
- [ ] Akteur, Zeitpunkt und Aktion sind nachvollziehbar.
- [ ] Unberechtigte Konten erhalten keinen Zugriff.

**Test erfolgreich:** [ ]

#### 7.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Admin und Auditor*in können die vorgesehenen Systemereignisse einsehen.
- [ ] Auditor*in kann keine Änderungsaktionen ausführen.
- [ ] Normale Nutzerkonten erhalten keinen unberechtigten Systemzugriff.
- [ ] Fachliche Reihenereignisse werden nicht unberechtigt in der Systemhistorie offengelegt.

**Test erfolgreich:** [ ]

#### 7.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] CSV-Datei ist lesbar.
- [ ] Export enthält nur die für die Rolle zulässigen Ereignisse.
- [ ] Direkter Exportaufruf ohne passende Berechtigung wird abgewiesen.
- [ ] Nicht erforderliche vertrauliche Daten werden nicht exportiert.

**Test erfolgreich:** [ ]

---

### 7.13 Aufbewahrung und automatische Löschung

#### 7.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Nicht abgelaufene Termine und Protokolle bleiben erhalten.
- [ ] Abgelaufene abgeschlossene Termine und Protokolle werden gemäß der Frist entfernt.
- [ ] Tagesordnungshistorie, die laut Fachregel am Thema erhalten bleiben muss, bleibt korrekt erhalten.
- [ ] Nicht abgeschlossene bzw. wieder geöffnete Termine werden nicht unberechtigt gelöscht.

**Test erfolgreich:** [ ]

#### 7.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Thema bleibt vor Fristablauf erhalten.
- [ ] Abgelaufenes archiviertes Thema wird gemäß der Fachregel endgültig entfernt.
- [ ] Zugehörige Inhalte und Dateien werden entsprechend der Löschregel behandelt.
- [ ] Nicht abgelaufene oder nicht archivierte Themen bleiben erhalten.

**Test erfolgreich:** [ ]

#### 7.13.3 Retention wiederholt ausführen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Wiederholte Ausführung erzeugt keine doppelten Löschvorgänge oder inkonsistenten Datensätze.
- [ ] Nicht abgelaufene Daten bleiben erhalten.
- [ ] Fehler einzelner Datensätze führen nicht zu unbemerkter Fehlbehandlung des gesamten Bestands.

**Test erfolgreich:** [ ]

---

### 7.14 Auditor*innenbereich

#### 7.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die vorgesehenen administrativen Prüfdaten sind lesbar.
- [ ] Startpasswort und andere Geheimnisse werden nicht angezeigt.
- [ ] Es bestehen keine Änderungsfunktionen für Auditor*innen.
- [ ] Fachliche Besprechungsreihen und Themeninhalte sind nicht zugänglich.

**Test erfolgreich:** [ ]

#### 7.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Lesender Zugriff auf ausdrücklich freigegebene administrative Prüfdaten ist möglich.
- [ ] Fachliche Inhalte sind nicht zugänglich.
- [ ] Schreibende Aktionen sind nicht möglich.
- [ ] Direkte URLs umgehen die Rollenbegrenzung nicht.

**Test erfolgreich:** [ ]

---

---

## 8. Produktiv – Moderator

Ein normales Benutzerkonto verwenden, das ausschließlich als Moderator der jeweiligen Testreihe zugewiesen ist. Für Fremdreihen darf keine Zuweisung bestehen.

**Verbindliche Durchführung für diese Rollengruppe**

- Alle folgenden Funktionsbereiche und Testfälle sind aus Sicht dieses Kontos durchzuführen.
- Bei erlaubten Aktionen muss die Funktion vollständig und mit korrektem Ergebnis funktionieren.
- Bei nicht erlaubten Aktionen den Aufruf über Navigation, direkte URL und – soweit möglich – direkte POST-Anfrage versuchen. Erwartet wird eine verweigerte Antwort (403/404 oder vorgesehene Umleitung), keine Datenänderung und keine Offenlegung geschützter Inhalte.
- Die nachfolgende Einzelprüfung nennt jeweils, ob die Rolle laut Berechtigungsmodell zugriffsberechtigt ist. Bei Serienfunktionen gilt die Berechtigung ausschließlich für die konkret zugewiesene Reihe.

### 8.1 Dashboard und Navigation

#### 8.1.1 Dashboard aufrufen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 8.1.2 Navigation und Darstellungsvarianten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Die gewählte Darstellungsvariante bleibt entsprechend der Anwendungseinstellung erhalten.

**Test erfolgreich:** [ ]

---

### 8.2 Persönliches Konto und eigene Aufgaben

#### 8.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 8.2.2 Eigene Aufgaben aufrufen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Eigene offene Themen werden im vorgesehenen Abschnitt angezeigt.
- [ ] Eigene Tagesordnungspunkte werden getrennt davon angezeigt.
- [ ] Nicht zugewiesene oder nicht berechtigte Inhalte werden nicht zusätzlich eingeblendet.
- [ ] Bei fehlenden Aufgaben wird ein geeigneter Leerzustand angezeigt.

**Test erfolgreich:** [ ]

---

### 8.3 Besprechungsreihen verwalten

#### 8.3.1 Besprechungsreihe anlegen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die neue Besprechungsreihe erscheint in der Übersicht.
- [ ] Bezeichnung, Beschreibung und Wiederholungseinstellungen entsprechen den Eingaben.
- [ ] Zugehörige Termine werden entsprechend Startdatum, Rhythmus, Intervall und Enddatum erzeugt.
- [ ] Die erstellende Moderatorin bzw. der erstellende Moderator besitzt die vorgesehene Serienzuweisung.
- [ ] Andere Serienzuweisungen wurden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 8.3.2 Besprechungsreihe bearbeiten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Geänderte Werte werden angezeigt.
- [ ] Nicht geänderte Werte bleiben erhalten.
- [ ] Bestehende Serienberechtigungen bleiben erhalten.
- [ ] Bereits vorhandene Termine und Themen sind weiterhin dem richtigen fachlichen Kontext zugeordnet.

**Test erfolgreich:** [ ]

#### 8.3.3 Besprechungsreihe verlängern – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Zusätzliche Termine werden bis zum neuen Enddatum erzeugt.
- [ ] Bereits vorhandene Termine bleiben erhalten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 8.3.4 Termine einer Reihe neu aufsetzen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Terminfolge entspricht den eingestellten Seriendaten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Bestehende Themen, Tagesordnungspunkte und Serienberechtigungen entsprechen den vorgesehenen Regeln.
- [ ] Nicht ausgewählte Reihen sind unverändert.

**Test erfolgreich:** [ ]

#### 8.3.5 Besprechungsreihe löschen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Reihe wird nicht mehr als aktive Reihe angeboten.
- [ ] Historische Inhalte werden entsprechend der gewählten Löschvariante behandelt.
- [ ] Vorgesehene historische Lesezugriffe bleiben erhalten.
- [ ] Andere Reihen und deren Berechtigungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 8.3.6 Berechtigungen einer Reihe verwalten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Das Testkonto ist der richtigen Reihe zugeordnet.
- [ ] Die jeweils ausgewählte Serienrolle wird korrekt angezeigt.
- [ ] Änderungen betreffen nur die ausgewählte Reihe.
- [ ] Die eigene Moderatorzuweisung lässt sich nicht unzulässig selbst entfernen oder herabstufen.
- [ ] Zuweisungen in anderen Reihen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 8.3.7 Fehlende Serienberechtigung prüfen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Fachliche Inhalte der nicht zugewiesenen Reihe werden nicht offengelegt.
- [ ] Direkte URL-Aufrufe zu Terminen und Themen gewähren keinen unberechtigten Zugriff.
- [ ] Die globale Adminrolle und eine Moderatorzuweisung in einer anderen Reihe gewähren keine Rechte für die geprüfte Testreihe.
- [ ] Reihenbearbeitung und Verwaltung der Serienmitglieder werden ohne Moderatorzuweisung für genau diese Reihe verweigert.
- [ ] Die zugewiesene andere Testreihe bleibt für das Admin-Konto gemäß seiner dortigen Moderatorrolle erreichbar.

**Test erfolgreich:** [ ]

---

#### 8.3.8 Globaler Admin mit zusätzlicher Moderatorzuweisung – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

- [ ] Ein globales Admin-Konto verwenden und es für Testreihe A ausdrücklich als Moderator zuweisen.
- [ ] Für Testreihe B keine Serienzuweisung für dieses Konto vergeben.
- [ ] Testreihe A über die Serienverwaltung öffnen und eine zulässige Verwaltungsaktion ausführen.
- [ ] Dieselbe Verwaltungsseite für Testreihe B über die direkte URL aufrufen.
- [ ] Prüfen, ob die globale Adminrolle ohne Serienzuweisung den Zugriff auf Testreihe B erweitert.

**Ergebnisprüfung**

- [ ] In Testreihe A ist die Moderatorverwaltung aufgrund der ausdrücklichen Serienzuweisung möglich.
- [ ] In Testreihe B wird der Zugriff verweigert.
- [ ] Die globale Adminrolle erweitert die Moderatorberechtigung nicht auf andere Reihen.
- [ ] Änderungen an Testreihe A verändern die Berechtigungen von Testreihe B nicht.

**Test erfolgreich:** [ ]

#### 8.3.9 Moderatorzugriff auf eine fremde Reihe verweigern – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff auf die eigene Reihe erlaubt, auf fremde Reihen verweigert.** Mit dem Testkonto muss die eigene zugewiesene Reihe verwaltbar sein. Für die fremde Reihe müssen Navigation, direkte URLs und schreibende Aktionen gesperrt bleiben; Daten und Berechtigungen bleiben unverändert.

- [ ] Ein Moderator-Konto für Testreihe A verwenden.
- [ ] Sicherstellen, dass für Testreihe B keine Zuweisung besteht.
- [ ] Testreihe A über die Serienverwaltung öffnen.
- [ ] Die Verwaltungsübersicht und Bearbeitungsseite von Testreihe B über direkte URLs aufrufen.
- [ ] Eine schreibende Aktion für Testreihe B über die direkte URL bzw. POST-Anfrage versuchen.

**Ergebnisprüfung**

- [ ] Testreihe A kann verwaltet werden.
- [ ] Testreihe B ist weder über die Navigation noch über direkte URLs erreichbar.
- [ ] Schreibende Aktionen für Testreihe B werden verweigert.
- [ ] Daten und Berechtigungen von Testreihe B bleiben unverändert.

**Test erfolgreich:** [ ]

### 8.4 Termine und Besprechungsübersicht

#### 8.4.1 Terminübersicht aufrufen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Termine der berechtigten Reihen werden angezeigt.
- [ ] Datum und Reihenbezeichnung stimmen.
- [ ] Vergangene und zukünftige Termine sind entsprechend gekennzeichnet bzw. erreichbar.
- [ ] Termine nicht zugewiesener Reihen werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 8.4.2 Einzelnen Termin verschieben – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Termin wird am neuen Datum angezeigt.
- [ ] Der bisherige Termin wird nicht zusätzlich als Duplikat angezeigt.
- [ ] Zugehörige Tagesordnungspunkte und Zuständigkeiten bleiben dem Termin zugeordnet.
- [ ] Die übrigen Termine der Reihe entsprechen weiterhin dem vorgesehenen Rhythmus.

**Test erfolgreich:** [ ]

#### 8.4.3 Einzelnen Termin löschen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der ausgewählte Termin wird entsprechend der Löschfunktion entfernt.
- [ ] Nicht ausgewählte Termine bleiben erhalten.
- [ ] Themen und historische Inhalte werden entsprechend den vorgesehenen Regeln behandelt.
- [ ] Es bleiben keine ungewollten Zuordnungen oder doppelten Einträge zurück.

**Test erfolgreich:** [ ]

#### 8.4.4 Teilnehmerliste bearbeiten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die ausgewählten Konten werden in der Teilnehmerliste angezeigt.
- [ ] Abgewählte Konten werden nicht mehr angezeigt.
- [ ] Die Änderung betrifft nur den ausgewählten Termin.
- [ ] Die Serienberechtigungen der Konten bleiben unverändert.

**Test erfolgreich:** [ ]

#### 8.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**- [ ] Abgeschlossene Inhalte sind nicht durch Teilnehmer*innen oder Leser*innen veränderbar.
- [ ] Der gespeicherte Protokollstand bleibt unverändert.- [ ] Die Anzeige des abgeschlossenen Termins bleibt möglich, sofern die Serienberechtigung dies erlaubt.
**Test erfolgreich:** [ ]

---

### 8.5 Themen anlegen und bearbeiten

#### 8.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Das Thema erscheint in der Themenübersicht.
- [ ] Titel und Hauptzuständigkeit entsprechen den Eingaben.
- [ ] Das Thema ist der ausgewählten Besprechungsreihe zugeordnet.
- [ ] Für den ausgewählten Termin ist der zugehörige Tagesordnungspunkt vorhanden.
- [ ] Das Thema ist nicht versehentlich in einer anderen Reihe angelegt worden.

**Test erfolgreich:** [ ]

#### 8.5.2 Thema über einen Termin anlegen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Das neue Thema ist angelegt.
- [ ] Der Tagesordnungspunkt ist dem geöffneten Termin zugeordnet.
- [ ] Hauptzuständigkeit und abweichende Zuständigkeit werden getrennt und korrekt angezeigt.
- [ ] Das Thema ist in der Themenübersicht auffindbar.

**Test erfolgreich:** [ ]

#### 8.5.3 Thema bearbeiten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Titel, Status und Hauptzuständigkeit entsprechen den gespeicherten Werten.
- [ ] Änderungen bleiben nach dem Neuladen erhalten.
- [ ] Zugehörige Tagesordnungspunkte und historische Protokollstände bleiben korrekt zugeordnet.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 8.5.4 Themenstatus ändern – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der neue Status wird in der Detailansicht angezeigt.
- [ ] Der Status wird in der Übersicht korrekt dargestellt.
- [ ] Der Status eines einzelnen Tagesordnungspunkts wird nicht unbeabsichtigt mitgeändert.

**Test erfolgreich:** [ ]

#### 8.5.5 Thema archivieren und wieder öffnen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Archivierte Themen erscheinen im Archiv und nicht mehr in der regulären offenen Themenliste.
- [ ] Wieder geöffnete Themen erscheinen wieder im vorgesehenen aktiven Bereich.
- [ ] Titel, Zuständigkeit, Kommentare und zugehörige historische Inhalte bleiben erhalten.
- [ ] Der Änderungsverlauf bildet die Aktion ab.

**Test erfolgreich:** [ ]

#### 8.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Das Thema ist der vorgesehenen Zielreihe zugeordnet.
- [ ] Der vorgesehene Zieltermin enthält den Tagesordnungspunkt.
- [ ] Übertragungsnotiz und Übertragungsverlauf sind nachvollziehbar.
- [ ] Quell- und Zielberechtigungen werden nicht unbeabsichtigt ausgeweitet.
- [ ] Andere Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 8.5.7 Themenvorschläge verwenden – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der ausgewählte Vorschlag wird korrekt übernommen.
- [ ] Das Thema bzw. der Tagesordnungspunkt wird mit den eingegebenen Daten angelegt.
- [ ] Es wird kein zusätzlicher oder doppelter Datensatz angelegt.

**Test erfolgreich:** [ ]

---

### 8.6 Tagesordnungspunkte und Wiedervorlagen

#### 8.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der terminbezogene Text wird korrekt angezeigt.
- [ ] Der Status des Tagesordnungspunkts entspricht der Auswahl.
- [ ] Eine abweichende Zuständigkeit wird korrekt angezeigt.
- [ ] Der allgemeine Themenstatus bleibt davon getrennt.

**Test erfolgreich:** [ ]

#### 8.6.2 Tagesordnungspunkte sortieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Reihenfolge entspricht der zuletzt vorgenommenen Sortierung.
- [ ] Jeder Tagesordnungspunkt ist weiterhin dem richtigen Thema zugeordnet.
- [ ] Es fehlen keine Punkte und es sind keine Duplikate entstanden.

**Test erfolgreich:** [ ]

#### 8.6.3 Tagesordnungspunkt entfernen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Punkt ist aus dem ausgewählten Termin entfernt.
- [ ] Das Thema selbst bleibt entsprechend der vorgesehenen Datenregel erhalten.
- [ ] Andere Tagesordnungspunkte bleiben unverändert.

**Test erfolgreich:** [ ]

#### 8.6.4 Wiedervorlage anlegen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Tagesordnungspunkt erscheint im vorgesehenen Zieltermin.
- [ ] Die Verbindung zum vorherigen Tagesordnungspunkt ist nachvollziehbar.
- [ ] Status und Zuständigkeit entsprechen den vorgesehenen Übernahmeregeln.
- [ ] Es ist keine doppelte Wiedervorlage entstanden.

**Test erfolgreich:** [ ]

#### 8.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Wiedervorlagekette ist chronologisch nachvollziehbar.
- [ ] Jeder Punkt ist dem richtigen Termin zugeordnet.
- [ ] Frühere Protokollstände bleiben unverändert.
- [ ] Es entstehen keine doppelten oder voneinander getrennten Ketten.

**Test erfolgreich:** [ ]

#### 8.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Datum, Reihenbezeichnung, Text, Status und Verantwortlichkeit werden dem historischen Eintrag entsprechend angezeigt.
- [ ] Historische Einträge lassen sich nicht unberechtigt verändern.
- [ ] Zugriff ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 8.7 Kommentare, Anlagen und Links

#### 8.7.1 Kommentar hinzufügen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Kommentar wird beim richtigen Thema angezeigt.
- [ ] Autor und Erstellungszeitpunkt werden korrekt angezeigt.
- [ ] Der Kommentar bleibt nach dem Neuladen erhalten.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 8.7.2 Datei als Themenanlage hochladen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Anlage wird beim richtigen Thema angezeigt.
- [ ] Bezeichnung und Datei sind korrekt zugeordnet.
- [ ] Die Datei lässt sich mit einem berechtigten Konto herunterladen.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 8.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der eingetragene Pfad bzw. Link wird korrekt angezeigt.
- [ ] Unterstützte Pfade werden entsprechend der Anwendung als Link dargestellt.
- [ ] Nicht unterstützte oder ungültige Werte werden nicht als unsichere Links ausgegeben.
- [ ] Die Anwendung behauptet nicht, die Erreichbarkeit einer externen Freigabe zu garantieren.

**Test erfolgreich:** [ ]

#### 8.7.4 Anlage herunterladen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Berechtigte Konten können die zugehörige Datei herunterladen.
- [ ] Dateiinhalt und Dateiname entsprechen der hochgeladenen Datei.
- [ ] Nicht berechtigte Konten erhalten keinen Dateizugriff.

**Test erfolgreich:** [ ]

#### 8.7.5 Anlage löschen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die Anlage wird nicht mehr in der Themenansicht angezeigt.
- [ ] Der direkte Download der entfernten Anlage ist nicht mehr möglich.
- [ ] Andere Anlagen und Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 8.7.6 Upload-Grenzen prüfen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Zulässige Dateien innerhalb des Limits werden angenommen.
- [ ] Zu große Dateien werden abgewiesen.
- [ ] Nicht erlaubte Dateiendungen werden abgewiesen.
- [ ] Abgewiesene Uploads erzeugen keine ungewollten Anlagen-Datensätze.

**Test erfolgreich:** [ ]

---

### 8.8 Besprechung abschließen und Protokoll

#### 8.8.1 Besprechung abschließen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Termin ist als abgeschlossen gekennzeichnet.
- [ ] Ein Protokoll-Snapshot wurde erstellt.
- [ ] Teilnehmerliste und Tagesordnungstexte sind gegen weitere Bearbeitung gesperrt.
- [ ] Der Abschluss wird im Änderungsverlauf dokumentiert.

**Test erfolgreich:** [ ]

#### 8.8.2 Protokoll anzeigen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Protokoll zeigt den beim Abschluss gesicherten Stand.
- [ ] Historische Werte werden nicht durch spätere Änderungen am Thema überschrieben.
- [ ] Protokoll ist für berechtigte Leser*innen sichtbar.

**Test erfolgreich:** [ ]

#### 8.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Druckansicht enthält den richtigen Termin und Protokollstand.
- [ ] PDF lässt sich öffnen.
- [ ] PDF enthält die vorgesehenen Protokolldaten.
- [ ] Organisationsbezeichnung und Logo erscheinen entsprechend der Konfiguration.
- [ ] Unberechtigte Konten können den Export nicht abrufen.

**Test erfolgreich:** [ ]

#### 8.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Termin ist nach dem Wiederöffnen bearbeitbar.
- [ ] Der vorherige Protokollstand bleibt als historischer Stand nachvollziehbar.
- [ ] Die erneute Bearbeitung und der erneute Abschluss funktionieren.
- [ ] Teilnehmer*innen ohne Moderatorrechte können den Termin nicht wieder öffnen.

**Test erfolgreich:** [ ]

#### 8.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] PDF enthält die dem Thema zugeordneten historischen Einträge.
- [ ] Datum, Reihe, Texte und Statuswerte sind korrekt.
- [ ] Der Export ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 8.9 Offene Themen und Archiv

#### 8.9.1 Offene Themen aufrufen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Nur fachlich zugängliche Themen werden angezeigt.
- [ ] Status, Zuständigkeit und Besprechungsreihe werden korrekt angezeigt.
- [ ] Auswahl und Filter führen zu passenden Ergebnissen.

**Test erfolgreich:** [ ]

#### 8.9.2 Archiv aufrufen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Archivierte Themen sind im Archiv auffindbar.
- [ ] Historische Inhalte werden entsprechend der Berechtigung angezeigt.
- [ ] Nicht archivierte Themen werden nicht fälschlich als archiviert dargestellt.

**Test erfolgreich:** [ ]

#### 8.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der vorgesehene historische Lesezugriff des früheren Reihenmitglieds bleibt bestehen.
- [ ] Das unbeteiligte Konto erhält keinen Zugriff.
- [ ] Gelöschte aktive Reihenfunktionen werden nicht unbeabsichtigt wieder verfügbar.

**Test erfolgreich:** [ ]

---

### 8.10 Berechtigungsanträge

#### 8.10.1 Serienberechtigung beantragen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Antrag wird der richtigen Person und Besprechungsreihe zugeordnet.
- [ ] Gewünschte Rolle wird korrekt angezeigt.
- [ ] Der Antrag erscheint mit offenem Status.
- [ ] Durch den Antrag allein entstehen noch keine fachlichen Schreibrechte.

**Test erfolgreich:** [ ]

#### 8.10.2 Berechtigungsantrag entscheiden – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

#### 8.10.3 Bereits vorhandenen Antrag erneut bearbeiten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Es entstehen keine unzulässigen doppelten offenen Anträge.
- [ ] Bereits entschiedene Anträge werden nicht irrtümlich als offen behandelt.
- [ ] Die bestehende Serienzuweisung wird nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

---

### 8.11 Benutzer- und Themenimport/-export

#### 8.11.1 Benutzer als CSV exportieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Exportdatei ist lesbar.
- [ ] Enthaltene Konten und Felder entsprechen dem vorgesehenen Exportumfang.
- [ ] Passwörter oder andere nicht exportierbare Geheimnisse sind nicht enthalten.

**Test erfolgreich:** [ ]

#### 8.11.2 Benutzer per CSV importieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Gültige Testkonten werden angelegt bzw. entsprechend der Importregel verarbeitet.
- [ ] Fehlerhafte Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Vorhandene Konten werden nicht ungewollt überschrieben.
- [ ] Serienzuweisungen werden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 8.11.3 Themen als CSV exportieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Export ist lesbar und enthält die vorgesehenen Themen.
- [ ] Zuständigkeiten, Status und Reihenbezüge sind korrekt.
- [ ] Inhalte außerhalb des zulässigen Berechtigungs- bzw. Exportumfangs werden nicht offengelegt.

**Test erfolgreich:** [ ]

#### 8.11.4 Themen per CSV importieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Gültige Testthemen werden entsprechend der Importregeln angelegt bzw. verarbeitet.
- [ ] Ungültige Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Reihenbezüge und Zuständigkeiten sind korrekt.
- [ ] Es entstehen keine unbeabsichtigten Duplikate.

**Test erfolgreich:** [ ]

---

### 8.12 Änderungsverlauf und Audit

#### 8.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Moderator*in sieht die Ereignisse der eigenen moderierten Reihe.
- [ ] Ereignisse anderer Reihen werden nicht offengelegt.
- [ ] Akteur, Zeitpunkt und Aktion sind nachvollziehbar.
- [ ] Unberechtigte Konten erhalten keinen Zugriff.

**Test erfolgreich:** [ ]

#### 8.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Admin und Auditor*in können die vorgesehenen Systemereignisse einsehen.
- [ ] Auditor*in kann keine Änderungsaktionen ausführen.
- [ ] Normale Nutzerkonten erhalten keinen unberechtigten Systemzugriff.
- [ ] Fachliche Reihenereignisse werden nicht unberechtigt in der Systemhistorie offengelegt.

**Test erfolgreich:** [ ]

#### 8.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] CSV-Datei ist lesbar.
- [ ] Export enthält nur die für die Rolle zulässigen Ereignisse.
- [ ] Direkter Exportaufruf ohne passende Berechtigung wird abgewiesen.
- [ ] Nicht erforderliche vertrauliche Daten werden nicht exportiert.

**Test erfolgreich:** [ ]

---

### 8.13 Aufbewahrung und automatische Löschung

#### 8.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Nicht abgelaufene Termine und Protokolle bleiben erhalten.
- [ ] Abgelaufene abgeschlossene Termine und Protokolle werden gemäß der Frist entfernt.
- [ ] Tagesordnungshistorie, die laut Fachregel am Thema erhalten bleiben muss, bleibt korrekt erhalten.
- [ ] Nicht abgeschlossene bzw. wieder geöffnete Termine werden nicht unberechtigt gelöscht.

**Test erfolgreich:** [ ]

#### 8.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Thema bleibt vor Fristablauf erhalten.
- [ ] Abgelaufenes archiviertes Thema wird gemäß der Fachregel endgültig entfernt.
- [ ] Zugehörige Inhalte und Dateien werden entsprechend der Löschregel behandelt.
- [ ] Nicht abgelaufene oder nicht archivierte Themen bleiben erhalten.

**Test erfolgreich:** [ ]

#### 8.13.3 Retention wiederholt ausführen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Wiederholte Ausführung erzeugt keine doppelten Löschvorgänge oder inkonsistenten Datensätze.
- [ ] Nicht abgelaufene Daten bleiben erhalten.
- [ ] Fehler einzelner Datensätze führen nicht zu unbemerkter Fehlbehandlung des gesamten Bestands.

**Test erfolgreich:** [ ]

---

### 8.14 Auditor*innenbereich

#### 8.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die vorgesehenen administrativen Prüfdaten sind lesbar.
- [ ] Startpasswort und andere Geheimnisse werden nicht angezeigt.
- [ ] Es bestehen keine Änderungsfunktionen für Auditor*innen.
- [ ] Fachliche Besprechungsreihen und Themeninhalte sind nicht zugänglich.

**Test erfolgreich:** [ ]

#### 8.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Lesender Zugriff auf ausdrücklich freigegebene administrative Prüfdaten ist möglich.
- [ ] Fachliche Inhalte sind nicht zugänglich.
- [ ] Schreibende Aktionen sind nicht möglich.
- [ ] Direkte URLs umgehen die Rollenbegrenzung nicht.

**Test erfolgreich:** [ ]

---

---

## 9. Produktiv – Globale Rolle Admin

Ein globales Admin-Konto verwenden, dem für die geprüfte Bestandsreihe ausdrücklich keine Serienrolle zugewiesen ist. Wo der Test eine Serienrolle voraussetzt, zusätzlich einen getrennten Kontrolllauf mit Admin plus Moderatorzuweisung durchführen.

**Verbindliche Durchführung für diese Rollengruppe**

- Alle folgenden Funktionsbereiche und Testfälle sind aus Sicht dieses Kontos durchzuführen.
- Bei erlaubten Aktionen muss die Funktion vollständig und mit korrektem Ergebnis funktionieren.
- Bei nicht erlaubten Aktionen den Aufruf über Navigation, direkte URL und – soweit möglich – direkte POST-Anfrage versuchen. Erwartet wird eine verweigerte Antwort (403/404 oder vorgesehene Umleitung), keine Datenänderung und keine Offenlegung geschützter Inhalte.
- Die nachfolgende Einzelprüfung nennt jeweils, ob die Rolle laut Berechtigungsmodell zugriffsberechtigt ist. Bei Serienfunktionen gilt die Berechtigung ausschließlich für die konkret zugewiesene Reihe.

### 9.1 Dashboard und Navigation

#### 9.1.1 Dashboard aufrufen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 9.1.2 Navigation und Darstellungsvarianten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Die gewählte Darstellungsvariante bleibt entsprechend der Anwendungseinstellung erhalten.

**Test erfolgreich:** [ ]

---

### 9.2 Persönliches Konto und eigene Aufgaben

#### 9.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 9.2.2 Eigene Aufgaben aufrufen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Eigene offene Themen werden im vorgesehenen Abschnitt angezeigt.
- [ ] Eigene Tagesordnungspunkte werden getrennt davon angezeigt.
- [ ] Nicht zugewiesene oder nicht berechtigte Inhalte werden nicht zusätzlich eingeblendet.
- [ ] Bei fehlenden Aufgaben wird ein geeigneter Leerzustand angezeigt.

**Test erfolgreich:** [ ]

---

### 9.3 Besprechungsreihen verwalten

#### 9.3.1 Besprechungsreihe anlegen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die neue Besprechungsreihe erscheint in der Übersicht.
- [ ] Bezeichnung, Beschreibung und Wiederholungseinstellungen entsprechen den Eingaben.
- [ ] Zugehörige Termine werden entsprechend Startdatum, Rhythmus, Intervall und Enddatum erzeugt.
- [ ] Die erstellende Moderatorin bzw. der erstellende Moderator besitzt die vorgesehene Serienzuweisung.
- [ ] Andere Serienzuweisungen wurden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 9.3.2 Besprechungsreihe bearbeiten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Geänderte Werte werden angezeigt.
- [ ] Nicht geänderte Werte bleiben erhalten.
- [ ] Bestehende Serienberechtigungen bleiben erhalten.
- [ ] Bereits vorhandene Termine und Themen sind weiterhin dem richtigen fachlichen Kontext zugeordnet.

**Test erfolgreich:** [ ]

#### 9.3.3 Besprechungsreihe verlängern – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Zusätzliche Termine werden bis zum neuen Enddatum erzeugt.
- [ ] Bereits vorhandene Termine bleiben erhalten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 9.3.4 Termine einer Reihe neu aufsetzen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Terminfolge entspricht den eingestellten Seriendaten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Bestehende Themen, Tagesordnungspunkte und Serienberechtigungen entsprechen den vorgesehenen Regeln.
- [ ] Nicht ausgewählte Reihen sind unverändert.

**Test erfolgreich:** [ ]

#### 9.3.5 Besprechungsreihe löschen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Reihe wird nicht mehr als aktive Reihe angeboten.
- [ ] Historische Inhalte werden entsprechend der gewählten Löschvariante behandelt.
- [ ] Vorgesehene historische Lesezugriffe bleiben erhalten.
- [ ] Andere Reihen und deren Berechtigungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 9.3.6 Berechtigungen einer Reihe verwalten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das Testkonto ist der richtigen Reihe zugeordnet.
- [ ] Die jeweils ausgewählte Serienrolle wird korrekt angezeigt.
- [ ] Änderungen betreffen nur die ausgewählte Reihe.
- [ ] Die eigene Moderatorzuweisung lässt sich nicht unzulässig selbst entfernen oder herabstufen.
- [ ] Zuweisungen in anderen Reihen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 9.3.7 Fehlende Serienberechtigung prüfen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Fachliche Inhalte der nicht zugewiesenen Reihe werden nicht offengelegt.
- [ ] Direkte URL-Aufrufe zu Terminen und Themen gewähren keinen unberechtigten Zugriff.
- [ ] Die globale Adminrolle und eine Moderatorzuweisung in einer anderen Reihe gewähren keine Rechte für die geprüfte Testreihe.
- [ ] Reihenbearbeitung und Verwaltung der Serienmitglieder werden ohne Moderatorzuweisung für genau diese Reihe verweigert.
- [ ] Die zugewiesene andere Testreihe bleibt für das Admin-Konto gemäß seiner dortigen Moderatorrolle erreichbar.

**Test erfolgreich:** [ ]

---

#### 9.3.8 Globaler Admin mit zusätzlicher Moderatorzuweisung – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

- [ ] Ein globales Admin-Konto verwenden und es für Testreihe A ausdrücklich als Moderator zuweisen.
- [ ] Für Testreihe B keine Serienzuweisung für dieses Konto vergeben.
- [ ] Testreihe A über die Serienverwaltung öffnen und eine zulässige Verwaltungsaktion ausführen.
- [ ] Dieselbe Verwaltungsseite für Testreihe B über die direkte URL aufrufen.
- [ ] Prüfen, ob die globale Adminrolle ohne Serienzuweisung den Zugriff auf Testreihe B erweitert.

**Ergebnisprüfung**

- [ ] In Testreihe A ist die Moderatorverwaltung aufgrund der ausdrücklichen Serienzuweisung möglich.
- [ ] In Testreihe B wird der Zugriff verweigert.
- [ ] Die globale Adminrolle erweitert die Moderatorberechtigung nicht auf andere Reihen.
- [ ] Änderungen an Testreihe A verändern die Berechtigungen von Testreihe B nicht.

**Test erfolgreich:** [ ]

#### 9.3.9 Moderatorzugriff auf eine fremde Reihe verweigern – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

- [ ] Ein Moderator-Konto für Testreihe A verwenden.
- [ ] Sicherstellen, dass für Testreihe B keine Zuweisung besteht.
- [ ] Testreihe A über die Serienverwaltung öffnen.
- [ ] Die Verwaltungsübersicht und Bearbeitungsseite von Testreihe B über direkte URLs aufrufen.
- [ ] Eine schreibende Aktion für Testreihe B über die direkte URL bzw. POST-Anfrage versuchen.

**Ergebnisprüfung**

- [ ] Testreihe A kann verwaltet werden.
- [ ] Testreihe B ist weder über die Navigation noch über direkte URLs erreichbar.
- [ ] Schreibende Aktionen für Testreihe B werden verweigert.
- [ ] Daten und Berechtigungen von Testreihe B bleiben unverändert.

**Test erfolgreich:** [ ]

### 9.4 Termine und Besprechungsübersicht

#### 9.4.1 Terminübersicht aufrufen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Termine der berechtigten Reihen werden angezeigt.
- [ ] Datum und Reihenbezeichnung stimmen.
- [ ] Vergangene und zukünftige Termine sind entsprechend gekennzeichnet bzw. erreichbar.
- [ ] Termine nicht zugewiesener Reihen werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 9.4.2 Einzelnen Termin verschieben – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Termin wird am neuen Datum angezeigt.
- [ ] Der bisherige Termin wird nicht zusätzlich als Duplikat angezeigt.
- [ ] Zugehörige Tagesordnungspunkte und Zuständigkeiten bleiben dem Termin zugeordnet.
- [ ] Die übrigen Termine der Reihe entsprechen weiterhin dem vorgesehenen Rhythmus.

**Test erfolgreich:** [ ]

#### 9.4.3 Einzelnen Termin löschen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der ausgewählte Termin wird entsprechend der Löschfunktion entfernt.
- [ ] Nicht ausgewählte Termine bleiben erhalten.
- [ ] Themen und historische Inhalte werden entsprechend den vorgesehenen Regeln behandelt.
- [ ] Es bleiben keine ungewollten Zuordnungen oder doppelten Einträge zurück.

**Test erfolgreich:** [ ]

#### 9.4.4 Teilnehmerliste bearbeiten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die ausgewählten Konten werden in der Teilnehmerliste angezeigt.
- [ ] Abgewählte Konten werden nicht mehr angezeigt.
- [ ] Die Änderung betrifft nur den ausgewählten Termin.
- [ ] Die Serienberechtigungen der Konten bleiben unverändert.

**Test erfolgreich:** [ ]

#### 9.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**- [ ] Abgeschlossene Inhalte sind nicht durch Teilnehmer*innen oder Leser*innen veränderbar.
- [ ] Der gespeicherte Protokollstand bleibt unverändert.- [ ] Die Anzeige des abgeschlossenen Termins bleibt möglich, sofern die Serienberechtigung dies erlaubt.
**Test erfolgreich:** [ ]

---

### 9.5 Themen anlegen und bearbeiten

#### 9.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das Thema erscheint in der Themenübersicht.
- [ ] Titel und Hauptzuständigkeit entsprechen den Eingaben.
- [ ] Das Thema ist der ausgewählten Besprechungsreihe zugeordnet.
- [ ] Für den ausgewählten Termin ist der zugehörige Tagesordnungspunkt vorhanden.
- [ ] Das Thema ist nicht versehentlich in einer anderen Reihe angelegt worden.

**Test erfolgreich:** [ ]

#### 9.5.2 Thema über einen Termin anlegen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das neue Thema ist angelegt.
- [ ] Der Tagesordnungspunkt ist dem geöffneten Termin zugeordnet.
- [ ] Hauptzuständigkeit und abweichende Zuständigkeit werden getrennt und korrekt angezeigt.
- [ ] Das Thema ist in der Themenübersicht auffindbar.

**Test erfolgreich:** [ ]

#### 9.5.3 Thema bearbeiten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Titel, Status und Hauptzuständigkeit entsprechen den gespeicherten Werten.
- [ ] Änderungen bleiben nach dem Neuladen erhalten.
- [ ] Zugehörige Tagesordnungspunkte und historische Protokollstände bleiben korrekt zugeordnet.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 9.5.4 Themenstatus ändern – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der neue Status wird in der Detailansicht angezeigt.
- [ ] Der Status wird in der Übersicht korrekt dargestellt.
- [ ] Der Status eines einzelnen Tagesordnungspunkts wird nicht unbeabsichtigt mitgeändert.

**Test erfolgreich:** [ ]

#### 9.5.5 Thema archivieren und wieder öffnen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Archivierte Themen erscheinen im Archiv und nicht mehr in der regulären offenen Themenliste.
- [ ] Wieder geöffnete Themen erscheinen wieder im vorgesehenen aktiven Bereich.
- [ ] Titel, Zuständigkeit, Kommentare und zugehörige historische Inhalte bleiben erhalten.
- [ ] Der Änderungsverlauf bildet die Aktion ab.

**Test erfolgreich:** [ ]

#### 9.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das Thema ist der vorgesehenen Zielreihe zugeordnet.
- [ ] Der vorgesehene Zieltermin enthält den Tagesordnungspunkt.
- [ ] Übertragungsnotiz und Übertragungsverlauf sind nachvollziehbar.
- [ ] Quell- und Zielberechtigungen werden nicht unbeabsichtigt ausgeweitet.
- [ ] Andere Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 9.5.7 Themenvorschläge verwenden – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der ausgewählte Vorschlag wird korrekt übernommen.
- [ ] Das Thema bzw. der Tagesordnungspunkt wird mit den eingegebenen Daten angelegt.
- [ ] Es wird kein zusätzlicher oder doppelter Datensatz angelegt.

**Test erfolgreich:** [ ]

---

### 9.6 Tagesordnungspunkte und Wiedervorlagen

#### 9.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der terminbezogene Text wird korrekt angezeigt.
- [ ] Der Status des Tagesordnungspunkts entspricht der Auswahl.
- [ ] Eine abweichende Zuständigkeit wird korrekt angezeigt.
- [ ] Der allgemeine Themenstatus bleibt davon getrennt.

**Test erfolgreich:** [ ]

#### 9.6.2 Tagesordnungspunkte sortieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Reihenfolge entspricht der zuletzt vorgenommenen Sortierung.
- [ ] Jeder Tagesordnungspunkt ist weiterhin dem richtigen Thema zugeordnet.
- [ ] Es fehlen keine Punkte und es sind keine Duplikate entstanden.

**Test erfolgreich:** [ ]

#### 9.6.3 Tagesordnungspunkt entfernen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Punkt ist aus dem ausgewählten Termin entfernt.
- [ ] Das Thema selbst bleibt entsprechend der vorgesehenen Datenregel erhalten.
- [ ] Andere Tagesordnungspunkte bleiben unverändert.

**Test erfolgreich:** [ ]

#### 9.6.4 Wiedervorlage anlegen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Tagesordnungspunkt erscheint im vorgesehenen Zieltermin.
- [ ] Die Verbindung zum vorherigen Tagesordnungspunkt ist nachvollziehbar.
- [ ] Status und Zuständigkeit entsprechen den vorgesehenen Übernahmeregeln.
- [ ] Es ist keine doppelte Wiedervorlage entstanden.

**Test erfolgreich:** [ ]

#### 9.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Wiedervorlagekette ist chronologisch nachvollziehbar.
- [ ] Jeder Punkt ist dem richtigen Termin zugeordnet.
- [ ] Frühere Protokollstände bleiben unverändert.
- [ ] Es entstehen keine doppelten oder voneinander getrennten Ketten.

**Test erfolgreich:** [ ]

#### 9.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Datum, Reihenbezeichnung, Text, Status und Verantwortlichkeit werden dem historischen Eintrag entsprechend angezeigt.
- [ ] Historische Einträge lassen sich nicht unberechtigt verändern.
- [ ] Zugriff ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 9.7 Kommentare, Anlagen und Links

#### 9.7.1 Kommentar hinzufügen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Kommentar wird beim richtigen Thema angezeigt.
- [ ] Autor und Erstellungszeitpunkt werden korrekt angezeigt.
- [ ] Der Kommentar bleibt nach dem Neuladen erhalten.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 9.7.2 Datei als Themenanlage hochladen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Anlage wird beim richtigen Thema angezeigt.
- [ ] Bezeichnung und Datei sind korrekt zugeordnet.
- [ ] Die Datei lässt sich mit einem berechtigten Konto herunterladen.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 9.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der eingetragene Pfad bzw. Link wird korrekt angezeigt.
- [ ] Unterstützte Pfade werden entsprechend der Anwendung als Link dargestellt.
- [ ] Nicht unterstützte oder ungültige Werte werden nicht als unsichere Links ausgegeben.
- [ ] Die Anwendung behauptet nicht, die Erreichbarkeit einer externen Freigabe zu garantieren.

**Test erfolgreich:** [ ]

#### 9.7.4 Anlage herunterladen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Berechtigte Konten können die zugehörige Datei herunterladen.
- [ ] Dateiinhalt und Dateiname entsprechen der hochgeladenen Datei.
- [ ] Nicht berechtigte Konten erhalten keinen Dateizugriff.

**Test erfolgreich:** [ ]

#### 9.7.5 Anlage löschen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Anlage wird nicht mehr in der Themenansicht angezeigt.
- [ ] Der direkte Download der entfernten Anlage ist nicht mehr möglich.
- [ ] Andere Anlagen und Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 9.7.6 Upload-Grenzen prüfen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Zulässige Dateien innerhalb des Limits werden angenommen.
- [ ] Zu große Dateien werden abgewiesen.
- [ ] Nicht erlaubte Dateiendungen werden abgewiesen.
- [ ] Abgewiesene Uploads erzeugen keine ungewollten Anlagen-Datensätze.

**Test erfolgreich:** [ ]

---

### 9.8 Besprechung abschließen und Protokoll

#### 9.8.1 Besprechung abschließen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Termin ist als abgeschlossen gekennzeichnet.
- [ ] Ein Protokoll-Snapshot wurde erstellt.
- [ ] Teilnehmerliste und Tagesordnungstexte sind gegen weitere Bearbeitung gesperrt.
- [ ] Der Abschluss wird im Änderungsverlauf dokumentiert.

**Test erfolgreich:** [ ]

#### 9.8.2 Protokoll anzeigen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Protokoll zeigt den beim Abschluss gesicherten Stand.
- [ ] Historische Werte werden nicht durch spätere Änderungen am Thema überschrieben.
- [ ] Protokoll ist für berechtigte Leser*innen sichtbar.

**Test erfolgreich:** [ ]

#### 9.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Druckansicht enthält den richtigen Termin und Protokollstand.
- [ ] PDF lässt sich öffnen.
- [ ] PDF enthält die vorgesehenen Protokolldaten.
- [ ] Organisationsbezeichnung und Logo erscheinen entsprechend der Konfiguration.
- [ ] Unberechtigte Konten können den Export nicht abrufen.

**Test erfolgreich:** [ ]

#### 9.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Der Termin ist nach dem Wiederöffnen bearbeitbar.
- [ ] Der vorherige Protokollstand bleibt als historischer Stand nachvollziehbar.
- [ ] Die erneute Bearbeitung und der erneute Abschluss funktionieren.
- [ ] Teilnehmer*innen ohne Moderatorrechte können den Termin nicht wieder öffnen.

**Test erfolgreich:** [ ]

#### 9.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] PDF enthält die dem Thema zugeordneten historischen Einträge.
- [ ] Datum, Reihe, Texte und Statuswerte sind korrekt.
- [ ] Der Export ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 9.9 Offene Themen und Archiv

#### 9.9.1 Offene Themen aufrufen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Nur fachlich zugängliche Themen werden angezeigt.
- [ ] Status, Zuständigkeit und Besprechungsreihe werden korrekt angezeigt.
- [ ] Auswahl und Filter führen zu passenden Ergebnissen.

**Test erfolgreich:** [ ]

#### 9.9.2 Archiv aufrufen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Archivierte Themen sind im Archiv auffindbar.
- [ ] Historische Inhalte werden entsprechend der Berechtigung angezeigt.
- [ ] Nicht archivierte Themen werden nicht fälschlich als archiviert dargestellt.

**Test erfolgreich:** [ ]

#### 9.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der vorgesehene historische Lesezugriff des früheren Reihenmitglieds bleibt bestehen.
- [ ] Das unbeteiligte Konto erhält keinen Zugriff.
- [ ] Gelöschte aktive Reihenfunktionen werden nicht unbeabsichtigt wieder verfügbar.

**Test erfolgreich:** [ ]

---

### 9.10 Berechtigungsanträge

#### 9.10.1 Serienberechtigung beantragen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Antrag wird der richtigen Person und Besprechungsreihe zugeordnet.
- [ ] Gewünschte Rolle wird korrekt angezeigt.
- [ ] Der Antrag erscheint mit offenem Status.
- [ ] Durch den Antrag allein entstehen noch keine fachlichen Schreibrechte.

**Test erfolgreich:** [ ]

#### 9.10.2 Berechtigungsantrag entscheiden – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

#### 9.10.3 Bereits vorhandenen Antrag erneut bearbeiten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Es entstehen keine unzulässigen doppelten offenen Anträge.
- [ ] Bereits entschiedene Anträge werden nicht irrtümlich als offen behandelt.
- [ ] Die bestehende Serienzuweisung wird nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

---

### 9.11 Benutzer- und Themenimport/-export

#### 9.11.1 Benutzer als CSV exportieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Exportdatei ist lesbar.
- [ ] Enthaltene Konten und Felder entsprechen dem vorgesehenen Exportumfang.
- [ ] Passwörter oder andere nicht exportierbare Geheimnisse sind nicht enthalten.

**Test erfolgreich:** [ ]

#### 9.11.2 Benutzer per CSV importieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Gültige Testkonten werden angelegt bzw. entsprechend der Importregel verarbeitet.
- [ ] Fehlerhafte Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Vorhandene Konten werden nicht ungewollt überschrieben.
- [ ] Serienzuweisungen werden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 9.11.3 Themen als CSV exportieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Export ist lesbar und enthält die vorgesehenen Themen.
- [ ] Zuständigkeiten, Status und Reihenbezüge sind korrekt.
- [ ] Inhalte außerhalb des zulässigen Berechtigungs- bzw. Exportumfangs werden nicht offengelegt.

**Test erfolgreich:** [ ]

#### 9.11.4 Themen per CSV importieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Gültige Testthemen werden entsprechend der Importregeln angelegt bzw. verarbeitet.
- [ ] Ungültige Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Reihenbezüge und Zuständigkeiten sind korrekt.
- [ ] Es entstehen keine unbeabsichtigten Duplikate.

**Test erfolgreich:** [ ]

---

### 9.12 Änderungsverlauf und Audit

#### 9.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Moderator*in sieht die Ereignisse der eigenen moderierten Reihe.
- [ ] Ereignisse anderer Reihen werden nicht offengelegt.
- [ ] Akteur, Zeitpunkt und Aktion sind nachvollziehbar.
- [ ] Unberechtigte Konten erhalten keinen Zugriff.

**Test erfolgreich:** [ ]

#### 9.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Admin und Auditor*in können die vorgesehenen Systemereignisse einsehen.
- [ ] Auditor*in kann keine Änderungsaktionen ausführen.
- [ ] Normale Nutzerkonten erhalten keinen unberechtigten Systemzugriff.
- [ ] Fachliche Reihenereignisse werden nicht unberechtigt in der Systemhistorie offengelegt.

**Test erfolgreich:** [ ]

#### 9.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] CSV-Datei ist lesbar.
- [ ] Export enthält nur die für die Rolle zulässigen Ereignisse.
- [ ] Direkter Exportaufruf ohne passende Berechtigung wird abgewiesen.
- [ ] Nicht erforderliche vertrauliche Daten werden nicht exportiert.

**Test erfolgreich:** [ ]

---

### 9.13 Aufbewahrung und automatische Löschung

#### 9.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Nicht abgelaufene Termine und Protokolle bleiben erhalten.
- [ ] Abgelaufene abgeschlossene Termine und Protokolle werden gemäß der Frist entfernt.
- [ ] Tagesordnungshistorie, die laut Fachregel am Thema erhalten bleiben muss, bleibt korrekt erhalten.
- [ ] Nicht abgeschlossene bzw. wieder geöffnete Termine werden nicht unberechtigt gelöscht.

**Test erfolgreich:** [ ]

#### 9.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Thema bleibt vor Fristablauf erhalten.
- [ ] Abgelaufenes archiviertes Thema wird gemäß der Fachregel endgültig entfernt.
- [ ] Zugehörige Inhalte und Dateien werden entsprechend der Löschregel behandelt.
- [ ] Nicht abgelaufene oder nicht archivierte Themen bleiben erhalten.

**Test erfolgreich:** [ ]

#### 9.13.3 Retention wiederholt ausführen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Wiederholte Ausführung erzeugt keine doppelten Löschvorgänge oder inkonsistenten Datensätze.
- [ ] Nicht abgelaufene Daten bleiben erhalten.
- [ ] Fehler einzelner Datensätze führen nicht zu unbemerkter Fehlbehandlung des gesamten Bestands.

**Test erfolgreich:** [ ]

---

### 9.14 Auditor*innenbereich

#### 9.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die vorgesehenen administrativen Prüfdaten sind lesbar.
- [ ] Startpasswort und andere Geheimnisse werden nicht angezeigt.
- [ ] Es bestehen keine Änderungsfunktionen für Auditor*innen.
- [ ] Fachliche Besprechungsreihen und Themeninhalte sind nicht zugänglich.

**Test erfolgreich:** [ ]

#### 9.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Lesender Zugriff auf ausdrücklich freigegebene administrative Prüfdaten ist möglich.
- [ ] Fachliche Inhalte sind nicht zugänglich.
- [ ] Schreibende Aktionen sind nicht möglich.
- [ ] Direkte URLs umgehen die Rollenbegrenzung nicht.

**Test erfolgreich:** [ ]

---

---

## 10. Produktiv – Globale Rolle Auditor

Ein globales Auditor-Konto verwenden. Auch bei vorhandener zusätzlicher Serienzuweisung darf es keine fachlichen Reiheninhalte sehen oder verändern. Nur ausdrücklich freigegebene administrative Prüfdaten sind lesbar.

**Verbindliche Durchführung für diese Rollengruppe**

- Alle folgenden Funktionsbereiche und Testfälle sind aus Sicht dieses Kontos durchzuführen.
- Bei erlaubten Aktionen muss die Funktion vollständig und mit korrektem Ergebnis funktionieren.
- Bei nicht erlaubten Aktionen den Aufruf über Navigation, direkte URL und – soweit möglich – direkte POST-Anfrage versuchen. Erwartet wird eine verweigerte Antwort (403/404 oder vorgesehene Umleitung), keine Datenänderung und keine Offenlegung geschützter Inhalte.
- Die nachfolgende Einzelprüfung nennt jeweils, ob die Rolle laut Berechtigungsmodell zugriffsberechtigt ist. Bei Serienfunktionen gilt die Berechtigung ausschließlich für die konkret zugewiesene Reihe.

### 10.1 Dashboard und Navigation

#### 10.1.1 Dashboard aufrufen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 10.1.2 Navigation und Darstellungsvarianten – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Die gewählte Darstellungsvariante bleibt entsprechend der Anwendungseinstellung erhalten.

**Test erfolgreich:** [ ]

---

### 10.2 Persönliches Konto und eigene Aufgaben

#### 10.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 10.2.2 Eigene Aufgaben aufrufen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Eigene offene Themen werden im vorgesehenen Abschnitt angezeigt.
- [ ] Eigene Tagesordnungspunkte werden getrennt davon angezeigt.
- [ ] Nicht zugewiesene oder nicht berechtigte Inhalte werden nicht zusätzlich eingeblendet.
- [ ] Bei fehlenden Aufgaben wird ein geeigneter Leerzustand angezeigt.

**Test erfolgreich:** [ ]

---

### 10.3 Besprechungsreihen verwalten

#### 10.3.1 Besprechungsreihe anlegen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die neue Besprechungsreihe erscheint in der Übersicht.
- [ ] Bezeichnung, Beschreibung und Wiederholungseinstellungen entsprechen den Eingaben.
- [ ] Zugehörige Termine werden entsprechend Startdatum, Rhythmus, Intervall und Enddatum erzeugt.
- [ ] Die erstellende Moderatorin bzw. der erstellende Moderator besitzt die vorgesehene Serienzuweisung.
- [ ] Andere Serienzuweisungen wurden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 10.3.2 Besprechungsreihe bearbeiten – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Geänderte Werte werden angezeigt.
- [ ] Nicht geänderte Werte bleiben erhalten.
- [ ] Bestehende Serienberechtigungen bleiben erhalten.
- [ ] Bereits vorhandene Termine und Themen sind weiterhin dem richtigen fachlichen Kontext zugeordnet.

**Test erfolgreich:** [ ]

#### 10.3.3 Besprechungsreihe verlängern – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Zusätzliche Termine werden bis zum neuen Enddatum erzeugt.
- [ ] Bereits vorhandene Termine bleiben erhalten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Serienzuweisungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 10.3.4 Termine einer Reihe neu aufsetzen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Terminfolge entspricht den eingestellten Seriendaten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Bestehende Themen, Tagesordnungspunkte und Serienberechtigungen entsprechen den vorgesehenen Regeln.
- [ ] Nicht ausgewählte Reihen sind unverändert.

**Test erfolgreich:** [ ]

#### 10.3.5 Besprechungsreihe löschen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Reihe wird nicht mehr als aktive Reihe angeboten.
- [ ] Historische Inhalte werden entsprechend der gewählten Löschvariante behandelt.
- [ ] Vorgesehene historische Lesezugriffe bleiben erhalten.
- [ ] Andere Reihen und deren Berechtigungen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 10.3.6 Berechtigungen einer Reihe verwalten – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das Testkonto ist der richtigen Reihe zugeordnet.
- [ ] Die jeweils ausgewählte Serienrolle wird korrekt angezeigt.
- [ ] Änderungen betreffen nur die ausgewählte Reihe.
- [ ] Die eigene Moderatorzuweisung lässt sich nicht unzulässig selbst entfernen oder herabstufen.
- [ ] Zuweisungen in anderen Reihen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 10.3.7 Fehlende Serienberechtigung prüfen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Fachliche Inhalte der nicht zugewiesenen Reihe werden nicht offengelegt.
- [ ] Direkte URL-Aufrufe zu Terminen und Themen gewähren keinen unberechtigten Zugriff.
- [ ] Die globale Adminrolle und eine Moderatorzuweisung in einer anderen Reihe gewähren keine Rechte für die geprüfte Testreihe.
- [ ] Reihenbearbeitung und Verwaltung der Serienmitglieder werden ohne Moderatorzuweisung für genau diese Reihe verweigert.
- [ ] Die zugewiesene andere Testreihe bleibt für das Admin-Konto gemäß seiner dortigen Moderatorrolle erreichbar.

**Test erfolgreich:** [ ]

---

#### 10.3.8 Globaler Admin mit zusätzlicher Moderatorzuweisung – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

- [ ] Ein globales Admin-Konto verwenden und es für Testreihe A ausdrücklich als Moderator zuweisen.
- [ ] Für Testreihe B keine Serienzuweisung für dieses Konto vergeben.
- [ ] Testreihe A über die Serienverwaltung öffnen und eine zulässige Verwaltungsaktion ausführen.
- [ ] Dieselbe Verwaltungsseite für Testreihe B über die direkte URL aufrufen.
- [ ] Prüfen, ob die globale Adminrolle ohne Serienzuweisung den Zugriff auf Testreihe B erweitert.

**Ergebnisprüfung**

- [ ] In Testreihe A ist die Moderatorverwaltung aufgrund der ausdrücklichen Serienzuweisung möglich.
- [ ] In Testreihe B wird der Zugriff verweigert.
- [ ] Die globale Adminrolle erweitert die Moderatorberechtigung nicht auf andere Reihen.
- [ ] Änderungen an Testreihe A verändern die Berechtigungen von Testreihe B nicht.

**Test erfolgreich:** [ ]

#### 10.3.9 Moderatorzugriff auf eine fremde Reihe verweigern – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

- [ ] Ein Moderator-Konto für Testreihe A verwenden.
- [ ] Sicherstellen, dass für Testreihe B keine Zuweisung besteht.
- [ ] Testreihe A über die Serienverwaltung öffnen.
- [ ] Die Verwaltungsübersicht und Bearbeitungsseite von Testreihe B über direkte URLs aufrufen.
- [ ] Eine schreibende Aktion für Testreihe B über die direkte URL bzw. POST-Anfrage versuchen.

**Ergebnisprüfung**

- [ ] Testreihe A kann verwaltet werden.
- [ ] Testreihe B ist weder über die Navigation noch über direkte URLs erreichbar.
- [ ] Schreibende Aktionen für Testreihe B werden verweigert.
- [ ] Daten und Berechtigungen von Testreihe B bleiben unverändert.

**Test erfolgreich:** [ ]

### 10.4 Termine und Besprechungsübersicht

#### 10.4.1 Terminübersicht aufrufen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Termine der berechtigten Reihen werden angezeigt.
- [ ] Datum und Reihenbezeichnung stimmen.
- [ ] Vergangene und zukünftige Termine sind entsprechend gekennzeichnet bzw. erreichbar.
- [ ] Termine nicht zugewiesener Reihen werden nicht angezeigt.

**Test erfolgreich:** [ ]

#### 10.4.2 Einzelnen Termin verschieben – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Termin wird am neuen Datum angezeigt.
- [ ] Der bisherige Termin wird nicht zusätzlich als Duplikat angezeigt.
- [ ] Zugehörige Tagesordnungspunkte und Zuständigkeiten bleiben dem Termin zugeordnet.
- [ ] Die übrigen Termine der Reihe entsprechen weiterhin dem vorgesehenen Rhythmus.

**Test erfolgreich:** [ ]

#### 10.4.3 Einzelnen Termin löschen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der ausgewählte Termin wird entsprechend der Löschfunktion entfernt.
- [ ] Nicht ausgewählte Termine bleiben erhalten.
- [ ] Themen und historische Inhalte werden entsprechend den vorgesehenen Regeln behandelt.
- [ ] Es bleiben keine ungewollten Zuordnungen oder doppelten Einträge zurück.

**Test erfolgreich:** [ ]

#### 10.4.4 Teilnehmerliste bearbeiten – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die ausgewählten Konten werden in der Teilnehmerliste angezeigt.
- [ ] Abgewählte Konten werden nicht mehr angezeigt.
- [ ] Die Änderung betrifft nur den ausgewählten Termin.
- [ ] Die Serienberechtigungen der Konten bleiben unverändert.

**Test erfolgreich:** [ ]

#### 10.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**- [ ] Abgeschlossene Inhalte sind nicht durch Teilnehmer*innen oder Leser*innen veränderbar.
- [ ] Der gespeicherte Protokollstand bleibt unverändert.- [ ] Die Anzeige des abgeschlossenen Termins bleibt möglich, sofern die Serienberechtigung dies erlaubt.
**Test erfolgreich:** [ ]

---

### 10.5 Themen anlegen und bearbeiten

#### 10.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das Thema erscheint in der Themenübersicht.
- [ ] Titel und Hauptzuständigkeit entsprechen den Eingaben.
- [ ] Das Thema ist der ausgewählten Besprechungsreihe zugeordnet.
- [ ] Für den ausgewählten Termin ist der zugehörige Tagesordnungspunkt vorhanden.
- [ ] Das Thema ist nicht versehentlich in einer anderen Reihe angelegt worden.

**Test erfolgreich:** [ ]

#### 10.5.2 Thema über einen Termin anlegen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das neue Thema ist angelegt.
- [ ] Der Tagesordnungspunkt ist dem geöffneten Termin zugeordnet.
- [ ] Hauptzuständigkeit und abweichende Zuständigkeit werden getrennt und korrekt angezeigt.
- [ ] Das Thema ist in der Themenübersicht auffindbar.

**Test erfolgreich:** [ ]

#### 10.5.3 Thema bearbeiten – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Titel, Status und Hauptzuständigkeit entsprechen den gespeicherten Werten.
- [ ] Änderungen bleiben nach dem Neuladen erhalten.
- [ ] Zugehörige Tagesordnungspunkte und historische Protokollstände bleiben korrekt zugeordnet.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 10.5.4 Themenstatus ändern – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der neue Status wird in der Detailansicht angezeigt.
- [ ] Der Status wird in der Übersicht korrekt dargestellt.
- [ ] Der Status eines einzelnen Tagesordnungspunkts wird nicht unbeabsichtigt mitgeändert.

**Test erfolgreich:** [ ]

#### 10.5.5 Thema archivieren und wieder öffnen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Archivierte Themen erscheinen im Archiv und nicht mehr in der regulären offenen Themenliste.
- [ ] Wieder geöffnete Themen erscheinen wieder im vorgesehenen aktiven Bereich.
- [ ] Titel, Zuständigkeit, Kommentare und zugehörige historische Inhalte bleiben erhalten.
- [ ] Der Änderungsverlauf bildet die Aktion ab.

**Test erfolgreich:** [ ]

#### 10.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Das Thema ist der vorgesehenen Zielreihe zugeordnet.
- [ ] Der vorgesehene Zieltermin enthält den Tagesordnungspunkt.
- [ ] Übertragungsnotiz und Übertragungsverlauf sind nachvollziehbar.
- [ ] Quell- und Zielberechtigungen werden nicht unbeabsichtigt ausgeweitet.
- [ ] Andere Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 10.5.7 Themenvorschläge verwenden – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der ausgewählte Vorschlag wird korrekt übernommen.
- [ ] Das Thema bzw. der Tagesordnungspunkt wird mit den eingegebenen Daten angelegt.
- [ ] Es wird kein zusätzlicher oder doppelter Datensatz angelegt.

**Test erfolgreich:** [ ]

---

### 10.6 Tagesordnungspunkte und Wiedervorlagen

#### 10.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der terminbezogene Text wird korrekt angezeigt.
- [ ] Der Status des Tagesordnungspunkts entspricht der Auswahl.
- [ ] Eine abweichende Zuständigkeit wird korrekt angezeigt.
- [ ] Der allgemeine Themenstatus bleibt davon getrennt.

**Test erfolgreich:** [ ]

#### 10.6.2 Tagesordnungspunkte sortieren – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Reihenfolge entspricht der zuletzt vorgenommenen Sortierung.
- [ ] Jeder Tagesordnungspunkt ist weiterhin dem richtigen Thema zugeordnet.
- [ ] Es fehlen keine Punkte und es sind keine Duplikate entstanden.

**Test erfolgreich:** [ ]

#### 10.6.3 Tagesordnungspunkt entfernen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Punkt ist aus dem ausgewählten Termin entfernt.
- [ ] Das Thema selbst bleibt entsprechend der vorgesehenen Datenregel erhalten.
- [ ] Andere Tagesordnungspunkte bleiben unverändert.

**Test erfolgreich:** [ ]

#### 10.6.4 Wiedervorlage anlegen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Tagesordnungspunkt erscheint im vorgesehenen Zieltermin.
- [ ] Die Verbindung zum vorherigen Tagesordnungspunkt ist nachvollziehbar.
- [ ] Status und Zuständigkeit entsprechen den vorgesehenen Übernahmeregeln.
- [ ] Es ist keine doppelte Wiedervorlage entstanden.

**Test erfolgreich:** [ ]

#### 10.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Wiedervorlagekette ist chronologisch nachvollziehbar.
- [ ] Jeder Punkt ist dem richtigen Termin zugeordnet.
- [ ] Frühere Protokollstände bleiben unverändert.
- [ ] Es entstehen keine doppelten oder voneinander getrennten Ketten.

**Test erfolgreich:** [ ]

#### 10.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Datum, Reihenbezeichnung, Text, Status und Verantwortlichkeit werden dem historischen Eintrag entsprechend angezeigt.
- [ ] Historische Einträge lassen sich nicht unberechtigt verändern.
- [ ] Zugriff ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 10.7 Kommentare, Anlagen und Links

#### 10.7.1 Kommentar hinzufügen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Kommentar wird beim richtigen Thema angezeigt.
- [ ] Autor und Erstellungszeitpunkt werden korrekt angezeigt.
- [ ] Der Kommentar bleibt nach dem Neuladen erhalten.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 10.7.2 Datei als Themenanlage hochladen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Anlage wird beim richtigen Thema angezeigt.
- [ ] Bezeichnung und Datei sind korrekt zugeordnet.
- [ ] Die Datei lässt sich mit einem berechtigten Konto herunterladen.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

**Test erfolgreich:** [ ]

#### 10.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der eingetragene Pfad bzw. Link wird korrekt angezeigt.
- [ ] Unterstützte Pfade werden entsprechend der Anwendung als Link dargestellt.
- [ ] Nicht unterstützte oder ungültige Werte werden nicht als unsichere Links ausgegeben.
- [ ] Die Anwendung behauptet nicht, die Erreichbarkeit einer externen Freigabe zu garantieren.

**Test erfolgreich:** [ ]

#### 10.7.4 Anlage herunterladen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Berechtigte Konten können die zugehörige Datei herunterladen.
- [ ] Dateiinhalt und Dateiname entsprechen der hochgeladenen Datei.
- [ ] Nicht berechtigte Konten erhalten keinen Dateizugriff.

**Test erfolgreich:** [ ]

#### 10.7.5 Anlage löschen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Die Anlage wird nicht mehr in der Themenansicht angezeigt.
- [ ] Der direkte Download der entfernten Anlage ist nicht mehr möglich.
- [ ] Andere Anlagen und Themen bleiben unverändert.

**Test erfolgreich:** [ ]

#### 10.7.6 Upload-Grenzen prüfen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Zulässige Dateien innerhalb des Limits werden angenommen.
- [ ] Zu große Dateien werden abgewiesen.
- [ ] Nicht erlaubte Dateiendungen werden abgewiesen.
- [ ] Abgewiesene Uploads erzeugen keine ungewollten Anlagen-Datensätze.

**Test erfolgreich:** [ ]

---

### 10.8 Besprechung abschließen und Protokoll

#### 10.8.1 Besprechung abschließen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Termin ist als abgeschlossen gekennzeichnet.
- [ ] Ein Protokoll-Snapshot wurde erstellt.
- [ ] Teilnehmerliste und Tagesordnungstexte sind gegen weitere Bearbeitung gesperrt.
- [ ] Der Abschluss wird im Änderungsverlauf dokumentiert.

**Test erfolgreich:** [ ]

#### 10.8.2 Protokoll anzeigen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Protokoll zeigt den beim Abschluss gesicherten Stand.
- [ ] Historische Werte werden nicht durch spätere Änderungen am Thema überschrieben.
- [ ] Protokoll ist für berechtigte Leser*innen sichtbar.

**Test erfolgreich:** [ ]

#### 10.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Druckansicht enthält den richtigen Termin und Protokollstand.
- [ ] PDF lässt sich öffnen.
- [ ] PDF enthält die vorgesehenen Protokolldaten.
- [ ] Organisationsbezeichnung und Logo erscheinen entsprechend der Konfiguration.
- [ ] Unberechtigte Konten können den Export nicht abrufen.

**Test erfolgreich:** [ ]

#### 10.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Termin ist nach dem Wiederöffnen bearbeitbar.
- [ ] Der vorherige Protokollstand bleibt als historischer Stand nachvollziehbar.
- [ ] Die erneute Bearbeitung und der erneute Abschluss funktionieren.
- [ ] Teilnehmer*innen ohne Moderatorrechte können den Termin nicht wieder öffnen.

**Test erfolgreich:** [ ]

#### 10.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] PDF enthält die dem Thema zugeordneten historischen Einträge.
- [ ] Datum, Reihe, Texte und Statuswerte sind korrekt.
- [ ] Der Export ist auf berechtigte Konten begrenzt.

**Test erfolgreich:** [ ]

---

### 10.9 Offene Themen und Archiv

#### 10.9.1 Offene Themen aufrufen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Nur fachlich zugängliche Themen werden angezeigt.
- [ ] Status, Zuständigkeit und Besprechungsreihe werden korrekt angezeigt.
- [ ] Auswahl und Filter führen zu passenden Ergebnissen.

**Test erfolgreich:** [ ]

#### 10.9.2 Archiv aufrufen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Archivierte Themen sind im Archiv auffindbar.
- [ ] Historische Inhalte werden entsprechend der Berechtigung angezeigt.
- [ ] Nicht archivierte Themen werden nicht fälschlich als archiviert dargestellt.

**Test erfolgreich:** [ ]

#### 10.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der vorgesehene historische Lesezugriff des früheren Reihenmitglieds bleibt bestehen.
- [ ] Das unbeteiligte Konto erhält keinen Zugriff.
- [ ] Gelöschte aktive Reihenfunktionen werden nicht unbeabsichtigt wieder verfügbar.

**Test erfolgreich:** [ ]

---

### 10.10 Berechtigungsanträge

#### 10.10.1 Serienberechtigung beantragen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Der Antrag wird der richtigen Person und Besprechungsreihe zugeordnet.
- [ ] Gewünschte Rolle wird korrekt angezeigt.
- [ ] Der Antrag erscheint mit offenem Status.
- [ ] Durch den Antrag allein entstehen noch keine fachlichen Schreibrechte.

**Test erfolgreich:** [ ]

#### 10.10.2 Berechtigungsantrag entscheiden – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

#### 10.10.3 Bereits vorhandenen Antrag erneut bearbeiten – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Es entstehen keine unzulässigen doppelten offenen Anträge.
- [ ] Bereits entschiedene Anträge werden nicht irrtümlich als offen behandelt.
- [ ] Die bestehende Serienzuweisung wird nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

---

### 10.11 Benutzer- und Themenimport/-export

#### 10.11.1 Benutzer als CSV exportieren – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Exportdatei ist lesbar.
- [ ] Enthaltene Konten und Felder entsprechen dem vorgesehenen Exportumfang.
- [ ] Passwörter oder andere nicht exportierbare Geheimnisse sind nicht enthalten.

**Test erfolgreich:** [ ]

#### 10.11.2 Benutzer per CSV importieren – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Gültige Testkonten werden angelegt bzw. entsprechend der Importregel verarbeitet.
- [ ] Fehlerhafte Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Vorhandene Konten werden nicht ungewollt überschrieben.
- [ ] Serienzuweisungen werden nicht unbeabsichtigt verändert.

**Test erfolgreich:** [ ]

#### 10.11.3 Themen als CSV exportieren – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Export ist lesbar und enthält die vorgesehenen Themen.
- [ ] Zuständigkeiten, Status und Reihenbezüge sind korrekt.
- [ ] Inhalte außerhalb des zulässigen Berechtigungs- bzw. Exportumfangs werden nicht offengelegt.

**Test erfolgreich:** [ ]

#### 10.11.4 Themen per CSV importieren – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Gültige Testthemen werden entsprechend der Importregeln angelegt bzw. verarbeitet.
- [ ] Ungültige Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Reihenbezüge und Zuständigkeiten sind korrekt.
- [ ] Es entstehen keine unbeabsichtigten Duplikate.

**Test erfolgreich:** [ ]

---

### 10.12 Änderungsverlauf und Audit

#### 10.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Moderator*in sieht die Ereignisse der eigenen moderierten Reihe.
- [ ] Ereignisse anderer Reihen werden nicht offengelegt.
- [ ] Akteur, Zeitpunkt und Aktion sind nachvollziehbar.
- [ ] Unberechtigte Konten erhalten keinen Zugriff.

**Test erfolgreich:** [ ]

#### 10.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Admin und Auditor*in können die vorgesehenen Systemereignisse einsehen.
- [ ] Auditor*in kann keine Änderungsaktionen ausführen.
- [ ] Normale Nutzerkonten erhalten keinen unberechtigten Systemzugriff.
- [ ] Fachliche Reihenereignisse werden nicht unberechtigt in der Systemhistorie offengelegt.

**Test erfolgreich:** [ ]

#### 10.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] CSV-Datei ist lesbar.
- [ ] Export enthält nur die für die Rolle zulässigen Ereignisse.
- [ ] Direkter Exportaufruf ohne passende Berechtigung wird abgewiesen.
- [ ] Nicht erforderliche vertrauliche Daten werden nicht exportiert.

**Test erfolgreich:** [ ]

---

### 10.13 Aufbewahrung und automatische Löschung

#### 10.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Nicht abgelaufene Termine und Protokolle bleiben erhalten.
- [ ] Abgelaufene abgeschlossene Termine und Protokolle werden gemäß der Frist entfernt.
- [ ] Tagesordnungshistorie, die laut Fachregel am Thema erhalten bleiben muss, bleibt korrekt erhalten.
- [ ] Nicht abgeschlossene bzw. wieder geöffnete Termine werden nicht unberechtigt gelöscht.

**Test erfolgreich:** [ ]

#### 10.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Thema bleibt vor Fristablauf erhalten.
- [ ] Abgelaufenes archiviertes Thema wird gemäß der Fachregel endgültig entfernt.
- [ ] Zugehörige Inhalte und Dateien werden entsprechend der Löschregel behandelt.
- [ ] Nicht abgelaufene oder nicht archivierte Themen bleiben erhalten.

**Test erfolgreich:** [ ]

#### 10.13.3 Retention wiederholt ausführen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Ergebnisprüfung**

- [ ] Wiederholte Ausführung erzeugt keine doppelten Löschvorgänge oder inkonsistenten Datensätze.
- [ ] Nicht abgelaufene Daten bleiben erhalten.
- [ ] Fehler einzelner Datensätze führen nicht zu unbemerkter Fehlbehandlung des gesamten Bestands.

**Test erfolgreich:** [ ]

---

### 10.14 Auditor*innenbereich

#### 10.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Die vorgesehenen administrativen Prüfdaten sind lesbar.
- [ ] Startpasswort und andere Geheimnisse werden nicht angezeigt.
- [ ] Es bestehen keine Änderungsfunktionen für Auditor*innen.
- [ ] Fachliche Besprechungsreihen und Themeninhalte sind nicht zugänglich.

**Test erfolgreich:** [ ]

#### 10.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Ergebnisprüfung**

- [ ] Lesender Zugriff auf ausdrücklich freigegebene administrative Prüfdaten ist möglich.
- [ ] Fachliche Inhalte sind nicht zugänglich.
- [ ] Schreibende Aktionen sind nicht möglich.
- [ ] Direkte URLs umgehen die Rollenbegrenzung nicht.

**Test erfolgreich:** [ ]

---
