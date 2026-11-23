using System.Net.Http.Headers;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Windows.Forms;

internal static class Program
{
    private static readonly string DataDirectory = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "MeetingManager", "EnaioAgent");
    private static readonly string CredentialsFile = Path.Combine(DataDirectory, "credentials.bin");
    private static readonly JsonSerializerOptions JsonOptions = new() { PropertyNameCaseInsensitive = true };
    private static readonly string LogFile = Path.Combine(DataDirectory, "agent.log");

    [STAThread]
    private static int Main(string[] args)
    {
        try
        {
            LogLocal("INFO", "Agent-Prozess gestartet. Windows-Benutzer: " + Environment.UserName + "; Betriebssystem: " + Environment.OSVersion + "; Arbeitsverzeichnis: " + Environment.CurrentDirectory);
            LogLocal("INFO", "Lokales Diagnoseprotokoll: " + LogFile);
            if (args.Length == 3 && args[0].Equals("pair", StringComparison.OrdinalIgnoreCase))
            {
                Pair(args[1], args[2]);
                Console.WriteLine("Dieser Arbeitsplatz ist jetzt mit dem Meeting-Manager-Konto verbunden.");
                Console.WriteLine("Zum Start des Hintergrundbetriebs dieses Programm ohne Argumente ausführen.");
                return 0;
            }
            if (args.Length != 0)
            {
                Console.Error.WriteLine("Verwendung: MeetingManager.EnaioAgent.exe pair <Meeting-Manager-URL> <Kopplungscode>");
                return 2;
            }

            LogLocal("INFO", "Lese lokale Agent-Kopplung und Zugangsdaten.");
            var credentials = LoadCredentials();
            LogLocal("INFO", "Zugangsdaten geladen. Stelle Verbindung zum Meeting Manager her: " + new Uri(credentials.BaseUrl).Host);
            using var http = new HttpClient { BaseAddress = new Uri(credentials.BaseUrl.TrimEnd('/') + "/"), Timeout = TimeSpan.FromSeconds(45) };
            http.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", credentials.DeviceToken);
            Log(http, "INFO", "enaio-Agent gestartet. COM-Aufrufe laufen auf dem STA-Hauptthread.");
            while (true)
            {
                try
                {
                    using var response = http.GetAsync("enaio/agent/jobs/next/").GetAwaiter().GetResult();
                    if (response.StatusCode == System.Net.HttpStatusCode.Conflict)
                        Log(http, "ERROR", "Server lehnt Agent-Abfrage ab (HTTP 409): " + response.Content.ReadAsStringAsync().GetAwaiter().GetResult());
                    else
                    {
                        response.EnsureSuccessStatusCode();
                        using var doc = JsonDocument.Parse(response.Content.ReadAsStringAsync().GetAwaiter().GetResult());
                        if (doc.RootElement.TryGetProperty("job", out var job) && job.ValueKind == JsonValueKind.Object)
                            ProcessJob(http, job);
                    }
                }
                catch (HttpRequestException ex) { Log(http, "ERROR", "Verbindungsfehler: " + ex); }
                catch (COMException ex) { Log(http, "ERROR", "enaio-COM-Fehler: " + ex); }
                catch (Exception ex) { Log(http, "ERROR", "Auftragsfehler: " + ex); }
                Thread.Sleep(TimeSpan.FromSeconds(5));
            }
        }
        catch (Exception ex) { LogLocal("ERROR", "Agent konnte nicht gestartet werden: " + ex); return 1; }
    }

    private static void Pair(string baseUrl, string code)
    {
        if (!Uri.TryCreate(baseUrl, UriKind.Absolute, out var uri) || uri.Scheme != Uri.UriSchemeHttps)
            throw new InvalidOperationException("Bitte eine gültige HTTPS-Adresse des Meeting Managers angeben.");
        LogLocal("INFO", "Starte Kopplung mit Meeting Manager: " + uri.Host);
        using var http = new HttpClient { BaseAddress = new Uri(uri.ToString().TrimEnd('/') + "/") };
        var body = JsonSerializer.Serialize(new { pairing_code = code, device_name = Environment.MachineName });
        using var response = http.PostAsync("enaio/agent/register/", new StringContent(body, Encoding.UTF8, "application/json")).GetAwaiter().GetResult();
        response.EnsureSuccessStatusCode();
        using var doc = JsonDocument.Parse(response.Content.ReadAsStringAsync().GetAwaiter().GetResult());
        var token = doc.RootElement.GetProperty("device_token").GetString() ?? throw new InvalidOperationException("Der Server hat kein Gerätetoken geliefert.");
        Directory.CreateDirectory(DataDirectory);
        var plain = JsonSerializer.SerializeToUtf8Bytes(new AgentCredentials(uri.ToString(), token));
        try { File.WriteAllBytes(CredentialsFile, ProtectedData.Protect(plain, null, DataProtectionScope.CurrentUser)); }
        finally { CryptographicOperations.ZeroMemory(plain); }
        LogLocal("INFO", "Kopplung erfolgreich. Zugangsdaten wurden DPAPI-verschlüsselt gespeichert.");
    }

    private static void Log(HttpClient http, string level, string message)
    {
        LogLocal(level, message);
        try
        {
            var payload = JsonSerializer.Serialize(new { level, message = message.Length > 3900 ? message[..3900] : message });
            using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(5));
            using var content = new StringContent(payload, Encoding.UTF8, "application/json");
            using var response = http.PostAsync("enaio/agent/logs/write/", content, timeout.Token).GetAwaiter().GetResult();
            response.EnsureSuccessStatusCode();
        }
        catch (Exception ex)
        {
            LogLocal("WARNING", "Logeintrag konnte nicht an den Meeting Manager übertragen werden: " + ex.Message);
        }
    }

    private static void LogLocal(string level, string message)
    {
        try
        {
            Directory.CreateDirectory(DataDirectory);
            if (File.Exists(LogFile) && new FileInfo(LogFile).Length > 2 * 1024 * 1024)
                File.WriteAllText(LogFile, "");
            var line = $"[{DateTimeOffset.Now:O}] [{level}] {message}{Environment.NewLine}";
            File.AppendAllText(LogFile, line, Encoding.UTF8);
            if (level == "ERROR" || level == "WARNING") Console.Error.WriteLine(line);
            else Console.WriteLine(line);
        }
        catch (Exception ex)
        {
            try { Console.Error.WriteLine("Lokales Agent-Log konnte nicht geschrieben werden: " + ex); } catch { }
        }
    }

    private static AgentCredentials LoadCredentials()
    {
        if (!File.Exists(CredentialsFile))
            throw new InvalidOperationException("Dieser Arbeitsplatz ist noch nicht gekoppelt. Zuerst 'pair <URL> <Kopplungscode>' ausführen.");
        var plain = ProtectedData.Unprotect(File.ReadAllBytes(CredentialsFile), null, DataProtectionScope.CurrentUser);
        try { return JsonSerializer.Deserialize<AgentCredentials>(plain, JsonOptions) ?? throw new InvalidOperationException("Die gespeicherten Agent-Zugangsdaten sind ungültig."); }
        finally { CryptographicOperations.ZeroMemory(plain); }
    }

    private static void ProcessJob(HttpClient http, JsonElement job)
    {
        try
        {
            var kind = job.GetProperty("kind").GetString();
            Log(http, "INFO", "Auftrag empfangen: " + kind + ".");
            var leaseToken = job.GetProperty("lease_token").GetString() ?? "";
            var statusUrl = job.GetProperty("status_url").GetString() ?? throw new InvalidOperationException("Der Auftrag enthält keine Statusadresse.");
            if (kind == "select_root_folder")
            {
                var selection = EnaioClient.SelectRootFolder(() => IsJobActive(http, statusUrl, leaseToken));
                using var response = http.PostAsync(job.GetProperty("complete_url").GetString(), new StringContent(JsonSerializer.Serialize(new { selection.folder_id, selection.folder_type, selection.folder_name, selection.folder_path, lease_token = job.GetProperty("lease_token").GetString() }), Encoding.UTF8, "application/json")).GetAwaiter().GetResult();
                response.EnsureSuccessStatusCode();
                Log(http, "INFO", "Zentraler enaio-Stammordner wurde erfolgreich übermittelt.");
            }
            else if (kind == "file_protocol")
            {
                if (!IsJobActive(http, statusUrl, leaseToken))
                    throw new InvalidOperationException("Der Ablageauftrag wurde abgebrochen oder ist abgelaufen.");
                var pdf = http.GetByteArrayAsync(job.GetProperty("pdf_url").GetString()).GetAwaiter().GetResult();
                var tempFile = Path.Combine(Path.GetTempPath(), "MeetingManager-" + Guid.NewGuid().ToString("N") + ".pdf");
                try
                {
                    File.WriteAllBytes(tempFile, pdf);
                    if (!IsJobActive(http, statusUrl, leaseToken))
                        throw new InvalidOperationException("Der Ablageauftrag wurde vor dem enaio-Import abgebrochen oder ist abgelaufen.");
                    var result = EnaioClient.FileProtocol(job.GetProperty("filing"), tempFile);
                    var payload = JsonSerializer.Serialize(new { uploaded = true, object_id = result.ObjectId, object_type = result.ObjectType, display_path = result.Path, lease_token = job.GetProperty("lease_token").GetString() });
                    using var response = http.PostAsync(job.GetProperty("complete_url").GetString(), new StringContent(payload, Encoding.UTF8, "application/json")).GetAwaiter().GetResult();
                    response.EnsureSuccessStatusCode();
                    Log(http, "INFO", "Protokoll wurde in enaio abgelegt: " + result.Path);
                }
                finally { try { File.Delete(tempFile); } catch { } }
            }
        }
        catch (Exception ex)
        {
            Log(http, "ERROR", "Auftragsverarbeitung fehlgeschlagen: " + ex);
            try
            {
                var payload = JsonSerializer.Serialize(new { lease_token = job.GetProperty("lease_token").GetString(), error = ex.Message });
                using var response = http.PostAsync(job.GetProperty("fail_url").GetString(), new StringContent(payload, Encoding.UTF8, "application/json")).GetAwaiter().GetResult();
                response.EnsureSuccessStatusCode();
            }
            catch (Exception reportError) { Log(http, "ERROR", "Fehlerrückmeldung an den Server fehlgeschlagen: " + reportError); }
            throw;
        }
    }

    private static bool IsJobActive(HttpClient http, string statusUrl, string leaseToken)
    {
        var separator = statusUrl.Contains('?') ? "&" : "?";
        using var response = http.GetAsync(statusUrl + separator + "lease=" + Uri.EscapeDataString(leaseToken)).GetAwaiter().GetResult();
        response.EnsureSuccessStatusCode();
        using var document = JsonDocument.Parse(response.Content.ReadAsStringAsync().GetAwaiter().GetResult());
        return document.RootElement.TryGetProperty("active", out var active) && active.GetBoolean();
    }

    private sealed record AgentCredentials(string BaseUrl, string DeviceToken);
}

