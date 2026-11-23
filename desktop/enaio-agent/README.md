# Meeting Manager – enaio Windows-Agent

Der Agent läuft im angemeldeten Windows-Benutzerkonto, verwendet den dort geöffneten enaio-classic-Client über COM und fragt Aufträge des zugehörigen Meeting-Manager-Kontos über HTTPS ab. Es wird kein URL-Protokoll registriert.

## Voraussetzungen

- Windows x64 und .NET 8 Desktop Runtime
- enaio classic 11.x installiert und im Benutzerkonto geöffnet
- HTTPS-Zugriff auf den Meeting Manager

## Koppeln und starten

1. Im Meeting Manager unter **Konto** auf **Arbeitsplatz mit enaio verbinden** klicken.
2. Innerhalb von zehn Minuten ausführen: `MeetingManager.EnaioAgent.exe pair https://meeting-manager.example <Kopplungscode>`
3. Danach `MeetingManager.EnaioAgent.exe` ohne Argumente starten. Für automatischen Start eine Verknüpfung im Autostart-Ordner dieses Windows-Benutzers ablegen.

Das Gerätetoken wird mit Windows DPAPI für den aktuellen Benutzer verschlüsselt gespeichert. Der Kopplungscode ist zehn Minuten gültig und einmalig.

## enaio-Objektdefinition

Die technischen Namen sind installationsabhängig und werden einmalig vom Administrator unter **Verwaltung → enaio-Einstellungen** hinterlegt:

- enaio-Schrankname
- technischer Registertyp
- technisches Register-Namensfeld (interner Feldname für den Namen der Besprechungsreihe)

Der Dokumenttyp ist serverseitig fest auf **Standard** gesetzt. Fehlen diese Angaben, verweigert der Agent die Ablage statt einen falschen Zielort zu verwenden.

## Build

`dotnet publish -c Release -r win-x64 --self-contained false`

Die COM-Integration muss auf einem Arbeitsplatz mit der konkreten enaio-11.x-Installation getestet werden; GitHub-CI kann diese lokale Integration nicht simulieren.
