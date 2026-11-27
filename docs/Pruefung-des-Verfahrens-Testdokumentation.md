# Prüfung des Verfahrens – Manuelle Testdokumentation

**Grundlage:** Branch `beta`  
**Zweck:** Vollständige manuelle Funktionsprüfung des Meeting Managers  
**Art der Dokumentation:** Ablauf- und Ergebnischeckliste mit serverlokal gespeichertem Prüfstatus, Live-Aktualisierung und Markdown-Export im TESTING-Modus

**Verwendung**

- Die Testfälle in einer geeigneten Testinstallation mit vorbereiteten Testkonten durchführen.
- Testblöcke mit **PR-Test erforderlich** sind durch die Änderungen des aktuellen Pull Requests betroffen und müssen in diesem PR erneut ausgeführt werden.
- Ein PR-Test-Marker ist kein Erfolgsnachweis. Die zugehörigen Kästchen bleiben bis zur tatsächlichen erfolgreichen Prüfung leer.
- Für jeden Testfall die nummerierten Prüfschritte der Reihe nach ausführen. Im aktivierten TESTING-Modus ausschließlich die Kästchen unter **Ergebnisprüfung** abhaken; die Durchführungsschritte selbst werden ohne Checkboxen angezeigt. Jeder Klick wird unmittelbar in der lokalen Datei `docs/Pruefung-des-Verfahrens-Testdokumentation.md` auf dem Anwendungsserver gespeichert. Andere Nutzer derselben Installation sehen Änderungen automatisch spätestens nach 15 Sekunden. Der vollständige Prüfstand kann über **Aktuellen Test als .md herunterladen** exportiert und anschließend manuell in GitHub hochgeladen oder in den gewünschten Branch übernommen werden. Außerhalb des TESTING-Modus ist die Checkliste schreibgeschützt. Die Speicherung erfolgt weder in einer Datenbank noch automatisch in GitHub. Mehrere Serverinstallationen führen unabhängige lokale Checklisten ohne Synchronisierung.
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

#### 1.1.1 Datenverwaltungsbereich aufrufen – Prüfrollen: globaler Admin, globale Nutzer*in ohne Adminrechte und globale Auditor*in

**Prüfschritt**

 1. Mit einem globalen Admin-Konto anmelden und **Verwaltung → Daten** über die Navigation öffnen.
 1. Die verfügbaren Datenverwaltungsfunktionen und die vollständige URL des Bereichs prüfen.
 1. Mit einem globalen Nutzerkonto ohne Adminrechte anmelden und dieselbe URL direkt aufrufen.
 1. Mit einem globalen Auditor-Konto anmelden und dieselbe URL direkt aufrufen.
 1. Mit dem globalen Admin-Konto erneut anmelden und zur Verwaltungsübersicht zurückkehren.

**Ergebnisprüfung**

- [ ] Der globale Admin kann den Datenverwaltungsbereich öffnen und die verfügbaren Funktionen sehen.
- [ ] Das globale Nutzerkonto ohne Adminrechte erhält beim direkten Aufruf keinen Zugriff auf den Datenverwaltungsbereich.
- [ ] Das globale Auditor-Konto erhält beim direkten Aufruf keinen Zugriff auf den Datenverwaltungsbereich.

- **Test erfolgreich:** [ ]

#### 1.1.2 Vollständigen Datenexport durchführen – Rolle: Admin

**Prüfschritt**

 1. Datenverwaltungsbereich öffnen.
 1. Funktion zum vollständigen Backup-Export aufrufen.
 1. Export starten.
 1. Exportdatei speichern.
 1. Datei und Ergebnisanzeige prüfen.

**Ergebnisprüfung**

- [ ] Export wird ohne Fehlermeldung abgeschlossen.
- [ ] Exportdatei ist vorhanden und im vorgesehenen Format lesbar bzw. weiterverarbeitbar.
- [ ] Export enthält keine Zugangsdaten oder Geheimnisse, die nicht Bestandteil des vorgesehenen Sicherungsformats sein dürfen.

- **Test erfolgreich:** [ ]

#### 1.1.3 Datenimport in isolierter Testinstallation prüfen – Rolle: Admin

**Prüfschritt**

 1. Ausschließlich eine isolierte Testinstallation verwenden.
 1. Vorhandenen Testdatenbestand sichern.
 1. Datenimport öffnen.
 1. Geeignete Test-Sicherungsdatei auswählen.
 1. Import starten.
 1. Ergebnisanzeige prüfen.
 1. Betroffene Testdatenbereiche öffnen.

**Ergebnisprüfung**

- [ ] Die Daten aus der ausgewählten Sicherungsdatei werden ohne Importfehler eingelesen und in den zugehörigen Übersichten angezeigt.
- [ ] Eine Sicherungsdatei mit ungültiger Struktur oder fehlenden Pflichtbestandteilen wird mit einer Fehlermeldung abgewiesen; der vorhandene Datenbestand bleibt unverändert.
- [ ] Konten, Reihen, Termine, Themen und Berechtigungen stimmen nach dem Import mit dem zuvor erstellten Sicherungsstand überein.
- [ ] Keine produktiven Daten werden berührt.

- **Test erfolgreich:** [ ]

---


### 1.2 Administration und Software-Updates

#### 1.2.1 Updatebereich aufrufen – Rolle: Admin

**Prüfschritt**

 1. Administrationsbereich für Software-Updates öffnen.
 1. Angezeigte Versions- und Branchinformationen prüfen.
 1. Verfügbare Updateinformationen aufrufen.
 1. Ohne Ausführung eines Updates zur Übersicht zurückkehren.

**Ergebnisprüfung**

- [ ] Updatebereich ist für Admins erreichbar.
- [ ] Versions- und Statusinformationen werden angezeigt.
- [ ] Nicht berechtigte Rollen erhalten keinen Zugriff.

- **Test erfolgreich:** [ ]

#### 1.2.2 Update auf einer isolierten Testinstallation ausführen – Rolle: Admin bzw. Betrieb

**Prüfschritt**

 1. Vor dem Update Datenbank und Medienbestand sichern.
 1. Updatebereich öffnen.
 1. Gewünschten freigegebenen Branch auswählen.
 1. Update starten.
 1. Status und Protokoll des Updatevorgangs abwarten.
 1. Nach Abschluss die Anwendung neu laden.
 1. Anmeldung durchführen.
 1. Besprechungsübersicht, Themen, Protokoll und Anlagen öffnen.

**Ergebnisprüfung**

- [ ] Updatevorgang wird mit nachvollziehbarem Status beendet.
- [ ] Angezeigter Branch und Commit entsprechen der Auswahl.
- [ ] Anwendung ist erreichbar.
- [ ] Vorhandene Testdaten und Serienberechtigungen bleiben erhalten.
- [ ] Login, fachliche Ansichten und Dateizugriffe funktionieren.

- **Test erfolgreich:** [ ]

---


## 2. Ersteinrichtung

Prüfungen zur ersten Konfiguration, zu Konten, Organisation und initialen Berechtigungen.

### 2.1 Anmeldung und Sitzung

#### 2.1.1 Anmeldung mit gültigem Konto – Prüfrollen: globale Nutzer*in ohne Serienzuweisung, Serienleser*in, Serienteilnehmer*in, Serienmoderator*in, globaler Admin und globale Auditor*in

**Prüfschritt**

 1. Nacheinander die folgenden Kontokonstellationen mit getrennten Konten verwenden:
    1. Globale Nutzer*in ohne Serienzuweisung.
    1. Globale Nutzer*in mit Serienrolle Leser*in.
    1. Globale Nutzer*in mit Serienrolle Teilnehmer*in.
    1. Globale Nutzer*in mit Serienrolle Moderator*in.
    1. Globaler Admin ohne Serienzuweisung.
    1. Globaler Admin mit zusätzlicher Serienrolle Moderator*in.
    1. Globale Auditor*in.
 1. Für jedes dieser Konten die folgenden Schritte ausführen:
    1. Anmeldeseite öffnen.
    1. Gültigen Benutzernamen und das zugehörige gültige Passwort eingeben.
    1. Anmelden anklicken.

**Ergebnisprüfung**

- [ ] Angemeldete Startseite wird angezeigt.
- [ ] Angezeigter Benutzer entspricht dem angemeldeten Konto.
- [ ] Navigation und verfügbare Bereiche entsprechen der Rolle und den Serienzuweisungen.

- **Test erfolgreich:** [ ]

#### 2.1.2 Anmeldung mit ungültigen Zugangsdaten – rollenunabhängig; Referenzkonto: globale Nutzer*in ohne Serienzuweisung

Die Authentifizierungsprüfung ist nicht von einer Serienrolle abhängig. Eine Wiederholung für jede Serienrolle sowie für Admin und Auditor ist nicht erforderlich.

**Prüfschritt**

 1. Anmeldeseite öffnen.
 1. Einen nicht vorhandenen Benutzernamen eingeben.
 1. Ein beliebiges Passwort eingeben.
 1. Anmelden anklicken.
 1. Den Versuch mit einem gültigen Benutzernamen und falschem Passwort wiederholen.

**Ergebnisprüfung**

- [ ] Anmeldung wird in beiden Fällen abgewiesen.
- [ ] Es wird keine geschützte Seite angezeigt.
- [ ] Die Fehlermeldung gibt nicht preis, ob ein Benutzerkonto existiert.

- **Test erfolgreich:** [ ]

#### 2.1.3 Erzwungener Passwortwechsel – Rolle: Nutzer*in, Admin

**Prüfschritt**

 1. Mit einem Konto anmelden, für das ein Passwortwechsel erforderlich ist.
 1. Angezeigtes Formular zum Passwortwechsel öffnen.
 1. Neues Passwort eingeben.
 1. Neues Passwort wiederholen.
 1. Speichern bzw. Passwort ändern anklicken.
 1. Abmelden und erneut mit dem neuen Passwort anmelden.

**Ergebnisprüfung**

- [ ] Passwortwechsel wird vor dem Zugriff auf die übrige Anwendung verlangt.
- [ ] Nach erfolgreicher Änderung ist die Anmeldung mit dem neuen Passwort möglich.
- [ ] Das Konto wird nicht erneut zum Passwortwechsel aufgefordert, sofern keine neue Frist oder Rücksetzung gesetzt wurde.

- **Test erfolgreich:** [ ]

#### 2.1.4 Abmeldung und Sitzungsschutz – Prüfrollen: globale Nutzer*in ohne Serienzuweisung, Serienleser*in, Serienmoderator*in, globaler Admin und globale Auditor*in

**Prüfschritt**

 1. Nacheinander getrennte Konten für die folgenden Berechtigungsbereiche verwenden:
    1. Globale Nutzer*in ohne Serienzuweisung.
    1. Globale Nutzer*in mit Serienrolle Leser*in.
    1. Globale Nutzer*in mit Serienrolle Moderator*in.
    1. Globaler Admin ohne Serienzuweisung.
    1. Globaler Admin mit zusätzlicher Serienrolle Moderator*in.
    1. Globale Auditor*in.
 1. Die Serienrolle Teilnehmer*in nicht zusätzlich wiederholen, da die Sitzungssperre rollenunabhängig ist und Leser*in sowie Moderator*in den lesenden bzw. verwaltenden Serienzugriff abdecken.
 1. Für jedes aufgeführte Konto die folgenden Schritte ausführen:
    1. Anmelden und eine für dieses Konto tatsächlich erreichbare geschützte Seite öffnen.
    1. Abmelden anklicken.
    1. Die zuvor geöffnete geschützte URL erneut aufrufen.
    1. Im Browser zurück navigieren und die Seite neu laden.

**Ergebnisprüfung**

- [ ] Abmeldung führt zur Anmeldeseite bzw. zum nicht angemeldeten Zustand.
- [ ] Geschützte Inhalte sind nach der Abmeldung nicht erneut abrufbar.
- [ ] Eine erneute Anmeldung ist erforderlich.

- **Test erfolgreich:** [ ]

#### 2.1.5 Passwort-Zurücksetzen über den bereitgestellten Link – Rolle: Nutzer*in, Admin

**Prüfschritt**

 1. Einen gültigen Passwort-Zurücksetzen-Link für ein Testkonto öffnen.
 1. Neues Passwort eingeben.
 1. Passwort wiederholen.
 1. Änderung bestätigen.
 1. Den Link erneut öffnen.
 1. Mit dem neuen Passwort anmelden.

**Ergebnisprüfung**

- [ ] Das neue Passwort wird akzeptiert.
- [ ] Ein bereits verwendeter bzw. ungültiger Link kann nicht erneut zum Zurücksetzen verwendet werden.
- [ ] Die Anmeldung mit dem neuen Passwort ist möglich.

- **Test erfolgreich:** [ ]

---


### 2.2 Benutzerverwaltung

#### 2.2.1 Benutzerkonto anlegen – Rolle: Admin

**Prüfschritt**

 1. **Verwaltung** öffnen.
 1. **Nutzer** öffnen.
 1. **Neu** anklicken.
 1. Benutzernamen eintragen.
 1. Vorname und Nachname eintragen.
 1. E-Mail-Adresse eintragen.
 1. Organisationskennzeichen eintragen.
 1. Aktivstatus festlegen.
 1. Angezeigte Rollen- bzw. Kontoeinstellungen prüfen.
 1. Speichern anklicken.
 1. Benutzerübersicht neu laden.

**Ergebnisprüfung**

- [ ] Neues Konto erscheint in der Benutzerübersicht.
- [ ] Stammdaten und Aktivstatus entsprechen den Eingaben.
- [ ] Konto erhält keine unbeabsichtigten Serienberechtigungen.
- [ ] Passwortbereitstellung bzw. erforderlicher Passwortwechsel entspricht der vorgesehenen Einrichtung.

- **Test erfolgreich:** [ ]

#### 2.2.2 Benutzerkonto bearbeiten – Rolle: Admin

**Prüfschritt**

 1. Benutzerverwaltung öffnen.
 1. Ein Testkonto auswählen.
 1. Bearbeiten öffnen.
 1. Name oder E-Mail-Adresse ändern.
 1. Organisationskennzeichen ändern.
 1. Aktivstatus ändern, soweit für den Test vorgesehen.
 1. Speichern.
 1. Konto erneut öffnen.

**Ergebnisprüfung**

- [ ] Die geänderten Kontodaten entsprechen nach dem Neuladen den gespeicherten Eingaben.
- [ ] Nicht geänderte Daten bleiben erhalten.
- [ ] Bestehende Serienzuweisungen bleiben erhalten, sofern sie nicht ausdrücklich geändert wurden.

- **Test erfolgreich:** [ ]

#### 2.2.3 Benutzerkonto deaktivieren und aktivieren – Rolle: Admin

**Prüfschritt**

 1. Ein entbehrliches Testkonto auswählen.
 1. Aktivstatus deaktivieren.
 1. Speichern.
 1. Anmeldeversuch mit dem Testkonto durchführen.
 1. Konto erneut in der Benutzerverwaltung öffnen.
 1. Aktivstatus wieder aktivieren.
 1. Speichern.
 1. Anmeldung erneut versuchen.

**Ergebnisprüfung**

- [ ] Deaktiviertes Konto kann sich nicht anmelden.
- [ ] Reaktiviertes Konto kann sich gemäß Passwortstatus anmelden.
- [ ] Alle vor der Deaktivierung vorhandenen Serienzuweisungen sind nach der Reaktivierung weiterhin demselben Konto, derselben Reihe und derselben Rolle zugeordnet.

- **Test erfolgreich:** [ ]

#### 2.2.4 Benutzerkonto löschen – Rolle: Admin

**Prüfschritt**

 1. Ausschließlich ein entbehrliches Testkonto auswählen.
 1. Löschfunktion öffnen.
 1. Angezeigte Folgen prüfen.
 1. Löschung bestätigen.
 1. Benutzerübersicht und betroffene Serienzuweisungen prüfen.

**Ergebnisprüfung**

- [ ] Das gelöschte Testkonto erscheint nicht mehr in der Benutzerübersicht und kann sich nicht mehr anmelden.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.
- [ ] Historische Protokoll- und Audit-Einträge bleiben gemäß der konfigurierten Aufbewahrungsfrist erhalten; das gelöschte Konto kann sich nicht mehr anmelden.

- **Test erfolgreich:** [ ]

#### 2.2.5 Serienzuweisungen eines Benutzers verwalten – Rolle: Admin

**Prüfschritt**

 1. Benutzerverwaltung öffnen.
 1. Testkonto auswählen.
 1. Serienzuweisungen öffnen.
 1. Eine Reihe zuweisen.
 1. Serienrolle auswählen.
 1. Speichern.
 1. Weitere Reihe mit abweichender Rolle zuweisen.
 1. Speichern.
 1. Benutzeransicht erneut öffnen.

**Ergebnisprüfung**

- [ ] Jede Zuweisung ist der richtigen Reihe zugeordnet.
- [ ] Unterschiedliche Rollen je Reihe bleiben getrennt.
- [ ] Bestehende Zuweisungen werden bei Änderungen an einer anderen Reihe nicht überschrieben.
- [ ] Ein globaler Admin erhält durch die Zuweisungsbearbeitung keine unbeabsichtigte fachliche Rolle.

- **Test erfolgreich:** [ ]

#### 2.2.6 Passwort für Benutzer zurücksetzen – Rolle: Admin

**Prüfschritt**

 1. Benutzerverwaltung öffnen.
 1. Ein Testkonto auswählen.
 1. Passwort-Zurücksetzen-Funktion anklicken.
 1. Vorgang bestätigen.
 1. Mit dem Testkonto anmelden.
 1. Passwortwechsel durchführen.

**Ergebnisprüfung**

- [ ] Passwort wird gemäß dem vorgesehenen Rücksetzverfahren zurückgesetzt.
- [ ] Erforderlicher Passwortwechsel wird durchgesetzt.
- [ ] Andere Konten bleiben unverändert.

- **Test erfolgreich:** [ ]

---


### 2.3 Organisationsverwaltung

#### 2.3.1 Organisationseinstellungen bearbeiten – Rolle: Admin

**Prüfschritt**

 1. **Verwaltung** öffnen.
 1. **Organisation** bzw. Organisationseinstellungen öffnen.
 1. Organisationsbezeichnung ändern.
 1. Kurzbezeichnung ändern.
 1. Zeitzone auswählen.
 1. Änderungen speichern.
 1. Seite neu laden.

**Ergebnisprüfung**

- [ ] Organisationsbezeichnung und Kurzbezeichnung entsprechen nach dem Neuladen exakt den gespeicherten Eingaben.
- [ ] Datums- und Uhrzeitanzeigen verwenden die eingestellte Zeitzone.
- [ ] Einstellungen bleiben nach dem Neuladen erhalten.

- **Test erfolgreich:** [ ]

#### 2.3.2 Organisationslogo ändern – Rolle: Admin

**Prüfschritt**

 1. Organisationseinstellungen öffnen.
 1. Ein zulässiges Testlogo auswählen.
 1. Logo hochladen bzw. speichern.
 1. Dashboard und Protokoll-PDF öffnen.
 1. Falls vorgesehen, Logo entfernen bzw. durch ein anderes Testlogo ersetzen.

**Ergebnisprüfung**

- [ ] Logo wird in den vorgesehenen Bereichen angezeigt.
- [ ] Protokoll-PDF verwendet die vorgesehene Logo-Darstellung.
- [ ] Nicht unterstützte Dateien werden abgewiesen.
- [ ] Andere Organisationseinstellungen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 2.3.3 Farben und Darstellung konfigurieren – Rolle: Admin

**Prüfschritt**

 1. Organisationseinstellungen öffnen.
 1. Primärfarbe ändern.
 1. Sekundärfarbe ändern.
 1. Tertiärfarbe ändern.
 1. Optionale Hell- und Dunkelmodus-Farbwerte ändern, sofern angeboten.
 1. Speichern.
 1. Anwendung in Hell- und Dunkelmodus neu laden.

**Ergebnisprüfung**

- [ ] Farben werden in den vorgesehenen Bereichen verwendet.
- [ ] Ungültige Farbwerte werden abgewiesen.
- [ ] Nicht gesetzte optionale Farbwerte verwenden den vorgesehenen Basiswert.
- [ ] Lesbarkeit und Bedienbarkeit bleiben erhalten.

- **Test erfolgreich:** [ ]

#### 2.3.4 Aufbewahrungsfrist und Uploadlimit einstellen – Rolle: Admin

**Prüfschritt**

 1. Organisationseinstellungen öffnen.
 1. Zentrale Aufbewahrungsfrist ändern.
 1. Maximale Dateigröße für Anlagen ändern.
 1. Speichern.
 1. Einstellungen erneut öffnen.
 1. Upload mit einer Datei innerhalb und außerhalb des eingestellten Limits testen.

**Ergebnisprüfung**

- [ ] Die angezeigte Aufbewahrungsfrist entspricht dem gespeicherten Wert.
- [ ] Das angezeigte Uploadlimit entspricht dem gespeicherten Wert; Dateien oberhalb dieses Limits werden abgewiesen.
- [ ] Ungültige Werte werden abgewiesen.
- [ ] Bereits explizit gesetzte individuelle Themen-Aufbewahrungsfristen bleiben unverändert; Themen ohne individuelle Frist verwenden den neu gespeicherten zentralen Wert.

- **Test erfolgreich:** [ ]

---


### 2.4 Rollenübergreifende Zugriffsmatrix

Die folgenden Kurzprüfungen ergänzen die fachlichen Testfälle. Sie sind mit getrennten Konten und direkten URL-Aufrufen auszuführen.

#### 2.4.1 Leser*in – nur lesender Zugriff in zugewiesener Reihe

**Prüfschritt**

 1. Zugewiesene Reihe öffnen.
 1. Termin und Protokoll öffnen.
 1. Thema und Tagesordnung öffnen.
 1. Kommentar-, Bearbeitungs-, Lösch- und Abschlussaktionen versuchen.
 1. Direkte schreibende URLs der Testreihe aufrufen.

**Ergebnisprüfung**

- [ ] Lesen und Protokoll-Export sind im zugewiesenen Bereich möglich.
- [ ] Fachliche Änderungen und schreibende Aktionen werden verweigert.
- [ ] Nicht zugewiesene Reihen bleiben unzugänglich.

- **Test erfolgreich:** [ ]

#### 2.4.2 Teilnehmer*in – fachliche Bearbeitung ohne Reihenverwaltung

**Prüfschritt**

 1. Zugewiesene Reihe öffnen.
 1. Thema und Tagesordnung bearbeiten.
 1. Zuständigkeit setzen.
 1. Kommentar und Anlage hinzufügen.
 1. Wiedervorlage anlegen.
 1. Teilnehmerliste bearbeiten.
 1. Besprechung abschließen.
 1. Serienverwaltung und Wiederöffnung eines abgeschlossenen Termins versuchen.

**Ergebnisprüfung**

- [ ] Erlaubte fachliche Aktionen sind möglich.
- [ ] Reihenverwaltung und Wiederöffnung bleiben gesperrt.
- [ ] Andere Reihen sind nicht zugänglich.

- **Test erfolgreich:** [ ]

#### 2.4.3 Moderator*in – Verwaltung nur der eigenen Reihe

**Prüfschritt**

 1. Eigene Reihe öffnen.
 1. Reihe bearbeiten.
 1. Termine verwalten.
 1. Themen archivieren und wieder öffnen.
 1. Abgeschlossenen Termin wieder öffnen.
 1. Serienmitglieder verwalten.
 1. Fremde Reihe direkt aufrufen.
 1. Eigene Moderatorzuweisung zu ändern oder zu entfernen versuchen.

**Ergebnisprüfung**

- [ ] Moderationsfunktionen sind nur in der ausdrücklich zugewiesenen Reihe verfügbar.
- [ ] Fremde Reihen bleiben unzugänglich.
- [ ] Eigene Moderatorzuweisung ist gegen unzulässige Selbständerung geschützt.

- **Test erfolgreich:** [ ]

#### 2.4.4 Admin – globale Verwaltung ohne automatische Fachberechtigung

**Prüfschritt**

 1. Benutzerverwaltung öffnen.
 1. Organisationseinstellungen öffnen.
 1. Serienzuweisungen verwalten.
 1. Eine fachliche Reihe ohne eigene Serienzuweisung direkt aufrufen.
 1. Ein Thema dieser Reihe direkt aufrufen.
 1. Einen fachlichen Schreibvorgang versuchen.

**Ergebnisprüfung**

- [ ] Globale Verwaltungsfunktionen sind verfügbar.
- [ ] Fachliche Reiheninhalte bleiben ohne passende Serienzuweisung unzugänglich.
- [ ] Eine ausdrückliche Serienzuweisung ermöglicht nur die zugewiesene Rolle und Reihe.

- **Test erfolgreich:** [ ]

#### 2.4.5 Auditor*in – ausschließlich administrative Leserechte

**Prüfschritt**

 1. Auditor*innenübersicht öffnen.
 1. Benutzer- und Rolleninformationen lesen.
 1. Organisationseinstellungen lesen.
 1. Systemänderungsverlauf lesen.
 1. Fachliche Reihe und Thema direkt aufrufen.
 1. Administrative Schreibaktionen versuchen.

**Ergebnisprüfung**

- [ ] Administrative Prüfdaten sind lesbar.
- [ ] Fachliche Inhalte bleiben unzugänglich.
- [ ] Schreibende Aktionen sind gesperrt.
- [ ] Geheimnisse wie Startpasswörter werden nicht angezeigt.

- **Test erfolgreich:** [ ]

---


## 3. Testing

Prüfungen der isolierten Testumgebung, Testdaten, Hilfedokumentation und des abschließenden Testlaufs.

### 3.1 TESTING-Modus und Beispielkonfiguration

#### 3.1.1 TESTING-Kennzeichnung prüfen – Rolle: Admin auf isolierter Testinstallation

**Prüfschritt**

 1. TESTING-Modus in der Testinstallation aktivieren.
 1. Dashboard öffnen.
 1. Browser-Tab bzw. Seitentitel prüfen.
 1. Django-Administrationspfad aufrufen.
 1. TESTING-Modus deaktivieren.
 1. Dieselben Bereiche erneut aufrufen.

**Ergebnisprüfung**

- [ ] Bei aktivem TESTING-Modus ist die Testkennzeichnung sichtbar.
- [ ] Zusätzliche Testfunktionen sind nur im aktivierten Modus verfügbar.
- [ ] Nach Deaktivierung sind die zusätzlichen Testfunktionen nicht mehr erreichbar.

- **Test erfolgreich:** [ ]

#### 3.1.2 Testnutzer erzeugen – Rolle: globale Adminrolle im TESTING-Modus

**Prüfschritt**

 1. **Verwaltung** öffnen.
 1. **Beispielkonfiguration** öffnen.
 1. Bereich zum Erzeugen zufälliger Testnutzer aufrufen.
 1. Eine kleine Anzahl Testnutzer auswählen.
 1. Erzeugung starten.
 1. Benutzerübersicht öffnen.

**Ergebnisprüfung**

- [ ] Testkonten werden mit der vorgesehenen Kennzeichnung angelegt.
- [ ] Benutzernamen und E-Mail-Adressen entsprechen dem Testdatenformat.
- [ ] Bei der ersten Anmeldung mit einem neu erzeugten Testkonto wird der Passwortwechsel verlangt.
- [ ] Reguläre Benutzerkonten bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 3.1.3 Testbesprechungsreihen erzeugen – Rolle: globale Adminrolle im TESTING-Modus

**Prüfschritt**

 1. Beispielkonfiguration öffnen.
 1. Bereich zum Erzeugen von Testbesprechungsreihen aufrufen.
 1. Eine kleine Anzahl Reihen auswählen.
 1. Erzeugung starten.
 1. Serienübersicht öffnen.

**Ergebnisprüfung**

- [ ] Testreihen werden mit der vorgesehenen TEST-Kennzeichnung angelegt.
- [ ] Wiederholungsrhythmus und Wochentag sind gesetzt.
- [ ] Reguläre Besprechungsreihen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 3.1.4 Termine für Testreihen generieren – Rolle: globale Adminrolle im TESTING-Modus

**Prüfschritt**

 1. Beispielkonfiguration öffnen.
 1. Eine Testreihe auswählen.
 1. Funktion zum Generieren der Termine öffnen.
 1. Generierung starten.
 1. Terminübersicht der Testreihe öffnen.

**Ergebnisprüfung**

- [ ] Termine entsprechen dem Rhythmus der ausgewählten Testreihe.
- [ ] Die Terminübersicht enthält die generierten vergangenen und zukünftigen Termine mit den in der Testreihe festgelegten Wochentagen und Abständen.
- [ ] Bestehende Serienrollen werden nicht überschrieben.
- [ ] Es entstehen keine doppelten Termine.

- **Test erfolgreich:** [ ]

#### 3.1.5 Testthemen erzeugen – Rolle: globale Adminrolle im TESTING-Modus

**Prüfschritt**

 1. Beispielkonfiguration öffnen.
 1. Eine Testreihe auswählen.
 1. Bereich zum Erzeugen von Testthemen öffnen.
 1. Eine kleine Anzahl Themen festlegen.
 1. Erzeugung starten.
 1. Themenübersicht der Testreihe öffnen.

**Ergebnisprüfung**

- [ ] Themen sind eindeutig als Testdaten gekennzeichnet.
- [ ] Status und Hauptzuständigkeit sind gesetzt.
- [ ] Reguläre Themen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 3.1.6 Tagesordnungspunkte und Wiedervorlagen erzeugen – Rolle: globale Adminrolle im TESTING-Modus

**Prüfschritt**

 1. Beispielkonfiguration öffnen.
 1. Ein Testthema auswählen.
 1. Bereich zum Erzeugen von Tagesordnungspunkten öffnen.
 1. Eine kleine Anzahl Punkte festlegen.
 1. Erzeugung starten.
 1. Zugehörige Testtermine öffnen.

**Ergebnisprüfung**

- [ ] Tagesordnungspunkte werden den vorgesehenen Terminen zugeordnet.
- [ ] Status und Zuständigkeiten sind gesetzt.
- [ ] Wiedervorlagekette ist chronologisch verknüpft.
- [ ] Reguläre Themen und Termine bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 3.1.7 Testdaten zurücksetzen – Rolle: globale Adminrolle im TESTING-Modus

**Prüfschritt**

 1. Vorhandene Testdaten in der Testinstallation prüfen.
 1. Funktion **TEST-Daten zurücksetzen** öffnen.
 1. Angezeigte Auswahl und Folgen prüfen.
 1. Zurücksetzen bestätigen.
 1. Benutzer-, Reihen-, Termin- und Themenübersichten öffnen.

**Ergebnisprüfung**

- [ ] Als Testdaten gekennzeichnete Testkonten, Testreihen, Termine, Themen und Tagesordnungspunkte werden durch den Reset entfernt.
- [ ] Reguläre Reihen, Themen und Benutzer bleiben erhalten.
- [ ] Testkonten, die mit regulären fachlichen Datensätzen verknüpft sind, bleiben beim Zurücksetzen erhalten.
- [ ] Es verbleiben keine unbeabsichtigten Testdatenreste.