internal sealed record SelectedFolder(string folder_id, int folder_type, string folder_name, string folder_path);
internal sealed record FilingResult(string ObjectId, int ObjectType, string Path);

internal static class EnaioClient
{
    [DllImport("oleaut32.dll", PreserveSig = true)]
    private static extern int GetActiveObject(ref Guid rclsid, IntPtr reserved, [MarshalAs(UnmanagedType.IUnknown)] out object instance);

    private static dynamic Connect()
    {
        var type = Type.GetTypeFromProgID("optimal_AS.Application")
            ?? throw new InvalidOperationException("enaio classic ist nicht installiert oder die COM-Schnittstelle ist nicht registriert.");
        var clsid = type.GUID;
        var hr = GetActiveObject(ref clsid, IntPtr.Zero, out var instance);
        if (hr < 0 || instance is null)
            throw new InvalidOperationException("Es wurde keine bereits laufende enaio-COM-Instanz gefunden. Bitte enaio classic im selben Windows-Benutzerkonto öffnen und erneut versuchen. Es wird absichtlich keine neue enaio-Instanz gestartet.");
        return instance;
    }

    private sealed record OpenFolderCandidate(long Id, int Type, string Name, string Path)
    {
        public string Label => string.IsNullOrWhiteSpace(Path) ? Name + " (ID " + Id + ")" : Path + " (ID " + Id + ")";
    }

