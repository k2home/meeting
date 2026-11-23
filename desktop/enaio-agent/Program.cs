using System.Net.Http.Headers;
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

    [STAThread]
    private static int Main(string[] args)
    {
        try
        {
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

            var credentials = LoadCredentials();
            using var http = new HttpClient { BaseAddress = new Uri(credentials.BaseUrl.TrimEnd('/') + "/"), Timeout = TimeSpan.FromSeconds(45) };
            http.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", credentials.DeviceToken);
            Console.WriteLine("enaio-Agent läuft. COM-Aufrufe werden auf diesem STA-Thread ausgeführt. Beenden mit Strg+C.");
            while (true)
            {
                try
                {
                    using var response = http.GetAsync("enaio/agent/jobs/next/").GetAwaiter().GetResult();
                    if (response.StatusCode == System.Net.HttpStatusCode.Conflict)
                        Console.Error.WriteLine(response.Content.ReadAsStringAsync().GetAwaiter().GetResult());
                    else
                    {
                        response.EnsureSuccessStatusCode();
                        using var doc = JsonDocument.Parse(response.Content.ReadAsStringAsync().GetAwaiter().GetResult());
                        if (doc.RootElement.TryGetProperty("job", out var job) && job.ValueKind == JsonValueKind.Object)
                            ProcessJob(http, job);
                    }
                }
                catch (HttpRequestException ex) { Console.Error.WriteLine("Verbindungsfehler: " + ex.Message); }
                catch (COMException ex) { Console.Error.WriteLine("enaio-COM-Fehler: " + ex.Message); }
                catch (Exception ex) { Console.Error.WriteLine("Auftragsfehler: " + ex.Message); }
                Thread.Sleep(TimeSpan.FromSeconds(5));
            }
        }
        catch (Exception ex) { Console.Error.WriteLine(ex.Message); return 1; }
    }

    private static void Pair(string baseUrl, string code)
    {
        if (!Uri.TryCreate(baseUrl, UriKind.Absolute, out var uri) || uri.Scheme != Uri.UriSchemeHttps)
            throw new InvalidOperationException("Bitte eine gültige HTTPS-Adresse des Meeting Managers angeben.");
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
        var kind = job.GetProperty("kind").GetString();
        if (kind == "select_root_folder")
        {
            var selection = EnaioClient.SelectRootFolder();
            using var response = http.PostAsync(job.GetProperty("complete_url").GetString(), new StringContent(JsonSerializer.Serialize(new { selection.folder_id, selection.folder_type, selection.folder_name, selection.folder_path, lease_token = job.GetProperty("lease_token").GetString() }), Encoding.UTF8, "application/json")).GetAwaiter().GetResult();
            response.EnsureSuccessStatusCode();
            Console.WriteLine("Zentraler enaio-Stammordner wurde übermittelt.");
        }
        else if (kind == "file_protocol")
        {
            var pdf = http.GetByteArrayAsync(job.GetProperty("pdf_url").GetString()).GetAwaiter().GetResult();
            var tempFile = Path.Combine(Path.GetTempPath(), "MeetingManager-" + Guid.NewGuid().ToString("N") + ".pdf");
            try
            {
                File.WriteAllBytes(tempFile, pdf);
                var result = EnaioClient.FileProtocol(job.GetProperty("filing"), tempFile);
                var payload = JsonSerializer.Serialize(new { uploaded = true, object_id = result.ObjectId, object_type = result.ObjectType, display_path = result.Path, lease_token = job.GetProperty("lease_token").GetString() });
                using var response = http.PostAsync(job.GetProperty("complete_url").GetString(), new StringContent(payload, Encoding.UTF8, "application/json")).GetAwaiter().GetResult();
                response.EnsureSuccessStatusCode();
                Console.WriteLine("Protokoll wurde in enaio abgelegt: " + result.Path);
            }
            finally { try { File.Delete(tempFile); } catch { } }
        }
    }

    private sealed record AgentCredentials(string BaseUrl, string DeviceToken);
}