- **Test erfolgreich:** [ ]

---

### 3.2 Hilfe und Dokumentation

#### 3.2.1 Benutzerhilfe aufrufen – Prüfrollen: globale Nutzer*in ohne Serienzuweisung, globaler Admin und globale Auditor*in – **PR-Test erforderlich (#531)**

Die allgemeine Benutzerhilfe ist nicht von einer Serienzuweisung abhängig. Die Serienrollen Leser*in, Teilnehmer*in und Moderator*in müssen daher nicht zusätzlich einzeln geprüft werden; sie verwenden dieselbe globale Hilfefunktion.

Für jedes der drei Konten:
**Prüfschritt**

 1. Menüpunkt **Hilfe** öffnen.
 1. Benutzerhilfe aufrufen.
 1. Inhaltsübersicht und Verweise prüfen.
 1. Zur Anwendung zurückkehren.

**Ergebnisprüfung**

- [ ] Hilfe wird ohne Fehler angezeigt.
- [ ] Verlinkte Abschnitte sind erreichbar.
- [ ] Inhalte sind lesbar und der Navigation zugeordnet.

- **Test erfolgreich:** [ ]

#### 3.2.2 IT-Sicherheits- und Funktionsbeschreibung aufrufen – Prüfrollen: globale Nutzer*in ohne Serienzuweisung, globaler Admin und globale Auditor*in

Das Dokument wird im allgemeinen Hilfebereich bereitgestellt. Die Sichtbarkeit hängt nicht von einer Serienrolle ab; Leser*in, Teilnehmer*in und Moderator*in müssen deshalb nicht zusätzlich einzeln geprüft werden.

Für jedes der drei Konten:
**Prüfschritt**

 1. Bereich **Hilfe → IT, Informationssicherheit und Datenschutz** öffnen.
 1. Dokument in der Anwendung anzeigen.
 1. PDF-Version öffnen.
 1. PDF-Datei speichern und öffnen.

**Ergebnisprüfung**

- [ ] Dokument wird angezeigt.
- [ ] PDF lässt sich öffnen.
- [ ] Angezeigtes Dokument und PDF beziehen sich auf die vorgesehene Fassung.
- [ ] Es werden keine unberechtigten internen Daten offengelegt.

- **Test erfolgreich:** [ ]

#### 3.2.3 Testcheckliste aus Hilfe & Anleitung öffnen – Prüfrollen: globale Nutzer*in ohne Serienzuweisung, globaler Admin und globale Auditor*in – **PR-Test erforderlich (#531)**

Der Zugriff auf die allgemeine Hilfe und die Testcheckliste ist nicht von einer Serienzuweisung abhängig. Die Serienrollen Leser*in, Teilnehmer*in und Moderator*in müssen nicht zusätzlich einzeln geprüft werden. Die Funktionsprüfung erfolgt mit einem Konto je globaler Rolle.

**Prüfschritt**

 1. Für jedes der drei Konten (globale Nutzer*in ohne Serienzuweisung, globaler Admin, globale Auditor*in) die folgenden Schritte ausführen:
    1. Anmelden.
    1. **Hilfe & Anleitung** öffnen.
    1. Den Link **Prüfung des Verfahrens – Testcheckliste** im Inhaltsbereich anklicken.
    1. Prüfen, ob die Testdokumentation vollständig angezeigt wird.
    1. Abmelden.
 1. Die folgenden Funktionsprüfungen einmal mit einer globalen Nutzer*in ohne Serienzuweisung durchführen; für parallele Bearbeitungsschritte zusätzlich ein zweites Konto anderer globaler Rolle (vorzugsweise globaler Admin) verwenden:
    1. Erneut anmelden und TESTING-Modus aktivieren.
    1. Einen Testblock aufrufen.
    1. Ein Kontrollkästchen anklicken und die unmittelbare Speicherbestätigung abwarten.
    1. Prüfen, ob der entsprechende Marker in der lokalen Datei `docs/Pruefung-des-Verfahrens-Testdokumentation.md` auf dem Anwendungsserver geändert wurde.
    1. Dieselbe Checkliste in einem zweiten Browserfenster mit einem weiteren angemeldeten Nutzer öffnen.
    1. Im ersten Fenster einen weiteren Haken setzen und prüfen, ob das zweite Fenster spätestens nach 15 Sekunden aktualisiert wird, ohne die Seite neu zu laden.
    1. In beiden Fenstern gleichzeitig unterschiedliche Haken ändern und prüfen, ob beide Änderungen erhalten bleiben.
    1. Einen Haken wieder entfernen und prüfen, ob auch das Entfernen unmittelbar gespeichert und live übertragen wird.
    1. **Aktuellen Test als .md herunterladen** auswählen und die heruntergeladene vollständige Markdown-Datei öffnen.
    1. Prüfen, ob sämtliche gesetzten und entfernten Haken im Download enthalten sind.
    1. TESTING-Modus deaktivieren und Bearbeitbarkeit sowie Download erneut prüfen.
    1. Die Testcheckliste ohne Anmeldung direkt aufrufen.
    1. Über den Rücklink wieder **Hilfe & Anleitung** öffnen.

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

- **Test erfolgreich:** [ ]

---


### 3.3 Abschluss der Gesamtprüfung

#### 3.3.1 Vollständigkeit und Nachprüfung

**Ergebnisprüfung**

- [ ] Alle für die Installation relevanten Testblöcke sind durchgeführt oder als nicht relevant begründet dokumentiert.
- [ ] Alle in den Testfällen ausdrücklich genannten globalen Rollen und Serienrollen wurden mit getrennten Testkonten geprüft; nicht erforderliche Rollenwiederholungen sind ausgelassen.
- [ ] Direkte URL-Aufrufe sind bei den Berechtigungstests berücksichtigt.
- [ ] Alle Abweichungen sind dokumentiert und nicht als erfolgreich markiert.
- [ ] Kritische Fehler wurden nach der Korrektur erneut geprüft.
- [ ] Testdaten wurden nach Abschluss gemäß den Regeln der Testumgebung zurückgesetzt.

#### 3.3.2 Ergebnis der Gesamtprüfung

**Ergebnisprüfung**

- [ ] Alle durchgeführten und relevanten Testfälle sind erfolgreich abgeschlossen.
- [ ] Es bestehen keine offenen kritischen oder hohen Fehler.
- [ ] Abweichungen und nicht durchgeführte Tests sind separat dokumentiert.

**Prüfprotokoll**

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

#### 4.1.1 Dashboard aufrufen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Das Dashboard über die Hauptnavigation öffnen und vollständig laden lassen. Die angezeigten Kacheln, Kennzahlen und Verknüpfungen prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

- **Test erfolgreich:** [ ]

#### 4.1.2 Navigation und Darstellungsvarianten – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Die Hauptnavigation auf Desktop und mobiler Ansicht öffnen. Menüpunkte, Untermenüs und Darstellungsvarianten durchgehen; nicht angebotene Funktionen nicht über fremde Konten simulieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Nach dem Neuladen ist weiterhin die zuvor ausgewählte Darstellungsvariante aktiv.

- **Test erfolgreich:** [ ]

---

### 4.2 Persönliches Konto und eigene Aufgaben

#### 4.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Die persönlichen Kontoeinstellungen öffnen, ein unkritisches Testfeld ändern und speichern. Die Seite neu laden und den gespeicherten Wert kontrollieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 4.2.2 Eigene Aufgaben aufrufen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Die persönliche Aufgabenübersicht öffnen, vorhandene eigene Aufgaben durchgehen und – falls keine vorhanden sind – den vorgesehenen Leerzustand prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Eigene offene Themen werden im vorgesehenen Abschnitt angezeigt.
- [ ] Eigene Tagesordnungspunkte werden getrennt davon angezeigt.
- [ ] Nicht zugewiesene oder nicht berechtigte Inhalte werden nicht zusätzlich eingeblendet.
- [ ] Bei fehlenden Aufgaben wird ein geeigneter Leerzustand angezeigt.

- **Test erfolgreich:** [ ]

---

### 4.3 Besprechungsreihen verwalten

#### 4.3.1 Besprechungsreihe anlegen – Prüfrolle: globale Nutzerrolle + Moderator*in einer bestehenden Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit einem globalen Nutzerkonto anmelden, das in mindestens einer bestehenden Besprechungsreihe ausdrücklich als Moderator*in zugewiesen ist.
 1. Die Serienverwaltung öffnen und eine eindeutig benannte Testreihe mit Testbeschreibung, Startdatum, Rhythmus und Enddatum anlegen. Die vorgesehene Moderatorzuweisung setzen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die neue Besprechungsreihe erscheint in der Übersicht.
- [ ] Bezeichnung, Beschreibung und Wiederholungseinstellungen entsprechen den Eingaben.
- [ ] Jeder erzeugte Termin liegt innerhalb des festgelegten Start- und Enddatums und folgt dem gespeicherten Rhythmus und Intervall.
- [ ] Die erstellende Moderatorin bzw. der erstellende Moderator besitzt die vorgesehene Serienzuweisung.
- [ ] Serienzuweisungen außerhalb der neu angelegten Testreihe sind nach dem Speichern unverändert; insbesondere werden keine zusätzlichen Rollen in anderen Reihen angelegt.

- **Test erfolgreich:** [ ]

#### 4.3.2 Besprechungsreihe bearbeiten – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Eine der Rolle zugewiesene Testreihe öffnen, ein unkritisches Feld (z. B. Beschreibung) ändern, speichern und die Reihe erneut laden.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Geänderte Werte werden angezeigt.
- [ ] Nicht geänderte Werte bleiben erhalten.
- [ ] Bestehende Serienberechtigungen bleiben erhalten.
- [ ] Bereits vorhandene Termine und Themen sind weiterhin dem richtigen fachlichen Kontext zugeordnet.

- **Test erfolgreich:** [ ]

#### 4.3.3 Besprechungsreihe verlängern – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Eine zugewiesene Testreihe öffnen, das Enddatum um mindestens einen Serientermin verlängern und die Änderung speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Zusätzliche Termine werden bis zum neuen Enddatum erzeugt.
- [ ] Bereits vorhandene Termine bleiben erhalten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 4.3.4 Termine einer Reihe neu aufsetzen – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Eine eigens dafür angelegte Testreihe verwenden, den Wiederholungsrhythmus kontrolliert ändern und das Neuaufsetzen der Terminfolge auslösen. Vorher vorhandene Termine und Zuordnungen dokumentieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Terminfolge entspricht den eingestellten Seriendaten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Bestehende Themen, Tagesordnungspunkte und Serienberechtigungen entsprechen den vorgesehenen Regeln.
- [ ] Nicht ausgewählte Reihen sind unverändert.

- **Test erfolgreich:** [ ]

#### 4.3.5 Besprechungsreihe löschen – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Ausschließlich eine entbehrliche Testreihe verwenden, die vorgesehene Löschvariante auswählen und den Löschvorgang bestätigen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Reihe wird nicht mehr als aktive Reihe angeboten.
- [ ] Historische Inhalte entsprechen nach dem Löschen genau der im Prüfschritt gewählten Löschvariante; Inhalte außerhalb ihres Löschumfangs bleiben erhalten.
- [ ] Vorgesehene historische Lesezugriffe bleiben erhalten.
- [ ] Andere Reihen und deren Berechtigungen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 4.3.6 Berechtigungen einer Reihe verwalten – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Die Berechtigungsverwaltung einer zugewiesenen Testreihe öffnen, ein separates Testkonto hinzufügen oder dessen Rolle ändern und die Änderung speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Das Testkonto ist der richtigen Reihe zugeordnet.
- [ ] Die gespeicherte Serienrolle entspricht der im Prüfschritt ausgewählten Rolle.
- [ ] Änderungen betreffen nur die ausgewählte Reihe.
- [ ] Der Versuch, die eigene Moderatorzuweisung zu entfernen oder auf eine niedrigere Rolle zu setzen, wird abgewiesen; die Moderatorzuweisung bleibt bestehen.
- [ ] Zuweisungen in anderen Reihen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 4.3.7 Fehlende Serienberechtigung prüfen – Prüfrolle: globale Nutzerrolle + Moderator*in ausschließlich in einer anderen Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Eine Moderatorzuweisung gilt ausschließlich für die ausdrücklich zugewiesene Reihe. Für die nicht zugewiesene Zielreihe dürfen weder Reihenverwaltung noch fachliche Inhalte zugänglich sein.

**Prüfschritt**
 1. Mit einem globalen Nutzerkonto anmelden, das in Testreihe B Moderator*in ist, für die geprüfte Zielreihe A aber keine Serienzuweisung besitzt.
 1. Die Verwaltungsseite von Testreihe A über Navigation und direkte URL aufrufen. Ist die Seite nicht erreichbar, keine Bearbeitungs- oder Mitgliederverwaltungsaktion für A versuchen; die Prüfung der Reihenverwaltung für A hier beenden.
 1. Nur wenn die Verwaltungsseite von A erreichbar ist: Eine Bearbeitung der Reihe und die Verwaltung ihrer Serienmitglieder über die Oberfläche bzw. vorgesehene Direktaufrufe versuchen.
 1. Die Terminseite eines Termins aus A direkt aufrufen. Ist sie nicht erreichbar, keine nachgelagerte Terminaktion für A ausführen.
 1. Die Themenseite eines Themas aus A direkt aufrufen. Ist sie nicht erreichbar, keine nachgelagerte Themenaktion für A ausführen.
 1. Anschließend die Verwaltungs- und fachlichen Ansichten der tatsächlich zugewiesenen Testreihe B aufrufen.

**Ergebnisprüfung**

- [ ] Die Verwaltungsseite von Testreihe A ist nicht erreichbar; falls sie erreichbar ist, werden Reihenbearbeitung und Mitgliederverwaltung verweigert.
- [ ] Die direkten URL-Aufrufe zu Terminen und Themen aus A geben keine fachlichen Inhalte frei.
- [ ] Eine Moderatorzuweisung in Testreihe B gewährt keine Rechte für Testreihe A.
- [ ] Daten und Berechtigungen von Testreihe A bleiben unverändert.
- [ ] Testreihe B bleibt für das Konto gemäß seiner dortigen Moderatorrolle erreichbar.

- **Test erfolgreich:** [ ]

---

### 4.4 Termine und Besprechungsübersicht

#### 4.4.1 Terminübersicht aufrufen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Die Terminübersicht über die Navigation öffnen, die für das Testkonto verfügbaren Reihen bzw. Termine laden und den angezeigten Umfang prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Termine der berechtigten Reihen werden angezeigt.
- [ ] Datum und Reihenbezeichnung stimmen.
- [ ] Vergangene Termine sind als vergangen bzw. abgeschlossen und zukünftige Termine als anstehend erkennbar; beide gehören zur zugewiesenen Besprechungsreihe.
- [ ] Termine nicht zugewiesener Reihen werden nicht angezeigt.

- **Test erfolgreich:** [ ]

#### 4.4.2 Einzelnen Termin verschieben – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Einen zugewiesenen Testtermin öffnen, Datum oder Uhrzeit auf einen freien Testzeitpunkt ändern und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Termin wird am neuen Datum angezeigt.
- [ ] Der bisherige Termin wird nicht zusätzlich als Duplikat angezeigt.
- [ ] Zugehörige Tagesordnungspunkte und Zuständigkeiten bleiben dem Termin zugeordnet.
- [ ] Die übrigen Termine der Reihe entsprechen weiterhin dem vorgesehenen Rhythmus.

- **Test erfolgreich:** [ ]

#### 4.4.3 Einzelnen Termin löschen – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Einen eigens angelegten entbehrlichen Testtermin öffnen, den Löschvorgang auslösen und die Rückfrage bestätigen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der ausgewählte Termin ist nach dem Löschen weder in der Terminübersicht noch in der Terminliste der Reihe vorhanden.
- [ ] Nicht ausgewählte Termine bleiben erhalten.
- [ ] Der gelöschte Termin ist entfernt; seine Tagesordnungspunkte und Teilnehmenden sind dem nächsten nicht abgeschlossenen Termin derselben Reihe zugeordnet. Die zugehörigen Themen bleiben erhalten.
- [ ] Es bleiben keine ungewollten Zuordnungen oder doppelten Einträge zurück.

- **Test erfolgreich:** [ ]

#### 4.4.4 Teilnehmerliste bearbeiten – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Die Teilnehmerliste eines zugewiesenen Testtermins öffnen, ein separates Testkonto hinzufügen oder entfernen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die ausgewählten Konten werden in der Teilnehmerliste angezeigt.
- [ ] Abgewählte Konten werden nicht mehr angezeigt.
- [ ] Die Änderung betrifft nur den ausgewählten Termin.
- [ ] Die Serienberechtigungen der Konten bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 4.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: globale Nutzerrolle + Leser*in der geprüften Reihe
**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der exakt beschriebenen Serienrolle anmelden.
 1. Einen abgeschlossenen Testtermin der zugewiesenen Reihe öffnen und den Protokoll-/Tagesordnungsstand dokumentieren.
 1. Eine schreibende Aktion am abgeschlossenen Termin versuchen; falls die Oberfläche keine Aktion anbietet, den vorgesehenen Direktaufruf mit unveränderten Testdaten prüfen und anschließend den Termin neu laden.

**Ergebnisprüfung**
- [ ] Der Termin kann mit dem für diesen Testfall verwendeten Leserkonto weiterhin geöffnet werden.
- [ ] Schreibende Aktionen auf dem abgeschlossenen Termin werden für Leser*innen abgewiesen oder sind nicht verfügbar.
- [ ] Der gespeicherte Protokollstand und die Tagesordnung bleiben unverändert.

- **Test erfolgreich:** [ ]
### 4.5 Themen anlegen und bearbeiten

#### 4.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Im Dashboard die Funktion zum Anlegen eines Themas öffnen, ein eindeutig erkennbares Testthema mit Pflichtangaben erfassen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Das Thema erscheint in der Themenübersicht.
- [ ] Titel und Hauptzuständigkeit entsprechen den Eingaben.
- [ ] Das Thema ist der ausgewählten Besprechungsreihe zugeordnet.
- [ ] Für den ausgewählten Termin ist der zugehörige Tagesordnungspunkt vorhanden.
- [ ] Das Thema ist nicht versehentlich in einer anderen Reihe angelegt worden.

- **Test erfolgreich:** [ ]

#### 4.5.2 Thema über einen Termin anlegen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Einen zugänglichen Testtermin öffnen, dort ein neues Testthema mit eindeutiger Bezeichnung und Pflichtangaben anlegen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Das neue Thema ist angelegt.
- [ ] Der Tagesordnungspunkt ist dem geöffneten Termin zugeordnet.
- [ ] Die Hauptzuständigkeit entspricht dem ausgewählten Konto; die abweichende Zuständigkeit wird separat mit dem im Prüfschritt ausgewählten Konto angezeigt.
- [ ] Das Thema ist in der Themenübersicht auffindbar.

- **Test erfolgreich:** [ ]

#### 4.5.3 Thema bearbeiten – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Ein zugängliches Testthema öffnen, ein unkritisches Feld ändern, speichern und die Detailansicht erneut laden.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Titel, Status und Hauptzuständigkeit entsprechen den gespeicherten Werten.
- [ ] Änderungen bleiben nach dem Neuladen erhalten.
- [ ] Jeder Tagesordnungspunkt bleibt dem bearbeiteten Thema zugeordnet; vorhandene historische Protokoll-Snapshots behalten ihren zuvor gespeicherten Inhalt.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

- **Test erfolgreich:** [ ]

#### 4.5.4 Themenstatus ändern – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Ein zugängliches Testthema öffnen, den Status über die vorgesehene Statusaktion ändern und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der neue Status wird in der Detailansicht angezeigt.
- [ ] Die Übersicht zeigt denselben Statuswert wie die Themendetailansicht.
- [ ] Der Status des Tagesordnungspunkts bleibt unverändert; geändert wird ausschließlich der Status des übergeordneten Themas.

- **Test erfolgreich:** [ ]

#### 4.5.5 Thema archivieren und wieder öffnen – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Ein entbehrliches Testthema archivieren, die Archivansicht öffnen und das Thema anschließend über die vorgesehene Funktion wieder öffnen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Archivierte Themen erscheinen im Archiv und nicht mehr in der regulären offenen Themenliste.
- [ ] Wieder geöffnete Themen erscheinen wieder im vorgesehenen aktiven Bereich.
- [ ] Titel, Zuständigkeit, Kommentare und zugehörige historische Inhalte bleiben erhalten.
- [ ] Der Änderungsverlauf bildet die Aktion ab.

- **Test erfolgreich:** [ ]

#### 4.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Ein entbehrliches Testthema aus Testreihe A auswählen, die ausdrücklich als Ziel vorgesehene Testreihe B wählen und den Übertragungsvorgang bestätigen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Das Thema ist der vorgesehenen Zielreihe zugeordnet.
- [ ] Der vorgesehene Zieltermin enthält den Tagesordnungspunkt.
- [ ] Übertragungsnotiz und Übertragungsverlauf sind nachvollziehbar.
- [ ] Die Serienzuweisungen der beteiligten Konten in Quell- und Zielreihe bleiben unverändert; die Themenübertragung erzeugt keine zusätzliche Serienberechtigung.
- [ ] Andere Themen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 4.5.7 Themenvorschläge verwenden – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Die Themenvorschläge im vorgesehenen Eingabebereich öffnen, einen passenden Vorschlag auswählen und dessen Übernahme auslösen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Titel und übernommene Vorschlagsdaten entsprechen dem ausgewählten Vorschlag.
- [ ] Das Thema bzw. der Tagesordnungspunkt wird mit den eingegebenen Daten angelegt.
- [ ] Es wird kein zusätzlicher oder doppelter Datensatz angelegt.

- **Test erfolgreich:** [ ]

---

### 4.6 Tagesordnungspunkte und Wiedervorlagen

#### 4.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Einen zugänglichen Testtermin mit Tagesordnung öffnen, einen vorhandenen Test-Tagesordnungspunkt ändern und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der gespeicherte Text wird beim erneuten Öffnen des Tagesordnungspunkts wortgleich angezeigt.
- [ ] Der Status des Tagesordnungspunkts entspricht der Auswahl.
- [ ] Die abweichende Zuständigkeit entspricht dem im Prüfschritt ausgewählten Konto und bleibt von der Hauptzuständigkeit getrennt.
- [ ] Der allgemeine Themenstatus bleibt davon getrennt.

- **Test erfolgreich:** [ ]

#### 4.6.2 Tagesordnungspunkte sortieren – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Bei einem Testtermin mindestens zwei Tagesordnungspunkte in eine andere Reihenfolge bringen, die Sortierung speichern und die Seite neu laden.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Reihenfolge entspricht der zuletzt vorgenommenen Sortierung.
- [ ] Jeder Tagesordnungspunkt ist weiterhin dem richtigen Thema zugeordnet.
- [ ] Es fehlen keine Punkte und es sind keine Duplikate entstanden.

- **Test erfolgreich:** [ ]

#### 4.6.3 Tagesordnungspunkt entfernen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Einen entbehrlichen Test-Tagesordnungspunkt auswählen, die Entfernen-Funktion auslösen und die Änderung bestätigen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Punkt ist aus dem ausgewählten Termin entfernt.
- [ ] Das zugrunde liegende Thema bleibt in der Themenübersicht erhalten; entfernt wird ausschließlich der ausgewählte Tagesordnungspunkt.
- [ ] Andere Tagesordnungspunkte bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 4.6.4 Wiedervorlage anlegen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Bei einem Testthema eine Wiedervorlage mit einem konkreten Folgetermin setzen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Tagesordnungspunkt erscheint im vorgesehenen Zieltermin.
- [ ] Die Verbindung zum vorherigen Tagesordnungspunkt ist nachvollziehbar.
- [ ] Status und Zuständigkeit entsprechen den vorgesehenen Übernahmeregeln.
- [ ] Es ist keine doppelte Wiedervorlage entstanden.

- **Test erfolgreich:** [ ]

#### 4.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Eine Wiedervorlage für ein Testthema anlegen, den ersten Folgetermin bearbeiten bzw. abschließen und den nächsten vorgesehenen Termin auf die fortgeführte Wiedervorlage prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Wiedervorlagekette ist chronologisch nachvollziehbar.
- [ ] Jeder Punkt ist dem richtigen Termin zugeordnet.
- [ ] Frühere Protokollstände bleiben unverändert.
- [ ] Es entstehen keine doppelten oder voneinander getrennten Ketten.

- **Test erfolgreich:** [ ]

#### 4.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: globale Nutzerrolle + Leser*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Einen zugänglichen Termin mit bereits abgeschlossenen bzw. historischen Tagesordnungseinträgen öffnen und den historischen Eintrag gezielt auswählen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Datum, Reihenbezeichnung, Text, Status und Verantwortlichkeit stimmen mit den im historischen Tagesordnungseintrag gespeicherten Werten überein.
- [ ] Historische Einträge lassen sich nicht unberechtigt verändern.
- [ ] Zugriff ist auf berechtigte Konten begrenzt.

- **Test erfolgreich:** [ ]

---

### 4.7 Kommentare, Anlagen und Links

#### 4.7.1 Kommentar hinzufügen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Ein zugängliches Testthema öffnen, einen eindeutig als Test erkennbaren Kommentar hinzufügen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Kommentar wird beim richtigen Thema angezeigt.
- [ ] Als Autor wird das angemeldete Testkonto angezeigt; der Erstellungszeitpunkt liegt im Zeitraum der gerade ausgeführten Aktion.
- [ ] Der Kommentar bleibt nach dem Neuladen erhalten.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

- **Test erfolgreich:** [ ]

#### 4.7.2 Datei als Themenanlage hochladen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Ein zugängliches Testthema öffnen, eine harmlose Testdatei als Anlage auswählen und hochladen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Anlage wird beim richtigen Thema angezeigt.
- [ ] Die angezeigte Bezeichnung entspricht der eingegebenen Bezeichnung; die Datei ist dem ausgewählten Thema zugeordnet und lässt sich öffnen.
- [ ] Die Datei lässt sich mit einem berechtigten Konto herunterladen.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

- **Test erfolgreich:** [ ]

#### 4.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Bei einem zugänglichen Testthema einen dafür vorgesehenen Test-Netzwerkpfad oder eine unkritische Test-URL hinterlegen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der gespeicherte Pfad bzw. die URL entspricht exakt der eingegebenen Zeichenfolge.
- [ ] Unterstützte Pfade werden als anklickbarer Link dargestellt und öffnen das hinterlegte Ziel.
- [ ] Nicht unterstützte oder ungültige Werte werden nicht als unsichere Links ausgegeben.
- [ ] Die Anwendung behauptet nicht, die Erreichbarkeit einer externen Freigabe zu garantieren.

- **Test erfolgreich:** [ ]

#### 4.7.4 Anlage herunterladen – Prüfrolle: globale Nutzerrolle + Leser*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Ein zugängliches Testthema mit einer bekannten Testdatei öffnen, die Anlage herunterladen und den Dateiinhalt mit der hochgeladenen Testdatei vergleichen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Berechtigte Konten können die zugehörige Datei herunterladen.
- [ ] Dateiinhalt und Dateiname entsprechen der hochgeladenen Datei.
- [ ] Nicht berechtigte Konten erhalten keinen Dateizugriff.

- **Test erfolgreich:** [ ]

#### 4.7.5 Anlage löschen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Ein zugängliches Testthema mit einer entbehrlichen Testanlage öffnen, die Anlage löschen und die Rückfrage bestätigen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Anlage wird nicht mehr in der Themenansicht angezeigt.
- [ ] Der direkte Download der entfernten Anlage ist nicht mehr möglich.
- [ ] Andere Anlagen und Themen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 4.7.6 Upload-Grenzen prüfen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Für ein zugängliches Testthema eine Testdatei unterhalb und eine oberhalb der konfigurierten Upload-Grenze verwenden und beide Uploadversuche getrennt ausführen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Zulässige Dateien innerhalb des Limits werden angenommen.
- [ ] Zu große Dateien werden abgewiesen.
- [ ] Nicht erlaubte Dateiendungen werden abgewiesen.
- [ ] Abgewiesene Uploads erzeugen keine ungewollten Anlagen-Datensätze.

- **Test erfolgreich:** [ ]

---

### 4.8 Besprechung abschließen und Protokoll

#### 4.8.1 Besprechung abschließen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Einen dafür vorgesehenen Testtermin öffnen, die Abschlussfunktion auslösen und die Bestätigung durchführen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Termin ist als abgeschlossen gekennzeichnet.
- [ ] Ein Protokoll-Snapshot wurde erstellt.
- [ ] Teilnehmerliste und Tagesordnungstexte sind gegen weitere Bearbeitung gesperrt.
- [ ] Der Abschluss wird im Änderungsverlauf dokumentiert.

- **Test erfolgreich:** [ ]

#### 4.8.2 Protokoll anzeigen – Prüfrolle: globale Nutzerrolle + Leser*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Einen zugänglichen abgeschlossenen Testtermin öffnen und das gespeicherte Protokoll aufrufen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Protokoll zeigt den beim Abschluss gesicherten Stand.
- [ ] Historische Werte werden nicht durch spätere Änderungen am Thema überschrieben.
- [ ] Protokoll ist für berechtigte Leser*innen sichtbar.

- **Test erfolgreich:** [ ]

#### 4.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: globale Nutzerrolle + Leser*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Das Protokoll eines zugänglichen Testtermins öffnen, die Druckansicht aufrufen und zusätzlich den PDF-Export auslösen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Druckansicht enthält den richtigen Termin und Protokollstand.
- [ ] PDF lässt sich öffnen.
- [ ] PDF enthält die vorgesehenen Protokolldaten.
- [ ] Im PDF erscheinen die aktuell gespeicherte Organisationsbezeichnung und das aktuell gespeicherte Organisationslogo.
- [ ] Unberechtigte Konten können den Export nicht abrufen.

- **Test erfolgreich:** [ ]

#### 4.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Einen abgeschlossenen Testtermin der zugewiesenen Reihe öffnen und die Funktion zum Wiederöffnen auslösen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Termin ist nach dem Wiederöffnen bearbeitbar.
- [ ] Der vorherige Protokollstand bleibt als historischer Stand nachvollziehbar.
- [ ] Die erneute Bearbeitung und der erneute Abschluss funktionieren.
- [ ] Teilnehmer*innen ohne Moderatorrechte können den Termin nicht wieder öffnen.

- **Test erfolgreich:** [ ]

#### 4.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: globale Nutzerrolle + Leser*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Ein zugängliches Testthema mit Protokolleinträgen öffnen und den Themenprotokoll-PDF-Export auslösen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] PDF enthält die dem Thema zugeordneten historischen Einträge.
- [ ] PDF-Datum und Reihenbezeichnung stimmen mit dem ausgewählten Termin überein; Texte und Statuswerte entsprechen dem gespeicherten Themen- und Protokollstand.
- [ ] Der Export ist auf berechtigte Konten begrenzt.

