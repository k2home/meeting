# Meeting Manager – enaio Windows-Agent

Der Agent läuft im angemeldeten Windows-Benutzerkonto, verwendet den dort geöffneten enaio-classic-Client über COM und fragt Aufträge des zugehörigen Meeting-Manager-Kontos über HTTPS ab. Für die Zielordnerwahl muss der gewünschte Ordner in enaio geöffnet sein. Bei mehreren geöffneten Ordnern zeigt der Agent einen Auswahldialog, statt willkürlich den ersten Eintrag zu verwenden. Es wird kein URL-Protokoll registriert.

## Voraussetzungen

- Windows x64 und .NET 8 Desktop Runtime
- enaio classic 11.x installiert und im Benutzerkonto geöffnet
- HTTPS-Zugriff auf den Meeting Manager

## Koppeln und starten

1. Im Meeting Manager unter **Konto** auf **Arbeitsplatz mit enaio verbinden** klicken.
2. Innerhalb von zehn Minuten ausführen: `MeetingManager.EnaioAgent.exe pair https://meeting-manager.example <Kopplungscode>`
3. Danach `MeetingManager.EnaioAgent.exe` ohne Argumente starten. Für automatischen Start eine Verknüpfung im Autostart-Ordner dieses Windows-Benutzers ablegen.

Das Gerätetoken wird mit Windows DPAPI für den aktuellen Benutzer verschlüsselt gespeichert. Der Kopplungscode ist zehn Minuten gültig und einmalig.

## Diagnose und Logs

Der Agent schreibt Diagnosemeldungen in die Debug-Console unter **Verwaltung → enaio-Einstellungen**. Die Anzeige aktualisiert sich automatisch und bietet Filter, Kopieren und Download. Lokal wird zusätzlich `%LOCALAPPDATA%\MeetingManager\EnaioAgent\agent.log` geführt. Startfehler vor erfolgreicher Kopplung können naturgemäß nicht an den Server übertragen werden; in diesem Fall die lokale Logdatei prüfen. Zugangsdaten und Tokens werden vor der Server-Speicherung maskiert.

## enaio-Objektdefinition

Die technischen Namen sind installationsabhängig und werden einmalig vom Administrator unter **Verwaltung → enaio-Einstellungen** hinterlegt:

- enaio-Schrankname
- technischer Registertyp
- technisches Register-Namensfeld (interner Feldname für den Namen der Besprechungsreihe)
- technischer Dokumenttyp für das Protokoll-PDF

Der Dokumenttyp wird ebenfalls zentral konfiguriert. Der Agent ermittelt die zugehörige Typ-ID direkt aus der enaio-Objektdefinition. Fehlen diese Angaben oder stimmen technische Namen nicht, verweigert er die Ablage statt einen falschen Zielort zu verwenden. Register-Neuanlage und Dokumentablage erfolgen ausschließlich über die bestätigungspflichtige enaio-Indexdatenmaske.

## Build

`dotnet publish -c Release -r win-x64 --self-contained false`

Die COM-Integration muss auf einem Arbeitsplatz mit der konkreten enaio-11.x-Installation getestet werden; GitHub-CI kann diese lokale Integration nicht simulieren.