internal sealed record SelectedFolder(string folder_id, int folder_type, string folder_name, string folder_path);
internal sealed record FilingResult(string ObjectId, int ObjectType, string Path);

internal static class EnaioClient
{
    private static dynamic Connect()
    {
        var type = Type.GetTypeFromProgID("optimal_AS.Application") ?? throw new InvalidOperationException("enaio classic ist nicht installiert oder die COM-Schnittstelle ist nicht registriert.");
        return Activator.CreateInstance(type) ?? throw new InvalidOperationException("Die enaio-COM-Anwendung konnte nicht geöffnet werden.");
    }

    public static SelectedFolder SelectRootFolder()
    {
        dynamic app = Connect();
        try
        {
            string opened = Convert.ToString(app.GetAllOpenFolders()) ?? "";
            string first = opened.Split(';', StringSplitOptions.RemoveEmptyEntries).FirstOrDefault()
                ?? throw new InvalidOperationException("Bitte öffnen Sie in enaio zuerst einen Ordner oder ein Register.");
            string[] parts = first.Split(',');
            if (parts.Length != 2 || !long.TryParse(parts[0], out var startId) || !int.TryParse(parts[1], out var startType))
                throw new InvalidOperationException("enaio hat keine gültige Liste geöffneter Ordner zurückgegeben.");
            var started = Convert.ToInt32(app.SelectObject(startId, startType, false, "Ablage-Stammordner auswählen"));
            if (started != 1) throw new InvalidOperationException("enaio konnte die Ordnerauswahl nicht öffnen (Code " + started + ").");

            object selected = "";
            var result = 1;
            while (result == 1)
            {
                Application.DoEvents();
                result = Convert.ToInt32(app.GetSelectedObject(ref selected));
                Thread.Sleep(200);
            }
            if (result != 3) throw new InvalidOperationException("Die enaio-Ordnerauswahl wurde abgebrochen (Code " + result + ").");
            var chosen = Convert.ToString(selected)?.Split(';', StringSplitOptions.RemoveEmptyEntries).FirstOrDefault()
                ?? throw new InvalidOperationException("Es wurde kein Ordner ausgewählt.");
            var selectedParts = chosen.Split(',');
            if (selectedParts.Length != 2 || !long.TryParse(selectedParts[0], out var id) || !int.TryParse(selectedParts[1], out var objectType))
                throw new InvalidOperationException("enaio hat eine ungültige Ordner-ID zurückgegeben.");
            object name = "";
            if (Convert.ToInt32(app.GetObjectName(id, ref name)) != 0) throw new InvalidOperationException("Der Ordnername konnte nicht aus enaio gelesen werden.");
            var objectPath = Convert.ToString(app.GetObjectPath(id, objectType)) ?? "";
            object readablePath = "";
            var pathResult = Convert.ToInt32(app.GetObjectPatternPath(id, objectType, ref readablePath));
            if (pathResult != 0) throw new InvalidOperationException("Der lesbare enaio-Ordnerpfad konnte nicht ermittelt werden: " + Convert.ToString(app.GetLastError()));
            var path = Convert.ToString(readablePath);
            if (string.IsNullOrWhiteSpace(path)) path = objectPath;
            return new SelectedFolder(id.ToString(), objectType, Convert.ToString(name) ?? "", path);
        }
        finally { try { Marshal.FinalReleaseComObject((object)app); } catch { } }
    }