    public static SelectedFolder SelectRootFolder(Func<bool> isJobActive)
    {
        dynamic app = Connect();
        try
        {
            var opened = Convert.ToString(app.GetAllOpenFolders()) ?? "";
            var candidates = new List<OpenFolderCandidate>();
            foreach (var item in opened.Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
            {
                var parts = item.Split(',');
                if (parts.Length != 2 || !long.TryParse(parts[0], out var candidateId) || !int.TryParse(parts[1], out var candidateType))
                    continue;

                object candidateName = "";
                var nameResult = Convert.ToInt32(app.GetObjectName(candidateId, ref candidateName));
                var name = nameResult == 0 ? Convert.ToString(candidateName) ?? "" : "";
                object candidatePath = "";
                var pathResult = Convert.ToInt32(app.GetObjectPatternPath(candidateId, candidateType, ref candidatePath));
                var readablePath = pathResult == 0 ? Convert.ToString(candidatePath) ?? "" : "";
                if (string.IsNullOrWhiteSpace(readablePath))
                    readablePath = Convert.ToString(app.GetObjectPath(candidateId, candidateType)) ?? "";
                candidates.Add(new OpenFolderCandidate(candidateId, candidateType,
                    string.IsNullOrWhiteSpace(name) ? "Geöffneter enaio-Ordner" : name, readablePath));
            }

            if (candidates.Count == 0)
                throw new InvalidOperationException("enaio meldet keine geöffneten Ordner oder Register. Bitte öffnen Sie zuerst den gewünschten Ablageordner in enaio.");

            var startFolder = candidates.Count == 1 ? candidates[0] : ChooseOpenFolder(candidates);
            if (!isJobActive())
                throw new OperationCanceledException("Die Ordnerauswahl wurde im Meeting Manager abgebrochen oder ist abgelaufen.");

            LogLocal("INFO", "enaio-Auswahl startet im geöffneten Kontext: " + startFolder.Label);
            var started = Convert.ToInt32(app.SelectObject(startFolder.Id, startFolder.Type, false, "Ablageordner in enaio auswählen"));
            if (started != 1)
                throw new InvalidOperationException("enaio konnte die Objektauswahl nicht öffnen (Code " + started + "): " + Convert.ToString(app.GetLastError()));

            object selected = "";
            var result = 1;
            var elapsed = Stopwatch.StartNew();
            var nextLeaseCheck = TimeSpan.Zero;
            while (result == 1)
            {
                Application.DoEvents();
                if (elapsed.Elapsed >= TimeSpan.FromMinutes(4))
                    throw new TimeoutException("Die enaio-Ordnerauswahl wurde nach vier Minuten ohne Auswahl beendet.");
                if (elapsed.Elapsed >= nextLeaseCheck)
                {
                    if (!isJobActive())
                        throw new OperationCanceledException("Die enaio-Ordnerauswahl wurde im Meeting Manager abgebrochen oder ist abgelaufen.");
                    nextLeaseCheck = elapsed.Elapsed + TimeSpan.FromSeconds(2);
                }
                result = Convert.ToInt32(app.GetSelectedObject(ref selected));
                Thread.Sleep(200);
            }
            if (result != 3)
                throw new InvalidOperationException("Die enaio-Ordnerauswahl wurde abgebrochen (Code " + result + ").");

            var chosen = Convert.ToString(selected)?.Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries).FirstOrDefault()
                ?? throw new InvalidOperationException("enaio hat kein ausgewähltes Objekt zurückgegeben.");
            var selectedParts = chosen.Split(',');
            if (selectedParts.Length != 2 || !long.TryParse(selectedParts[0], out var id) || !int.TryParse(selectedParts[1], out var objectType))
                throw new InvalidOperationException("enaio hat eine ungültige Ordner-ID zurückgegeben.");

            object name = "";
            if (Convert.ToInt32(app.GetObjectName(id, ref name)) != 0)
                throw new InvalidOperationException("Der ausgewählte Ordnername konnte nicht aus enaio gelesen werden: " + Convert.ToString(app.GetLastError()));
            object readablePath = "";
            var pathResult = Convert.ToInt32(app.GetObjectPatternPath(id, objectType, ref readablePath));
            if (pathResult != 0)
                throw new InvalidOperationException("Der lesbare enaio-Ordnerpfad konnte nicht ermittelt werden: " + Convert.ToString(app.GetLastError()));
            var path = Convert.ToString(readablePath);
            if (string.IsNullOrWhiteSpace(path))
                path = Convert.ToString(app.GetObjectPath(id, objectType)) ?? "";
            if (string.IsNullOrWhiteSpace(path))
                throw new InvalidOperationException("enaio hat für den ausgewählten Ordner keinen vollständigen Pfad geliefert.");

            LogLocal("INFO", "enaio-Zielordner bestätigt: " + path + " (ID " + id + ", Typ " + objectType + ").");
            return new SelectedFolder(id.ToString(), objectType, Convert.ToString(name) ?? "", path);
        }
        finally { try { Marshal.FinalReleaseComObject((object)app); } catch { } }
    }