- **Test erfolgreich:** [ ]

---

### 4.9 Offene Themen und Archiv

#### 4.9.1 Offene Themen aufrufen – Prüfrolle: globale Nutzerrolle + Teilnehmer*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Die Übersicht der offenen Themen öffnen und die angezeigten Themen anhand der zugewiesenen Reihen prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Nur fachlich zugängliche Themen werden angezeigt.
- [ ] Angezeigter Status und Zuständigkeit entsprechen den gespeicherten Themenwerten; die angezeigte Reihe entspricht der tatsächlichen Zuordnung des Themas.
- [ ] Auswahl und Filter führen zu passenden Ergebnissen.

- **Test erfolgreich:** [ ]

#### 4.9.2 Archiv aufrufen – Prüfrolle: globale Nutzerrolle + Leser*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Das Archiv über die Navigation öffnen, die Ergebnisliste laden und den angezeigten Datenumfang prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Archivierte Themen sind im Archiv auffindbar.
- [ ] Es werden ausschließlich historische Inhalte der ausdrücklich zugewiesenen Reihe angezeigt; Inhalte nicht zugewiesener Reihen bleiben verborgen.
- [ ] Nicht archivierte Themen werden nicht fälschlich als archiviert dargestellt.

- **Test erfolgreich:** [ ]

#### 4.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: globale Nutzerrolle + Leser*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Eine eigens dafür vorgesehene Testreihe mit archivierten Inhalten verwenden, die vorgesehene Reihenlöschung durchführen bzw. den vorbereiteten Löschzustand nutzen und anschließend den historischen Zugriff prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der vorgesehene historische Lesezugriff des früheren Reihenmitglieds bleibt bestehen.
- [ ] Das unbeteiligte Konto erhält keinen Zugriff.
- [ ] Die gelöschte Reihe erscheint nicht mehr in den aktiven Reihenlisten; aus dem historischen Zugriff entsteht keine aktive Serienzuweisung und keine Berechtigung zur Reihenverwaltung.

- **Test erfolgreich:** [ ]

---

### 4.10 Berechtigungsanträge

#### 4.10.1 Serienberechtigung beantragen – Prüfrolle: globale Nutzerrolle ohne Serienzuweisung

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Auch ohne Serienzuweisung darf das Konto einen Antrag für eine Besprechungsreihe stellen; der Antrag selbst gewährt noch keinen Zugriff auf Reiheninhalte.

**Prüfschritt**
 1. Mit einem globalen Nutzerkonto anmelden, dem für keine Besprechungsreihe eine Serienrolle zugewiesen ist.
 1. Die Funktion zum Beantragen einer Serienberechtigung öffnen, eine Testreihe und die gewünschte Rolle auswählen und den Antrag absenden.
 1. Nach dem Absenden die Antragsübersicht neu laden und den gespeicherten Antrag prüfen.

**Ergebnisprüfung**

- [ ] Der Antrag wird der richtigen Person und Besprechungsreihe zugeordnet.
- [ ] Im Antrag wird genau die im Prüfschritt ausgewählte gewünschte Serienrolle angezeigt.
- [ ] Der Antrag erscheint mit offenem Status.
- [ ] Durch den Antrag allein entstehen noch keine fachlichen Schreibrechte.

- **Test erfolgreich:** [ ]

#### 4.10.2 Berechtigungsantrag entscheiden – Prüfrolle: globale Nutzerrolle (Moderator*in der geprüften Reihe)

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt für Anträge der eigenen moderierten Reihe; Zugriff verweigert für fremde Reihen.**

**Prüfschritt**
 1. Mit einem globalen Nutzerkonto anmelden, das für Testreihe A ausdrücklich als Moderator*in zugewiesen ist.
 1. Für ein separates Testkonto einen offenen Berechtigungsantrag für Testreihe A vorbereiten.
 1. Den Antrag für Testreihe A öffnen und einmal genehmigen oder ablehnen.
 1. Zusätzlich einen offenen Antrag für Testreihe B vorbereiten, für die keine Moderatorzuweisung besteht, und versuchen, diesen zu entscheiden.
 1. Die Antragsliste und die Serienzuweisungen beider Testkonten neu laden.

**Ergebnisprüfung**
- [ ] Der Antrag für die eigene moderierte Testreihe A wird aus der Liste offener Anträge entfernt bzw. als entschieden gekennzeichnet.
- [ ] Die gespeicherte Entscheidung für Testreihe A entspricht exakt der gewählten Genehmigung oder Ablehnung.
- [ ] Der Antrag für die fremde Testreihe B kann nicht entschieden werden und bleibt unverändert offen.
- [ ] Bei Genehmigung für Testreihe A erhält das Testkonto ausschließlich die genehmigte Serienrolle für diese Reihe.
- [ ] Andere Anträge und Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 4.10.3 Bereits vorhandenen Antrag erneut bearbeiten – Prüfrolle: globale Nutzerrolle ohne Serienzuweisung

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Auch ohne Serienzuweisung darf das Konto einen Antrag für eine Besprechungsreihe stellen; der Antrag selbst gewährt noch keinen Zugriff auf Reiheninhalte.

**Prüfschritt**
 1. Mit einem globalen Nutzerkonto anmelden, dem für keine Besprechungsreihe eine Serienrolle zugewiesen ist.
 1. Für dasselbe Testkonto einen bereits offenen Antrag für dieselbe Testreihe vorbereiten und den Antrag erneut absenden; falls die Oberfläche das Formular ausblendet, den entsprechenden POST-Aufruf direkt wiederholen.
 1. Nach dem Absenden die Antragsübersicht neu laden und den gespeicherten Antrag prüfen.

**Ergebnisprüfung**

- [ ] Es entstehen keine unzulässigen doppelten offenen Anträge.
- [ ] Bereits entschiedene Anträge werden nicht irrtümlich als offen behandelt.
- [ ] Durch die erneute Antragstellung entsteht keine Serienzuweisung und kein Zugriff auf Reiheninhalte, solange der Antrag nicht genehmigt wurde.

- **Test erfolgreich:** [ ]

---

### 4.11 Benutzer- und Themenimport/-export

#### 4.11.1 Benutzer als CSV exportieren – Prüfrolle: globale Nutzerrolle ohne globale Adminrolle
**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Benutzerverwaltung bzw. den Benutzerexport öffnen und den CSV-Export über die Oberfläche oder den vorgesehenen Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**
- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Benutzer-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Konten- oder Profildaten offengelegt.

- **Test erfolgreich:** [ ]
#### 4.11.2 Benutzer per CSV importieren – Prüfrolle: globale Nutzerrolle ohne globale Adminrolle
**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine CSV-Datei mit ausschließlich separaten Testkonten vorbereiten und den Import über die Oberfläche bzw. den vorgesehenen Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Import wird abgewiesen; es werden keine Testkonten angelegt oder bestehende Konten verändert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entstehen keine Teilimporte oder unvollständigen Benutzerzuordnungen.

- **Test erfolgreich:** [ ]
#### 4.11.3 Themen als CSV exportieren – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Die Themen-CSV-Funktion für eine zugängliche Testreihe aufrufen, den Export starten und die heruntergeladene Datei öffnen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Export ist lesbar und enthält die vorgesehenen Themen.
- [ ] CSV-Zuständigkeiten, Statuswerte und Reihenbezüge stimmen mit den gespeicherten Datensätzen der exportierten Reihe überein.
- [ ] Inhalte außerhalb des zulässigen Berechtigungs- bzw. Exportumfangs werden nicht offengelegt.

- **Test erfolgreich:** [ ]

#### 4.11.4 Themen per CSV importieren – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Eine vorbereitete CSV-Datei mit eindeutig markierten Testdatensätzen auswählen, den Import starten und die Rückmeldung der Anwendung prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Jede gültige CSV-Zeile legt genau das zugehörige Testthema an oder aktualisiert es; ungültige Zeilen werden nicht teilweise gespeichert.
- [ ] Ungültige Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Jeder importierte Datensatz ist der in der CSV-Zeile angegebenen Besprechungsreihe zugeordnet; die Zuständigkeit entspricht dem dort angegebenen Konto.
- [ ] Es entstehen keine unbeabsichtigten Duplikate.

- **Test erfolgreich:** [ ]

---

### 4.12 Änderungsverlauf und Audit

#### 4.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Den Änderungsverlauf einer zugewiesenen Testreihe öffnen und die serienbezogenen Ereignisse aufrufen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Moderator*in sieht die Ereignisse der eigenen moderierten Reihe.
- [ ] Ereignisse anderer Reihen werden nicht offengelegt.
- [ ] Akteur, Zeitpunkt und Aktion sind nachvollziehbar.
- [ ] Unberechtigte Konten erhalten keinen Zugriff.

- **Test erfolgreich:** [ ]

#### 4.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe
**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff auf die Änderungsverlaufseite erlaubt; Systemereignisse eingeschränkt.** Die Änderungsverlaufseite ist erreichbar. Das globale Nutzerkonto mit Moderatorzuweisung sieht ausschließlich Ereignisse seiner eigenen moderierten Reihe; systembezogene Ereignisse bleiben ausgeblendet.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen Rolle bzw. Serienzuweisung anmelden.
 1. Die Seite **Änderungsverlauf** über die Navigation oder direkt öffnen.
 1. Den Bereich für Systemereignisse aufrufen bzw. den passenden Filter verwenden.
 1. Prüfen, welche Ereignisse tatsächlich angezeigt werden; bei Bedarf die Seite neu laden und einen direkten Filteraufruf testen.

**Ergebnisprüfung**
- [ ] Die Änderungsverlaufseite wird geöffnet.
- [ ] Ereignisse der eigenen moderierten Reihe können weiterhin angezeigt werden.
- [ ] Systembezogene Ereignisse werden nicht angezeigt oder exportiert.
- [ ] Ereignisse anderer Reihen bleiben verborgen.

- **Test erfolgreich:** [ ]
#### 4.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Den für die Rolle zugänglichen Änderungsverlauf öffnen, den CSV-Export auslösen und die Datei öffnen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] CSV-Datei ist lesbar.
- [ ] Export enthält nur die für die Rolle zulässigen Ereignisse.
- [ ] Direkter Exportaufruf ohne passende Berechtigung wird abgewiesen.
- [ ] Nicht erforderliche vertrauliche Daten werden nicht exportiert.

- **Test erfolgreich:** [ ]

---

### 4.13 Aufbewahrung und automatische Löschung

#### 4.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: globale Nutzerrolle ohne globale Adminrolle
**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Verwaltungsseite für Aufbewahrungsfristen direkt und über die Navigation öffnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die administrativen Aufbewahrungseinstellungen werden nicht angezeigt und der Zugriff wird verweigert bzw. zur berechtigten Ansicht umgeleitet.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Fristwerte oder administrativen Löschoptionen offengelegt.

- **Test erfolgreich:** [ ]
#### 4.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: globale Nutzerrolle + Leser*in der geprüften Reihe

**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und die für die Zielreihe ausdrücklich vorgesehene Serienrolle sicherstellen.
 1. Das Archiv öffnen, bei einem vorbereiteten archivierten Testthema die angezeigte Aufbewahrungsfrist und das vorgesehene Löschdatum ablesen; nach einem separat durchgeführten Retention-Lauf den Eintrag erneut prüfen.
 1. Die Anzeige vor und nach dem Retention-Lauf vergleichen und die nachfolgenden Ergebnisprüfungen anhand des tatsächlichen Bestands durchführen.

**Ergebnisprüfung**

- [ ] Thema bleibt vor Fristablauf erhalten.
- [ ] Abgelaufenes archiviertes Thema wird gemäß der Fachregel endgültig entfernt.
- [ ] Mit dem abgelaufenen archivierten Thema verknüpfte Inhalte und Dateien werden gemäß derselben konfigurierten Aufbewahrungs- und Löschregel behandelt.
- [ ] Nicht abgelaufene oder nicht archivierte Themen bleiben erhalten.

- **Test erfolgreich:** [ ]

#### 4.13.3 Retention wiederholt ausführen – Prüfrolle: globale Nutzerrolle ohne globale Adminrolle
**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den vorgesehenen Retention-Auslöser bzw. den direkten Ausführungsendpunkt mit vorbereiteten Testdaten aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Retention-Lauf wird nicht gestartet bzw. die Aktion wird abgewiesen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Termine, Protokolle, Themen oder Dateien gelöscht oder verändert.

- **Test erfolgreich:** [ ]
### 4.14 Auditor*innenbereich

#### 4.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: globale Nutzerrolle ohne Auditorrolle
**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Auditor*innenübersicht über die Navigation und zusätzlich über ihre direkte URL aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Rolle erhält keine Auditor*innenübersicht; die Anwendung verweigert den Zugriff oder leitet zur regulären Startseite weiter.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Audit- oder Organisationsprüfdaten angezeigt.

- **Test erfolgreich:** [ ]
#### 4.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: globale Nutzerrolle ohne Auditorrolle
**Berechtigungserwartung für Globale Rolle Nutzer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die im Testfall aufgeführten Auditor*innen-URLs einzeln direkt aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Jeder geschützte Auditor*innen-Endpunkt verweigert den Zugriff oder leitet auf eine reguläre, für die Rolle zulässige Seite um.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Audit-, Benutzer- oder Organisationsdaten offengelegt.

- **Test erfolgreich:** [ ]
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

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Das Dashboard über die Hauptnavigation öffnen und vollständig laden lassen. Die angezeigten Kacheln, Kennzahlen und Verknüpfungen prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

- **Test erfolgreich:** [ ]

#### 5.1.2 Navigation und Darstellungsvarianten – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Hauptnavigation auf Desktop und mobiler Ansicht öffnen. Menüpunkte, Untermenüs und Darstellungsvarianten durchgehen; nicht angebotene Funktionen nicht über fremde Konten simulieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Nach dem Neuladen ist weiterhin die zuvor ausgewählte Darstellungsvariante aktiv.

- **Test erfolgreich:** [ ]

---

### 5.2 Persönliches Konto und eigene Aufgaben

#### 5.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die persönlichen Kontoeinstellungen öffnen, ein unkritisches Testfeld ändern und speichern. Die Seite neu laden und den gespeicherten Wert kontrollieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 5.2.2 Eigene Aufgaben aufrufen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die persönliche Aufgabenübersicht öffnen, vorhandene eigene Aufgaben durchgehen und – falls keine vorhanden sind – den vorgesehenen Leerzustand prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Eigene offene Themen werden im vorgesehenen Abschnitt angezeigt.
- [ ] Eigene Tagesordnungspunkte werden getrennt davon angezeigt.
- [ ] Nicht zugewiesene oder nicht berechtigte Inhalte werden nicht zusätzlich eingeblendet.
- [ ] Bei fehlenden Aufgaben wird ein geeigneter Leerzustand angezeigt.

- **Test erfolgreich:** [ ]

---

### 5.3 Besprechungsreihen verwalten

#### 5.3.1 Zugriff auf die Serienverwaltung prüfen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Seite der Serienverwaltung darf für diese Rolle ohne entsprechende Berechtigung nicht erreichbar sein.

**Prüfschritt**

 1. Mit einem Testkonto anmelden, dem für die geprüfte Besprechungsreihe ausdrücklich keine Serienzuweisung erteilt wurde.
 1. Prüfen, ob die Serienverwaltung in der Navigation angeboten wird.
 1. Die Seite der Serienverwaltung zusätzlich über ihre direkte URL aufrufen.
 1. Feststellen, dass der Zugriff verweigert wird und keine Serienverwaltungsseite mit Reihen oder Verwaltungsfunktionen angezeigt wird.

**Ergebnisprüfung**

- [ ] Die Serienverwaltung ist für diese Rolle weder über die Navigation noch über die direkte URL erreichbar.
- [ ] Es werden keine Reihen oder Verwaltungsfunktionen offengelegt.



- **Test erfolgreich:** [ ]

---

### 5.4 Termine und Besprechungsübersicht

#### 5.4.1 Terminübersicht aufrufen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Terminübersicht ist auch ohne Serienzuweisung erreichbar. Sie enthält in diesem Testkonto keine Termine.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden.
 1. Die Terminübersicht über die Navigation bzw. den vorgesehenen Aufruf öffnen.
 1. Die Ansicht bzw. Ergebnisliste laden und den angezeigten Datenumfang prüfen.

**Ergebnisprüfung**
- [ ] Die Terminübersicht wird ohne Zugriffsfehler geöffnet.
- [ ] Die Terminübersicht ist auch ohne Serienzuweisung erreichbar. Sie enthält in diesem Testkonto keine Termine.
- [ ] Es werden keine Termine, Themen oder Aufgaben aus nicht zugewiesenen Reihen offengelegt.

- **Test erfolgreich:** [ ]
#### 5.4.2 Einzelnen Termin verschieben – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Testtermin der nicht zugewiesenen bzw. nicht berechtigten Reihe direkt aufrufen und versuchen, Datum oder Uhrzeit zu ändern und zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Terminänderung wird verweigert oder die Aktion ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Datum, Uhrzeit und Serienzuordnung des Termins bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 5.4.3 Einzelnen Termin löschen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten entbehrlichen Testtermin der betroffenen Reihe aufrufen und die Löschaktion über Oberfläche bzw. POST-Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Termin wird nicht gelöscht.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Termin, Tagesordnungspunkte, Teilnehmerzuordnungen und Folgetermine bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 5.4.4 Teilnehmerliste bearbeiten – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Teilnehmerliste eines bekannten Testtermins öffnen und versuchen, ein separates Testkonto hinzuzufügen oder zu entfernen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Teilnehmeränderung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Teilnehmerliste und alle bestehenden Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 5.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten abgeschlossenen Testtermin öffnen und versuchen, einen Tagesordnungspunkt oder ein anderes gespeichertes Protokollmerkmal zu ändern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die schreibende Aktion am abgeschlossenen Termin wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Abschlussstatus, Protokoll-Snapshot und Tagesordnung bleiben unverändert.

- **Test erfolgreich:** [ ]
### 5.5 Themen anlegen und bearbeiten

#### 5.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Im Dashboard die Funktion zum Anlegen eines Themas aufrufen und ein eindeutig markiertes Testthema mit Pflichtangaben zu speichern versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Testthema wird nicht angelegt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht weder ein neuer Themendatensatz noch eine neue Zuordnung zu einem Termin.

- **Test erfolgreich:** [ ]
#### 5.5.2 Thema über einen Termin anlegen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Testtermin aufrufen und dort versuchen, ein neues Testthema mit eindeutiger Bezeichnung anzulegen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Testthema wird nicht angelegt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht weder ein neuer Themendatensatz noch ein zusätzlicher Tagesordnungseintrag.

- **Test erfolgreich:** [ ]
#### 5.5.3 Thema bearbeiten – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen, ein unkritisches Feld ändern und die Änderung speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Themenänderung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Titel, Beschreibung, Status, Zuständigkeit und Reihenbezug bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 5.5.4 Themenstatus ändern – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und versuchen, dessen Status zu ändern und zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Statusänderung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der ursprüngliche Themenstatus und die zugehörigen Zeitstempel bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 5.5.5 Thema archivieren und wieder öffnen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema aufrufen und die Archivierungs- sowie – falls bereits archiviert – die Wiederöffnen-Aktion versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Archivieren bzw. Wiederöffnen wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Status, Archivierungsdatum und bisherige Themeninhalte bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 5.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema auswählen und versuchen, es in eine andere Testreihe zu übertragen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Übertragung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Thema bleibt der ursprünglichen Reihe zugeordnet; in der Zielreihe entsteht keine Kopie.

- **Test erfolgreich:** [ ]
#### 5.5.7 Themenvorschläge verwenden – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Der Vorschlags-Endpunkt ist erreichbar, liefert aber ausschließlich Themen aus zugänglichen Reihen. Ohne Serienzuweisung ist die Ergebnisliste leer.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden.
 1. Den direkten Endpunkt `/topics/suggestions/?q=te` mit einem Suchbegriff von mindestens zwei Zeichen aufrufen.
 1. Die JSON-Antwort und das Feld `results` prüfen.

**Ergebnisprüfung**
- [ ] Der Themenvorschlags-Endpunkt wird ohne Zugriffsfehler geöffnet.
- [ ] Der Vorschlags-Endpunkt ist erreichbar, liefert aber ausschließlich Themen aus zugänglichen Reihen. Ohne Serienzuweisung ist die Ergebnisliste leer.
- [ ] Es werden keine Termine, Themen oder Aufgaben aus nicht zugewiesenen Reihen offengelegt.

- **Test erfolgreich:** [ ]
### 5.6 Tagesordnungspunkte und Wiedervorlagen

#### 5.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Tagesordnungspunkt eines Testtermins öffnen, ein Feld ändern und speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Bearbeitung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Text, Zuständigkeit, Status und Zuordnung des Tagesordnungspunkts bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 5.6.2 Tagesordnungspunkte sortieren – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen Testtermin mit mindestens zwei Tagesordnungspunkten öffnen und versuchen, deren Reihenfolge zu ändern und zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Sortierung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die ursprüngliche Reihenfolge und Positionswerte bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 5.6.3 Tagesordnungspunkt entfernen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Tagesordnungspunkt auswählen und versuchen, ihn über die Oberfläche oder den vorgesehenen POST-Aufruf zu entfernen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Tagesordnungspunkt wird nicht entfernt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Tagesordnungseintrag, Themenbezug und historische Inhalte bleiben erhalten.

- **Test erfolgreich:** [ ]
#### 5.6.4 Wiedervorlage anlegen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und versuchen, eine Wiedervorlage für einen Folgetermin anzulegen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Wiedervorlage wird nicht angelegt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht keine neue Termin- oder Tagesordnungspunktzuordnung.

- **Test erfolgreich:** [ ]
#### 5.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine vorbereitete Wiedervorlage öffnen und versuchen, sie auf den nächsten Termin fortzuführen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Fortführung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entstehen keine neuen Wiedervorlagen, Verknüpfungen oder doppelten Tagesordnungseinträge.

- **Test erfolgreich:** [ ]
#### 5.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Historie eines bekannten Termins bzw. Themas über die vorgesehene Seite und die direkte URL aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Historische Tagesordnungseinträge werden für diese Rolle nicht angezeigt oder ausgegeben.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine historischen Themen-, Protokoll- oder Zuständigkeitsdaten offengelegt.

- **Test erfolgreich:** [ ]
### 5.7 Kommentare, Anlagen und Links

#### 5.7.1 Kommentar hinzufügen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und einen eindeutig als Test erkennbaren Kommentar absenden.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Kommentar wird nicht gespeichert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht kein neuer Kommentar und bestehende Kommentare bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 5.7.2 Datei als Themenanlage hochladen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und eine harmlose Testdatei als Anlage hochzuladen versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Upload wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht kein neuer Anlagendatensatz und keine Datei wird dauerhaft gespeichert.

- **Test erfolgreich:** [ ]
#### 5.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und versuchen, einen Test-Netzwerkpfad oder eine unkritische Test-URL als Anlage zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Hinterlegen des Pfads bzw. Links wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird kein neuer Anlagen-, Pfad- oder Linkeintrag gespeichert.

- **Test erfolgreich:** [ ]
#### 5.7.4 Anlage herunterladen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine bekannte Testanlage direkt über den Download-Link bzw. den vorgesehenen Download-Endpunkt aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Download wird verweigert oder liefert keine geschützte Datei aus.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Dateiinhalt und Metadaten der Anlage werden nicht offengelegt.

- **Test erfolgreich:** [ ]
#### 5.7.5 Anlage löschen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine bekannte Testanlage auswählen und versuchen, sie zu löschen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Löschung der Anlage wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Anlagendatensatz und gespeicherte Datei bleiben unverändert erhalten.

- **Test erfolgreich:** [ ]
#### 5.7.6 Upload-Grenzen prüfen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Bei einem bekannten Testthema den Upload einer harmlosen Testdatei über die vorgesehene Upload-Funktion versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Upload wird wegen fehlender Berechtigung verweigert; eine Größenprüfung darf nicht zu einem erfolgreichen Upload führen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Datei gespeichert und es entsteht kein Anlagendatensatz.

- **Test erfolgreich:** [ ]
### 5.8 Besprechung abschließen und Protokoll

#### 5.8.1 Besprechung abschließen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten noch offenen Testtermin öffnen und versuchen, ihn über die Abschlussfunktion abzuschließen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Abschlussvorgang wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Termin bleibt offen; Abschlusszeitpunkt und Protokoll-Snapshot werden nicht angelegt.

- **Test erfolgreich:** [ ]
#### 5.8.2 Protokoll anzeigen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die direkte URL eines bekannten abgeschlossenen Testtermins bzw. dessen Protokollansicht aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Protokoll wird nicht angezeigt oder ausgegeben.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Tagesordnung, Kommentare, Zuständigkeiten oder Protokoll-Snapshots offengelegt.

- **Test erfolgreich:** [ ]
#### 5.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Druckansicht eines bekannten Testprotokolls aufrufen und den PDF-Export versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Druckansicht und PDF-Export werden verweigert oder sind nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Protokoll-PDF-Datei erzeugt oder heruntergeladen.

- **Test erfolgreich:** [ ]
#### 5.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten abgeschlossenen Testtermin aufrufen und die Wiederöffnen-Aktion über Oberfläche bzw. POST-Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Wiederöffnung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Abschlussstatus und gespeicherter Protokoll-Snapshot bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 5.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und den Export des Themenprotokolls als PDF versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der PDF-Export wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Themenprotokoll-PDF-Datei erzeugt oder heruntergeladen.

- **Test erfolgreich:** [ ]
### 5.9 Offene Themen und Archiv

#### 5.9.1 Offene Themen aufrufen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Übersicht offener Themen über die Navigation und die direkte URL öffnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine offenen Themen aus nicht zugewiesenen Reihen angezeigt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Anwendung legt keine neuen Termin- oder Tagesordnungspunktzuordnungen an.

- **Test erfolgreich:** [ ]
#### 5.9.2 Archiv aufrufen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Das Archiv ist erreichbar. Ohne Serienzuweisung werden keine archivierten Themen angezeigt.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden.
 1. Das Archiv über die Navigation bzw. den vorgesehenen Aufruf öffnen.
 1. Die Ansicht bzw. Ergebnisliste laden und den angezeigten Datenumfang prüfen.

**Ergebnisprüfung**
- [ ] Das Archiv wird ohne Zugriffsfehler geöffnet.
- [ ] Das Archiv ist erreichbar. Ohne Serienzuweisung werden keine archivierten Themen angezeigt.
- [ ] Es werden keine Termine, Themen oder Aufgaben aus nicht zugewiesenen Reihen offengelegt.

- **Test erfolgreich:** [ ]
#### 5.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Eine eigens dafür vorgesehene Testreihe mit archivierten Inhalten verwenden, die vorgesehene Reihenlöschung durchführen bzw. den vorbereiteten Löschzustand nutzen und anschließend den historischen Zugriff prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der vorgesehene historische Lesezugriff des früheren Reihenmitglieds bleibt bestehen.
- [ ] Das unbeteiligte Konto erhält keinen Zugriff.
- [ ] Die gelöschte Reihe erscheint nicht mehr in den aktiven Reihenlisten; aus dem historischen Zugriff entsteht keine aktive Serienzuweisung und keine Berechtigung zur Reihenverwaltung.

- **Test erfolgreich:** [ ]

---

### 5.10 Berechtigungsanträge

#### 5.10.1 Serienberechtigung beantragen – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Funktion zum Beantragen einer Serienberechtigung öffnen, eine Testreihe und die gewünschte Rolle auswählen und den Antrag absenden.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Antrag wird der richtigen Person und Besprechungsreihe zugeordnet.
- [ ] Im Antrag wird genau die im Prüfschritt ausgewählte gewünschte Serienrolle angezeigt.
- [ ] Der Antrag erscheint mit offenem Status.
- [ ] Durch den Antrag allein entstehen noch keine fachlichen Schreibrechte.

- **Test erfolgreich:** [ ]

#### 5.10.2 Berechtigungsantrag entscheiden – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen offenen Test-Berechtigungsantrag öffnen und versuchen, ihn zu genehmigen oder abzulehnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Entscheidung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Antrag bleibt offen; Serienrollen und Zugriffsrechte des antragstellenden Kontos bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 5.10.3 Bereits vorhandenen Antrag erneut bearbeiten – Prüfrolle: Nutzer*in ohne Serienzuweisung

**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Für dasselbe Testkonto einen bereits offenen Antrag für dieselbe Testreihe vorbereiten und den Antrag erneut absenden; falls die Oberfläche das Formular ausblendet, den entsprechenden POST-Aufruf direkt wiederholen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Es entstehen keine unzulässigen doppelten offenen Anträge.
- [ ] Bereits entschiedene Anträge werden nicht irrtümlich als offen behandelt.
- [ ] Die Serienzuweisungen des Testkontos bleiben unverändert; das erneute Absenden eines bereits offenen Antrags legt keine zusätzliche Zuweisung an.

- **Test erfolgreich:** [ ]

---

### 5.11 Benutzer- und Themenimport/-export

#### 5.11.1 Benutzer als CSV exportieren – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Benutzerverwaltung bzw. den Benutzerexport öffnen und den CSV-Export über die Oberfläche oder den vorgesehenen Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Benutzer-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Konten- oder Profildaten offengelegt.

- **Test erfolgreich:** [ ]
#### 5.11.2 Benutzer per CSV importieren – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine CSV-Datei mit ausschließlich separaten Testkonten vorbereiten und den Import über die Oberfläche bzw. den vorgesehenen Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Import wird abgewiesen; es werden keine Testkonten angelegt oder bestehende Konten verändert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entstehen keine Teilimporte oder unvollständigen Benutzerzuordnungen.

- **Test erfolgreich:** [ ]
#### 5.11.3 Themen als CSV exportieren – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den Themen-CSV-Export für eine bekannte Reihe über Oberfläche oder Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Themen-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Themeninhalte und Zuständigkeiten nicht zugänglicher Reihen werden nicht offengelegt.

- **Test erfolgreich:** [ ]
#### 5.11.4 Themen per CSV importieren – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine vorbereitete CSV-Datei mit eindeutig markierten Testthemen auswählen und den Import versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Import wird verweigert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Themen angelegt und keine bestehenden Themen, Tagesordnungspunkte oder Reihenbezüge verändert.

- **Test erfolgreich:** [ ]
### 5.12 Änderungsverlauf und Audit

#### 5.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff auf die Änderungsverlaufseite erlaubt; Serienereignisse eingeschränkt.** Die Änderungsverlaufseite ist erreichbar, zeigt ohne Serienzuweisung aber keine serienbezogenen Ereignisse.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen Rolle bzw. Serienzuweisung anmelden.
 1. Die Seite **Änderungsverlauf** über die Navigation oder direkt öffnen.
 1. Den Bereich für Serienereignisse aufrufen bzw. den passenden Filter verwenden.
 1. Prüfen, welche Ereignisse tatsächlich angezeigt werden; bei Bedarf die Seite neu laden und einen direkten Filteraufruf testen.