    public static FilingResult FileProtocol(JsonElement filing, string pdfPath)
    {
        // Object-definition names differ per enaio installation. Never guess the archive or index field.
        var registerType = filing.GetProperty("register_type_name").GetString();
        var registerNameField = filing.GetProperty("register_name_field").GetString();
        var archiveName = filing.GetProperty("archive_name").GetString();
        if (string.IsNullOrWhiteSpace(registerType) || string.IsNullOrWhiteSpace(registerNameField) || string.IsNullOrWhiteSpace(archiveName))
            throw new InvalidOperationException("Die enaio-Objektdefinition fehlt. Bitte MEETING_ENAIO_ARCHIVE_NAME, MEETING_ENAIO_REGISTER_TYPE und MEETING_ENAIO_REGISTER_NAME_FIELD gemäß Ihrer enaio-Konfiguration setzen.");

        dynamic app = Connect();
        try
        {
            var rootId = filing.GetProperty("root_folder_id").GetString()!;
            var series = filing.GetProperty("register_name").GetString()!;
            var documentType = filing.GetProperty("document_type").GetString()!;
            var query = "[ANFRAGE]\r\nSCHRANK=" + Ini(archiveName) + "\r\nREGISTER=" + Ini(registerType) +
                "\r\nKLAUSEL1=" + Ini(registerType) + "@" + Ini(registerNameField) + "=" + Ini(series) +
                "\r\nAUSDRUCK1=" + Ini(registerType) + "@1121^1^" + rootId + "~0~1122^1^0\r\nDATENFELDER=0\r\nDATENHEADER=0\r\nANFRAGEFENSTER=0\r\n";
            var resultFile = Convert.ToString(app.StartRegRequest(query)) ?? "";
            var registerId = "";
            var registerObjectType = 0;
            if (string.IsNullOrWhiteSpace(resultFile) || resultFile == "READY" || !File.Exists(resultFile))
                throw new InvalidOperationException("Die Registersuche konnte nicht ausgeführt werden: " + Convert.ToString(app.GetLastError()));
            {
                var pair = File.ReadLines(resultFile).FirstOrDefault()?.Split(',');
                if (pair?.Length == 2) { registerId = pair[0]; int.TryParse(pair[1], out registerObjectType); }
            }

            if (string.IsNullOrWhiteSpace(registerId))
            {
                object newId = 0; object newType = 0;
                var insertRegister = "[EINFÜGEN]\r\nSCHRANK=" + Ini(archiveName) + "\r\nREGISTER=" + Ini(registerType) +
                    "\r\nSCHRANK-ID=" + rootId + "\r\nREGISTER-ID=0\r\nFELD1=" + Ini(registerNameField) + "=" + Ini(series) + "\r\n";
                var code = Convert.ToInt32(app.InsertIntoRegisterS(insertRegister, ref newId, ref newType));
                if (code != 0) throw new InvalidOperationException("enaio konnte das Register nicht anlegen (Code " + code + "): " + Convert.ToString(app.GetLastError()));
                registerId = Convert.ToString(newId) ?? "";
                registerObjectType = Convert.ToInt32(newType);
            }

            object documentId = 0; object documentObjectType = 0;
            var insertDocument = "[EINFÜGEN]\r\nSCHRANK=" + Ini(archiveName) + "\r\nREGISTER=" + Ini(registerType) +
                "\r\nDOKUMENT=" + Ini(documentType) + "\r\nSCHRANK-ID=" + rootId + "\r\nREGISTER-ID=" + registerId +
                "\r\nDATEI1=" + pdfPath.Replace("\\", "/") + "\r\n";
            var insertCode = Convert.ToInt32(app.InsertIntoDocumentS(insertDocument, ref documentId, ref documentObjectType));
            if (insertCode != 0) throw new InvalidOperationException("enaio konnte das PDF nicht ablegen (Code " + insertCode + "): " + Convert.ToString(app.GetLastError()));
            var path = Convert.ToString(app.GetObjectPath(Convert.ToInt64(documentId), Convert.ToInt32(documentObjectType))) ?? "";
            return new FilingResult(Convert.ToString(documentId) ?? "", Convert.ToInt32(documentObjectType), path);
        }
        finally { try { Marshal.FinalReleaseComObject((object)app); } catch { } }
    }

    private static string Ini(string value) => value.Replace("\r", " ").Replace("\n", " ").Trim();
}