    private static OpenFolderCandidate ChooseOpenFolder(List<OpenFolderCandidate> candidates)
    {
        using var dialog = new Form
        {
            Text = "Geöffneten enaio-Kontext auswählen",
            Width = 720,
            Height = 190,
            StartPosition = FormStartPosition.CenterScreen,
            FormBorderStyle = FormBorderStyle.FixedDialog,
            MaximizeBox = false,
            MinimizeBox = false,
            ShowInTaskbar = true
        };
        var label = new Label
        {
            Text = "In enaio sind mehrere Ordner/Register geöffnet. Von welchem geöffneten Ort soll die Auswahl gestartet werden?",
            Left = 16,
            Top = 16,
            Width = 670,
            Height = 42
        };
        var combo = new ComboBox
        {
            Left = 16,
            Top = 64,
            Width = 670,
            DropDownStyle = ComboBoxStyle.DropDownList
        };
        combo.DataSource = candidates;
        combo.DisplayMember = nameof(OpenFolderCandidate.Label);
        combo.SelectedIndex = 0;
        var ok = new Button { Text = "Weiter in enaio auswählen", Left = 420, Top = 108, Width = 170, DialogResult = DialogResult.OK };
        var cancel = new Button { Text = "Abbrechen", Left = 596, Top = 108, Width = 90, DialogResult = DialogResult.Cancel };
        dialog.Controls.AddRange(new Control[] { label, combo, ok, cancel });
        dialog.AcceptButton = ok;
        dialog.CancelButton = cancel;
        if (dialog.ShowDialog() != DialogResult.OK || combo.SelectedItem is not OpenFolderCandidate selected)
            throw new OperationCanceledException("Die Auswahl des geöffneten enaio-Kontexts wurde abgebrochen.");
        return selected;
    }

