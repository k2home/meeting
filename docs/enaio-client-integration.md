# enaio classic client integration

## Architektur ohne URL-Protokoll

Jede Person koppelt einen eigenen Windows-Agenten an ihr Meeting-Manager-Konto. Der Agent läuft im interaktiven Windows-Benutzerkonto und steuert ausschließlich den dort geöffneten enaio classic Client über dessen COM-Schnittstelle. Der Agent fragt den Server per HTTPS ab; es wird kein eigenes URL-Protokoll registriert.

Der zentrale Ablage-Stammordner wird einmalig von einem Administrator unter **Verwaltung → enaio-Einstellungen** konfiguriert. Die technische Schrank-/Registerdefinition wird dort ebenfalls hinterlegt. Protokollaufträge werden nur an den Agenten des angemeldeten Meeting-Manager-Benutzers ausgeliefert.

## Kopplung und Sicherheit

1. Die Person öffnet **Konto → Arbeitsplatz mit enaio verbinden**. Der Server erzeugt einen zehn Minuten gültigen Einmal-Kopplungscode.
2. Der lokale Agent wird mit `MeetingManager.EnaioAgent.exe pair https://<meeting-manager> <code>` gekoppelt.
3. Der Server gibt ein zufälliges Gerätetoken zurück. Der Agent speichert es mit Windows DPAPI im Profil des aktuellen Benutzers.
4. Der Agent fragt `GET /enaio/agent/jobs/next/` alle fünf Sekunden mit HTTP-Bearer-Authentifizierung ab.
5. Geräte sind jeweils einem Meeting-Manager-Benutzer zugeordnet. Ein Gerät kann keine Aufträge anderer Benutzer abrufen.

## Auftragsablauf

- **Zentralen Stammordner auswählen:** Der Administrator startet die Auswahl in Verwaltung. Der Agent nutzt `GetAllOpenFolders()`, startet `SelectObject()` aus einem aktuell geöffneten Ordner/Register und liest die Auswahl mit `GetSelectedObject()`, `GetObjectName()` und `GetObjectPath()`. Die Daten werden über den authentifizierten Agent-Endpunkt gespeichert.
- **Protokoll ablegen:** Der Agent lädt das PDF über einen benutzerspezifisch autorisierten Endpunkt herunter. Er sucht ein Register mit dem Besprechungsreihennamen direkt unter dem zentralen Stammordner, legt es bei Bedarf mit `InsertIntoRegisterS()` an und importiert das PDF mit `InsertIntoDocumentS()`. Der Dokumenttyp ist exakt **Standard**. Erst nach erfolgreichem COM-Import bestätigt der Agent die Ablage.
- Der Browser wartet auf den Auftragsstatus. Er öffnet keine URL und startet kein Protokollhandler-Programm.

## Einmalige enaio-Objektdefinition

Die Objektdefinitionen sind installationsabhängig. Ein Administrator muss unter **Verwaltung → enaio-Einstellungen** diese technischen Angaben aus der enaio-Objektdefinition übernehmen:

- enaio-Schrankname
- technischer Registertyp
- technisches Register-Namensfeld (Feld für den Besprechungsreihennamen)

Ohne diese Angaben wird die Ablage nicht ausgeführt. Es wird weder ein anderer Dokumenttyp gewählt noch ein unbestimmtes Feld geraten.

## Windows-Agent bauen

Voraussetzung: Windows x64 und .NET 8 Desktop Runtime.

`dotnet publish desktop/enaio-agent/MeetingManager.EnaioAgent.csproj -c Release -r win-x64 --self-contained false`

Die lokale COM-Integration muss gegen die installierte enaio-classic-11.x-Version getestet werden. Der Agent verwendet die dokumentierten Client-COM-Methoden; GitHub-CI kann die COM-Serverinstanz nicht simulieren.
