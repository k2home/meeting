# enaio classic client integration

This branch adds the Django-side transfer contract for the Windows-side enaio client adapter.

## Client API facts (enaio client 11.10)

- `GetAllOpenFolders()` returns IDs and object types of folders/registers currently open in the client.
- `SelectObject(objectId, objectType, false, title)` opens the selection hit list from that currently open location.
- `GetSelectedObject(...)` returns the selected object ID/type.
- `GetObjectPath(objectId, objectType)` returns the folder/register hierarchy.
- `InsertIntoDocumentS(...)` imports a PDF but requires the configured cabinet and document type. The document type is installation-specific and must not be guessed.

The client adapter must start from one of the currently open folders returned by `GetAllOpenFolders()`, let the user choose the destination, and only then call the transfer completion endpoint after the import has succeeded.

## Django transfer protocol

1. An authenticated protocol page posts to `meeting/<id>/protocol/enaio/start/`.
2. Django returns a one-time `meetingmanager-enaio://transfer/<token>` launch URI. The token expires after ten minutes; only its SHA-256 digest is stored. The adapter retrieves the filing metadata from `enaio/transfer/<token>/details/` using the token.
3. The registered Windows client adapter receives the token, downloads `enaio/transfer/<token>/pdf/`, selects the target in the open enaio cabinet, and imports the PDF through the enaio client API.
4. Only after a successful import, the adapter posts JSON to `enaio/transfer/<token>/complete/`:
   `{"uploaded":true,"object_id":"...","object_type":123,"display_path":"...","display_name":"..."}`
5. Django stores the selected destination as the user's personal default. A token can be completed only once.

The token is a short-lived bearer credential. The adapter must not log it or persist it beyond the current handoff.

## Filing rules and client adapter contract

- The central root folder is configured by an administrator in **Verwaltung → enaio-Einstellungen**. Django exposes its folder ID, optional object type and display path through the token-protected `details/` endpoint.
- The adapter must use the exact document type **Standard**. Resolve its configured internal type/main type for the target archive using the enaio client API; if no matching Standard type is available, stop with a clear error. Do not substitute another document type.
- The register name is the meeting series name. Find an existing register with that name directly under the configured root folder; if none exists, create a register with that name and use the newly returned register ID. Do not create duplicate registers when a matching one already exists.
- Place the PDF inside that register and report the resulting register ID/type and readable path to the completion endpoint. The legacy per-user filing target is no longer used to choose the destination.

The meetingmanager-enaio URL scheme must be registered on each workstation. The handler accepts only the transfer URI format, downloads the one-time PDF, applies the filing rules above, and reports success only after the import has completed. The token must not be logged or retained after handoff.

The Django-side transfer and administration changes do not themselves install the Windows client adapter. The actual client-side register lookup/creation and COM import still require the workstation adapter and must be verified against the installed enaio classic 11.x client API.


## Selecting the central filing folder from enaio

The administration page supports both manual entry of the folder ID and selection from the open enaio classic client. The folder name and readable path are returned by the client and shown read-only in Django.

1. The authenticated administration page sends a CSRF-protected POST to `verwaltung/enaio/auswahl/start/`. Django creates a five-minute, one-time selection token and returns a `meetingmanager-enaio://select-folder/<token>` launch URI plus a browser status URL.
2. The workstation adapter handles the URI and requests `enaio/folder-selection/<token>/details/`. The response contains the callback URL. The adapter uses `GetAllOpenFolders()` to start from folders/registers currently open in the client and lets the administrator select a folder (using `SelectObject` / `GetSelectedObject` as appropriate).
3. The adapter reads the selected folder's ID, object type, name and readable path from the enaio client API, then POSTs JSON to the supplied callback URL: `{"folder_id":"...","folder_type":123,"folder_name":"...","folder_path":"..."}`.
4. Django validates the one-time token and saves the ID, object type, name and path as the central filing destination. The administration page polls its authenticated status endpoint and reloads when selection is complete.

The token is a short-lived bearer credential: do not log it or retain it after handoff. Manual entry of the folder ID remains available; in that case the name/path display stays empty until the folder is selected from enaio.
