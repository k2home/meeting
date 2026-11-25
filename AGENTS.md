# Arbeitsanweisungen für KI-Agenten

Diese Datei enthält verbindliche Arbeitsregeln für KI-Agenten (insbesondere ChatGPT und Codex), die dieses Repository bearbeiten.

## Repository- und Branch-Regeln

- Arbeite grundsätzlich auf dem vom Nutzer ausdrücklich genannten Feature-Branch bzw. dem Branch des zugehörigen Pull Requests.
- Für die laufende Arbeit an PR #528 ist dies `feat/testing-mode-fixtures`.
- Ändere oder merge `beta` oder andere Ziel-/Produktionsbranches niemals direkt, sofern der Nutzer dies nicht ausdrücklich beauftragt.
- Bewahre bestehende Funktionen, Daten, Berechtigungen und insbesondere die bestehenden Serienberechtigungen. Ändere Berechtigungsregeln nicht beiläufig.
- Kläre Rückfragen und Unklarheiten vor der Umsetzung. Triff bei fachlich mehrdeutigen Anforderungen keine stillschweigenden Annahmen.
- Führe passende Tests und Prüfungen aus, soweit möglich. Behaupte niemals, Tests oder CI-Prüfungen seien erfolgreich, wenn sie nicht tatsächlich ausgeführt wurden und erfolgreich waren. Weise offen auf nicht ausgeführte oder noch laufende Prüfungen hin.

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

Der Abschlussbericht muss die tatsächlich vorgenommenen Änderungen knapp zusammenfassen und den Status der Tests/CI-Prüfungen korrekt wiedergeben. Die oben beschriebene Dokumentationsprüfung ist darin gesondert auszuweisen.