    private static int ResolveObjectType(string definitions, string requestedName, string kind)
    {
        foreach (var entry in (definitions ?? "").Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
        {
            var parts = entry.Split(',');
            if (parts.Length == 2 && parts[0].Trim().Equals(requestedName.Trim(), StringComparison.OrdinalIgnoreCase)
                && int.TryParse(parts[1].Trim(), out var objectType))
                return objectType;
        }
        throw new InvalidOperationException("Der konfigurierte " + kind + " '" + requestedName + "' wurde im enaio-Schrank nicht gefunden. Bitte den technischen Namen unter Verwaltung → enaio-Einstellungen prüfen.");
    }

    private static string CreateHandoffFile(string content)
    {
        var path = Path.Combine(Path.GetTempPath(), "MeetingManager-enaio-" + Guid.NewGuid().ToString("N") + ".ini");
        File.WriteAllText(path, content, new UTF8Encoding(false));
        return path;
    }

    public static FilingResult FileProtocol(JsonElement filing, string pdfPath)
    {
        var registerType = filing.GetProperty("register_type_name").GetString() ?? "";
        var registerNameField = filing.GetProperty("register_name_field").GetString() ?? "";
        var archiveName = filing.GetProperty("archive_name").GetString() ?? "";
        var documentType = filing.GetProperty("document_type").GetString() ?? "Standard";
        if (string.IsNullOrWhiteSpace(registerType) || string.IsNullOrWhiteSpace(registerNameField) || string.IsNullOrWhiteSpace(archiveName))
            throw new InvalidOperationException("Die zentrale enaio-Objektdefinition ist unvollständig. Bitte Schrankname, Registertyp und Register-Namensfeld unter Verwaltung → enaio-Einstellungen hinterlegen.");
        if (!File.Exists(pdfPath))
            throw new FileNotFoundException("Das zu übergebende Protokoll-PDF wurde nicht gefunden.", pdfPath);

        dynamic app = Connect();
        string? registerHandoff = null;
        string? documentHandoff = null;
        try
        {
            var rootId = Convert.ToInt64(filing.GetProperty("root_folder_id").GetString());
            var series = filing.GetProperty("register_name").GetString() ?? "";
            var registerTypeId = ResolveObjectType(Convert.ToString(app.GetRegTypeFromArchive(archiveName)) ?? "", registerType, "Registertyp");
            var documentTypeId = ResolveObjectType(Convert.ToString(app.GetDocTypesFromArchive(archiveName)) ?? "", documentType, "Dokumenttyp");

            var query = "[ANFRAGE]\r\nSCHRANK=" + Ini(archiveName) + "\r\nREGISTER=" + Ini(registerType) +
                "\r\nKLAUSEL1=" + Ini(registerType) + "@" + Ini(registerNameField) + "=" + Ini(series) +
                "\r\nAUSDRUCK1=" + Ini(registerType) + "@1121^1^" + rootId + "~0~1122^1^0\r\nDATENFELDER=0\r\nDATENHEADER=0\r\nANFRAGEFENSTER=0\r\n";
            var resultFile = Convert.ToString(app.StartRegRequest(query)) ?? "";
            var registerId = 0L;
            if (string.IsNullOrWhiteSpace(resultFile) || resultFile == "READY" || !File.Exists(resultFile))
                throw new InvalidOperationException("Die Registersuche in enaio konnte nicht ausgeführt werden: " + Convert.ToString(app.GetLastError()));
            var pair = File.ReadLines(resultFile).FirstOrDefault(line => !string.IsNullOrWhiteSpace(line))?.Split(',');
            if (pair?.Length == 2)
                long.TryParse(pair[0].Trim(), out registerId);

            if (registerId == 0)
            {
                LogLocal("INFO", "Das Register '" + series + "' fehlt. enaio öffnet jetzt die Indexdatenmaske zur bestätigten Registeranlage.");
                registerHandoff = CreateHandoffFile("[Data]\r\nFeld0=" + Ini(registerNameField) + "=" + Ini(series) + "\r\n");
                object newRegisterId = 0;
                var registerCode = Convert.ToInt32(app.InsertNewDMSObject(registerTypeId, rootId, registerHandoff, ref newRegisterId));
                if (registerCode != 0)
                    throw new InvalidOperationException(registerCode == -123
                        ? "Die Registeranlage wurde in enaio abgebrochen."
                        : "enaio konnte die Registermaske nicht erfolgreich abschließen (Code " + registerCode + "): " + Convert.ToString(app.GetLastError()));
                if (!long.TryParse(Convert.ToString(newRegisterId), out registerId) || registerId <= 0)
                    throw new InvalidOperationException("enaio hat die bestätigte Registeranlage nicht mit einer gültigen Register-ID quittiert.");
                LogLocal("INFO", "Register wurde vom Benutzer in enaio bestätigt (ID " + registerId + ").");
            }

            documentHandoff = CreateHandoffFile("[Data]\r\n[Files]\r\nFile0=" + pdfPath.Replace("\\", "/") + "\r\n");
            LogLocal("INFO", "enaio öffnet jetzt die Indexdatenmaske zur bestätigten Ablage des Protokolls in Register " + series + ".");
            object newDocumentId = 0;
            var documentCode = Convert.ToInt32(app.InsertNewDMSObject(documentTypeId, registerId, documentHandoff, ref newDocumentId));
            if (documentCode != 0)
                throw new InvalidOperationException(documentCode == -123
                    ? "Die Dokumentablage wurde in enaio vom Benutzer abgebrochen."
                    : "enaio konnte die Dokumentmaske nicht erfolgreich abschließen (Code " + documentCode + "): " + Convert.ToString(app.GetLastError()));
            if (!long.TryParse(Convert.ToString(newDocumentId), out var documentId) || documentId <= 0)
                throw new InvalidOperationException("enaio hat die bestätigte Dokumentablage nicht mit einer gültigen Dokument-ID quittiert.");

            var path = Convert.ToString(app.GetObjectPath(documentId, documentTypeId)) ?? "";
            LogLocal("INFO", "Protokollablage in enaio bestätigt: " + path + " (Dokument-ID " + documentId + ").");
            return new FilingResult(documentId.ToString(), documentTypeId, path);
        }
        finally
        {
            if (registerHandoff is not null) { try { File.Delete(registerHandoff); } catch { } }
            if (documentHandoff is not null) { try { File.Delete(documentHandoff); } catch { } }
            try { Marshal.FinalReleaseComObject((object)app); } catch { }
        }
    }

    private static string Ini(string value) => value.Replace("\r", " ").Replace("\n", " ").Trim();
}
