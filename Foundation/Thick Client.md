[[TC-checklist]]
[[Thick-client 2]]
---

 **Detect It Easy**  --> tool for detection 

## 1. Environment Setup & Essential Tools

### Windows VM (Testing Sandbox)
- **OS**: Windows 10/11 (clean snapshot).
- **Disable Defender real-time scanning** or add exclusions for tool folders (otherwise many tools get flagged).
- **Install a text editor** (Notepad++), **7-Zip**, and **Python** (for scripts).

### Core Toolkit Installation
| Tool | Purpose | Source |
|------|---------|--------|
| **dnSpy** | .NET decompiler, debugger, patching | [GitHub releases](https://github.com/dnSpy/dnSpy/releases) |
| **Process Monitor (ProcMon)** | Real-time file, registry, network, thread activity | Sysinternals |
| **Process Explorer** | View loaded DLLs, handles, strings in memory | Sysinternals |
| **Strings** | Extract ASCII/Unicode strings from binaries | Sysinternals |
| **Wireshark** | Capture network traffic (with Npcap) | wireshark.org |
| **Burp Suite Community** | HTTP/HTTPS interception | portswigger.net |
| **Proxifier** | Force apps through proxy (even non-proxy-aware) | proxifier.com |
| **Frida** | Dynamic instrumentation toolkit | frida.re (install `frida-tools` with pip on host, `frida-server` on VM) |
| **AccessChk** | Check file/reg/service permissions | Sysinternals |
| **Sigcheck** | Verify digital signatures | Sysinternals |
| **Dependency Walker** (or modern `Dependencies`) | DLL dependency analysis | github.com/lucasg/Dependencies |
| **CFF Explorer** | PE editor (for DLL export forwarding) | ntcore.com |
| **x64dbg / x32dbg** | Native debugger | x64dbg.com |
| **SQLite Browser** | View local SQLite databases | sqlitebrowser.org |

### Setting Up Interception
1. **Burp Suite** on Linux/Windows (wherever) listening on all interfaces on port 8080.
2. In the VM, set system proxy to point to Burp's IP:8080.
3. Export Burp's CA certificate, import into Windows Trusted Root Certification Authorities (`certlm.msc`).
4. **Proxifier**: Create a proxy rule pointing to Burp’s address/port; then add a rule that forces all applications (or just the target process) through that proxy. This captures traffic from apps that ignore system proxy settings.

---

## 2. Phase 0: Recon – Know Your Enemy

Start by running the application and logging in with test credentials.

### Identify Technology Stack
- **Task Manager** → Details tab → Locate the process. Check "Description", "Company". Right-click → Properties → Details. Look at product name, copyright. Often reveals framework.
- **Process Explorer**: Double-click the process, go to "Threads" tab, look at loaded modules. If you see `mscorlib.dll`, `System.dll`, `System.Windows.Forms.dll` → .NET Framework. If you see `Microsoft.AspNetCore.*` → possibly .NET Core self-contained. If you see `libjvm` → Java. `electron.exe` → Electron.
- **Detect It Easy (DIE)** – Drag the main executable into DIE; it tells compiler, linker, framework.

Example: `VulnApp.exe` shows "Microsoft Visual C# / Basic .NET" → .NET.

### Discover Network Architecture
- **Wireshark** start capture on your active interface. Filter to see all traffic from the VM (if you're on the VM, capture on Ethernet).
- Use ProcMon: filter `Process Name is VulnApp.exe` and `Operation is TCP Connect` or `UDP Send`. You'll see remote IPs and ports.
- Run `netstat -ano | findstr <PID>` in CMD to list current connections.

From this, you might see:
- Persistent HTTPS to `api.vulnapp.com:443`
- A raw TCP connection to `192.168.1.100:9000` (custom protocol)
- Localhost connections (possible IPC)

---

## 3. Phase 1: Static Analysis – Plunder the Files

Install the application. Navigate to its installation directory (e.g., `C:\Program Files\VulnApp`) and `%APPDATA%\VulnApp`.

### 3.1 Extract Strings
```powershell
.\strings64.exe -n 8 VulnApp.exe > strings_8.txt
.\strings64.exe -n 8 VulnApp.dll > strings_dll.txt
```
Look for:
- `http://`, `https://` URLs
- `password`, `pwd`, `user`, `conn`, `secret`, `key`, `api`
- SQL connection strings like `Server=...;Database=...;Uid=...;Pwd=...`
- Hardcoded encryption keys/IVs (often base64-encoded)
- Internal IP addresses

### 3.2 Configuration Files
Check:
- `*.config` (e.g., `VulnApp.exe.config`)
- `*.xml`, `*.json`, `*.ini`
- `Settings.settings` or `*.user` files
- Inside `%APPDATA%` local data folders.

If you find encrypted settings, note the algorithm and look for hardcoded keys/IVs later in the binary. Look for plaintext secrets or connection strings. Sometimes there are debug settings like `<add key="Debug" value="true"/>` that enable verbose logging.

### 3.3 Decompile .NET Assemblies
**dnSpy** (x64 if app is 64-bit, x86 otherwise).
- Open `VulnApp.exe` with dnSpy. You see the full source code (unless obfuscated).
- Immediately search:
  - `password`, `key`, `iv`, `encrypt`, `decrypt`, `connection`
  - `Login`, `Authenticate`, `Token`
  - `Update`, `DownloadFile`
- Analyze the logic:
  - Does the authentication send credentials in plaintext?
  - Are there hardcoded API tokens or passwords?
  - How is the license check implemented? Can we patch it?
  - Is there an admin panel hidden behind a role check? Look for `if (role == "Admin")` – you can change that later.
- If you see `DES`, `RijndaelManaged`, `AesManaged`, check how keys/IVs are set. If they are static strings, you’ve found weak crypto.

### 3.4 DLL/Assembly Enumeration
List all DLLs in the install folder and check:
- Are they known vulnerable third-party libraries? (e.g., log4net, Newtonsoft.Json, SQLite).
- Use `sigcheck64 -s -a <folder>` to check digital signatures. Unsigned DLLs from the application itself can be replaced (but be careful, we’ll test hijacking).

Examine the .NET dependencies inside dnSpy (References). Look for outdated JSON.NET versions – might be susceptible to deserialization.

### 3.5 Identify Hardcoded Secrets & Weak Crypto
Example finding: In `DatabaseHelper.cs`:
```csharp
string connString = "Server=db.vulnapp.com;Database=prod;User Id=sa;Password=SuperSecret123;";
```
That’s a critical direct database access.

Or:
```csharp
private static byte[] Key = Convert.FromBase64String("tR6wZ4...");
private static byte[] IV = Encoding.UTF8.GetBytes("1234567890123456");
```
AES with static IV and key = broken crypto. You can decrypt any config or traffic.

---

## 4. Phase 2: Dynamic Analysis – Watch It Live

### 4.1 Intercept HTTP/HTTPS Traffic
- Start Burp, enable invisible proxying if needed.
- Launch Proxifier, add rule for `VulnApp.exe` to forward all traffic to Burp. Many thick clients don’t use system proxy.
- If the app uses HTTPS and you’ve installed Burp’s CA, you’ll see decrypted traffic.
- If you get TLS errors, the app may use **certificate pinning**. Bypass options: patch the validation callback (dnSpy), use Frida to hook.

**Frida script to bypass .NET SSL pinning** (common pattern):
```javascript
// Hook ServicePointManager.ServerCertificateValidationCallback
var ServicePointManager = Assembly.Load("System").GetType("System.Net.ServicePointManager");
var original = ServicePointManager.GetProperty("ServerCertificateValidationCallback");
// Set it to always return true
var TrueDelegate = new RemoteCertificateValidationCallback((sender, cert, chain, sslPolicyErrors) => true);
ServicePointManager.GetProperty("ServerCertificateValidationCallback").SetValue(null, TrueDelegate);
```
Run with:
```bash
frida -H 192.168.x.x -f VulnApp.exe -l bypass_pinning.js --no-pause
```
Adjust based on actual process. If the app uses `HttpClient` with custom handler, you may need to hook that handler’s `ServerCertificateCustomValidationCallback`.

### 4.2 Wireshark Capture & Essential Filters
Start Wireshark capturing on the interface the VM uses (or on the host if traffic is routed). Run the app, use its features.

**Key display filters:**
- Show only traffic from/to the app’s known IPs (get IPs via netstat or ProcMon):
  ```
  ip.addr == 203.0.113.50 || ip.addr == 192.168.1.100
  ```
- HTTP:
  ```
  http
  ```
- TCP streams for custom protocol:
  ```
  tcp.port == 9000
  ```
- Follow TCP stream to see raw payload. Look for readable text, SQL queries, JSON. If binary, note patterns.
- Check for unencrypted sensitive data (login credentials, tokens).

**If the custom TCP is TLS:** It might use `SslStream`. You can try to man-in-the-middle by redirecting traffic, but if certificate pinning is used, Frida can hook `SslStream.AuthenticateAsClient` to bypass validation. Or use `echo-mitm` with a custom certificate if they trust system store.

### 4.3 Process Monitor (ProcMon) – The Ultimate Spy
Launch ProcMon and set filter: `Process Name is VulnApp.exe`. Clear display. Perform key actions (login, load data, update). Stop capture.

**Crucial filters to add for analysis:**
- **File system writes**: `Operation is WriteFile` → see what files are modified (config, logs, temp).
- **Registry**: `Operation is RegSetValue` → find keys written (settings, auto-start entries).
- **Network**: `Operation is TCP Connect` or `UDP Send` → verify all endpoints.
- **DLL loading**: `Operation is Load Image` → shows every DLL loaded. Look for paths like `C:\Program Files\VulnApp\` and note DLLs loaded from user-writable locations (`%TEMP%`, `%APPDATA%`).
- **Missing DLLs**: Add filter `Result is NAME NOT FOUND` and `Path ends with .dll`. This shows DLLs the app tries to load but that don't exist. This is **gold for DLL hijacking**.

Example: ProcMon shows `VulnApp.exe` trying to load `C:\Program Files\VulnApp\VERSION.dll` but "NAME NOT FOUND". If that folder is writable by a standard user (we'll check later), you can plant a malicious DLL.

### 4.4 Identify DLL Load Order & Potential Hijacks
Check ProcMon for loads of `CRYPTBASE.dll`, `WINMM.dll`, etc., that are searched in the app directory first. If any of those are missing and the folder is writable, classic hijack.

But more sophisticated: The app might load a library like `CustomProtocol.dll` from its directory. Check if you can replace it while the app is running (if not a service, you need write access). Test folder permissions with `icacls "C:\Program Files\VulnApp"`. If "BUILTIN\Users" has (W) or (M), you can overwrite.

### 4.5 Memory Dumping on the Fly
While app is running, use **Process Explorer**:
- Double-click process → "Threads" tab → "Strings" button. Search for "password", "token". This scans live process memory.
- Or use ProcDump: `procdump64 -ma VulnApp.exe memory.dmp`, then analyze offline with strings or WinDbg.

Often, decrypted secrets and plaintext credentials linger in memory.

---

## 5. Phase 3: Local Privilege Escalation & Client-Side Attacks

### 5.1 File & Folder Permission Weaknesses
We want to see if we can tamper with the installation directory or data folders.

Command:
```powershell
icacls "C:\Program Files\VulnApp" /T
```
If you see `BUILTIN\Users:(OI)(CI)(W)` or `Everyone:(F)`, you can modify files. This could allow DLL replacement, config file tampering to inject malicious proxy, or replacing the entire executable.

Also check `%APPDATA%\VulnApp` permissions. Typically writable by user, but if there’s a configuration file that sets, say, an external tool path that runs with elevated privileges, you might be able to achieve persistence or escalation.

### 5.2 DLL Hijacking
Scenario: ProcMon found `VERSION.dll` missing in the app directory, and we confirmed users can write there.

**Create a malicious DLL** using `msfvenom` or custom C++ DLL that exports all functions the real `VERSION.dll` would export (so the app doesn't crash). For .NET apps, you might need a native DLL with proper exports. A common technique is to use DLL proxy (forwarding exports to the original DLL while executing payload).

Simplest test: Create a DLL with a `DllMain` that writes a file to disk or pops a calc, just to confirm code execution. If the app runs as SYSTEM (e.g., a service) and loads your DLL, you’ve got privilege escalation.

Check with `accesschk`:
```cmd
accesschk64.exe -dqv "C:\Program Files\VulnApp"
```

### 5.3 Service Misconfigurations
The thick client might install a Windows service. Check with:
```powershell
Get-Service -Name "*vuln*" | Select-Object Name, DisplayName, Status, StartType
```
Then:
```cmd
sc qc <ServiceName>
```
If `BINARY_PATH_NAME` is unquoted and contains spaces, classic unquoted service path. Also use `accesschk` to see if we can modify the service binary or config.

### 5.4 Named Pipe & COM Hijacking
- List pipes: `pipelist.exe` or from PowerShell: `Get-ChildItem \\.\pipe\`. Look for ones related to the app.
- Check permissions: `accesschk64.exe \\.\pipe\VulnPipe`. If `Everyone` or `Authenticated Users` has `FILE_ALL_ACCESS`, a lower-privileged attacker could impersonate clients or tamper with communication.
- For COM objects, look for CLSID entries in registry under `HKCR\CLSID`. If a COM server runs out-of-process with elevated rights, and it’s launched by the thick client, you may be able to hijack.

### 5.5 Sensitive Local Data Storage
- Check for SQLite databases: `dir /s /b *.db *.sqlite *.sqlite3` in install and appdata.
- Open with DB Browser. Look for user tables, tokens, keys. Sometimes passwords stored in plaintext.
- Check for log files in `%APPDATA%` or `%TEMP%`—verbose logging might contain session cookies or API keys.

### 5.6 Registry Weaknesses
- Monitor with ProcMon for RegSetValue operations. Look at paths under `HKCU\Software\VulnApp`. If settings like `LicenseKey` or `ServerURL` are stored, maybe you can alter them to point to your malicious server.
- If the app checks for a registry key to enable debug mode, you can set it and get more insight.

---

## 6. Phase 4: Memory Analysis & Reverse Engineering Deep-Dive

### 6.1 Live Debugging with dnSpy
Launch VulnApp via dnSpy (debug → Start debugging). Set breakpoints on interesting methods (e.g., `Login_Click`, `GetLicense`, `Encrypt`). When the breakpoint hits:
- Inspect local variables; you might see plaintext credentials.
- Modify variables in real-time: change `isAdmin = false` to `true`, bypass checks.
- Step through encryption routines to extract key/IV from memory.

### 6.2 Patching the Binary
Example: License check always fails. In dnSpy, find `LicenseManager.Validate()` method that returns false. Right-click → Edit Method (C#). Change to `return true;`. Compile, then File → Save Module. Now run the patched exe—license bypassed.

Or patch out certificate validation: find the callback, edit to always return true.

**Note:** Keep original binary for evidence. Patching proves client-side trust.

### 6.3 Crypto Analysis
Find the decryption function. In dnSpy, it might look like:
```csharp
public static string Decrypt(string cipherText)
{
    byte[] cipherBytes = Convert.FromBase64String(cipherText);
    using (Aes aes = Aes.Create())
    {
        aes.Key = Key; // hardcoded
        aes.IV = IV;
        // ...
    }
}
```
Copy the Key and IV values. Then use CyberChef or Python to decrypt captured config data or network payloads. This verifies weak encryption.

### 6.4 Frida for Advanced Hooking
If the app is packed or obfuscated .NET, you can still hook .NET methods with Frida using the CLR plugin. Example hook `RijndaelManagedTransform.DecryptBlock` to capture plaintext:
```javascript
var DecryptBlock = Module.findExportByName("System.Core.dll", "System.Security.Cryptography.RijndaelManagedTransform.DecryptBlock");
// or use Frida's .NET API
```
For native apps, you'd hook Windows CryptoAPI functions (`CryptDecrypt`, `BCryptDecrypt`).

Frida script to log all HTTP request content:
```javascript
// Hook System.Net.Http.HttpClient.SendAsync
// (simplified concept - real implementation uses reflection)
```
There are mature Frida scripts online (e.g., from OWASP, BChecks).

---

## 7. Phase 5: Server-Side Attacks (Your Web Skills Shine)

Now that you understand the protocol, you can craft custom requests.

### 7.1 API Testing via Burp Repeater
Replay captured HTTP requests and attack parameters:
- **IDOR**: Change user IDs, order numbers.
- **SQLi**: If input fields seem concatenated.
- **Command injection**: in filename parameters.
- **JWT attacks**: Check token validation.
- **XXE**: If XML is used (SOAP/WCF).

### 7.2 Deserialization
If the client sends serialized .NET objects (e.g., `BinaryFormatter`, `NetDataContractSerializer`, `JavaScriptSerializer` with type info), use `ysoserial.net` to generate payloads. Test in Burp by replacing the request body. Look for Base64-encoded strings that deserialize into objects; decompiled code shows `Deserialize` calls.

### 7.3 Direct Backend Connection Exploitation
If you found a database connection string and the server allows remote connections, connect with a SQL client (e.g., HeidiSQL) and enumerate databases—verify impact.

### 7.4 Update Mechanism Attacks
Monitor update with ProcMon/Wireshark:
- Does it download over HTTP? (Clear-text update → MiTM possible)
- Does it verify digital signature? Check in dnSpy: `UpdateManager.DownloadUpdate()`. If no signature check, you can serve a malicious update from a spoofed server.
- Is the update directory writable? Then you can drop a malicious file that gets executed.

---

## 8. Verification – Proving Exploitability

For each finding, create a minimal Proof-of-Concept (PoC):

- **Hardcoded password**: Show you can connect to the DB and query data.
- **DLL Hijacking**: Demonstrate a DLL that writes a file to disk or launches calc when the app starts (if service, system privilege).
- **Weak encryption**: Decrypt intercepted traffic or config files and show plaintext.
- **Memory dump secrets**: Show extracted session token that can be reused.
- **API injection**: Run a SQL query that extracts database version.
- **Unrestricted file upload/command injection**: Get a reverse shell on the server (if in scope).

Document screenshots, step-by-step to reproduce, and impact.

---

## 9. Attack Vector & Vulnerability Checklist

Print this out for each engagement:

- [ ] **Hardcoded secrets** (strings, decompile, config)
- [ ] **Weak cryptography** (hardcoded key/IV, ECB mode, no HMAC)
- [ ] **Insecure communication** (HTTP, self-signed cert without pinning, custom TCP without encryption)
- [ ] **Certificate validation disabled or bypassable**
- [ ] **Insecure update** (HTTP, no signature, writable update path)
- [ ] **DLL hijacking** (missing DLL + writable folder)
- [ ] **File/folder permission issues** (writable install dir, service binaries)
- [ ] **Sensitive data in local storage** (SQLite, log files)
- [ ] **Sensitive data in memory**
- [ ] **Client-side trust** (license, role checks bypassable via patching)
- [ ] **Unquoted service paths / weak service permissions**
- [ ] **IPC weaknesses** (named pipe ACLs, COM)
- [ ] **API vulnerabilities** (IDOR, SQLi, XXE, auth bypass, injection)
- [ ] **Deserialization**
- [ ] **Verbose error messages exposing internals**
- [ ] **Outdated/vulnerable dependencies**

---

## Final Words

You start with the easy wins (strings, decompile, config), move to monitoring what it does (ProcMon, Wireshark, Burp), then dig into logic flaws and privilege escalations. With your web background, server-side attacks will feel natural; the thick client is just another front-end.

Now, take your first application, apply this methodology step by step, and document everything. You'll be surprised how many critical bugs you'll find.

Let me know what you find in that VM!