**Ergebnisprüfung**
- [ ] Die Änderungsverlaufseite wird geöffnet.
- [ ] Ohne Serienzuweisung werden keine serienbezogenen Ereignisse angezeigt.
- [ ] Ereignisse anderer Reihen oder globale Systemereignisse werden nicht offengelegt.

- **Test erfolgreich:** [ ]
#### 5.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff auf die Änderungsverlaufseite erlaubt; Systemereignisse eingeschränkt.** Die Änderungsverlaufseite ist erreichbar; systembezogene Ereignisse sind für Nutzer*innen ohne globale Admin- oder Auditorrolle nicht sichtbar.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen Rolle bzw. Serienzuweisung anmelden.
 1. Die Seite **Änderungsverlauf** über die Navigation oder direkt öffnen.
 1. Den Bereich für Systemereignisse aufrufen bzw. den passenden Filter verwenden.
 1. Prüfen, welche Ereignisse tatsächlich angezeigt werden; bei Bedarf die Seite neu laden und einen direkten Filteraufruf testen.

**Ergebnisprüfung**
- [ ] Die Änderungsverlaufseite wird geöffnet.
- [ ] Es werden keine systembezogenen Ereignisse angezeigt.
- [ ] Die Seite gibt keine globalen Systemereignisse über Filter oder direkte URL-Parameter preis.

- **Test erfolgreich:** [ ]
#### 5.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den CSV-Export des Änderungsverlaufs über Oberfläche oder Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Audit-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Serien- oder Systemereignisse außerhalb des Berechtigungsumfangs werden nicht offengelegt.

- **Test erfolgreich:** [ ]
### 5.13 Aufbewahrung und automatische Löschung

#### 5.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Verwaltungsseite für Aufbewahrungsfristen direkt und über die Navigation öffnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die administrativen Aufbewahrungseinstellungen werden nicht angezeigt und der Zugriff wird verweigert bzw. zur berechtigten Ansicht umgeleitet.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Fristwerte oder administrativen Löschoptionen offengelegt.

- **Test erfolgreich:** [ ]
#### 5.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.** Die Archivansicht ist erreichbar. Ohne Serienzuweisung werden jedoch keine archivierten Themen oder deren Aufbewahrungsdaten angezeigt.

**Prüfschritt**
 1. Mit einem globalen Nutzerkonto anmelden, dem für keine Besprechungsreihe eine Serienrolle zugewiesen ist.
 1. Das Archiv über die Navigation oder die vorgesehene direkte URL öffnen.
 1. Die Archivliste laden und prüfen, ob archivierte Themen bzw. Aufbewahrungsdaten angezeigt werden.

**Ergebnisprüfung**
- [ ] Die Archivansicht wird ohne Zugriffsfehler geöffnet.
- [ ] Ohne Serienzuweisung enthält die Liste keine archivierten Themen.
- [ ] Es werden keine Themen, Dateien oder Aufbewahrungsdaten aus nicht zugewiesenen Reihen offengelegt.

- **Test erfolgreich:** [ ]
#### 5.13.3 Retention wiederholt ausführen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den vorgesehenen Retention-Auslöser bzw. den direkten Ausführungsendpunkt mit vorbereiteten Testdaten aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Retention-Lauf wird nicht gestartet bzw. die Aktion wird abgewiesen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Termine, Protokolle, Themen oder Dateien gelöscht oder verändert.

- **Test erfolgreich:** [ ]
### 5.14 Auditor*innenbereich

#### 5.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Auditor*innenübersicht über die Navigation und zusätzlich über ihre direkte URL aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Rolle erhält keine Auditor*innenübersicht; die Anwendung verweigert den Zugriff oder leitet zur regulären Startseite weiter.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Audit- oder Organisationsprüfdaten angezeigt.

- **Test erfolgreich:** [ ]
#### 5.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: Nutzer*in ohne Serienzuweisung
**Berechtigungserwartung für Ohne Berechtigungen: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die im Testfall aufgeführten Auditor*innen-URLs einzeln direkt aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Jeder geschützte Auditor*innen-Endpunkt verweigert den Zugriff oder leitet auf eine reguläre, für die Rolle zulässige Seite um.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Audit-, Benutzer- oder Organisationsdaten offengelegt.

- **Test erfolgreich:** [ ]
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

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Das Dashboard über die Hauptnavigation öffnen und vollständig laden lassen. Die angezeigten Kacheln, Kennzahlen und Verknüpfungen prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

- **Test erfolgreich:** [ ]

#### 6.1.2 Navigation und Darstellungsvarianten – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Hauptnavigation auf Desktop und mobiler Ansicht öffnen. Menüpunkte, Untermenüs und Darstellungsvarianten durchgehen; nicht angebotene Funktionen nicht über fremde Konten simulieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Nach dem Neuladen ist weiterhin die zuvor ausgewählte Darstellungsvariante aktiv.

- **Test erfolgreich:** [ ]

---

### 6.2 Persönliches Konto und eigene Aufgaben

#### 6.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die persönlichen Kontoeinstellungen öffnen, ein unkritisches Testfeld ändern und speichern. Die Seite neu laden und den gespeicherten Wert kontrollieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 6.2.2 Eigene Aufgaben aufrufen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Aufgabenübersicht ist für Leser*innen erreichbar. Angezeigt werden ausschließlich eigene Aufgaben aus ausdrücklich zugänglichen Reihen; bei fehlenden Aufgaben erscheint ein Leerzustand.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden.
 1. Die eigene Aufgabenübersicht über die Navigation bzw. den vorgesehenen Aufruf öffnen.
 1. Die Ansicht bzw. Ergebnisliste laden und den angezeigten Datenumfang prüfen.

**Ergebnisprüfung**
- [ ] Die Aufgabenübersicht wird ohne Zugriffsfehler geöffnet.
- [ ] Die Aufgabenübersicht ist für Leser*innen erreichbar. Angezeigt werden ausschließlich eigene Aufgaben aus ausdrücklich zugänglichen Reihen; bei fehlenden Aufgaben erscheint ein Leerzustand.
- [ ] Es werden keine Termine, Themen oder Aufgaben aus nicht zugewiesenen Reihen offengelegt.

- **Test erfolgreich:** [ ]
### 6.3 Besprechungsreihen verwalten

#### 6.3.1 Zugriff auf die Serienverwaltung prüfen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Seite der Serienverwaltung darf für Leser*innen nicht erreichbar sein, weil eine Leserzuweisung keine Moderatorrechte für die Reihenverwaltung umfasst.

**Prüfschritt**

 1. Mit einem Testkonto anmelden, das der geprüften Besprechungsreihe ausdrücklich als Leser*in zugewiesen ist.
 1. Prüfen, ob die Serienverwaltung in der Navigation angeboten wird.
 1. Die Seite der Serienverwaltung zusätzlich über ihre direkte URL aufrufen.
 1. Feststellen, dass der Zugriff verweigert wird und keine Serienverwaltungsseite mit Reihen oder Verwaltungsfunktionen angezeigt wird.

**Ergebnisprüfung**

- [ ] Die Serienverwaltung ist für diese Rolle weder über die Navigation noch über die direkte URL erreichbar.
- [ ] Es werden keine Reihen oder Verwaltungsfunktionen offengelegt.



- **Test erfolgreich:** [ ]

---

### 6.4 Termine und Besprechungsübersicht

#### 6.4.1 Terminübersicht aufrufen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Terminübersicht über die Navigation öffnen, die für das Testkonto verfügbaren Reihen bzw. Termine laden und den angezeigten Umfang prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Termine der berechtigten Reihen werden angezeigt.
- [ ] Datum und Reihenbezeichnung stimmen.
- [ ] Vergangene Termine sind als vergangen bzw. abgeschlossen und zukünftige Termine als anstehend erkennbar; beide gehören zur zugewiesenen Besprechungsreihe.
- [ ] Termine nicht zugewiesener Reihen werden nicht angezeigt.

- **Test erfolgreich:** [ ]

#### 6.4.2 Einzelnen Termin verschieben – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Testtermin der nicht zugewiesenen bzw. nicht berechtigten Reihe direkt aufrufen und versuchen, Datum oder Uhrzeit zu ändern und zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Terminänderung wird verweigert oder die Aktion ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Datum, Uhrzeit und Serienzuordnung des Termins bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 6.4.3 Einzelnen Termin löschen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten entbehrlichen Testtermin der betroffenen Reihe aufrufen und die Löschaktion über Oberfläche bzw. POST-Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Termin wird nicht gelöscht.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Termin, Tagesordnungspunkte, Teilnehmerzuordnungen und Folgetermine bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 6.4.4 Teilnehmerliste bearbeiten – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Teilnehmerliste eines bekannten Testtermins öffnen und versuchen, ein separates Testkonto hinzuzufügen oder zu entfernen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Teilnehmeränderung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Teilnehmerliste und alle bestehenden Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 6.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der exakt beschriebenen Serienrolle anmelden.
 1. Einen abgeschlossenen Testtermin der zugewiesenen Reihe öffnen und den Protokoll-/Tagesordnungsstand dokumentieren.
 1. Eine schreibende Aktion am abgeschlossenen Termin versuchen; falls die Oberfläche keine Aktion anbietet, den vorgesehenen Direktaufruf mit unveränderten Testdaten prüfen und anschließend den Termin neu laden.

**Ergebnisprüfung**
- [ ] Der Termin kann mit dem für diesen Testfall verwendeten Konto weiterhin geöffnet werden.
- [ ] Schreibende Aktionen auf dem abgeschlossenen Termin werden für Leser*innen abgewiesen oder sind nicht verfügbar.
- [ ] Der gespeicherte Protokollstand und die Tagesordnung bleiben unverändert.

- **Test erfolgreich:** [ ]
### 6.5 Themen anlegen und bearbeiten

#### 6.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Im Dashboard die Funktion zum Anlegen eines Themas aufrufen und ein eindeutig markiertes Testthema mit Pflichtangaben zu speichern versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Testthema wird nicht angelegt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht weder ein neuer Themendatensatz noch eine neue Zuordnung zu einem Termin.

- **Test erfolgreich:** [ ]
#### 6.5.2 Thema über einen Termin anlegen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Testtermin aufrufen und dort versuchen, ein neues Testthema mit eindeutiger Bezeichnung anzulegen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Testthema wird nicht angelegt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht weder ein neuer Themendatensatz noch ein zusätzlicher Tagesordnungseintrag.

- **Test erfolgreich:** [ ]
#### 6.5.3 Thema bearbeiten – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen, ein unkritisches Feld ändern und die Änderung speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Themenänderung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Titel, Beschreibung, Status, Zuständigkeit und Reihenbezug bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 6.5.4 Themenstatus ändern – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und versuchen, dessen Status zu ändern und zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Statusänderung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der ursprüngliche Themenstatus und die zugehörigen Zeitstempel bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 6.5.5 Thema archivieren und wieder öffnen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema aufrufen und die Archivierungs- sowie – falls bereits archiviert – die Wiederöffnen-Aktion versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Archivieren bzw. Wiederöffnen wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Status, Archivierungsdatum und bisherige Themeninhalte bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 6.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema auswählen und versuchen, es in eine andere Testreihe zu übertragen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Übertragung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Thema bleibt der ursprünglichen Reihe zugeordnet; in der Zielreihe entsteht keine Kopie.

- **Test erfolgreich:** [ ]
#### 6.5.7 Themenvorschläge verwenden – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den Themenvorschlags-Endpunkt bzw. die Vorschlagsfunktion in einem Testformular aufrufen und versuchen, einen Vorschlag zu übernehmen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Themenvorschläge aus nicht zugänglichen Reihen ausgegeben.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird kein Thema angelegt oder verändert.

- **Test erfolgreich:** [ ]
### 6.6 Tagesordnungspunkte und Wiedervorlagen

#### 6.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Tagesordnungspunkt eines Testtermins öffnen, ein Feld ändern und speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Bearbeitung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Text, Zuständigkeit, Status und Zuordnung des Tagesordnungspunkts bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 6.6.2 Tagesordnungspunkte sortieren – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen Testtermin mit mindestens zwei Tagesordnungspunkten öffnen und versuchen, deren Reihenfolge zu ändern und zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Sortierung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die ursprüngliche Reihenfolge und Positionswerte bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 6.6.3 Tagesordnungspunkt entfernen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Tagesordnungspunkt auswählen und versuchen, ihn über die Oberfläche oder den vorgesehenen POST-Aufruf zu entfernen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Tagesordnungspunkt wird nicht entfernt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Tagesordnungseintrag, Themenbezug und historische Inhalte bleiben erhalten.

- **Test erfolgreich:** [ ]
#### 6.6.4 Wiedervorlage anlegen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und versuchen, eine Wiedervorlage für einen Folgetermin anzulegen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Wiedervorlage wird nicht angelegt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht keine neue Termin- oder Tagesordnungspunktzuordnung.

- **Test erfolgreich:** [ ]
#### 6.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine vorbereitete Wiedervorlage öffnen und versuchen, sie auf den nächsten Termin fortzuführen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Fortführung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entstehen keine neuen Wiedervorlagen, Verknüpfungen oder doppelten Tagesordnungseinträge.

- **Test erfolgreich:** [ ]
#### 6.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen zugänglichen Termin mit bereits abgeschlossenen bzw. historischen Tagesordnungseinträgen öffnen und den historischen Eintrag gezielt auswählen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Datum, Reihenbezeichnung, Text, Status und Verantwortlichkeit stimmen mit den im historischen Tagesordnungseintrag gespeicherten Werten überein.
- [ ] Historische Einträge lassen sich nicht unberechtigt verändern.
- [ ] Zugriff ist auf berechtigte Konten begrenzt.

- **Test erfolgreich:** [ ]

---

### 6.7 Kommentare, Anlagen und Links

#### 6.7.1 Kommentar hinzufügen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und einen eindeutig als Test erkennbaren Kommentar absenden.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Kommentar wird nicht gespeichert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht kein neuer Kommentar und bestehende Kommentare bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 6.7.2 Datei als Themenanlage hochladen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und eine harmlose Testdatei als Anlage hochzuladen versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Upload wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht kein neuer Anlagendatensatz und keine Datei wird dauerhaft gespeichert.

- **Test erfolgreich:** [ ]
#### 6.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und versuchen, einen Test-Netzwerkpfad oder eine unkritische Test-URL als Anlage zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Hinterlegen des Pfads bzw. Links wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird kein neuer Anlagen-, Pfad- oder Linkeintrag gespeichert.

- **Test erfolgreich:** [ ]
#### 6.7.4 Anlage herunterladen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema mit einer bekannten Testdatei öffnen, die Anlage herunterladen und den Dateiinhalt mit der hochgeladenen Testdatei vergleichen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Berechtigte Konten können die zugehörige Datei herunterladen.
- [ ] Dateiinhalt und Dateiname entsprechen der hochgeladenen Datei.
- [ ] Nicht berechtigte Konten erhalten keinen Dateizugriff.

- **Test erfolgreich:** [ ]

#### 6.7.5 Anlage löschen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine bekannte Testanlage auswählen und versuchen, sie zu löschen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Löschung der Anlage wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Anlagendatensatz und gespeicherte Datei bleiben unverändert erhalten.

- **Test erfolgreich:** [ ]
#### 6.7.6 Upload-Grenzen prüfen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Bei einem bekannten Testthema den Upload einer harmlosen Testdatei über die vorgesehene Upload-Funktion versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Upload wird wegen fehlender Berechtigung verweigert; eine Größenprüfung darf nicht zu einem erfolgreichen Upload führen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Datei gespeichert und es entsteht kein Anlagendatensatz.

- **Test erfolgreich:** [ ]
### 6.8 Besprechung abschließen und Protokoll

#### 6.8.1 Besprechung abschließen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten noch offenen Testtermin öffnen und versuchen, ihn über die Abschlussfunktion abzuschließen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Abschlussvorgang wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Termin bleibt offen; Abschlusszeitpunkt und Protokoll-Snapshot werden nicht angelegt.

- **Test erfolgreich:** [ ]
#### 6.8.2 Protokoll anzeigen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen zugänglichen abgeschlossenen Testtermin öffnen und das gespeicherte Protokoll aufrufen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Protokoll zeigt den beim Abschluss gesicherten Stand.
- [ ] Historische Werte werden nicht durch spätere Änderungen am Thema überschrieben.
- [ ] Protokoll ist für berechtigte Leser*innen sichtbar.

- **Test erfolgreich:** [ ]

#### 6.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Das Protokoll eines zugänglichen Testtermins öffnen, die Druckansicht aufrufen und zusätzlich den PDF-Export auslösen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Druckansicht enthält den richtigen Termin und Protokollstand.
- [ ] PDF lässt sich öffnen.
- [ ] PDF enthält die vorgesehenen Protokolldaten.
- [ ] Im PDF erscheinen die aktuell gespeicherte Organisationsbezeichnung und das aktuell gespeicherte Organisationslogo.
- [ ] Unberechtigte Konten können den Export nicht abrufen.

- **Test erfolgreich:** [ ]

#### 6.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten abgeschlossenen Testtermin aufrufen und die Wiederöffnen-Aktion über Oberfläche bzw. POST-Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Wiederöffnung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Abschlussstatus und gespeicherter Protokoll-Snapshot bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 6.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema mit Protokolleinträgen öffnen und den Themenprotokoll-PDF-Export auslösen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] PDF enthält die dem Thema zugeordneten historischen Einträge.
- [ ] PDF-Datum und Reihenbezeichnung stimmen mit dem ausgewählten Termin überein; Texte und Statuswerte entsprechen dem gespeicherten Themen- und Protokollstand.
- [ ] Der Export ist auf berechtigte Konten begrenzt.

- **Test erfolgreich:** [ ]

---

### 6.9 Offene Themen und Archiv

#### 6.9.1 Offene Themen aufrufen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Übersicht der offenen Themen öffnen und die angezeigten Themen anhand der zugewiesenen Reihen prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Nur fachlich zugängliche Themen werden angezeigt.
- [ ] Angezeigter Status und Zuständigkeit entsprechen den gespeicherten Themenwerten; die angezeigte Reihe entspricht der tatsächlichen Zuordnung des Themas.
- [ ] Auswahl und Filter führen zu passenden Ergebnissen.

- **Test erfolgreich:** [ ]

#### 6.9.2 Archiv aufrufen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Das Archiv über die Navigation öffnen, die Ergebnisliste laden und den angezeigten Datenumfang prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Archivierte Themen sind im Archiv auffindbar.
- [ ] Es werden ausschließlich historische Inhalte der ausdrücklich zugewiesenen Reihe angezeigt; Inhalte nicht zugewiesener Reihen bleiben verborgen.
- [ ] Nicht archivierte Themen werden nicht fälschlich als archiviert dargestellt.

- **Test erfolgreich:** [ ]

#### 6.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die direkte URL eines vorbereiteten historischen Eintrags aus einer gelöschten bzw. nicht zugänglichen Reihe aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Historische Inhalte werden nicht angezeigt oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Themen-, Protokoll- oder Anlagendaten offengelegt.

- **Test erfolgreich:** [ ]
### 6.10 Berechtigungsanträge

#### 6.10.1 Höhere Serienberechtigung beantragen – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Leser*innen dürfen für eine ihnen zugewiesene Reihe eine höhere Serienrolle beantragen; die höhere Berechtigung entsteht erst nach Genehmigung.

**Prüfschritt**
 1. Mit einem Leser-Konto anmelden, das der geprüften Testreihe ausdrücklich als Leser*in zugewiesen ist.
 1. Die persönliche Benutzerübersicht öffnen und bei dieser Reihe eine höhere Rolle (Teilnehmer*in oder Moderator*in) auswählen.
 1. Den Antrag absenden und anschließend die Benutzerübersicht neu laden.

**Ergebnisprüfung**
- [ ] Der Antrag wird der richtigen Person und Testreihe zugeordnet und als offen angezeigt.
- [ ] Die bestehende Leserzuweisung bleibt bis zur Entscheidung unverändert.
- [ ] Durch den Antrag allein entstehen keine Schreib- oder Moderatorrechte.
- [ ] Andere Reihen und Berechtigungen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 6.10.2 Berechtigungsantrag entscheiden – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen offenen Test-Berechtigungsantrag öffnen und versuchen, ihn zu genehmigen oder abzulehnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Entscheidung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Antrag bleibt offen; Serienrollen und Zugriffsrechte des antragstellenden Kontos bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 6.10.3 Bereits vorhandenen Antrag erneut bearbeiten – Prüfrolle: Leser*in (Serienrolle)

**Berechtigungserwartung für Leser: Zugriff erlaubt.** Die persönliche Benutzerübersicht ist erreichbar. Ein bereits offener Antrag darf jedoch nicht doppelt angelegt werden.

**Prüfschritt**
 1. Mit einem Leser-Konto anmelden, das der Testreihe ausdrücklich als Leser*in zugewiesen ist.
 1. Für dieses Konto und dieselbe Testreihe einen offenen Antrag vorbereiten.
 1. Die persönliche Benutzerübersicht öffnen; da der offene Antrag das Formular ausblendet, den entsprechenden POST-Aufruf mit denselben Daten direkt wiederholen.
 1. Anschließend die Antragsliste und die Serienzuweisung neu laden.

**Ergebnisprüfung**
- [ ] Die Benutzerübersicht und die Antragsfunktion sind erreichbar.
- [ ] Der bereits offene Antrag wird als solcher erkannt; es entsteht kein zweiter offener Antrag.
- [ ] Die bestehende Leserzuweisung bleibt unverändert.
- [ ] Andere Anträge und Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]
### 6.11 Benutzer- und Themenimport/-export

#### 6.11.1 Benutzer als CSV exportieren – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Benutzerverwaltung bzw. den Benutzerexport öffnen und den CSV-Export über die Oberfläche oder den vorgesehenen Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Benutzer-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Konten- oder Profildaten offengelegt.

- **Test erfolgreich:** [ ]
#### 6.11.2 Benutzer per CSV importieren – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine CSV-Datei mit ausschließlich separaten Testkonten vorbereiten und den Import über die Oberfläche bzw. den vorgesehenen Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Import wird abgewiesen; es werden keine Testkonten angelegt oder bestehende Konten verändert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entstehen keine Teilimporte oder unvollständigen Benutzerzuordnungen.

- **Test erfolgreich:** [ ]
#### 6.11.3 Themen als CSV exportieren – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den Themen-CSV-Export für eine bekannte Reihe über Oberfläche oder Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Themen-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Themeninhalte und Zuständigkeiten nicht zugänglicher Reihen werden nicht offengelegt.

- **Test erfolgreich:** [ ]
#### 6.11.4 Themen per CSV importieren – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine vorbereitete CSV-Datei mit eindeutig markierten Testthemen auswählen und den Import versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Import wird verweigert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Themen angelegt und keine bestehenden Themen, Tagesordnungspunkte oder Reihenbezüge verändert.

- **Test erfolgreich:** [ ]
### 6.12 Änderungsverlauf und Audit

#### 6.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff auf die Änderungsverlaufseite erlaubt; Serienereignisse eingeschränkt.** Die Änderungsverlaufseite ist erreichbar. Leser*innen erhalten jedoch keinen Zugriff auf serienbezogene Änderungsereignisse, da hierfür eine Moderatorzuweisung erforderlich ist.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen Rolle bzw. Serienzuweisung anmelden.
 1. Die Seite **Änderungsverlauf** über die Navigation oder direkt öffnen.
 1. Den Bereich für Serienereignisse aufrufen bzw. den passenden Filter verwenden.
 1. Prüfen, welche Ereignisse tatsächlich angezeigt werden; bei Bedarf die Seite neu laden und einen direkten Filteraufruf testen.

**Ergebnisprüfung**
- [ ] Die Änderungsverlaufseite wird geöffnet.
- [ ] Es werden keine serienbezogenen Änderungsereignisse angezeigt.
- [ ] Ereignisse anderer Reihen werden nicht offengelegt.

- **Test erfolgreich:** [ ]
#### 6.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff auf die Änderungsverlaufseite erlaubt; Systemereignisse eingeschränkt.** Die Änderungsverlaufseite ist erreichbar; systembezogene Ereignisse sind für Leser*innen nicht sichtbar.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen Rolle bzw. Serienzuweisung anmelden.
 1. Die Seite **Änderungsverlauf** über die Navigation oder direkt öffnen.
 1. Den Bereich für Systemereignisse aufrufen bzw. den passenden Filter verwenden.
 1. Prüfen, welche Ereignisse tatsächlich angezeigt werden; bei Bedarf die Seite neu laden und einen direkten Filteraufruf testen.

**Ergebnisprüfung**
- [ ] Die Änderungsverlaufseite wird geöffnet.
- [ ] Es werden keine systembezogenen Ereignisse angezeigt.
- [ ] Die Seite gibt keine globalen Systemereignisse über Filter oder direkte URL-Parameter preis.

- **Test erfolgreich:** [ ]
#### 6.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den CSV-Export des Änderungsverlaufs über Oberfläche oder Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Audit-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Serien- oder Systemereignisse außerhalb des Berechtigungsumfangs werden nicht offengelegt.

- **Test erfolgreich:** [ ]
### 6.13 Aufbewahrung und automatische Löschung

#### 6.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Verwaltungsseite für Aufbewahrungsfristen direkt und über die Navigation öffnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die administrativen Aufbewahrungseinstellungen werden nicht angezeigt und der Zugriff wird verweigert bzw. zur berechtigten Ansicht umgeleitet.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Fristwerte oder administrativen Löschoptionen offengelegt.

- **Test erfolgreich:** [ ]
#### 6.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff erlaubt.** Leser*innen dürfen archivierte Themen ihrer zugewiesenen Reihe und die dort angezeigte Aufbewahrungsfrist bzw. das Löschdatum einsehen; administrative Aufbewahrungseinstellungen bleiben ihnen verborgen.

**Prüfschritt**
 1. Mit einem Testkonto anmelden, das der geprüften Reihe ausdrücklich als Leser*in zugewiesen ist.
 1. Das Archiv über die Navigation öffnen und ein vorbereitetes archiviertes Thema aus der zugewiesenen Reihe auswählen.
 1. Die angezeigte Aufbewahrungsfrist und das vorgesehene Löschdatum ablesen; anschließend prüfen, dass keine administrative Änderungsfunktion angeboten wird.

**Ergebnisprüfung**
- [ ] Die Archivansicht wird ohne Zugriffsfehler geöffnet.
- [ ] Archivierte Themen der zugewiesenen Reihe und deren Aufbewahrungsdaten werden angezeigt.
- [ ] Themen und Aufbewahrungsdaten fremder Reihen werden nicht offengelegt.
- [ ] Administrative Aufbewahrungsfristen können mit der Leserrolle nicht geändert werden.

- **Test erfolgreich:** [ ]
#### 6.13.3 Retention wiederholt ausführen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den vorgesehenen Retention-Auslöser bzw. den direkten Ausführungsendpunkt mit vorbereiteten Testdaten aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Retention-Lauf wird nicht gestartet bzw. die Aktion wird abgewiesen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Termine, Protokolle, Themen oder Dateien gelöscht oder verändert.

- **Test erfolgreich:** [ ]
### 6.14 Auditor*innenbereich

#### 6.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Auditor*innenübersicht über die Navigation und zusätzlich über ihre direkte URL aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Rolle erhält keine Auditor*innenübersicht; die Anwendung verweigert den Zugriff oder leitet zur regulären Startseite weiter.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Audit- oder Organisationsprüfdaten angezeigt.

- **Test erfolgreich:** [ ]
#### 6.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: Leser*in (Serienrolle)
**Berechtigungserwartung für Leser: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die im Testfall aufgeführten Auditor*innen-URLs einzeln direkt aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Jeder geschützte Auditor*innen-Endpunkt verweigert den Zugriff oder leitet auf eine reguläre, für die Rolle zulässige Seite um.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Audit-, Benutzer- oder Organisationsdaten offengelegt.

- **Test erfolgreich:** [ ]
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

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Das Dashboard über die Hauptnavigation öffnen und vollständig laden lassen. Die angezeigten Kacheln, Kennzahlen und Verknüpfungen prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

- **Test erfolgreich:** [ ]

#### 7.1.2 Navigation und Darstellungsvarianten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Hauptnavigation auf Desktop und mobiler Ansicht öffnen. Menüpunkte, Untermenüs und Darstellungsvarianten durchgehen; nicht angebotene Funktionen nicht über fremde Konten simulieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Nach dem Neuladen ist weiterhin die zuvor ausgewählte Darstellungsvariante aktiv.

- **Test erfolgreich:** [ ]

---

### 7.2 Persönliches Konto und eigene Aufgaben

#### 7.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die persönlichen Kontoeinstellungen öffnen, ein unkritisches Testfeld ändern und speichern. Die Seite neu laden und den gespeicherten Wert kontrollieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 7.2.2 Eigene Aufgaben aufrufen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die persönliche Aufgabenübersicht öffnen, vorhandene eigene Aufgaben durchgehen und – falls keine vorhanden sind – den vorgesehenen Leerzustand prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Eigene offene Themen werden im vorgesehenen Abschnitt angezeigt.
- [ ] Eigene Tagesordnungspunkte werden getrennt davon angezeigt.
- [ ] Nicht zugewiesene oder nicht berechtigte Inhalte werden nicht zusätzlich eingeblendet.
- [ ] Bei fehlenden Aufgaben wird ein geeigneter Leerzustand angezeigt.

- **Test erfolgreich:** [ ]

---

### 7.3 Besprechungsreihen verwalten

#### 7.3.1 Zugriff auf die Serienverwaltung prüfen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Seite der Serienverwaltung darf für Teilnehmer*innen nicht erreichbar sein, weil eine Teilnehmerzuweisung keine Moderatorrechte für die Reihenverwaltung umfasst.

**Prüfschritt**

 1. Mit einem Testkonto anmelden, das der geprüften Besprechungsreihe ausdrücklich als Teilnehmer*in zugewiesen ist.
 1. Prüfen, ob die Serienverwaltung in der Navigation angeboten wird.
 1. Die Seite der Serienverwaltung zusätzlich über ihre direkte URL aufrufen.
 1. Feststellen, dass der Zugriff verweigert wird und keine Serienverwaltungsseite mit Reihen oder Verwaltungsfunktionen angezeigt wird.

**Ergebnisprüfung**

- [ ] Die Serienverwaltung ist für diese Rolle weder über die Navigation noch über die direkte URL erreichbar.
- [ ] Es werden keine Reihen oder Verwaltungsfunktionen offengelegt.



- **Test erfolgreich:** [ ]

---

### 7.4 Termine und Besprechungsübersicht

#### 7.4.1 Terminübersicht aufrufen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Terminübersicht über die Navigation öffnen, die für das Testkonto verfügbaren Reihen bzw. Termine laden und den angezeigten Umfang prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Termine der berechtigten Reihen werden angezeigt.
- [ ] Datum und Reihenbezeichnung stimmen.
- [ ] Vergangene Termine sind als vergangen bzw. abgeschlossen und zukünftige Termine als anstehend erkennbar; beide gehören zur zugewiesenen Besprechungsreihe.
- [ ] Termine nicht zugewiesener Reihen werden nicht angezeigt.

- **Test erfolgreich:** [ ]

#### 7.4.2 Einzelnen Termin verschieben – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Testtermin der nicht zugewiesenen bzw. nicht berechtigten Reihe direkt aufrufen und versuchen, Datum oder Uhrzeit zu ändern und zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Terminänderung wird verweigert oder die Aktion ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Datum, Uhrzeit und Serienzuordnung des Termins bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 7.4.3 Einzelnen Termin löschen – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten entbehrlichen Testtermin der betroffenen Reihe aufrufen und die Löschaktion über Oberfläche bzw. POST-Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Termin wird nicht gelöscht.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Termin, Tagesordnungspunkte, Teilnehmerzuordnungen und Folgetermine bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 7.4.4 Teilnehmerliste bearbeiten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Teilnehmerliste eines zugewiesenen Testtermins öffnen, ein separates Testkonto hinzufügen oder entfernen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die ausgewählten Konten werden in der Teilnehmerliste angezeigt.
- [ ] Abgewählte Konten werden nicht mehr angezeigt.
- [ ] Die Änderung betrifft nur den ausgewählten Termin.
- [ ] Die Serienberechtigungen der Konten bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 7.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der exakt beschriebenen Serienrolle anmelden.
 1. Einen abgeschlossenen Testtermin der zugewiesenen Reihe öffnen und den Protokoll-/Tagesordnungsstand dokumentieren.
 1. Eine schreibende Aktion am abgeschlossenen Termin versuchen; falls die Oberfläche keine Aktion anbietet, den vorgesehenen Direktaufruf mit unveränderten Testdaten prüfen und anschließend den Termin neu laden.

**Ergebnisprüfung**
- [ ] Der Termin kann mit dem für diesen Testfall verwendeten Konto weiterhin geöffnet werden.
- [ ] Schreibende Aktionen auf dem abgeschlossenen Termin werden für Teilnehmer*innen abgewiesen oder sind nicht verfügbar.
- [ ] Der gespeicherte Protokollstand und die Tagesordnung bleiben unverändert.

- **Test erfolgreich:** [ ]
### 7.5 Themen anlegen und bearbeiten

#### 7.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Im Dashboard die Funktion zum Anlegen eines Themas öffnen, ein eindeutig erkennbares Testthema mit Pflichtangaben erfassen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Das Thema erscheint in der Themenübersicht.
- [ ] Titel und Hauptzuständigkeit entsprechen den Eingaben.
- [ ] Das Thema ist der ausgewählten Besprechungsreihe zugeordnet.
- [ ] Für den ausgewählten Termin ist der zugehörige Tagesordnungspunkt vorhanden.
- [ ] Das Thema ist nicht versehentlich in einer anderen Reihe angelegt worden.

- **Test erfolgreich:** [ ]

#### 7.5.2 Thema über einen Termin anlegen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen zugänglichen Testtermin öffnen, dort ein neues Testthema mit eindeutiger Bezeichnung und Pflichtangaben anlegen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Das neue Thema ist angelegt.
- [ ] Der Tagesordnungspunkt ist dem geöffneten Termin zugeordnet.
- [ ] Die Hauptzuständigkeit entspricht dem ausgewählten Konto; die abweichende Zuständigkeit wird separat mit dem im Prüfschritt ausgewählten Konto angezeigt.
- [ ] Das Thema ist in der Themenübersicht auffindbar.

- **Test erfolgreich:** [ ]

#### 7.5.3 Thema bearbeiten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema öffnen, ein unkritisches Feld ändern, speichern und die Detailansicht erneut laden.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Titel, Status und Hauptzuständigkeit entsprechen den gespeicherten Werten.
- [ ] Änderungen bleiben nach dem Neuladen erhalten.
- [ ] Jeder Tagesordnungspunkt bleibt dem bearbeiteten Thema zugeordnet; vorhandene historische Protokoll-Snapshots behalten ihren zuvor gespeicherten Inhalt.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

- **Test erfolgreich:** [ ]

#### 7.5.4 Themenstatus ändern – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema öffnen, den Status über die vorgesehene Statusaktion ändern und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der neue Status wird in der Detailansicht angezeigt.
- [ ] Die Übersicht zeigt denselben Statuswert wie die Themendetailansicht.
- [ ] Der Status des Tagesordnungspunkts bleibt unverändert; geändert wird ausschließlich der Status des übergeordneten Themas.

- **Test erfolgreich:** [ ]

#### 7.5.5 Thema archivieren und wieder öffnen – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema aufrufen und die Archivierungs- sowie – falls bereits archiviert – die Wiederöffnen-Aktion versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Archivieren bzw. Wiederöffnen wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Status, Archivierungsdatum und bisherige Themeninhalte bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 7.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein entbehrliches Testthema aus Testreihe A auswählen, die ausdrücklich als Ziel vorgesehene Testreihe B wählen und den Übertragungsvorgang bestätigen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Das Thema ist der vorgesehenen Zielreihe zugeordnet.
- [ ] Der vorgesehene Zieltermin enthält den Tagesordnungspunkt.
- [ ] Übertragungsnotiz und Übertragungsverlauf sind nachvollziehbar.
- [ ] Die Serienzuweisungen der beteiligten Konten in Quell- und Zielreihe bleiben unverändert; die Themenübertragung erzeugt keine zusätzliche Serienberechtigung.
- [ ] Andere Themen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 7.5.7 Themenvorschläge verwenden – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Themenvorschläge im vorgesehenen Eingabebereich öffnen, einen passenden Vorschlag auswählen und dessen Übernahme auslösen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Titel und übernommene Vorschlagsdaten entsprechen dem ausgewählten Vorschlag.
- [ ] Das Thema bzw. der Tagesordnungspunkt wird mit den eingegebenen Daten angelegt.
- [ ] Es wird kein zusätzlicher oder doppelter Datensatz angelegt.

- **Test erfolgreich:** [ ]

---

### 7.6 Tagesordnungspunkte und Wiedervorlagen

#### 7.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen zugänglichen Testtermin mit Tagesordnung öffnen, einen vorhandenen Test-Tagesordnungspunkt ändern und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der gespeicherte Text wird beim erneuten Öffnen des Tagesordnungspunkts wortgleich angezeigt.
- [ ] Der Status des Tagesordnungspunkts entspricht der Auswahl.
- [ ] Die abweichende Zuständigkeit entspricht dem im Prüfschritt ausgewählten Konto und bleibt von der Hauptzuständigkeit getrennt.
- [ ] Der allgemeine Themenstatus bleibt davon getrennt.

- **Test erfolgreich:** [ ]

#### 7.6.2 Tagesordnungspunkte sortieren – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Bei einem Testtermin mindestens zwei Tagesordnungspunkte in eine andere Reihenfolge bringen, die Sortierung speichern und die Seite neu laden.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Reihenfolge entspricht der zuletzt vorgenommenen Sortierung.
- [ ] Jeder Tagesordnungspunkt ist weiterhin dem richtigen Thema zugeordnet.
- [ ] Es fehlen keine Punkte und es sind keine Duplikate entstanden.

- **Test erfolgreich:** [ ]

#### 7.6.3 Tagesordnungspunkt entfernen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen entbehrlichen Test-Tagesordnungspunkt auswählen, die Entfernen-Funktion auslösen und die Änderung bestätigen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Punkt ist aus dem ausgewählten Termin entfernt.
- [ ] Das zugrunde liegende Thema bleibt in der Themenübersicht erhalten; entfernt wird ausschließlich der ausgewählte Tagesordnungspunkt.
- [ ] Andere Tagesordnungspunkte bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 7.6.4 Wiedervorlage anlegen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Bei einem Testthema eine Wiedervorlage mit einem konkreten Folgetermin setzen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Tagesordnungspunkt erscheint im vorgesehenen Zieltermin.
- [ ] Die Verbindung zum vorherigen Tagesordnungspunkt ist nachvollziehbar.
- [ ] Status und Zuständigkeit entsprechen den vorgesehenen Übernahmeregeln.
- [ ] Es ist keine doppelte Wiedervorlage entstanden.

- **Test erfolgreich:** [ ]

#### 7.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Eine Wiedervorlage für ein Testthema anlegen, den ersten Folgetermin bearbeiten bzw. abschließen und den nächsten vorgesehenen Termin auf die fortgeführte Wiedervorlage prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Wiedervorlagekette ist chronologisch nachvollziehbar.
- [ ] Jeder Punkt ist dem richtigen Termin zugeordnet.
- [ ] Frühere Protokollstände bleiben unverändert.
- [ ] Es entstehen keine doppelten oder voneinander getrennten Ketten.

- **Test erfolgreich:** [ ]

#### 7.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen zugänglichen Termin mit bereits abgeschlossenen bzw. historischen Tagesordnungseinträgen öffnen und den historischen Eintrag gezielt auswählen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Datum, Reihenbezeichnung, Text, Status und Verantwortlichkeit stimmen mit den im historischen Tagesordnungseintrag gespeicherten Werten überein.
- [ ] Historische Einträge lassen sich nicht unberechtigt verändern.
- [ ] Zugriff ist auf berechtigte Konten begrenzt.

- **Test erfolgreich:** [ ]

---

### 7.7 Kommentare, Anlagen und Links

#### 7.7.1 Kommentar hinzufügen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema öffnen, einen eindeutig als Test erkennbaren Kommentar hinzufügen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Kommentar wird beim richtigen Thema angezeigt.
- [ ] Als Autor wird das angemeldete Testkonto angezeigt; der Erstellungszeitpunkt liegt im Zeitraum der gerade ausgeführten Aktion.
- [ ] Der Kommentar bleibt nach dem Neuladen erhalten.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

- **Test erfolgreich:** [ ]

#### 7.7.2 Datei als Themenanlage hochladen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema öffnen, eine harmlose Testdatei als Anlage auswählen und hochladen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Anlage wird beim richtigen Thema angezeigt.
- [ ] Die angezeigte Bezeichnung entspricht der eingegebenen Bezeichnung; die Datei ist dem ausgewählten Thema zugeordnet und lässt sich öffnen.
- [ ] Die Datei lässt sich mit einem berechtigten Konto herunterladen.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

- **Test erfolgreich:** [ ]

#### 7.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Bei einem zugänglichen Testthema einen dafür vorgesehenen Test-Netzwerkpfad oder eine unkritische Test-URL hinterlegen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der gespeicherte Pfad bzw. die URL entspricht exakt der eingegebenen Zeichenfolge.
- [ ] Unterstützte Pfade werden als anklickbarer Link dargestellt und öffnen das hinterlegte Ziel.
- [ ] Nicht unterstützte oder ungültige Werte werden nicht als unsichere Links ausgegeben.
- [ ] Die Anwendung behauptet nicht, die Erreichbarkeit einer externen Freigabe zu garantieren.

- **Test erfolgreich:** [ ]

#### 7.7.4 Anlage herunterladen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema mit einer bekannten Testdatei öffnen, die Anlage herunterladen und den Dateiinhalt mit der hochgeladenen Testdatei vergleichen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Berechtigte Konten können die zugehörige Datei herunterladen.
- [ ] Dateiinhalt und Dateiname entsprechen der hochgeladenen Datei.
- [ ] Nicht berechtigte Konten erhalten keinen Dateizugriff.

- **Test erfolgreich:** [ ]

#### 7.7.5 Anlage löschen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema mit einer entbehrlichen Testanlage öffnen, die Anlage löschen und die Rückfrage bestätigen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Anlage wird nicht mehr in der Themenansicht angezeigt.
- [ ] Der direkte Download der entfernten Anlage ist nicht mehr möglich.
- [ ] Andere Anlagen und Themen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 7.7.6 Upload-Grenzen prüfen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Für ein zugängliches Testthema eine Testdatei unterhalb und eine oberhalb der konfigurierten Upload-Grenze verwenden und beide Uploadversuche getrennt ausführen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Zulässige Dateien innerhalb des Limits werden angenommen.
- [ ] Zu große Dateien werden abgewiesen.
- [ ] Nicht erlaubte Dateiendungen werden abgewiesen.
- [ ] Abgewiesene Uploads erzeugen keine ungewollten Anlagen-Datensätze.

- **Test erfolgreich:** [ ]

---

### 7.8 Besprechung abschließen und Protokoll

#### 7.8.1 Besprechung abschließen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen dafür vorgesehenen Testtermin öffnen, die Abschlussfunktion auslösen und die Bestätigung durchführen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Termin ist als abgeschlossen gekennzeichnet.
- [ ] Ein Protokoll-Snapshot wurde erstellt.
- [ ] Teilnehmerliste und Tagesordnungstexte sind gegen weitere Bearbeitung gesperrt.
- [ ] Der Abschluss wird im Änderungsverlauf dokumentiert.

- **Test erfolgreich:** [ ]

#### 7.8.2 Protokoll anzeigen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen zugänglichen abgeschlossenen Testtermin öffnen und das gespeicherte Protokoll aufrufen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Protokoll zeigt den beim Abschluss gesicherten Stand.
- [ ] Historische Werte werden nicht durch spätere Änderungen am Thema überschrieben.
- [ ] Protokoll ist für berechtigte Leser*innen sichtbar.

- **Test erfolgreich:** [ ]

#### 7.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Das Protokoll eines zugänglichen Testtermins öffnen, die Druckansicht aufrufen und zusätzlich den PDF-Export auslösen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Druckansicht enthält den richtigen Termin und Protokollstand.
- [ ] PDF lässt sich öffnen.
- [ ] PDF enthält die vorgesehenen Protokolldaten.
- [ ] Im PDF erscheinen die aktuell gespeicherte Organisationsbezeichnung und das aktuell gespeicherte Organisationslogo.
- [ ] Unberechtigte Konten können den Export nicht abrufen.

- **Test erfolgreich:** [ ]

#### 7.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten abgeschlossenen Testtermin aufrufen und die Wiederöffnen-Aktion über Oberfläche bzw. POST-Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Wiederöffnung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Abschlussstatus und gespeicherter Protokoll-Snapshot bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 7.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema mit Protokolleinträgen öffnen und den Themenprotokoll-PDF-Export auslösen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] PDF enthält die dem Thema zugeordneten historischen Einträge.
- [ ] PDF-Datum und Reihenbezeichnung stimmen mit dem ausgewählten Termin überein; Texte und Statuswerte entsprechen dem gespeicherten Themen- und Protokollstand.
- [ ] Der Export ist auf berechtigte Konten begrenzt.

- **Test erfolgreich:** [ ]

---

### 7.9 Offene Themen und Archiv

#### 7.9.1 Offene Themen aufrufen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Übersicht der offenen Themen öffnen und die angezeigten Themen anhand der zugewiesenen Reihen prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Nur fachlich zugängliche Themen werden angezeigt.
- [ ] Angezeigter Status und Zuständigkeit entsprechen den gespeicherten Themenwerten; die angezeigte Reihe entspricht der tatsächlichen Zuordnung des Themas.
- [ ] Auswahl und Filter führen zu passenden Ergebnissen.

- **Test erfolgreich:** [ ]

#### 7.9.2 Archiv aufrufen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Das Archiv über die Navigation öffnen, die Ergebnisliste laden und den angezeigten Datenumfang prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Archivierte Themen sind im Archiv auffindbar.
- [ ] Es werden ausschließlich historische Inhalte der ausdrücklich zugewiesenen Reihe angezeigt; Inhalte nicht zugewiesener Reihen bleiben verborgen.
- [ ] Nicht archivierte Themen werden nicht fälschlich als archiviert dargestellt.

- **Test erfolgreich:** [ ]

#### 7.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die direkte URL eines vorbereiteten historischen Eintrags aus einer gelöschten bzw. nicht zugänglichen Reihe aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Historische Inhalte werden nicht angezeigt oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Themen-, Protokoll- oder Anlagendaten offengelegt.

- **Test erfolgreich:** [ ]
### 7.10 Berechtigungsanträge

#### 7.10.1 Höhere Serienberechtigung beantragen – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Teilnehmer*innen dürfen für eine ihnen zugewiesene Reihe eine höhere Serienrolle beantragen; Moderatorrechte entstehen erst nach Genehmigung.

**Prüfschritt**
 1. Mit einem Teilnehmer-Konto anmelden, das der geprüften Testreihe ausdrücklich als Teilnehmer*in zugewiesen ist.
 1. Die persönliche Benutzerübersicht öffnen und für diese Reihe Moderator*in als gewünschte Rolle auswählen.
 1. Den Antrag absenden und anschließend die Benutzerübersicht neu laden.

**Ergebnisprüfung**
- [ ] Der Antrag wird der richtigen Person und Testreihe zugeordnet und als offen angezeigt.
- [ ] Die bestehende Teilnehmerzuweisung bleibt bis zur Entscheidung unverändert.
- [ ] Durch den Antrag allein entstehen keine Moderatorrechte.
- [ ] Andere Reihen und Berechtigungen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 7.10.2 Berechtigungsantrag entscheiden – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen offenen Test-Berechtigungsantrag öffnen und versuchen, ihn zu genehmigen oder abzulehnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Entscheidung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Antrag bleibt offen; Serienrollen und Zugriffsrechte des antragstellenden Kontos bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 7.10.3 Bereits vorhandenen Antrag erneut bearbeiten – Prüfrolle: Teilnehmer*in (Serienrolle)

**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Die persönliche Benutzerübersicht ist erreichbar. Ein bereits offener Antrag darf jedoch nicht doppelt angelegt werden.

**Prüfschritt**
 1. Mit einem Teilnehmer-Konto anmelden, das der Testreihe ausdrücklich als Teilnehmer*in zugewiesen ist.
 1. Für dieses Konto und dieselbe Testreihe einen offenen Antrag vorbereiten.
 1. Die persönliche Benutzerübersicht öffnen; da der offene Antrag das Formular ausblendet, den entsprechenden POST-Aufruf mit denselben Daten direkt wiederholen.
 1. Anschließend die Antragsliste und die Serienzuweisung neu laden.

**Ergebnisprüfung**
- [ ] Die Benutzerübersicht und die Antragsfunktion sind erreichbar.
- [ ] Der bereits offene Antrag wird als solcher erkannt; es entsteht kein zweiter offener Antrag.
- [ ] Die bestehende Teilnehmerzuweisung bleibt unverändert.
- [ ] Andere Anträge und Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]
### 7.11 Benutzer- und Themenimport/-export

#### 7.11.1 Benutzer als CSV exportieren – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Benutzerverwaltung bzw. den Benutzerexport öffnen und den CSV-Export über die Oberfläche oder den vorgesehenen Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Benutzer-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Konten- oder Profildaten offengelegt.

- **Test erfolgreich:** [ ]
#### 7.11.2 Benutzer per CSV importieren – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine CSV-Datei mit ausschließlich separaten Testkonten vorbereiten und den Import über die Oberfläche bzw. den vorgesehenen Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Import wird abgewiesen; es werden keine Testkonten angelegt oder bestehende Konten verändert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entstehen keine Teilimporte oder unvollständigen Benutzerzuordnungen.

- **Test erfolgreich:** [ ]
#### 7.11.3 Themen als CSV exportieren – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den Themen-CSV-Export für eine bekannte Reihe über Oberfläche oder Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Themen-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Themeninhalte und Zuständigkeiten nicht zugänglicher Reihen werden nicht offengelegt.

- **Test erfolgreich:** [ ]
#### 7.11.4 Themen per CSV importieren – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine vorbereitete CSV-Datei mit eindeutig markierten Testthemen auswählen und den Import versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Import wird verweigert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Themen angelegt und keine bestehenden Themen, Tagesordnungspunkte oder Reihenbezüge verändert.

- **Test erfolgreich:** [ ]
### 7.12 Änderungsverlauf und Audit

#### 7.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff auf die Änderungsverlaufseite erlaubt; Serienereignisse eingeschränkt.** Die Änderungsverlaufseite ist erreichbar. Teilnehmer*innen erhalten jedoch keinen Zugriff auf serienbezogene Änderungsereignisse, da hierfür eine Moderatorzuweisung erforderlich ist.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen Rolle bzw. Serienzuweisung anmelden.
 1. Die Seite **Änderungsverlauf** über die Navigation oder direkt öffnen.
 1. Den Bereich für Serienereignisse aufrufen bzw. den passenden Filter verwenden.
 1. Prüfen, welche Ereignisse tatsächlich angezeigt werden; bei Bedarf die Seite neu laden und einen direkten Filteraufruf testen.

**Ergebnisprüfung**
- [ ] Die Änderungsverlaufseite wird geöffnet.
- [ ] Es werden keine serienbezogenen Änderungsereignisse angezeigt.
- [ ] Ereignisse anderer Reihen werden nicht offengelegt.

- **Test erfolgreich:** [ ]
#### 7.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff auf die Änderungsverlaufseite erlaubt; Systemereignisse eingeschränkt.** Die Änderungsverlaufseite ist erreichbar; systembezogene Ereignisse sind für Teilnehmer*innen nicht sichtbar.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen Rolle bzw. Serienzuweisung anmelden.
 1. Die Seite **Änderungsverlauf** über die Navigation oder direkt öffnen.
 1. Den Bereich für Systemereignisse aufrufen bzw. den passenden Filter verwenden.
 1. Prüfen, welche Ereignisse tatsächlich angezeigt werden; bei Bedarf die Seite neu laden und einen direkten Filteraufruf testen.

**Ergebnisprüfung**
- [ ] Die Änderungsverlaufseite wird geöffnet.
- [ ] Es werden keine systembezogenen Ereignisse angezeigt.
- [ ] Die Seite gibt keine globalen Systemereignisse über Filter oder direkte URL-Parameter preis.

- **Test erfolgreich:** [ ]
#### 7.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den CSV-Export des Änderungsverlaufs über Oberfläche oder Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Audit-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Serien- oder Systemereignisse außerhalb des Berechtigungsumfangs werden nicht offengelegt.

- **Test erfolgreich:** [ ]
### 7.13 Aufbewahrung und automatische Löschung

#### 7.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Verwaltungsseite für Aufbewahrungsfristen direkt und über die Navigation öffnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die administrativen Aufbewahrungseinstellungen werden nicht angezeigt und der Zugriff wird verweigert bzw. zur berechtigten Ansicht umgeleitet.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Fristwerte oder administrativen Löschoptionen offengelegt.

- **Test erfolgreich:** [ ]
#### 7.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff erlaubt.** Teilnehmer*innen dürfen archivierte Themen ihrer zugewiesenen Reihe und die dort angezeigte Aufbewahrungsfrist bzw. das Löschdatum einsehen; administrative Aufbewahrungseinstellungen bleiben ihnen verborgen.

**Prüfschritt**
 1. Mit einem Testkonto anmelden, das der geprüften Reihe ausdrücklich als Teilnehmer*in zugewiesen ist.
 1. Das Archiv über die Navigation öffnen und ein vorbereitetes archiviertes Thema aus der zugewiesenen Reihe auswählen.
 1. Die angezeigte Aufbewahrungsfrist und das vorgesehene Löschdatum ablesen; anschließend prüfen, dass keine administrative Änderungsfunktion angeboten wird.

**Ergebnisprüfung**
- [ ] Die Archivansicht wird ohne Zugriffsfehler geöffnet.
- [ ] Archivierte Themen der zugewiesenen Reihe und deren Aufbewahrungsdaten werden angezeigt.
- [ ] Themen und Aufbewahrungsdaten fremder Reihen werden nicht offengelegt.
- [ ] Administrative Aufbewahrungsfristen können mit der Teilnehmerrolle nicht geändert werden.

- **Test erfolgreich:** [ ]
#### 7.13.3 Retention wiederholt ausführen – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den vorgesehenen Retention-Auslöser bzw. den direkten Ausführungsendpunkt mit vorbereiteten Testdaten aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Retention-Lauf wird nicht gestartet bzw. die Aktion wird abgewiesen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Termine, Protokolle, Themen oder Dateien gelöscht oder verändert.

- **Test erfolgreich:** [ ]
### 7.14 Auditor*innenbereich

#### 7.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Auditor*innenübersicht über die Navigation und zusätzlich über ihre direkte URL aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Rolle erhält keine Auditor*innenübersicht; die Anwendung verweigert den Zugriff oder leitet zur regulären Startseite weiter.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Audit- oder Organisationsprüfdaten angezeigt.

- **Test erfolgreich:** [ ]
#### 7.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: Teilnehmer*in (Serienrolle)
**Berechtigungserwartung für Teilnehmer: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die im Testfall aufgeführten Auditor*innen-URLs einzeln direkt aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Jeder geschützte Auditor*innen-Endpunkt verweigert den Zugriff oder leitet auf eine reguläre, für die Rolle zulässige Seite um.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Audit-, Benutzer- oder Organisationsdaten offengelegt.

- **Test erfolgreich:** [ ]
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

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Das Dashboard über die Hauptnavigation öffnen und vollständig laden lassen. Die angezeigten Kacheln, Kennzahlen und Verknüpfungen prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

- **Test erfolgreich:** [ ]

#### 8.1.2 Navigation und Darstellungsvarianten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Hauptnavigation auf Desktop und mobiler Ansicht öffnen. Menüpunkte, Untermenüs und Darstellungsvarianten durchgehen; nicht angebotene Funktionen nicht über fremde Konten simulieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Nach dem Neuladen ist weiterhin die zuvor ausgewählte Darstellungsvariante aktiv.

- **Test erfolgreich:** [ ]

---

### 8.2 Persönliches Konto und eigene Aufgaben

#### 8.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die persönlichen Kontoeinstellungen öffnen, ein unkritisches Testfeld ändern und speichern. Die Seite neu laden und den gespeicherten Wert kontrollieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 8.2.2 Eigene Aufgaben aufrufen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die persönliche Aufgabenübersicht öffnen, vorhandene eigene Aufgaben durchgehen und – falls keine vorhanden sind – den vorgesehenen Leerzustand prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Eigene offene Themen werden im vorgesehenen Abschnitt angezeigt.
- [ ] Eigene Tagesordnungspunkte werden getrennt davon angezeigt.
- [ ] Nicht zugewiesene oder nicht berechtigte Inhalte werden nicht zusätzlich eingeblendet.
- [ ] Bei fehlenden Aufgaben wird ein geeigneter Leerzustand angezeigt.

- **Test erfolgreich:** [ ]

---

### 8.3 Besprechungsreihen verwalten

#### 8.3.1 Besprechungsreihe anlegen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Serienverwaltung öffnen und eine eindeutig benannte Testreihe mit Testbeschreibung, Startdatum, Rhythmus und Enddatum anlegen. Die vorgesehene Moderatorzuweisung setzen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die neue Besprechungsreihe erscheint in der Übersicht.
- [ ] Bezeichnung, Beschreibung und Wiederholungseinstellungen entsprechen den Eingaben.
- [ ] Jeder erzeugte Termin liegt innerhalb des festgelegten Start- und Enddatums und folgt dem gespeicherten Rhythmus und Intervall.
- [ ] Die erstellende Moderatorin bzw. der erstellende Moderator besitzt die vorgesehene Serienzuweisung.
- [ ] Serienzuweisungen außerhalb der neu angelegten Testreihe sind nach dem Speichern unverändert; insbesondere werden keine zusätzlichen Rollen in anderen Reihen angelegt.

- **Test erfolgreich:** [ ]

#### 8.3.2 Besprechungsreihe bearbeiten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Eine der Rolle zugewiesene Testreihe öffnen, ein unkritisches Feld (z. B. Beschreibung) ändern, speichern und die Reihe erneut laden.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Geänderte Werte werden angezeigt.
- [ ] Nicht geänderte Werte bleiben erhalten.
- [ ] Bestehende Serienberechtigungen bleiben erhalten.
- [ ] Bereits vorhandene Termine und Themen sind weiterhin dem richtigen fachlichen Kontext zugeordnet.

- **Test erfolgreich:** [ ]

#### 8.3.3 Besprechungsreihe verlängern – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Eine zugewiesene Testreihe öffnen, das Enddatum um mindestens einen Serientermin verlängern und die Änderung speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Zusätzliche Termine werden bis zum neuen Enddatum erzeugt.
- [ ] Bereits vorhandene Termine bleiben erhalten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 8.3.4 Termine einer Reihe neu aufsetzen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Eine eigens dafür angelegte Testreihe verwenden, den Wiederholungsrhythmus kontrolliert ändern und das Neuaufsetzen der Terminfolge auslösen. Vorher vorhandene Termine und Zuordnungen dokumentieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Terminfolge entspricht den eingestellten Seriendaten.
- [ ] Es entstehen keine doppelten Termine.
- [ ] Bestehende Themen, Tagesordnungspunkte und Serienberechtigungen entsprechen den vorgesehenen Regeln.
- [ ] Nicht ausgewählte Reihen sind unverändert.

- **Test erfolgreich:** [ ]

#### 8.3.5 Besprechungsreihe löschen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ausschließlich eine entbehrliche Testreihe verwenden, die vorgesehene Löschvariante auswählen und den Löschvorgang bestätigen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Reihe wird nicht mehr als aktive Reihe angeboten.
- [ ] Historische Inhalte entsprechen nach dem Löschen genau der im Prüfschritt gewählten Löschvariante; Inhalte außerhalb ihres Löschumfangs bleiben erhalten.
- [ ] Vorgesehene historische Lesezugriffe bleiben erhalten.
- [ ] Andere Reihen und deren Berechtigungen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 8.3.6 Berechtigungen einer Reihe verwalten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Berechtigungsverwaltung einer zugewiesenen Testreihe öffnen, ein separates Testkonto hinzufügen oder dessen Rolle ändern und die Änderung speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Das Testkonto ist der richtigen Reihe zugeordnet.
- [ ] Die gespeicherte Serienrolle entspricht der im Prüfschritt ausgewählten Rolle.
- [ ] Änderungen betreffen nur die ausgewählte Reihe.
- [ ] Der Versuch, die eigene Moderatorzuweisung zu entfernen oder auf eine niedrigere Rolle zu setzen, wird abgewiesen; die Moderatorzuweisung bleibt bestehen.
- [ ] Zuweisungen in anderen Reihen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 8.3.7 Zugriff auf fachliche Inhalte einer nicht zugewiesenen Reihe prüfen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt auf die eigene Reihe, Zugriff verweigert auf nicht zugewiesene Reihen.** Die Moderatorrolle gilt ausschließlich für die ausdrücklich zugewiesene Reihe.

**Prüfschritt**
 1. Mit einem Moderator-Konto anmelden, das für Testreihe A als Moderator zugewiesen ist.
 1. Sicherstellen, dass für Testreihe B keine Serienzuweisung besteht.
 1. Einen Termin und ein Thema aus Testreihe A über die vorgesehenen Ansichten öffnen.
 1. Die bekannten direkten URLs eines Termins und eines Themas aus Testreihe B aufrufen.

**Ergebnisprüfung**
- [ ] Das Moderator-Konto kann Termine und Themen aus Testreihe A über die fachlichen Ansichten öffnen; Inhalte aus Testreihe B bleiben unzugänglich.
- [ ] Die direkten URLs zu Terminen und Themen aus Testreihe B liefern keinen fachlichen Inhalt.
- [ ] Es werden keine Daten oder Anlagen aus Testreihe B offengelegt.
- [ ] Die Serienzuweisung und Inhalte beider Testreihen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 8.3.8 Moderatorzugriff auf eine fremde Reihe verweigern – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt auf die eigene Reihe, Zugriff verweigert auf fremde Reihen.** Mit dem Testkonto muss Testreihe A verwaltbar sein. Für Testreihe B darf keine Moderatorzuweisung bestehen; bei erreichbarer Verwaltungsseite müssen schreibende Aktionen trotzdem verweigert werden.

**Prüfschritt**

 1. Ein Moderator-Konto für Testreihe A verwenden.
 1. Sicherstellen, dass für Testreihe B keine Zuweisung besteht.
 1. Testreihe A über die Serienverwaltung öffnen und eine vorhandene Einstellung der Reihe aufrufen.
 1. Die Verwaltungsübersicht bzw. Bearbeitungsseite von Testreihe B über Navigation und direkte URL aufrufen. Ist die Seite nicht erreichbar, keine schreibende Aktion für B versuchen und die Prüfung der Reihenverwaltung für B beenden.
 1. Nur wenn die Verwaltungsseite von B erreichbar ist: Eine schreibende Aktion für Testreihe B über die Oberfläche bzw. den vorgesehenen POST-Direktaufruf versuchen.
 1. Den Daten- und Berechtigungsstand von Testreihe B nur dann vor und nach dem Versuch vergleichen, wenn eine schreibende Aktion tatsächlich versucht wurde.

**Ergebnisprüfung**

- [ ] Die Verwaltungsübersicht von Testreihe A ist erreichbar; Bearbeitungs- und Mitgliederverwaltungsfunktionen werden für die eigene Moderatorreihe angeboten.
- [ ] Die Verwaltungsseite von Testreihe B ist nicht erreichbar; falls sie erreichbar ist, werden schreibende Aktionen verweigert.
- [ ] Daten und Berechtigungen von Testreihe B bleiben unverändert.

- **Test erfolgreich:** [ ]

### 8.4 Termine und Besprechungsübersicht

#### 8.4.1 Terminübersicht aufrufen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Terminübersicht über die Navigation öffnen, die für das Testkonto verfügbaren Reihen bzw. Termine laden und den angezeigten Umfang prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Termine der berechtigten Reihen werden angezeigt.
- [ ] Datum und Reihenbezeichnung stimmen.
- [ ] Vergangene Termine sind als vergangen bzw. abgeschlossen und zukünftige Termine als anstehend erkennbar; beide gehören zur zugewiesenen Besprechungsreihe.
- [ ] Termine nicht zugewiesener Reihen werden nicht angezeigt.

- **Test erfolgreich:** [ ]

#### 8.4.2 Einzelnen Termin verschieben – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen zugewiesenen Testtermin öffnen, Datum oder Uhrzeit auf einen freien Testzeitpunkt ändern und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Termin wird am neuen Datum angezeigt.
- [ ] Der bisherige Termin wird nicht zusätzlich als Duplikat angezeigt.
- [ ] Zugehörige Tagesordnungspunkte und Zuständigkeiten bleiben dem Termin zugeordnet.
- [ ] Die übrigen Termine der Reihe entsprechen weiterhin dem vorgesehenen Rhythmus.

- **Test erfolgreich:** [ ]

#### 8.4.3 Einzelnen Termin löschen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen eigens angelegten entbehrlichen Testtermin öffnen, den Löschvorgang auslösen und die Rückfrage bestätigen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der ausgewählte Termin ist nach dem Löschen weder in der Terminübersicht noch in der Terminliste der Reihe vorhanden.
- [ ] Nicht ausgewählte Termine bleiben erhalten.
- [ ] Der gelöschte Termin ist entfernt; seine Tagesordnungspunkte und Teilnehmenden sind dem nächsten nicht abgeschlossenen Termin derselben Reihe zugeordnet. Die zugehörigen Themen bleiben erhalten.
- [ ] Es bleiben keine ungewollten Zuordnungen oder doppelten Einträge zurück.

- **Test erfolgreich:** [ ]

#### 8.4.4 Teilnehmerliste bearbeiten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Teilnehmerliste eines zugewiesenen Testtermins öffnen, ein separates Testkonto hinzufügen oder entfernen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die ausgewählten Konten werden in der Teilnehmerliste angezeigt.
- [ ] Abgewählte Konten werden nicht mehr angezeigt.
- [ ] Die Änderung betrifft nur den ausgewählten Termin.
- [ ] Die Serienberechtigungen der Konten bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 8.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)
**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der exakt beschriebenen Serienrolle anmelden.
 1. Einen abgeschlossenen Testtermin der zugewiesenen Reihe öffnen und den Protokoll-/Tagesordnungsstand dokumentieren.
 1. Vor dem Wiederöffnen eine schreibende Aktion am abgeschlossenen Termin versuchen und anschließend prüfen, dass der Abschlussstatus bestehen bleibt.
 1. Den Termin über die gesonderte Moderatorfunktion wieder öffnen, eine zulässige Änderung durchführen und den Termin erneut abschließen.

**Ergebnisprüfung**
- [ ] Der Moderator kann den abgeschlossenen Termin seiner zugewiesenen Reihe öffnen und den gespeicherten Protokollstand einsehen.
- [ ] Der abgeschlossene Termin bleibt bis zur ausdrücklichen Wiederöffnung schreibgeschützt.
- [ ] Nach dem Wiederöffnen bleibt der vorherige Protokollstand im Änderungsverlauf nachvollziehbar; eine erneute Bearbeitung und ein erneuter Abschluss sind möglich.

- **Test erfolgreich:** [ ]
### 8.5 Themen anlegen und bearbeiten

#### 8.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Im Dashboard die Funktion zum Anlegen eines Themas öffnen, ein eindeutig erkennbares Testthema mit Pflichtangaben erfassen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Das Thema erscheint in der Themenübersicht.
- [ ] Titel und Hauptzuständigkeit entsprechen den Eingaben.
- [ ] Das Thema ist der ausgewählten Besprechungsreihe zugeordnet.
- [ ] Für den ausgewählten Termin ist der zugehörige Tagesordnungspunkt vorhanden.
- [ ] Das Thema ist nicht versehentlich in einer anderen Reihe angelegt worden.

- **Test erfolgreich:** [ ]

#### 8.5.2 Thema über einen Termin anlegen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen zugänglichen Testtermin öffnen, dort ein neues Testthema mit eindeutiger Bezeichnung und Pflichtangaben anlegen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Das neue Thema ist angelegt.
- [ ] Der Tagesordnungspunkt ist dem geöffneten Termin zugeordnet.
- [ ] Die Hauptzuständigkeit entspricht dem ausgewählten Konto; die abweichende Zuständigkeit wird separat mit dem im Prüfschritt ausgewählten Konto angezeigt.
- [ ] Das Thema ist in der Themenübersicht auffindbar.

- **Test erfolgreich:** [ ]

#### 8.5.3 Thema bearbeiten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema öffnen, ein unkritisches Feld ändern, speichern und die Detailansicht erneut laden.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Titel, Status und Hauptzuständigkeit entsprechen den gespeicherten Werten.
- [ ] Änderungen bleiben nach dem Neuladen erhalten.
- [ ] Jeder Tagesordnungspunkt bleibt dem bearbeiteten Thema zugeordnet; vorhandene historische Protokoll-Snapshots behalten ihren zuvor gespeicherten Inhalt.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

- **Test erfolgreich:** [ ]

#### 8.5.4 Themenstatus ändern – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema öffnen, den Status über die vorgesehene Statusaktion ändern und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der neue Status wird in der Detailansicht angezeigt.
- [ ] Die Übersicht zeigt denselben Statuswert wie die Themendetailansicht.
- [ ] Der Status des Tagesordnungspunkts bleibt unverändert; geändert wird ausschließlich der Status des übergeordneten Themas.

- **Test erfolgreich:** [ ]

#### 8.5.5 Thema archivieren und wieder öffnen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein entbehrliches Testthema archivieren, die Archivansicht öffnen und das Thema anschließend über die vorgesehene Funktion wieder öffnen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Archivierte Themen erscheinen im Archiv und nicht mehr in der regulären offenen Themenliste.
- [ ] Wieder geöffnete Themen erscheinen wieder im vorgesehenen aktiven Bereich.
- [ ] Titel, Zuständigkeit, Kommentare und zugehörige historische Inhalte bleiben erhalten.
- [ ] Der Änderungsverlauf bildet die Aktion ab.

- **Test erfolgreich:** [ ]

#### 8.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein entbehrliches Testthema aus Testreihe A auswählen, die ausdrücklich als Ziel vorgesehene Testreihe B wählen und den Übertragungsvorgang bestätigen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Das Thema ist der vorgesehenen Zielreihe zugeordnet.
- [ ] Der vorgesehene Zieltermin enthält den Tagesordnungspunkt.
- [ ] Übertragungsnotiz und Übertragungsverlauf sind nachvollziehbar.
- [ ] Die Serienzuweisungen der beteiligten Konten in Quell- und Zielreihe bleiben unverändert; die Themenübertragung erzeugt keine zusätzliche Serienberechtigung.
- [ ] Andere Themen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 8.5.7 Themenvorschläge verwenden – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Themenvorschläge im vorgesehenen Eingabebereich öffnen, einen passenden Vorschlag auswählen und dessen Übernahme auslösen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Titel und übernommene Vorschlagsdaten entsprechen dem ausgewählten Vorschlag.
- [ ] Das Thema bzw. der Tagesordnungspunkt wird mit den eingegebenen Daten angelegt.
- [ ] Es wird kein zusätzlicher oder doppelter Datensatz angelegt.

- **Test erfolgreich:** [ ]

---

### 8.6 Tagesordnungspunkte und Wiedervorlagen

#### 8.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen zugänglichen Testtermin mit Tagesordnung öffnen, einen vorhandenen Test-Tagesordnungspunkt ändern und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der gespeicherte Text wird beim erneuten Öffnen des Tagesordnungspunkts wortgleich angezeigt.
- [ ] Der Status des Tagesordnungspunkts entspricht der Auswahl.
- [ ] Die abweichende Zuständigkeit entspricht dem im Prüfschritt ausgewählten Konto und bleibt von der Hauptzuständigkeit getrennt.
- [ ] Der allgemeine Themenstatus bleibt davon getrennt.

- **Test erfolgreich:** [ ]

#### 8.6.2 Tagesordnungspunkte sortieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Bei einem Testtermin mindestens zwei Tagesordnungspunkte in eine andere Reihenfolge bringen, die Sortierung speichern und die Seite neu laden.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Reihenfolge entspricht der zuletzt vorgenommenen Sortierung.
- [ ] Jeder Tagesordnungspunkt ist weiterhin dem richtigen Thema zugeordnet.
- [ ] Es fehlen keine Punkte und es sind keine Duplikate entstanden.

- **Test erfolgreich:** [ ]

#### 8.6.3 Tagesordnungspunkt entfernen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen entbehrlichen Test-Tagesordnungspunkt auswählen, die Entfernen-Funktion auslösen und die Änderung bestätigen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Punkt ist aus dem ausgewählten Termin entfernt.
- [ ] Das zugrunde liegende Thema bleibt in der Themenübersicht erhalten; entfernt wird ausschließlich der ausgewählte Tagesordnungspunkt.
- [ ] Andere Tagesordnungspunkte bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 8.6.4 Wiedervorlage anlegen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Bei einem Testthema eine Wiedervorlage mit einem konkreten Folgetermin setzen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Tagesordnungspunkt erscheint im vorgesehenen Zieltermin.
- [ ] Die Verbindung zum vorherigen Tagesordnungspunkt ist nachvollziehbar.
- [ ] Status und Zuständigkeit entsprechen den vorgesehenen Übernahmeregeln.
- [ ] Es ist keine doppelte Wiedervorlage entstanden.

- **Test erfolgreich:** [ ]

#### 8.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Eine Wiedervorlage für ein Testthema anlegen, den ersten Folgetermin bearbeiten bzw. abschließen und den nächsten vorgesehenen Termin auf die fortgeführte Wiedervorlage prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Wiedervorlagekette ist chronologisch nachvollziehbar.
- [ ] Jeder Punkt ist dem richtigen Termin zugeordnet.
- [ ] Frühere Protokollstände bleiben unverändert.
- [ ] Es entstehen keine doppelten oder voneinander getrennten Ketten.

- **Test erfolgreich:** [ ]

#### 8.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen zugänglichen Termin mit bereits abgeschlossenen bzw. historischen Tagesordnungseinträgen öffnen und den historischen Eintrag gezielt auswählen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Datum, Reihenbezeichnung, Text, Status und Verantwortlichkeit stimmen mit den im historischen Tagesordnungseintrag gespeicherten Werten überein.
- [ ] Historische Einträge lassen sich nicht unberechtigt verändern.
- [ ] Zugriff ist auf berechtigte Konten begrenzt.

- **Test erfolgreich:** [ ]

---

### 8.7 Kommentare, Anlagen und Links

#### 8.7.1 Kommentar hinzufügen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema öffnen, einen eindeutig als Test erkennbaren Kommentar hinzufügen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Kommentar wird beim richtigen Thema angezeigt.
- [ ] Als Autor wird das angemeldete Testkonto angezeigt; der Erstellungszeitpunkt liegt im Zeitraum der gerade ausgeführten Aktion.
- [ ] Der Kommentar bleibt nach dem Neuladen erhalten.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

- **Test erfolgreich:** [ ]

#### 8.7.2 Datei als Themenanlage hochladen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema öffnen, eine harmlose Testdatei als Anlage auswählen und hochladen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Anlage wird beim richtigen Thema angezeigt.
- [ ] Die angezeigte Bezeichnung entspricht der eingegebenen Bezeichnung; die Datei ist dem ausgewählten Thema zugeordnet und lässt sich öffnen.
- [ ] Die Datei lässt sich mit einem berechtigten Konto herunterladen.
- [ ] Der Änderungsverlauf enthält den vorgesehenen Eintrag.

- **Test erfolgreich:** [ ]

#### 8.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Bei einem zugänglichen Testthema einen dafür vorgesehenen Test-Netzwerkpfad oder eine unkritische Test-URL hinterlegen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der gespeicherte Pfad bzw. die URL entspricht exakt der eingegebenen Zeichenfolge.
- [ ] Unterstützte Pfade werden als anklickbarer Link dargestellt und öffnen das hinterlegte Ziel.
- [ ] Nicht unterstützte oder ungültige Werte werden nicht als unsichere Links ausgegeben.
- [ ] Die Anwendung behauptet nicht, die Erreichbarkeit einer externen Freigabe zu garantieren.

- **Test erfolgreich:** [ ]

#### 8.7.4 Anlage herunterladen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema mit einer bekannten Testdatei öffnen, die Anlage herunterladen und den Dateiinhalt mit der hochgeladenen Testdatei vergleichen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Berechtigte Konten können die zugehörige Datei herunterladen.
- [ ] Dateiinhalt und Dateiname entsprechen der hochgeladenen Datei.
- [ ] Nicht berechtigte Konten erhalten keinen Dateizugriff.

- **Test erfolgreich:** [ ]

#### 8.7.5 Anlage löschen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema mit einer entbehrlichen Testanlage öffnen, die Anlage löschen und die Rückfrage bestätigen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die Anlage wird nicht mehr in der Themenansicht angezeigt.
- [ ] Der direkte Download der entfernten Anlage ist nicht mehr möglich.
- [ ] Andere Anlagen und Themen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 8.7.6 Upload-Grenzen prüfen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Für ein zugängliches Testthema eine Testdatei unterhalb und eine oberhalb der konfigurierten Upload-Grenze verwenden und beide Uploadversuche getrennt ausführen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Zulässige Dateien innerhalb des Limits werden angenommen.
- [ ] Zu große Dateien werden abgewiesen.
- [ ] Nicht erlaubte Dateiendungen werden abgewiesen.
- [ ] Abgewiesene Uploads erzeugen keine ungewollten Anlagen-Datensätze.

- **Test erfolgreich:** [ ]

---

### 8.8 Besprechung abschließen und Protokoll

#### 8.8.1 Besprechung abschließen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen dafür vorgesehenen Testtermin öffnen, die Abschlussfunktion auslösen und die Bestätigung durchführen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Termin ist als abgeschlossen gekennzeichnet.
- [ ] Ein Protokoll-Snapshot wurde erstellt.
- [ ] Teilnehmerliste und Tagesordnungstexte sind gegen weitere Bearbeitung gesperrt.
- [ ] Der Abschluss wird im Änderungsverlauf dokumentiert.

- **Test erfolgreich:** [ ]

#### 8.8.2 Protokoll anzeigen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen zugänglichen abgeschlossenen Testtermin öffnen und das gespeicherte Protokoll aufrufen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Protokoll zeigt den beim Abschluss gesicherten Stand.
- [ ] Historische Werte werden nicht durch spätere Änderungen am Thema überschrieben.
- [ ] Protokoll ist für berechtigte Leser*innen sichtbar.

- **Test erfolgreich:** [ ]

#### 8.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Das Protokoll eines zugänglichen Testtermins öffnen, die Druckansicht aufrufen und zusätzlich den PDF-Export auslösen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Druckansicht enthält den richtigen Termin und Protokollstand.
- [ ] PDF lässt sich öffnen.
- [ ] PDF enthält die vorgesehenen Protokolldaten.
- [ ] Im PDF erscheinen die aktuell gespeicherte Organisationsbezeichnung und das aktuell gespeicherte Organisationslogo.
- [ ] Unberechtigte Konten können den Export nicht abrufen.

- **Test erfolgreich:** [ ]

#### 8.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Einen abgeschlossenen Testtermin der zugewiesenen Reihe öffnen und die Funktion zum Wiederöffnen auslösen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Der Termin ist nach dem Wiederöffnen bearbeitbar.
- [ ] Der vorherige Protokollstand bleibt als historischer Stand nachvollziehbar.
- [ ] Die erneute Bearbeitung und der erneute Abschluss funktionieren.
- [ ] Teilnehmer*innen ohne Moderatorrechte können den Termin nicht wieder öffnen.

- **Test erfolgreich:** [ ]

#### 8.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Ein zugängliches Testthema mit Protokolleinträgen öffnen und den Themenprotokoll-PDF-Export auslösen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] PDF enthält die dem Thema zugeordneten historischen Einträge.
- [ ] PDF-Datum und Reihenbezeichnung stimmen mit dem ausgewählten Termin überein; Texte und Statuswerte entsprechen dem gespeicherten Themen- und Protokollstand.
- [ ] Der Export ist auf berechtigte Konten begrenzt.

- **Test erfolgreich:** [ ]

---

### 8.9 Offene Themen und Archiv

#### 8.9.1 Offene Themen aufrufen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Übersicht der offenen Themen öffnen und die angezeigten Themen anhand der zugewiesenen Reihen prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Nur fachlich zugängliche Themen werden angezeigt.
- [ ] Angezeigter Status und Zuständigkeit entsprechen den gespeicherten Themenwerten; die angezeigte Reihe entspricht der tatsächlichen Zuordnung des Themas.
- [ ] Auswahl und Filter führen zu passenden Ergebnissen.

- **Test erfolgreich:** [ ]

#### 8.9.2 Archiv aufrufen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Das Archiv über die Navigation öffnen, die Ergebnisliste laden und den angezeigten Datenumfang prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Archivierte Themen sind im Archiv auffindbar.
- [ ] Es werden ausschließlich historische Inhalte der ausdrücklich zugewiesenen Reihe angezeigt; Inhalte nicht zugewiesener Reihen bleiben verborgen.
- [ ] Nicht archivierte Themen werden nicht fälschlich als archiviert dargestellt.

- **Test erfolgreich:** [ ]

#### 8.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)
**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die direkte URL eines vorbereiteten historischen Eintrags aus einer gelöschten bzw. nicht zugänglichen Reihe aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Historische Inhalte werden nicht angezeigt oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Themen-, Protokoll- oder Anlagendaten offengelegt.

- **Test erfolgreich:** [ ]
### 8.10 Berechtigungsanträge

#### 8.10.1 Serienberechtigung für die eigene moderierte Reihe beantragen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff verweigert.** Eine Moderatorin bzw. ein Moderator kann für die bereits moderierte Reihe keinen weiteren Berechtigungsantrag stellen oder die eigene Moderatorrolle selbst herabstufen.

**Prüfschritt**
 1. Mit einem Moderator-Konto anmelden, das der geprüften Reihe ausdrücklich als Moderator*in zugewiesen ist.
 1. Die persönliche Benutzerübersicht öffnen und prüfen, dass die Rollenwahl für diese Reihe gesperrt ist.
 1. Einen direkten POST-Aufruf für einen Berechtigungsantrag zu genau dieser Reihe versuchen.
 1. Die Benutzerübersicht und die Serienzuweisung neu laden.

**Ergebnisprüfung**
- [ ] Für die bereits moderierte Reihe kann kein neuer Berechtigungsantrag erstellt werden.
- [ ] Die bestehende Moderatorzuweisung bleibt unverändert.
- [ ] Es entsteht kein offener oder doppelter Antrag.
- [ ] Andere Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 8.10.2 Berechtigungsantrag entscheiden – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt für Anträge der eigenen moderierten Reihe; Zugriff verweigert für fremde Reihen.**

**Prüfschritt**
 1. Mit einem Moderator-Konto anmelden, das für Testreihe A ausdrücklich als Moderator*in zugewiesen ist.
 1. Für ein separates Testkonto einen offenen Berechtigungsantrag für Testreihe A vorbereiten.
 1. Den Antrag für Testreihe A öffnen und einmal genehmigen oder ablehnen.
 1. Zusätzlich einen offenen Antrag für Testreihe B vorbereiten, für die keine Moderatorzuweisung besteht, und versuchen, diesen zu entscheiden.
 1. Die Antragsliste und die Serienzuweisungen beider Testkonten neu laden.

**Ergebnisprüfung**
- [ ] Der Antrag für die eigene moderierte Testreihe A wird aus der Liste offener Anträge entfernt bzw. als entschieden gekennzeichnet.
- [ ] Die gespeicherte Entscheidung für Testreihe A entspricht exakt der gewählten Genehmigung oder Ablehnung.
- [ ] Der Antrag für die fremde Testreihe B kann nicht entschieden werden und bleibt unverändert offen.
- [ ] Bei Genehmigung für Testreihe A erhält das Testkonto ausschließlich die genehmigte Serienrolle für diese Reihe.
- [ ] Andere Anträge und Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 8.10.3 Bereits vorhandenen Antrag für die eigene moderierte Reihe erneut bearbeiten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff verweigert.** Für eine Reihe, in der das Konto bereits Moderator*in ist, ist die erneute Beantragung oder Bearbeitung eines eigenen Berechtigungsantrags gesperrt.

**Prüfschritt**
 1. Mit einem Moderator-Konto anmelden, das der geprüften Reihe ausdrücklich als Moderator*in zugewiesen ist.
 1. Einen vorhandenen offenen Antrag dieses Kontos für dieselbe Reihe vorbereiten, sofern der Testbestand einen solchen Altantrag enthält.
 1. Die persönliche Benutzerübersicht öffnen und den direkten POST-Aufruf für dieselbe Reihe erneut versuchen.
 1. Die Antragsliste und die Serienzuweisung neu laden.

**Ergebnisprüfung**
- [ ] Die Moderatorrolle kann für dieselbe Reihe nicht erneut beantragt oder geändert werden.
- [ ] Es entsteht kein weiterer offener Antrag.
- [ ] Vorhandene Antragsdaten und die Moderatorzuweisung bleiben unverändert.
- [ ] Andere Reihen und deren Berechtigungen bleiben unverändert.

- **Test erfolgreich:** [ ]
### 8.11 Benutzer- und Themenimport/-export

#### 8.11.1 Benutzer als CSV exportieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)
**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Benutzerverwaltung bzw. den Benutzerexport öffnen und den CSV-Export über die Oberfläche oder den vorgesehenen Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Benutzer-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Konten- oder Profildaten offengelegt.

- **Test erfolgreich:** [ ]
#### 8.11.2 Benutzer per CSV importieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)
**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine CSV-Datei mit ausschließlich separaten Testkonten vorbereiten und den Import über die Oberfläche bzw. den vorgesehenen Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Import wird abgewiesen; es werden keine Testkonten angelegt oder bestehende Konten verändert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entstehen keine Teilimporte oder unvollständigen Benutzerzuordnungen.

- **Test erfolgreich:** [ ]
#### 8.11.3 Themen als CSV exportieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Themen-CSV-Funktion für eine zugängliche Testreihe aufrufen, den Export starten und die heruntergeladene Datei öffnen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Export ist lesbar und enthält die vorgesehenen Themen.
- [ ] CSV-Zuständigkeiten, Statuswerte und Reihenbezüge stimmen mit den gespeicherten Datensätzen der exportierten Reihe überein.
- [ ] Inhalte außerhalb des zulässigen Berechtigungs- bzw. Exportumfangs werden nicht offengelegt.

- **Test erfolgreich:** [ ]

#### 8.11.4 Themen per CSV importieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Eine vorbereitete CSV-Datei mit eindeutig markierten Testdatensätzen auswählen, den Import starten und die Rückmeldung der Anwendung prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Jede gültige CSV-Zeile legt genau das zugehörige Testthema an oder aktualisiert es; ungültige Zeilen werden nicht teilweise gespeichert.
- [ ] Ungültige Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Jeder importierte Datensatz ist der in der CSV-Zeile angegebenen Besprechungsreihe zugeordnet; die Zuständigkeit entspricht dem dort angegebenen Konto.
- [ ] Es entstehen keine unbeabsichtigten Duplikate.

- **Test erfolgreich:** [ ]

---

### 8.12 Änderungsverlauf und Audit

#### 8.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Den Änderungsverlauf einer zugewiesenen Testreihe öffnen und die serienbezogenen Ereignisse aufrufen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Moderator*in sieht die Ereignisse der eigenen moderierten Reihe.
- [ ] Ereignisse anderer Reihen werden nicht offengelegt.
- [ ] Akteur, Zeitpunkt und Aktion sind nachvollziehbar.
- [ ] Unberechtigte Konten erhalten keinen Zugriff.

- **Test erfolgreich:** [ ]

#### 8.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)
**Berechtigungserwartung für Moderator: Zugriff auf die Änderungsverlaufseite erlaubt; Systemereignisse eingeschränkt.** Die Änderungsverlaufseite ist erreichbar. Moderator*innen sehen die Ereignisse ihrer eigenen moderierten Reihen, aber keine systembezogenen Ereignisse.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen Rolle bzw. Serienzuweisung anmelden.
 1. Die Seite **Änderungsverlauf** über die Navigation oder direkt öffnen.
 1. Den Bereich für Systemereignisse aufrufen bzw. den passenden Filter verwenden.
 1. Prüfen, welche Ereignisse tatsächlich angezeigt werden; bei Bedarf die Seite neu laden und einen direkten Filteraufruf testen.

**Ergebnisprüfung**
- [ ] Die Änderungsverlaufseite wird geöffnet.
- [ ] Ereignisse der eigenen moderierten Reihe können weiterhin angezeigt werden.
- [ ] Systembezogene Ereignisse werden nicht angezeigt oder exportiert.
- [ ] Ereignisse anderer Reihen bleiben verborgen.

- **Test erfolgreich:** [ ]
#### 8.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)

**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Den für die Rolle zugänglichen Änderungsverlauf öffnen, den CSV-Export auslösen und die Datei öffnen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] CSV-Datei ist lesbar.
- [ ] Export enthält nur die für die Rolle zulässigen Ereignisse.
- [ ] Direkter Exportaufruf ohne passende Berechtigung wird abgewiesen.
- [ ] Nicht erforderliche vertrauliche Daten werden nicht exportiert.

- **Test erfolgreich:** [ ]

---

### 8.13 Aufbewahrung und automatische Löschung

#### 8.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)
**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Verwaltungsseite für Aufbewahrungsfristen direkt und über die Navigation öffnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die administrativen Aufbewahrungseinstellungen werden nicht angezeigt und der Zugriff wird verweigert bzw. zur berechtigten Ansicht umgeleitet.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Fristwerte oder administrativen Löschoptionen offengelegt.

- **Test erfolgreich:** [ ]
#### 8.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)
**Berechtigungserwartung für Moderator: Zugriff erlaubt.** Moderator*innen dürfen archivierte Themen ihrer zugewiesenen Reihe und die dort angezeigte Aufbewahrungsfrist bzw. das Löschdatum einsehen; die globalen Aufbewahrungseinstellungen werden in diesem Test nicht verändert.

**Prüfschritt**
 1. Mit einem Testkonto anmelden, das der geprüften Reihe ausdrücklich als Moderator*in zugewiesen ist.
 1. Das Archiv über die Navigation öffnen und ein vorbereitetes archiviertes Thema aus der zugewiesenen Reihe auswählen.
 1. Die angezeigte Aufbewahrungsfrist und das vorgesehene Löschdatum ablesen.

**Ergebnisprüfung**
- [ ] Die Archivansicht wird ohne Zugriffsfehler geöffnet.
- [ ] Archivierte Themen der zugewiesenen Reihe und deren Aufbewahrungsdaten werden angezeigt.
- [ ] Themen und Aufbewahrungsdaten fremder Reihen werden nicht offengelegt.
- [ ] Die in den globalen Verwaltungseinstellungen hinterlegten Aufbewahrungsfristen werden durch diesen Test nicht verändert.

- **Test erfolgreich:** [ ]
#### 8.13.3 Retention wiederholt ausführen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)
**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den vorgesehenen Retention-Auslöser bzw. den direkten Ausführungsendpunkt mit vorbereiteten Testdaten aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Retention-Lauf wird nicht gestartet bzw. die Aktion wird abgewiesen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Termine, Protokolle, Themen oder Dateien gelöscht oder verändert.

- **Test erfolgreich:** [ ]
### 8.14 Auditor*innenbereich

#### 8.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)
**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Auditor*innenübersicht über die Navigation und zusätzlich über ihre direkte URL aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Rolle erhält keine Auditor*innenübersicht; die Anwendung verweigert den Zugriff oder leitet zur regulären Startseite weiter.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Audit- oder Organisationsprüfdaten angezeigt.

- **Test erfolgreich:** [ ]
#### 8.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)
**Berechtigungserwartung für Moderator: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die im Testfall aufgeführten Auditor*innen-URLs einzeln direkt aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Jeder geschützte Auditor*innen-Endpunkt verweigert den Zugriff oder leitet auf eine reguläre, für die Rolle zulässige Seite um.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Audit-, Benutzer- oder Organisationsdaten offengelegt.

- **Test erfolgreich:** [ ]
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

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Das Dashboard über die Hauptnavigation öffnen und vollständig laden lassen. Die angezeigten Kacheln, Kennzahlen und Verknüpfungen prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Dashboard wird ohne Fehler geladen.
- [ ] Es werden nur die für das Konto vorgesehenen Inhalte und Einstiege angezeigt.
- [ ] Verlinkte Bereiche lassen sich öffnen.
- [ ] Nicht berechtigte fachliche Inhalte werden nicht angezeigt.

- **Test erfolgreich:** [ ]

#### 9.1.2 Navigation und Darstellungsvarianten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Hauptnavigation auf Desktop und mobiler Ansicht öffnen. Menüpunkte, Untermenüs und Darstellungsvarianten durchgehen; nicht angebotene Funktionen nicht über fremde Konten simulieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Nach dem Neuladen ist weiterhin die zuvor ausgewählte Darstellungsvariante aktiv.

- **Test erfolgreich:** [ ]

---

### 9.2 Persönliches Konto und eigene Aufgaben

#### 9.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die persönlichen Kontoeinstellungen öffnen, ein unkritisches Testfeld ändern und speichern. Die Seite neu laden und den gespeicherten Wert kontrollieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 9.2.2 Eigene Aufgaben aufrufen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die persönliche Aufgabenübersicht über Navigation und direkte URL öffnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Aufgaben aus nicht zugewiesenen Reihen angezeigt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Seite gibt keine Themen- oder Zuständigkeitsdaten fremder Reihen preis.

- **Test erfolgreich:** [ ]
### 9.3 Besprechungsreihen verwalten

#### 9.3.1 Besprechungsreihe anlegen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Serienverwaltung öffnen und eine eindeutig benannte Testreihe mit Testbeschreibung, Startdatum, Rhythmus und Enddatum anlegen. Die vorgesehene Moderatorzuweisung setzen und speichern.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die neue Besprechungsreihe erscheint in der Übersicht.
- [ ] Bezeichnung, Beschreibung und Wiederholungseinstellungen entsprechen den Eingaben.
- [ ] Jeder erzeugte Termin liegt innerhalb des festgelegten Start- und Enddatums und folgt dem gespeicherten Rhythmus und Intervall.
- [ ] Die erstellende Moderatorin bzw. der erstellende Moderator besitzt die vorgesehene Serienzuweisung.
- [ ] Serienzuweisungen außerhalb der neu angelegten Testreihe sind nach dem Speichern unverändert; insbesondere werden keine zusätzlichen Rollen in anderen Reihen angelegt.

- **Test erfolgreich:** [ ]

#### 9.3.2 Besprechungsreihe bearbeiten – Prüfrolle: globaler Admin (ohne Moderatorzuweisung in der geprüften Reihe; Moderator*in in einer anderen Reihe)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die globale Adminrolle und eine Moderatorzuweisung in einer anderen Reihe ersetzen keine Moderatorzuweisung für die konkret geprüfte Bestandsreihe.

**Prüfschritt**
 1. Mit einem globalen Admin-Konto anmelden, das für Testreihe B Moderator*in, für die geprüfte Bestandsreihe A aber nicht als Moderator*in zugewiesen ist.
 1. Die Bearbeitungsseite von Testreihe A über die Serienverwaltung und zusätzlich über die direkte URL aufrufen. Ist die Bearbeitungsseite nicht erreichbar, keine Änderungsaktion versuchen und die Prüfung dieses Funktionsbereichs beenden.
 1. Nur wenn die Bearbeitungsseite von A erreichbar ist: Eine Änderung an einem unkritischen Feld versuchen, ohne sie bei unerwarteter Freigabe endgültig zu speichern.
 1. Den Daten- bzw. Protokollstand von A nur dann vor und nach dem Versuch vergleichen, wenn eine Änderungsaktion tatsächlich versucht wurde.

**Ergebnisprüfung**
- [ ] Die Bearbeitungsseite von Testreihe A ist nicht erreichbar; falls sie erreichbar ist, wird die Änderungsaktion ohne Moderatorzuweisung für A verweigert.
- [ ] Testreihe A bleibt unverändert; Bezeichnung, Beschreibung, Wiederholungseinstellungen und Moderatorzuweisungen werden nicht geändert.
- [ ] Die Moderatorzuweisung in Testreihe B erweitert die Rechte für Testreihe A nicht.

- **Test erfolgreich:** [ ]
#### 9.3.3 Besprechungsreihe verlängern – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Serienverwaltung öffnen und versuchen, das Enddatum einer Bestandsreihe ohne Moderatorzuweisung zu verlängern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Verlängerung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Enddatum, Terminfolge und Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.3.4 Termine einer Reihe neu aufsetzen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Serienverwaltung öffnen und versuchen, die Terminfolge einer Bestandsreihe ohne Moderatorzuweisung neu aufzusetzen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Neuaufsetzen wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Bestehende Termine, Themen, Tagesordnungspunkte und Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.3.5 Besprechungsreihe löschen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Serienverwaltung öffnen und versuchen, eine Bestandsreihe ohne Moderatorzuweisung zu löschen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Löschung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Besprechungsreihe und sämtliche zugehörigen Termine, Themen und Berechtigungen bleiben erhalten.

- **Test erfolgreich:** [ ]
#### 9.3.6 Berechtigungen einer Reihe verwalten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Berechtigungsverwaltung einer bekannten Bestandsreihe öffnen und versuchen, die Rolle eines separaten Testkontos zu ändern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Berechtigungsänderung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Bestehende Serienzuweisungen und Rollen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.3.7 Zugriff auf fachliche Inhalte ohne Serienzuweisung prüfen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt auf die administrative Serienverwaltung, Zugriff verweigert auf fachliche Reiheninhalte ohne Moderatorzuweisung.** Die globale Adminrolle verleiht keinen automatischen Zugriff auf bestehende Termine oder Themen.

**Prüfschritt**
 1. Mit einem globalen Admin-Konto ohne Moderatorzuweisung für Testreihe A anmelden.
 1. Die administrative Serienverwaltungsübersicht öffnen.
 1. Einen Termin und ein Thema aus Testreihe A über deren bekannte direkte URLs aufrufen.
 1. Keine fachlichen Änderungen vornehmen.

**Ergebnisprüfung**
- [ ] Die administrative Serienverwaltungsübersicht ist erreichbar.
- [ ] Die direkten URLs zu Terminen und Themen aus Testreihe A liefern keinen fachlichen Inhalt.
- [ ] Es werden keine Tagesordnungspunkte, Teilnehmerdaten oder Anlagen aus Testreihe A offengelegt.
- [ ] Die globale Adminrolle allein gewährt keine fachliche Serienberechtigung.

- **Test erfolgreich:** [ ]
#### 9.3.8 Globaler Admin mit Moderatorzuweisung in Testreihe A – Prüfrolle: globale Adminrolle + Moderator*in in Testreihe A

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**

 1. Ein globales Admin-Konto verwenden und es für Testreihe A ausdrücklich als Moderator zuweisen.
 1. Für Testreihe B keine Serienzuweisung für dieses Konto vergeben.
 1. Testreihe A über die Serienverwaltung öffnen und eine zulässige Verwaltungsaktion ausführen.
 1. Dieselbe Verwaltungsseite für Testreihe B über die direkte URL aufrufen.
 1. Prüfen, ob die globale Adminrolle ohne Serienzuweisung den Zugriff auf Testreihe B erweitert.

**Ergebnisprüfung**

- [ ] In Testreihe A ist die Moderatorverwaltung aufgrund der ausdrücklichen Serienzuweisung möglich.
- [ ] In Testreihe B wird der Zugriff verweigert.
- [ ] Die globale Adminrolle erweitert die Moderatorberechtigung nicht auf andere Reihen.
- [ ] Änderungen an Testreihe A verändern die Berechtigungen von Testreihe B nicht.

- **Test erfolgreich:** [ ]

#### 9.3.9 Moderatorzugriff auf eine fremde Reihe verweigern – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Verwaltungsübersicht und Bearbeitungsseite einer Reihe ohne Moderatorzuweisung direkt aufrufen und eine schreibende Aktion versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die fremde Reihe wird nicht zur Verwaltung freigegeben.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Seriendaten und Berechtigungen der fremden Reihe bleiben unverändert.

- **Test erfolgreich:** [ ]
### 9.4 Termine und Besprechungsübersicht

#### 9.4.1 Terminübersicht aufrufen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Terminübersicht ist für den globalen Admin ohne Serienzuweisung erreichbar. Es werden keine fachlichen Termine angezeigt.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden.
 1. Die Terminübersicht über die Navigation bzw. den vorgesehenen Aufruf öffnen.
 1. Die Ansicht bzw. Ergebnisliste laden und den angezeigten Datenumfang prüfen.

**Ergebnisprüfung**
- [ ] Die Terminübersicht wird ohne Zugriffsfehler geöffnet.
- [ ] Die Terminübersicht ist für den globalen Admin ohne Serienzuweisung erreichbar. Es werden keine fachlichen Termine angezeigt.
- [ ] Es werden keine Termine, Themen oder Aufgaben aus nicht zugewiesenen Reihen offengelegt.

- **Test erfolgreich:** [ ]
#### 9.4.2 Einzelnen Termin verschieben – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Testtermin der nicht zugewiesenen bzw. nicht berechtigten Reihe direkt aufrufen und versuchen, Datum oder Uhrzeit zu ändern und zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Terminänderung wird verweigert oder die Aktion ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Datum, Uhrzeit und Serienzuordnung des Termins bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.4.3 Einzelnen Termin löschen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten entbehrlichen Testtermin der betroffenen Reihe aufrufen und die Löschaktion über Oberfläche bzw. POST-Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Termin wird nicht gelöscht.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Termin, Tagesordnungspunkte, Teilnehmerzuordnungen und Folgetermine bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.4.4 Teilnehmerliste bearbeiten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Teilnehmerliste eines bekannten Testtermins öffnen und versuchen, ein separates Testkonto hinzuzufügen oder zu entfernen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Teilnehmeränderung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Teilnehmerliste und alle bestehenden Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten abgeschlossenen Testtermin öffnen und versuchen, einen Tagesordnungspunkt oder ein anderes gespeichertes Protokollmerkmal zu ändern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die schreibende Aktion am abgeschlossenen Termin wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Abschlussstatus, Protokoll-Snapshot und Tagesordnung bleiben unverändert.

- **Test erfolgreich:** [ ]
### 9.5 Themen anlegen und bearbeiten

#### 9.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Im Dashboard die Funktion zum Anlegen eines Themas aufrufen und ein eindeutig markiertes Testthema mit Pflichtangaben zu speichern versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Testthema wird nicht angelegt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht weder ein neuer Themendatensatz noch eine neue Zuordnung zu einem Termin.

- **Test erfolgreich:** [ ]
#### 9.5.2 Thema über einen Termin anlegen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Testtermin aufrufen und dort versuchen, ein neues Testthema mit eindeutiger Bezeichnung anzulegen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Testthema wird nicht angelegt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht weder ein neuer Themendatensatz noch ein zusätzlicher Tagesordnungseintrag.

- **Test erfolgreich:** [ ]
#### 9.5.3 Thema bearbeiten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen, ein unkritisches Feld ändern und die Änderung speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Themenänderung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Titel, Beschreibung, Status, Zuständigkeit und Reihenbezug bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.5.4 Themenstatus ändern – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und versuchen, dessen Status zu ändern und zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Statusänderung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der ursprüngliche Themenstatus und die zugehörigen Zeitstempel bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.5.5 Thema archivieren und wieder öffnen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema aufrufen und die Archivierungs- sowie – falls bereits archiviert – die Wiederöffnen-Aktion versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Archivieren bzw. Wiederöffnen wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Status, Archivierungsdatum und bisherige Themeninhalte bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema auswählen und versuchen, es in eine andere Testreihe zu übertragen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Übertragung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Thema bleibt der ursprünglichen Reihe zugeordnet; in der Zielreihe entsteht keine Kopie.

- **Test erfolgreich:** [ ]
#### 9.5.7 Themenvorschläge verwenden – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Der Vorschlags-Endpunkt ist erreichbar, liefert aber ausschließlich Themen aus zugänglichen Reihen. Ohne Serienzuweisung ist die Ergebnisliste leer.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden.
 1. Den direkten Endpunkt `/topics/suggestions/?q=te` mit einem Suchbegriff von mindestens zwei Zeichen aufrufen.
 1. Die JSON-Antwort und das Feld `results` prüfen.

**Ergebnisprüfung**
- [ ] Der Themenvorschlags-Endpunkt wird ohne Zugriffsfehler geöffnet.
- [ ] Der Vorschlags-Endpunkt ist erreichbar, liefert aber ausschließlich Themen aus zugänglichen Reihen. Ohne Serienzuweisung ist die Ergebnisliste leer.
- [ ] Es werden keine Termine, Themen oder Aufgaben aus nicht zugewiesenen Reihen offengelegt.

- **Test erfolgreich:** [ ]
### 9.6 Tagesordnungspunkte und Wiedervorlagen

#### 9.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Tagesordnungspunkt eines Testtermins öffnen, ein Feld ändern und speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Bearbeitung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Text, Zuständigkeit, Status und Zuordnung des Tagesordnungspunkts bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.6.2 Tagesordnungspunkte sortieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen Testtermin mit mindestens zwei Tagesordnungspunkten öffnen und versuchen, deren Reihenfolge zu ändern und zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Sortierung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die ursprüngliche Reihenfolge und Positionswerte bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.6.3 Tagesordnungspunkt entfernen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Tagesordnungspunkt auswählen und versuchen, ihn über die Oberfläche oder den vorgesehenen POST-Aufruf zu entfernen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Tagesordnungspunkt wird nicht entfernt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Tagesordnungseintrag, Themenbezug und historische Inhalte bleiben erhalten.

- **Test erfolgreich:** [ ]
#### 9.6.4 Wiedervorlage anlegen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und versuchen, eine Wiedervorlage für einen Folgetermin anzulegen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Wiedervorlage wird nicht angelegt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht keine neue Termin- oder Tagesordnungspunktzuordnung.

- **Test erfolgreich:** [ ]
#### 9.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine vorbereitete Wiedervorlage öffnen und versuchen, sie auf den nächsten Termin fortzuführen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Fortführung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entstehen keine neuen Wiedervorlagen, Verknüpfungen oder doppelten Tagesordnungseinträge.

- **Test erfolgreich:** [ ]
#### 9.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Historie eines bekannten Termins bzw. Themas über die vorgesehene Seite und die direkte URL aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Historische Tagesordnungseinträge werden für diese Rolle nicht angezeigt oder ausgegeben.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine historischen Themen-, Protokoll- oder Zuständigkeitsdaten offengelegt.

- **Test erfolgreich:** [ ]
### 9.7 Kommentare, Anlagen und Links

#### 9.7.1 Kommentar hinzufügen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und einen eindeutig als Test erkennbaren Kommentar absenden.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Kommentar wird nicht gespeichert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht kein neuer Kommentar und bestehende Kommentare bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.7.2 Datei als Themenanlage hochladen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und eine harmlose Testdatei als Anlage hochzuladen versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Upload wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht kein neuer Anlagendatensatz und keine Datei wird dauerhaft gespeichert.

- **Test erfolgreich:** [ ]
#### 9.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und versuchen, einen Test-Netzwerkpfad oder eine unkritische Test-URL als Anlage zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Hinterlegen des Pfads bzw. Links wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird kein neuer Anlagen-, Pfad- oder Linkeintrag gespeichert.

- **Test erfolgreich:** [ ]
#### 9.7.4 Anlage herunterladen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine bekannte Testanlage direkt über den Download-Link bzw. den vorgesehenen Download-Endpunkt aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Download wird verweigert oder liefert keine geschützte Datei aus.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Dateiinhalt und Metadaten der Anlage werden nicht offengelegt.

- **Test erfolgreich:** [ ]
#### 9.7.5 Anlage löschen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine bekannte Testanlage auswählen und versuchen, sie zu löschen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Löschung der Anlage wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Anlagendatensatz und gespeicherte Datei bleiben unverändert erhalten.

- **Test erfolgreich:** [ ]
#### 9.7.6 Upload-Grenzen prüfen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Bei einem bekannten Testthema den Upload einer harmlosen Testdatei über die vorgesehene Upload-Funktion versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Upload wird wegen fehlender Berechtigung verweigert; eine Größenprüfung darf nicht zu einem erfolgreichen Upload führen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Datei gespeichert und es entsteht kein Anlagendatensatz.

- **Test erfolgreich:** [ ]
### 9.8 Besprechung abschließen und Protokoll

#### 9.8.1 Besprechung abschließen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten noch offenen Testtermin öffnen und versuchen, ihn über die Abschlussfunktion abzuschließen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Abschlussvorgang wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Termin bleibt offen; Abschlusszeitpunkt und Protokoll-Snapshot werden nicht angelegt.

- **Test erfolgreich:** [ ]
#### 9.8.2 Protokoll anzeigen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die direkte URL eines bekannten abgeschlossenen Testtermins bzw. dessen Protokollansicht aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Protokoll wird nicht angezeigt oder ausgegeben.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Tagesordnung, Kommentare, Zuständigkeiten oder Protokoll-Snapshots offengelegt.

- **Test erfolgreich:** [ ]
#### 9.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Druckansicht eines bekannten Testprotokolls aufrufen und den PDF-Export versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Druckansicht und PDF-Export werden verweigert oder sind nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Protokoll-PDF-Datei erzeugt oder heruntergeladen.

- **Test erfolgreich:** [ ]
#### 9.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: globaler Admin (ohne Moderatorzuweisung in der geprüften Reihe; Moderator*in in einer anderen Reihe)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Eine globale Adminrolle und eine Moderatorzuweisung in einer anderen Reihe berechtigen nicht dazu, einen abgeschlossenen Termin der geprüften Reihe wieder zu öffnen.

**Prüfschritt**
 1. Mit einem globalen Admin-Konto anmelden, das für Testreihe B Moderator*in, für die geprüfte Testreihe A aber nicht als Moderator*in zugewiesen ist.
 1. Einen abgeschlossenen Termin aus Testreihe A über die vorgesehene Terminansicht und zusätzlich über die direkte URL aufrufen. Ist die Terminseite nicht erreichbar, keine Wiederöffnen-Aktion versuchen und die Prüfung dieses Funktionsbereichs beenden.
 1. Nur wenn die Terminseite von A erreichbar ist: Die Wiederöffnen-Aktion über die Oberfläche und – soweit vorgesehen – über den POST-Direktaufruf versuchen.
 1. Den Daten- bzw. Protokollstand von A nur dann vor und nach dem Versuch vergleichen, wenn die Wiederöffnen-Aktion tatsächlich versucht wurde.

**Ergebnisprüfung**
- [ ] Die Terminseite von Testreihe A ist nicht erreichbar; falls sie erreichbar ist, wird die Wiederöffnen-Aktion ohne Moderatorzuweisung für A verweigert.
- [ ] Der abgeschlossene Termin in A bleibt unverändert und behält seinen bisherigen Abschlussstatus sowie seinen gespeicherten Protokollstand.
- [ ] Die Moderatorzuweisung in Testreihe B erweitert die Rechte zum Wiederöffnen eines Termins in Testreihe A nicht.

- **Test erfolgreich:** [ ]
#### 9.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und den Export des Themenprotokolls als PDF versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der PDF-Export wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Themenprotokoll-PDF-Datei erzeugt oder heruntergeladen.

- **Test erfolgreich:** [ ]
### 9.9 Offene Themen und Archiv

#### 9.9.1 Offene Themen aufrufen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Übersicht offener Themen über die Navigation und die direkte URL öffnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine offenen Themen aus nicht zugewiesenen Reihen angezeigt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Anwendung legt keine neuen Termin- oder Tagesordnungspunktzuordnungen an.

- **Test erfolgreich:** [ ]
#### 9.9.2 Archiv aufrufen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Das Archiv ist für den globalen Admin erreichbar. Ohne eigene Serienzuweisung werden keine fachlichen archivierten Themen angezeigt.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden.
 1. Das Archiv über die Navigation bzw. den vorgesehenen Aufruf öffnen.
 1. Die Ansicht bzw. Ergebnisliste laden und den angezeigten Datenumfang prüfen.

**Ergebnisprüfung**
- [ ] Das Archiv wird ohne Zugriffsfehler geöffnet.
- [ ] Das Archiv ist für den globalen Admin erreichbar. Ohne eigene Serienzuweisung werden keine fachlichen archivierten Themen angezeigt.
- [ ] Es werden keine Termine, Themen oder Aufgaben aus nicht zugewiesenen Reihen offengelegt.

- **Test erfolgreich:** [ ]
#### 9.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die direkte URL eines vorbereiteten historischen Eintrags aus einer gelöschten bzw. nicht zugänglichen Reihe aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Historische Inhalte werden nicht angezeigt oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Themen-, Protokoll- oder Anlagendaten offengelegt.

- **Test erfolgreich:** [ ]
### 9.10 Berechtigungsanträge

#### 9.10.1 Serienberechtigung beantragen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Auch ein globaler Admin ohne eigene Serienzuweisung kann über die persönliche Benutzerübersicht eine Serienberechtigung beantragen. Die Adminrolle ersetzt die beantragte Serienzuweisung nicht.

**Prüfschritt**
 1. Mit einem globalen Admin-Konto ohne Moderatorzuweisung für die Testreihe anmelden.
 1. Die persönliche Benutzerübersicht öffnen und für eine Testreihe eine gewünschte Serienrolle auswählen.
 1. Den Antrag absenden und anschließend die Benutzerübersicht neu laden.

**Ergebnisprüfung**
- [ ] Der Antrag wird der richtigen Person und Testreihe zugeordnet und als offen angezeigt.
- [ ] Die globale Adminrolle wird nicht automatisch in eine Serienrolle umgewandelt.
- [ ] Fachliche Inhalte bleiben bis zur Genehmigung der Serienzuweisung unzugänglich.
- [ ] Andere Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.10.2 Berechtigungsantrag entscheiden – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit einem globalen Admin-Konto anmelden.
 1. Für ein separates Testkonto einen offenen Berechtigungsantrag für eine Testreihe vorbereiten.
 1. Die Liste offener Anträge öffnen, den vorbereiteten Antrag auswählen und einmal genehmigen oder ablehnen.
 1. Die Liste und den Berechtigungsstatus des antragstellenden Testkontos erneut laden.

**Ergebnisprüfung**
- [ ] Der Antrag wird aus der Liste offener Anträge entfernt bzw. als entschieden gekennzeichnet.
- [ ] Die gespeicherte Entscheidung entspricht exakt der gewählten Genehmigung oder Ablehnung.
- [ ] Bei Genehmigung erhält das Testkonto ausschließlich die genehmigte Serienrolle für die ausgewählte Reihe.
- [ ] Bei Ablehnung entsteht keine Serienzuweisung; andere Anträge und Reihen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 9.10.3 Bereits vorhandenen Antrag erneut bearbeiten – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Für dasselbe Testkonto einen bereits offenen Antrag für dieselbe Testreihe vorbereiten und den Antrag erneut absenden; falls die Oberfläche das Formular ausblendet, den entsprechenden POST-Aufruf direkt wiederholen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Es entstehen keine unzulässigen doppelten offenen Anträge.
- [ ] Bereits entschiedene Anträge werden nicht irrtümlich als offen behandelt.
- [ ] Die Serienzuweisungen des Testkontos bleiben unverändert; das erneute Absenden eines bereits offenen Antrags legt keine zusätzliche Zuweisung an.

- **Test erfolgreich:** [ ]

---

### 9.11 Benutzer- und Themenimport/-export

#### 9.11.1 Benutzer als CSV exportieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Benutzerverwaltung öffnen, den Benutzer-CSV-Export auslösen und die heruntergeladene Datei auf Umfang und Inhalt prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Exportdatei ist lesbar.
- [ ] Enthaltene Konten und Felder entsprechen dem vorgesehenen Exportumfang.
- [ ] Passwörter oder andere nicht exportierbare Geheimnisse sind nicht enthalten.

- **Test erfolgreich:** [ ]

#### 9.11.2 Benutzer per CSV importieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Eine vorbereitete CSV-Datei mit separaten Testkonten verwenden, den Benutzerimport starten und die Import-Rückmeldung prüfen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Jede gültige CSV-Zeile legt das zugehörige Testkonto mit den enthaltenen Stammdaten an oder aktualisiert es; ungültige Zeilen legen kein Konto an.
- [ ] Fehlerhafte Zeilen werden nachvollziehbar ausgewiesen.
- [ ] Vorhandene Konten werden nicht ungewollt überschrieben.
- [ ] Bestehende Serienzuweisungen aller vorhandenen Konten bleiben nach dem CSV-Import unverändert; aus den importierten Stammdaten werden keine zusätzlichen Serienzuweisungen erzeugt.

- **Test erfolgreich:** [ ]

#### 9.11.3 Themen als CSV exportieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den Themen-CSV-Export für eine bekannte Reihe über Oberfläche oder Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Themen-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Themeninhalte und Zuständigkeiten nicht zugänglicher Reihen werden nicht offengelegt.

- **Test erfolgreich:** [ ]
#### 9.11.4 Themen per CSV importieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine vorbereitete CSV-Datei mit eindeutig markierten Testthemen auswählen und den Import versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Import wird verweigert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Themen angelegt und keine bestehenden Themen, Tagesordnungspunkte oder Reihenbezüge verändert.

- **Test erfolgreich:** [ ]
### 9.12 Änderungsverlauf und Audit

#### 9.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff auf die Änderungsverlaufseite erlaubt; Serienereignisse eingeschränkt.** Die Änderungsverlaufseite ist für den globalen Admin erreichbar und kann systembezogene Ereignisse anzeigen. Ohne Moderatorzuweisung für eine Reihe werden jedoch keine serienbezogenen Ereignisse dieser Reihe angezeigt.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen Rolle bzw. Serienzuweisung anmelden.
 1. Die Seite **Änderungsverlauf** über die Navigation oder direkt öffnen.
 1. Den Bereich für Serienereignisse aufrufen bzw. den passenden Filter verwenden.
 1. Prüfen, welche Ereignisse tatsächlich angezeigt werden; bei Bedarf die Seite neu laden und einen direkten Filteraufruf testen.

**Ergebnisprüfung**
- [ ] Die Änderungsverlaufseite wird geöffnet.
- [ ] Systembezogene Ereignisse sind für das globale Admin-Konto lesbar; serienbezogene Ereignisse ohne Moderatorzuweisung bleiben verborgen.
- [ ] Ohne Moderatorzuweisung werden keine serienbezogenen Ereignisse angezeigt.
- [ ] Ereignisse aus Reihen mit fremder Moderatorzuweisung werden nicht offengelegt.

- **Test erfolgreich:** [ ]
#### 9.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die systembezogene Historie ist für den globalen Admin lesbar; die Einträge sind nicht bearbeitbar.

**Prüfschritt**
 1. Mit einem globalen Admin-Konto ohne Serienzuweisung anmelden.
 1. Den systembezogenen Änderungsverlauf öffnen und die angezeigten Ereignisse prüfen.
 1. Prüfen, dass für die Ereignisse keine Bearbeitungs- oder Löschaktion angeboten wird.
 1. Einen direkten Aufruf einer nicht angebotenen Änderungsaktion versuchen, sofern dafür eine Route vorhanden ist.

**Ergebnisprüfung**

- [ ] Die systembezogene Historie wird für das globale Admin-Konto geöffnet und zeigt Systemereignisse.
- [ ] Für Systemereignisse werden keine Bearbeitungs- oder Löschfunktionen angeboten.
- [ ] Ein direkter Änderungs- oder Löschaufruf wird abgewiesen; die protokollierten Ereignisse bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 9.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Den für die Rolle zugänglichen Änderungsverlauf öffnen, den CSV-Export auslösen und die Datei öffnen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] CSV-Datei ist lesbar.
- [ ] Export enthält nur die für die Rolle zulässigen Ereignisse.
- [ ] Direkter Exportaufruf ohne passende Berechtigung wird abgewiesen.
- [ ] Nicht erforderliche vertrauliche Daten werden nicht exportiert.

- **Test erfolgreich:** [ ]

---

### 9.13 Aufbewahrung und automatische Löschung

#### 9.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Fristen sind für den globalen Admin einsehbar; die eigentliche Bereinigung wird durch den vorgesehenen Retention-Lauf ausgeführt.

**Prüfschritt**
 1. Mit einem globalen Admin-Konto ohne Serienzuweisung anmelden.
 1. Die Aufbewahrungseinstellungen öffnen und die globale Frist für Termine und Protokolle dokumentieren.
 1. In einer isolierten Testinstallation Testdaten vorbereiten: einen abgeschlossenen Termin vor Ablauf der globalen Frist mit einem Thema, dessen individuelle Themenfrist davon abweicht, einen abgeschlossenen Termin innerhalb der Frist sowie einen nicht abgeschlossenen Termin ohne Wiederöffnungsereignis. Die zugehörigen Tagesordnungspunkte und Protokoll-Snapshots dokumentieren.
 1. Den Retention-Lauf mit dem vorgesehenen Management-Befehl `python manage.py purge_expired_data` ausführen.
 1. Terminübersicht, Protokollansicht und historische Tagesordnung der Testdaten erneut öffnen und die vorhandenen Datensätze vergleichen.

**Ergebnisprüfung**

- [ ] Die angezeigte globale Aufbewahrungsfrist entspricht dem gespeicherten Wert in den Organisationseinstellungen.
- [ ] Der abgeschlossene Termin mit überschrittener globaler Frist und sein Protokoll-Snapshot werden durch den Retention-Lauf gelöscht.
- [ ] Der abgeschlossene Termin innerhalb der globalen Frist und sein Protokoll-Snapshot bleiben erhalten.
- [ ] Die historische Tagesordnung des gelöschten Termins bleibt mit ursprünglichem Datum, Reihenbezeichnung, Text, Status und Verantwortlichkeit für die zuvor berechtigten Konten verfügbar.
- [ ] Nicht abgeschlossene Termine ohne Wiederöffnungsereignis bleiben erhalten.

- **Test erfolgreich:** [ ]

#### 9.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Archivansicht ist für den globalen Admin erreichbar. Ohne Moderatorzuweisung für eine Reihe werden jedoch keine archivierten Themen oder deren Aufbewahrungsdaten angezeigt.

**Prüfschritt**
 1. Mit einem globalen Admin-Konto ohne Moderatorzuweisung für die geprüfte Bestandsreihe anmelden.
 1. Das Archiv über die Navigation oder die vorgesehene direkte URL öffnen.
 1. Die Archivliste laden und prüfen, ob archivierte Themen bzw. Aufbewahrungsdaten angezeigt werden.

**Ergebnisprüfung**
- [ ] Die Archivansicht wird ohne Zugriffsfehler geöffnet.
- [ ] Ohne Moderatorzuweisung enthält die Liste keine archivierten Themen der Bestandsreihe.
- [ ] Es werden keine Themen, Dateien oder Aufbewahrungsdaten aus Reihen ohne eigene Moderatorzuweisung offengelegt.

- **Test erfolgreich:** [ ]
#### 9.13.3 Retention wiederholt ausführen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)

**Berechtigungserwartung für Globale Rolle Admin: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Den Retention-Lauf ausschließlich mit vorbereiteten Testdaten bzw. in einer dafür vorgesehenen Testumgebung wiederholt ausführen und die resultierenden Statuswerte kontrollieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Wiederholte Ausführung erzeugt keine doppelten Löschvorgänge oder inkonsistenten Datensätze.
- [ ] Nicht abgelaufene Daten bleiben erhalten.
- [ ] Fehler einzelner Datensätze führen nicht zu unbemerkter Fehlbehandlung des gesamten Bestands.

- **Test erfolgreich:** [ ]

---

### 9.14 Auditor*innenbereich

#### 9.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Auditor*innenübersicht über die Navigation und zusätzlich über ihre direkte URL aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Rolle erhält keine Auditor*innenübersicht; die Anwendung verweigert den Zugriff oder leitet zur regulären Startseite weiter.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Audit- oder Organisationsprüfdaten angezeigt.

- **Test erfolgreich:** [ ]
#### 9.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: globaler Admin (ohne Serienzuweisung, sofern nicht ausdrücklich genannt)
**Berechtigungserwartung für Globale Rolle Admin: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die im Testfall aufgeführten Auditor*innen-URLs einzeln direkt aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Jeder geschützte Auditor*innen-Endpunkt verweigert den Zugriff oder leitet auf eine reguläre, für die Rolle zulässige Seite um.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Audit-, Benutzer- oder Organisationsdaten offengelegt.

- **Test erfolgreich:** [ ]
## 10. Produktiv – Globale Rolle Auditor

Ein globales Auditor-Konto verwenden. Auch bei vorhandener zusätzlicher Serienzuweisung darf es keine fachlichen Reiheninhalte sehen oder verändern. Nur ausdrücklich freigegebene administrative Prüfdaten sind lesbar.

**Verbindliche Durchführung für diese Rollengruppe**

- Alle folgenden Funktionsbereiche und Testfälle sind aus Sicht dieses Kontos durchzuführen.
- Bei erlaubten Aktionen muss die Funktion vollständig und mit korrektem Ergebnis funktionieren.
- Bei nicht erlaubten Aktionen den Aufruf über Navigation, direkte URL und – soweit möglich – direkte POST-Anfrage versuchen. Erwartet wird eine verweigerte Antwort (403/404 oder vorgesehene Umleitung), keine Datenänderung und keine Offenlegung geschützter Inhalte.
- Die nachfolgende Einzelprüfung nennt jeweils, ob die Rolle laut Berechtigungsmodell zugriffsberechtigt ist. Bei Serienfunktionen gilt die Berechtigung ausschließlich für die konkret zugewiesene Reihe.

### 10.1 Dashboard und Navigation

#### 10.1.1 Dashboard aufrufen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert (Weiterleitung).** Das allgemeine Dashboard wird für Auditor*innen nicht angezeigt; der Aufruf leitet zur Auditor*innenübersicht weiter.

**Prüfschritt**
 1. Mit einem globalen Auditor-Konto anmelden.
 1. Das Dashboard über die Navigation und zusätzlich über seine direkte URL aufrufen.
 1. Prüfen, ob die Anwendung zur Auditor*innenübersicht weiterleitet.

**Ergebnisprüfung**
- [ ] Das allgemeine Dashboard wird nicht angezeigt; stattdessen wird die Auditor*innenübersicht geöffnet.
- [ ] Es werden keine fachlichen Reihen, Termine oder Themeninhalte des allgemeinen Dashboards offengelegt.
- [ ] Die Auditor*innenübersicht zeigt nur die für diese globale Rolle vorgesehenen administrativen Prüfdaten.

- **Test erfolgreich:** [ ]
#### 10.1.2 Navigation und Darstellungsvarianten – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die Hauptnavigation auf Desktop und mobiler Ansicht öffnen. Menüpunkte, Untermenüs und Darstellungsvarianten durchgehen; nicht angebotene Funktionen nicht über fremde Konten simulieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Navigation bleibt bedienbar.
- [ ] Aktiver Bereich ist erkennbar.
- [ ] Inhalte und Bedienelemente überlagern sich nicht.
- [ ] Nach dem Neuladen ist weiterhin die zuvor ausgewählte Darstellungsvariante aktiv.

- **Test erfolgreich:** [ ]

---

### 10.2 Persönliches Konto und eigene Aufgaben

#### 10.2.1 Persönliche Kontodaten bearbeiten – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die persönlichen Kontoeinstellungen öffnen, ein unkritisches Testfeld ändern und speichern. Die Seite neu laden und den gespeicherten Wert kontrollieren.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Alle gespeicherten Werte werden nach dem Neuladen angezeigt.
- [ ] Die Benutzeranzeige verwendet die aktualisierten Kontodaten.
- [ ] Andere Konten und Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 10.2.2 Eigene Aufgaben aufrufen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert (Weiterleitung).** Die Aufgabenübersicht leitet globale Auditor*innen zur Auditor*innenübersicht weiter; eigene fachliche Aufgaben sind nicht zugänglich.

**Prüfschritt**
 1. Mit einem globalen Auditor-Konto anmelden.
 1. Die Aufgabenübersicht über die Navigation und zusätzlich über ihre direkte URL aufrufen.
 1. Prüfen, ob die Anwendung zur Auditor*innenübersicht weiterleitet.

**Ergebnisprüfung**
- [ ] Die Aufgabenübersicht wird nicht angezeigt; stattdessen wird die Auditor*innenübersicht geöffnet.
- [ ] Es werden keine persönlichen Aufgaben aus fachlichen Besprechungsreihen offengelegt.


- **Test erfolgreich:** [ ]
### 10.3 Besprechungsreihen verwalten

#### 10.3.1 Zugriff auf die Serienverwaltung prüfen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die globale Auditorrolle gewährt keine Moderatorrechte; die Seite der Serienverwaltung darf daher nicht erreichbar sein.

**Prüfschritt**

 1. Mit einem globalen Auditor-Konto anmelden.
 1. Prüfen, ob die Serienverwaltung in der Navigation angeboten wird.
 1. Die Seite der Serienverwaltung zusätzlich über ihre direkte URL aufrufen.
 1. Feststellen, dass der Zugriff verweigert wird und keine Serienverwaltungsseite mit Reihen oder Verwaltungsfunktionen angezeigt wird.

**Ergebnisprüfung**

- [ ] Die Serienverwaltung ist für diese Rolle weder über die Navigation noch über die direkte URL erreichbar.
- [ ] Es werden keine Reihen oder Verwaltungsfunktionen offengelegt.



- **Test erfolgreich:** [ ]

---

### 10.4 Termine und Besprechungsübersicht

#### 10.4.1 Terminübersicht aufrufen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Terminübersicht leitet globale Auditor*innen zur Auditor*innenübersicht weiter; fachliche Termine sind nicht zugänglich.

**Prüfschritt**
 1. Mit einem globalen Auditor-Konto anmelden.
 1. Die Terminübersicht über die Navigation öffnen und zusätzlich ihre direkte URL aufrufen.
 1. Prüfen, ob die Anwendung zur Auditor*innenübersicht weiterleitet.

**Ergebnisprüfung**
- [ ] Die Terminübersicht wird nicht als fachliche Terminansicht angezeigt, sondern leitet zur Auditor*innenübersicht weiter.
- [ ] Weder Termine noch Tagesordnungspunkte oder Teilnehmerdaten werden offengelegt.


- **Test erfolgreich:** [ ]
#### 10.4.2 Einzelnen Termin verschieben – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Testtermin der nicht zugewiesenen bzw. nicht berechtigten Reihe direkt aufrufen und versuchen, Datum oder Uhrzeit zu ändern und zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Terminänderung wird verweigert oder die Aktion ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Datum, Uhrzeit und Serienzuordnung des Termins bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 10.4.3 Einzelnen Termin löschen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten entbehrlichen Testtermin der betroffenen Reihe aufrufen und die Löschaktion über Oberfläche bzw. POST-Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Termin wird nicht gelöscht.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Termin, Tagesordnungspunkte, Teilnehmerzuordnungen und Folgetermine bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 10.4.4 Teilnehmerliste bearbeiten – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Teilnehmerliste eines bekannten Testtermins öffnen und versuchen, ein separates Testkonto hinzuzufügen oder zu entfernen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Teilnehmeränderung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Teilnehmerliste und alle bestehenden Serienzuweisungen bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 10.4.5 Schreibschutz abgeschlossener Termine – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten abgeschlossenen Testtermin öffnen und versuchen, einen Tagesordnungspunkt oder ein anderes gespeichertes Protokollmerkmal zu ändern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die schreibende Aktion am abgeschlossenen Termin wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Abschlussstatus, Protokoll-Snapshot und Tagesordnung bleiben unverändert.

- **Test erfolgreich:** [ ]
### 10.5 Themen anlegen und bearbeiten

#### 10.5.1 Thema aus dem Dashboard anlegen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Im Dashboard die Funktion zum Anlegen eines Themas aufrufen und ein eindeutig markiertes Testthema mit Pflichtangaben zu speichern versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Testthema wird nicht angelegt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht weder ein neuer Themendatensatz noch eine neue Zuordnung zu einem Termin.

- **Test erfolgreich:** [ ]
#### 10.5.2 Thema über einen Termin anlegen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Testtermin aufrufen und dort versuchen, ein neues Testthema mit eindeutiger Bezeichnung anzulegen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Testthema wird nicht angelegt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht weder ein neuer Themendatensatz noch ein zusätzlicher Tagesordnungseintrag.

- **Test erfolgreich:** [ ]
#### 10.5.3 Thema bearbeiten – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen, ein unkritisches Feld ändern und die Änderung speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Themenänderung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Titel, Beschreibung, Status, Zuständigkeit und Reihenbezug bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 10.5.4 Themenstatus ändern – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und versuchen, dessen Status zu ändern und zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Statusänderung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der ursprüngliche Themenstatus und die zugehörigen Zeitstempel bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 10.5.5 Thema archivieren und wieder öffnen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema aufrufen und die Archivierungs- sowie – falls bereits archiviert – die Wiederöffnen-Aktion versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Archivieren bzw. Wiederöffnen wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Status, Archivierungsdatum und bisherige Themeninhalte bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 10.5.6 Thema in eine andere Besprechungsreihe übertragen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema auswählen und versuchen, es in eine andere Testreihe zu übertragen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Übertragung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Thema bleibt der ursprünglichen Reihe zugeordnet; in der Zielreihe entsteht keine Kopie.

- **Test erfolgreich:** [ ]
#### 10.5.7 Themenvorschläge verwenden – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Der Vorschlags-Endpunkt ist erreichbar, liefert für die globale Auditorrolle wegen fehlenden fachlichen Zugriffs keine Themen.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden.
 1. Den direkten Endpunkt `/topics/suggestions/?q=te` mit einem Suchbegriff von mindestens zwei Zeichen aufrufen.
 1. Die JSON-Antwort und das Feld `results` prüfen.

**Ergebnisprüfung**
- [ ] Der Themenvorschlags-Endpunkt wird ohne Zugriffsfehler geöffnet.
- [ ] Der Vorschlags-Endpunkt ist erreichbar, liefert für die globale Auditorrolle wegen fehlenden fachlichen Zugriffs keine Themen.
- [ ] Es werden keine Termine, Themen oder Aufgaben aus nicht zugewiesenen Reihen offengelegt.

- **Test erfolgreich:** [ ]
### 10.6 Tagesordnungspunkte und Wiedervorlagen

#### 10.6.1 Tagesordnungspunkt bearbeiten – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Tagesordnungspunkt eines Testtermins öffnen, ein Feld ändern und speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Bearbeitung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Text, Zuständigkeit, Status und Zuordnung des Tagesordnungspunkts bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 10.6.2 Tagesordnungspunkte sortieren – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen Testtermin mit mindestens zwei Tagesordnungspunkten öffnen und versuchen, deren Reihenfolge zu ändern und zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Sortierung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die ursprüngliche Reihenfolge und Positionswerte bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 10.6.3 Tagesordnungspunkt entfernen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten Tagesordnungspunkt auswählen und versuchen, ihn über die Oberfläche oder den vorgesehenen POST-Aufruf zu entfernen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Tagesordnungspunkt wird nicht entfernt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Tagesordnungseintrag, Themenbezug und historische Inhalte bleiben erhalten.

- **Test erfolgreich:** [ ]
#### 10.6.4 Wiedervorlage anlegen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und versuchen, eine Wiedervorlage für einen Folgetermin anzulegen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Wiedervorlage wird nicht angelegt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht keine neue Termin- oder Tagesordnungspunktzuordnung.

- **Test erfolgreich:** [ ]
#### 10.6.5 Wiedervorlage über mehrere Termine fortführen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine vorbereitete Wiedervorlage öffnen und versuchen, sie auf den nächsten Termin fortzuführen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Fortführung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entstehen keine neuen Wiedervorlagen, Verknüpfungen oder doppelten Tagesordnungseinträge.

- **Test erfolgreich:** [ ]
#### 10.6.6 Historische Tagesordnungseinträge aufrufen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Historie eines bekannten Termins bzw. Themas über die vorgesehene Seite und die direkte URL aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Historische Tagesordnungseinträge werden für diese Rolle nicht angezeigt oder ausgegeben.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine historischen Themen-, Protokoll- oder Zuständigkeitsdaten offengelegt.

- **Test erfolgreich:** [ ]
### 10.7 Kommentare, Anlagen und Links

#### 10.7.1 Kommentar hinzufügen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und einen eindeutig als Test erkennbaren Kommentar absenden.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Kommentar wird nicht gespeichert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht kein neuer Kommentar und bestehende Kommentare bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 10.7.2 Datei als Themenanlage hochladen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und eine harmlose Testdatei als Anlage hochzuladen versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Upload wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entsteht kein neuer Anlagendatensatz und keine Datei wird dauerhaft gespeichert.

- **Test erfolgreich:** [ ]
#### 10.7.3 Netzwerkpfad oder Weblink hinterlegen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und versuchen, einen Test-Netzwerkpfad oder eine unkritische Test-URL als Anlage zu speichern.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Hinterlegen des Pfads bzw. Links wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird kein neuer Anlagen-, Pfad- oder Linkeintrag gespeichert.

- **Test erfolgreich:** [ ]
#### 10.7.4 Anlage herunterladen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine bekannte Testanlage direkt über den Download-Link bzw. den vorgesehenen Download-Endpunkt aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Download wird verweigert oder liefert keine geschützte Datei aus.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Dateiinhalt und Metadaten der Anlage werden nicht offengelegt.

- **Test erfolgreich:** [ ]
#### 10.7.5 Anlage löschen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine bekannte Testanlage auswählen und versuchen, sie zu löschen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Löschung der Anlage wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Anlagendatensatz und gespeicherte Datei bleiben unverändert erhalten.

- **Test erfolgreich:** [ ]
#### 10.7.6 Upload-Grenzen prüfen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Bei einem bekannten Testthema den Upload einer harmlosen Testdatei über die vorgesehene Upload-Funktion versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Upload wird wegen fehlender Berechtigung verweigert; eine Größenprüfung darf nicht zu einem erfolgreichen Upload führen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Datei gespeichert und es entsteht kein Anlagendatensatz.

- **Test erfolgreich:** [ ]
### 10.8 Besprechung abschließen und Protokoll

#### 10.8.1 Besprechung abschließen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten noch offenen Testtermin öffnen und versuchen, ihn über die Abschlussfunktion abzuschließen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Abschlussvorgang wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Termin bleibt offen; Abschlusszeitpunkt und Protokoll-Snapshot werden nicht angelegt.

- **Test erfolgreich:** [ ]
#### 10.8.2 Protokoll anzeigen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die direkte URL eines bekannten abgeschlossenen Testtermins bzw. dessen Protokollansicht aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Das Protokoll wird nicht angezeigt oder ausgegeben.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Tagesordnung, Kommentare, Zuständigkeiten oder Protokoll-Snapshots offengelegt.

- **Test erfolgreich:** [ ]
#### 10.8.3 Protokoll drucken und als PDF exportieren – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Druckansicht eines bekannten Testprotokolls aufrufen und den PDF-Export versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Druckansicht und PDF-Export werden verweigert oder sind nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Protokoll-PDF-Datei erzeugt oder heruntergeladen.

- **Test erfolgreich:** [ ]
#### 10.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen bekannten abgeschlossenen Testtermin aufrufen und die Wiederöffnen-Aktion über Oberfläche bzw. POST-Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Wiederöffnung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Abschlussstatus und gespeicherter Protokoll-Snapshot bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 10.8.5 Themenprotokoll als PDF exportieren – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Ein bekanntes Testthema öffnen und den Export des Themenprotokolls als PDF versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der PDF-Export wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Themenprotokoll-PDF-Datei erzeugt oder heruntergeladen.

- **Test erfolgreich:** [ ]
### 10.9 Offene Themen und Archiv

#### 10.9.1 Offene Themen aufrufen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Übersicht offener Themen über die Navigation und die direkte URL öffnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine offenen Themen aus nicht zugewiesenen Reihen angezeigt.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Anwendung legt keine neuen Termin- oder Tagesordnungspunktzuordnungen an.

- **Test erfolgreich:** [ ]
#### 10.9.2 Archiv aufrufen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert (Weiterleitung).** Das fachliche Archiv wird für Auditor*innen nicht angezeigt; der Aufruf leitet zur Auditor*innenübersicht weiter.

**Prüfschritt**
 1. Mit einem globalen Auditor-Konto anmelden.
 1. Das Archiv über die Navigation und zusätzlich über seine direkte URL aufrufen.
 1. Prüfen, ob die Anwendung zur Auditor*innenübersicht weiterleitet.

**Ergebnisprüfung**
- [ ] Das fachliche Archiv wird nicht angezeigt; stattdessen wird die Auditor*innenübersicht geöffnet.
- [ ] Archivierte Themen und zugehörige fachliche Inhalte werden nicht offengelegt.


- **Test erfolgreich:** [ ]
#### 10.9.3 Zugriff auf historische Inhalte nach Reihenlöschung – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die direkte URL eines vorbereiteten historischen Eintrags aus einer gelöschten bzw. nicht zugänglichen Reihe aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Historische Inhalte werden nicht angezeigt oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Themen-, Protokoll- oder Anlagendaten offengelegt.

- **Test erfolgreich:** [ ]
### 10.10 Berechtigungsanträge

#### 10.10.1 Serienberechtigung beantragen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Auditor*innen haben ausschließlich lesenden Zugriff und dürfen keine Serienberechtigungsanträge stellen.

**Prüfschritt**
 1. Mit einem globalen Auditor-Konto anmelden.
 1. Die persönliche Benutzerübersicht öffnen und prüfen, dass keine Funktion zum Beantragen einer Serienberechtigung angeboten wird.
 1. Einen direkten POST-Aufruf zum Beantragen einer Leser- oder Teilnehmerrolle für eine Testreihe versuchen.
 1. Die Antragsliste und Serienzuweisungen des Kontos neu laden.

**Ergebnisprüfung**
- [ ] Die Benutzerübersicht bietet keine Antragsfunktion für Auditor*innen an.
- [ ] Der direkte POST-Aufruf wird mit einer Zugriffsverweigerung abgewiesen.
- [ ] Es wird kein Serienberechtigungsantrag angelegt und keine Serienzuweisung verändert.
- [ ] Fachliche Reiheninhalte bleiben für das Auditor-Konto unzugänglich.

- **Test erfolgreich:** [ ]
#### 10.10.2 Berechtigungsantrag entscheiden – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Einen offenen Test-Berechtigungsantrag öffnen und versuchen, ihn zu genehmigen oder abzulehnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die Entscheidung wird verweigert oder ist nicht verfügbar.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Antrag bleibt offen; Serienrollen und Zugriffsrechte des antragstellenden Kontos bleiben unverändert.

- **Test erfolgreich:** [ ]
#### 10.10.3 Bereits vorhandenen Antrag erneut bearbeiten – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Auditor*innen dürfen bestehende Serienberechtigungsanträge nicht ändern oder erneut absenden.

**Prüfschritt**
 1. Mit einem globalen Auditor-Konto anmelden.
 1. Für das Testkonto einen bestehenden offenen Antrag in der Testdatenbank vorbereiten.
 1. Die persönliche Benutzerübersicht öffnen und versuchen, den vorhandenen Antrag erneut abzusenden bzw. zu bearbeiten.
 1. Zusätzlich den direkten POST-Aufruf mit der Antrags-ID versuchen.
 1. Den Status und die Anzahl der Anträge sowie die Serienzuweisungen erneut prüfen.

**Ergebnisprüfung**
- [ ] Die Antragsfunktion wird für Auditor*innen nicht angeboten.
- [ ] Der direkte POST-Aufruf wird mit einer Zugriffsverweigerung abgewiesen.
- [ ] Der vorhandene Antrag bleibt unverändert offen; es entsteht kein Duplikat.
- [ ] Serienzuweisungen und fachliche Zugriffsrechte bleiben unverändert.

- **Test erfolgreich:** [ ]
### 10.11 Benutzer- und Themenimport/-export

#### 10.11.1 Benutzer als CSV exportieren – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Benutzerverwaltung bzw. den Benutzerexport öffnen und den CSV-Export über die Oberfläche oder den vorgesehenen Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Benutzer-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Konten- oder Profildaten offengelegt.

- **Test erfolgreich:** [ ]
#### 10.11.2 Benutzer per CSV importieren – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine CSV-Datei mit ausschließlich separaten Testkonten vorbereiten und den Import über die Oberfläche bzw. den vorgesehenen Direktaufruf versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Import wird abgewiesen; es werden keine Testkonten angelegt oder bestehende Konten verändert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es entstehen keine Teilimporte oder unvollständigen Benutzerzuordnungen.

- **Test erfolgreich:** [ ]
#### 10.11.3 Themen als CSV exportieren – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den Themen-CSV-Export für eine bekannte Reihe über Oberfläche oder Direktaufruf starten.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es wird keine Themen-CSV-Datei ausgegeben oder heruntergeladen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Themeninhalte und Zuständigkeiten nicht zugänglicher Reihen werden nicht offengelegt.

- **Test erfolgreich:** [ ]
#### 10.11.4 Themen per CSV importieren – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Eine vorbereitete CSV-Datei mit eindeutig markierten Testthemen auswählen und den Import versuchen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Import wird verweigert.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Themen angelegt und keine bestehenden Themen, Tagesordnungspunkte oder Reihenbezüge verändert.

- **Test erfolgreich:** [ ]
### 10.12 Änderungsverlauf und Audit

#### 10.12.1 Serienbezogenen Änderungsverlauf anzeigen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff auf die Änderungsverlaufseite erlaubt; Systemereignisse sind lesbar, Serienereignisse und fachliche Reiheninhalte bleiben verborgen.**

**Prüfschritt**
 1. Mit einem globalen Auditor-Konto anmelden.
 1. Die Seite **Änderungsverlauf** über die Navigation oder direkt öffnen.
 1. Den Filter für systembezogene Ereignisse auswählen und die angezeigten Einträge prüfen.
 1. Den Filter für serienbezogene Ereignisse auswählen und die angezeigten Einträge prüfen.
 1. Einen direkten Aufruf des Serienereignis-Filters testen und die Seite neu laden.

**Ergebnisprüfung**
- [ ] Die Änderungsverlaufseite wird geöffnet.
- [ ] Systembezogene Ereignisse sind für das Auditor-Konto lesbar; serienbezogene Ereignisse und fachliche Reiheninhalte bleiben verborgen.
- [ ] Serienbezogene Ereignisse werden nicht angezeigt.
- [ ] Fachliche Inhalte anderer Reihen werden nicht offengelegt.

- **Test erfolgreich:** [ ]
#### 10.12.2 Systembezogenen Änderungsverlauf anzeigen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Die systembezogene Historie ist für die globale Auditor*in lesbar; die Einträge sind nicht bearbeitbar.

**Prüfschritt**
 1. Mit einem globalen Auditor-Konto anmelden.
 1. Den systembezogenen Änderungsverlauf öffnen und die angezeigten Ereignisse prüfen.
 1. Prüfen, dass für die Ereignisse keine Bearbeitungs- oder Löschaktion angeboten wird.
 1. Einen direkten Aufruf einer nicht angebotenen Änderungsaktion versuchen, sofern dafür eine Route vorhanden ist.

**Ergebnisprüfung**

- [ ] Die systembezogene Historie wird für das globale Auditor-Konto geöffnet und zeigt Systemereignisse.
- [ ] Serienbezogene Ereignisse und fachliche Inhalte nicht zugewiesener Reihen bleiben verborgen.
- [ ] Für Systemereignisse werden keine Bearbeitungs- oder Löschfunktionen angeboten.
- [ ] Ein direkter Änderungs- oder Löschaufruf wird abgewiesen; die protokollierten Ereignisse bleiben unverändert.

- **Test erfolgreich:** [ ]

#### 10.12.3 Änderungsverlauf als CSV exportieren – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Den für die Rolle zugänglichen Änderungsverlauf öffnen, den CSV-Export auslösen und die Datei öffnen.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] CSV-Datei ist lesbar.
- [ ] Export enthält nur die für die Rolle zulässigen Ereignisse.
- [ ] Direkter Exportaufruf ohne passende Berechtigung wird abgewiesen.
- [ ] Nicht erforderliche vertrauliche Daten werden nicht exportiert.

- **Test erfolgreich:** [ ]

---

### 10.13 Aufbewahrung und automatische Löschung

#### 10.13.1 Aufbewahrungsfristen für Termine und Protokolle prüfen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Die Verwaltungsseite für Aufbewahrungsfristen direkt und über die Navigation öffnen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Die administrativen Aufbewahrungseinstellungen werden nicht angezeigt und der Zugriff wird verweigert bzw. zur berechtigten Ansicht umgeleitet.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Fristwerte oder administrativen Löschoptionen offengelegt.

- **Test erfolgreich:** [ ]
#### 10.13.2 Aufbewahrungsfrist archivierter Themen prüfen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff auf die Auditor*innenübersicht erlaubt; Zugriff auf das Serienarchiv nicht erlaubt.** Der Archivaufruf leitet globale Auditor*innen zur Auditor*innenübersicht weiter und gibt keine archivierten Reiheninhalte aus.

**Prüfschritt**
 1. Mit einem globalen Auditor-Konto anmelden.
 1. Das Archiv über die Navigation öffnen und zusätzlich die direkte URL aufrufen.
 1. Prüfen, ob die Anwendung zur Auditor*innenübersicht weiterleitet.

**Ergebnisprüfung**
- [ ] Das Serienarchiv wird nicht angezeigt; stattdessen erfolgt die vorgesehene Weiterleitung zur Auditor*innenübersicht.
- [ ] Es werden keine archivierten Themen, Aufbewahrungsfristen oder Löschdaten aus Serien angezeigt.


- **Test erfolgreich:** [ ]
#### 10.13.3 Retention wiederholt ausführen – Prüfrolle: globale Auditor*in
**Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.** Die Funktion darf mit dieser Rolle nicht erfolgreich ausgeführt werden. Direkte URL- und Aktionsaufrufe müssen ebenfalls scheitern; Daten und Berechtigungen müssen unverändert bleiben.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto und der beschriebenen globalen Rolle bzw. Serienzuweisung anmelden.
 1. Zuerst die übergeordnete Seite des Funktionsbereichs über die Navigation und – soweit sinnvoll – über die direkte URL öffnen. Ist die Seite gesperrt, die Prüfung dieses Funktionsbereichs für diese Rolle beenden und keine nachgelagerte Aktion aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist: Den vorgesehenen Retention-Auslöser bzw. den direkten Ausführungsendpunkt mit vorbereiteten Testdaten aufrufen.
 1. Nur wenn die übergeordnete Seite erreichbar ist und ein konkreter Aktionsversuch erfolgt: Den Zustand der betroffenen Testdaten vor und nach dem Versuch vergleichen.

**Ergebnisprüfung**

- [ ] Falls die übergeordnete Seite nicht erreichbar ist: Die Zugriffsverweigerung ist nachgewiesen; der Funktionsbereich ist für diese Rolle nicht zugänglich.

- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Der Retention-Lauf wird nicht gestartet bzw. die Aktion wird abgewiesen.
- [ ] Nur wenn die übergeordnete Seite erreichbar ist: Es werden keine Termine, Protokolle, Themen oder Dateien gelöscht oder verändert.

- **Test erfolgreich:** [ ]
### 10.14 Auditor*innenbereich

#### 10.14.1 Auditor*innenübersicht aufrufen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die im Testfall bezeichnete Funktion über die Oberfläche aufrufen, die erforderliche Aktion mit geeigneten Testdaten ausführen und anschließend die Ansicht neu laden.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Die vorgesehenen administrativen Prüfdaten sind lesbar.
- [ ] Startpasswort und andere Geheimnisse werden nicht angezeigt.
- [ ] Es bestehen keine Änderungsfunktionen für Auditor*innen.
- [ ] Fachliche Besprechungsreihen und Themeninhalte sind nicht zugänglich.

- **Test erfolgreich:** [ ]

#### 10.14.2 Auditor*innenzugriff gegen direkte URLs prüfen – Prüfrolle: globale Auditor*in

**Berechtigungserwartung für Globale Rolle Auditor: Zugriff erlaubt.** Die Funktion muss mit diesem Konto und der für den Testfall vorausgesetzten Serienzuweisung erreichbar und ausführbar sein.

**Prüfschritt**
 1. Mit dem im Testfall genannten Konto anmelden und kontrollieren, dass die globale Rolle sowie die Serienzuweisung der Rollenbeschreibung entsprechen.
 1. Die im Testfall bezeichnete Funktion über die Oberfläche aufrufen, die erforderliche Aktion mit geeigneten Testdaten ausführen und anschließend die Ansicht neu laden.
 1. Vor einer schreibenden Aktion den Ausgangszustand der betroffenen Testdaten festhalten. Nach dem Aufruf die betroffene Ansicht neu laden und den tatsächlichen Zustand mit den nachfolgenden Ergebnisprüfungen vergleichen. Bei reinen Lese- oder Zugriffsprüfungen entfällt der Zustandsvergleich.

**Ergebnisprüfung**

- [ ] Lesender Zugriff auf ausdrücklich freigegebene administrative Prüfdaten ist möglich.
- [ ] Fachliche Inhalte sind nicht zugänglich.
- [ ] Schreibende Aktionen sind nicht möglich.
- [ ] Direkte URLs umgehen die Rollenbegrenzung nicht.

- **Test erfolgreich:** [ ]

---
