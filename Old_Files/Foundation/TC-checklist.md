
## The Ultimate Thick Client Pentest Checklist (Step-by-Step, Ordered by ROI)

Follow this sequence. Each step builds on the last, and you can often stop early if you find critical bugs. The items are arranged so that **quick wins come first**, saving you time.

I’ve marked each step with:
- 🔴 **Critical** – likely high impact, do immediately
- 🟡 **Important** – solid findings, essential
- 🟢 **Depth** – deeper analysis, can turn up gold

---

### 🔍 PHASE 0: Preparation & Baseline

**Goal**: Understand what you're dealing with before diving deep.

- [ ] 🟡 **0.1 – Identify the technology stack**  
  *Tools*: Task Manager → Properties, Detect It Easy (DIE), Process Explorer → loaded modules.  
  *Look for*: .NET (mscorlib.dll), Java (java.exe/javaw.exe), C++ (msvcrt.dll, no clr), Electron (electron.exe), Go, etc.  
  *Output*: Decide primary tool path (dnSpy, JADX, Ghidra).

- [ ] 🟡 **0.2 – Discover network endpoints**  
  *Tools*: `netstat -ano | findstr <PID>` (while app is running), ProcMon filter `Operation is TCP Connect`, Wireshark capture.  
  *Look for*: Remote IPs, ports, localhost listeners. Note HTTP/HTTPS vs custom TCP/UDP.  
  *Output*: You know which proxies and analysis tools to set up.

- [ ] 🟢 **0.3 – Grab all installation files**  
  *Tools*: Copy the entire install directory, check `%APPDATA%\<AppName>`, `%LOCALAPPDATA%`, `ProgramData`. Also get the installer (MSI, EXE).  
  *Look for*: Extra binaries, updater exes, uninstallers, companion services.  
  *Output*: All components ready for static analysis.

---

### 🔥 PHASE 1: Static – Immediate Low-Hanging Fruit

**Goal**: Find hardcoded secrets, weak configurations, and obvious client-side logic flaws without running anything.

- [ ] 🔴 **1.1 – Dump and review strings**  
  *Tool*: `strings64.exe -n 8 <binary> > strings.txt` (or `strings` on Linux).  
  *Search (ctrl+f) for*: `password`, `pwd`, `user id`, `uid`, `server`, `database`, `connection`, `jdbc`, `key`, `secret`, `token`, `api_key`, `http://`, `https://`, IP addresses, `SELECT`, `INSERT`.  
  *Also check*: Base64-looking strings (long alphanumeric with =).  
  *Verdict*: Hardcoded credentials, connection strings, API keys → **critical finding**.

- [ ] 🔴 **1.2 – Examine configuration files**  
  *Location*: Install directory (`*.config`, `*.xml`, `*.json`, `*.ini`, `*.yaml`), and user AppData folders.  
  *Look for*: Plaintext passwords, connection strings, `debug=true`, proxy settings, custom server URLs, encryption keys.  
  *Verdict*: Any plaintext secret → report. Also note if encrypted settings appear (to decrypt later).

- [ ] 🟡 **1.3 – Decompile/disassemble the main binary**  
  *If .NET*: Drag into dnSpy.  
  *If Java*: Open JAR with JADX-GUI.  
  *If C++/native*: Load into Ghidra (auto-analyze).  
  *Immediately search for the same patterns as strings*: passwords, URLs, encryption routines.  
  *For managed code (.NET/Java)*: find authentication, license checks, crypto, update logic.  
  *For native code*: look at imported functions (e.g., `CryptDecrypt`, `WinHttpOpen`) and cross-reference their usage.  
  *Verdict*: Hardcoded keys, static IVs, client-side role checks, plaintext DB creds → confirm.

- [ ] 🟡 **1.4 – Identify third-party dependencies & versions**  
  *For .NET*: Check references in dnSpy, or look at DLLs in install folder.  
  *For Java*: Look at `META-INF/MANIFEST.MF`, lib folder.  
  *For native*: Check DLLs (Dependencies tool) and import table.  
  *Cross-reference with known vulnerabilities*: Use Retire.js for Electron, search for CVEs for log4net, Newtonsoft.Json, OpenSSL, etc.  
  *Verdict*: Outdated vulnerable library → potential RCE.

- [ ] 🟢 **1.5 – Review update mechanism (if any)**  
  *In decompiled code*: Find update function. Check if it downloads over HTTP, verifies signature, where it saves files.  
  *Verdict*: Unsigned updates over HTTP → critical MiTM or arbitrary code execution.

---

### 🌐 PHASE 2: Dynamic – Watch Network & System Activity

**Goal**: See what the app actually does at runtime, catch secrets in transit or in memory, and spot hijack opportunities.

- [ ] 🔴 **2.1 – Set up HTTPS interception**  
  *Tools*: Burp Suite, Proxifier (force app through Burp). Install Burp's CA as trusted root.  
  *Action*: Browse through the app, trigger all functions.  
  *Look for*: Sensitive data in URLs, request/response bodies (credentials, tokens, PII).  
  *Verdict*: Unencrypted sensitive data, weak API endpoints → direct findings.

- [ ] 🟡 **2.2 – Capture all network traffic (even non-HTTP)**  
  *Tool*: Wireshark, filter on app’s IPs/ports.  
  *Follow TCP/UDP streams*: look for plaintext custom protocols, SQL queries, credentials.  
  *Verdict*: Unencrypted sensitive info over custom protocols → critical.

- [ ] 🔴 **2.3 – Run ProcMon (Process Monitor) with precise filters**  
  *Filter*: `Process Name is <app.exe>` then `Operation is WriteFile` or `RegSetValue` or `TCP Connect` or `Load Image`.  
  *Start capture, perform key actions (login, sync, update), stop capture.*  
  *Analyze*:
    - **File writes**: Where does it write? Logs, configs, temp files? Look for sensitive data in those files.
    - **Registry writes**: Find stored settings, potential auto-run entries.
    - **Network connections**: Verify all endpoints.
    - **Load Image (DLL loading)**: Note which DLLs are loaded from the app directory.
  *Crucial filter*: `Result is NAME NOT FOUND` and `Path ends with .dll` → **missing DLLs are prime hijack targets**.
  *Verdict*: Missing DLL + writable directory → DLL hijacking; sensitive log data → info disclosure.

- [ ] 🟡 **2.4 – Check file and folder permissions**  
  *Tool*: `icacls "C:\Program Files\VulnApp" /T` and `accesschk64 -dqv <path>`.  
  *Look for*: `BUILTIN\Users` with Write (W) or Full (F). Also check service binary paths (unquoted service paths).  
  *Verdict*: Writable install directory → replace EXE/DLL, privilege escalation if service.

- [ ] 🟢 **2.5 – Capture a memory dump for quick secrets**  
  *Tool*: Process Explorer (right-click process → Create Dump → Full). Or `procdump64 -ma <process>`.  
  *Run `strings` on dump*: search for password, token, key.  
  *Verdict*: Plaintext secrets in memory → confidentially breach.

---

### 🧨 PHASE 3: Client-Side Attacks & Local Privilege Escalation

**Goal**: Exploit weak local trust, DLL hijacking, service misconfigurations to gain code execution or escalate privileges.

- [ ] 🔴 **3.1 – Test DLL/assembly hijacking**  
  *Prerequisite*: Identified missing DLL from ProcMon + writable directory (or per-user writable path in `%APPDATA%`).  
  *Exploit*: Create a malicious DLL with the same exports and place it where the app searches. For testing, just pop a calc.exe.  
  *Verify*: If app runs as SYSTEM (service), this is local privilege escalation.  
  *Verdict*: DLL hijacking successful → high/critical.

- [ ] 🟡 **3.2 – Analyze Windows services (if app installs one)**  
  *Commands*: `sc qc <ServiceName>`, `accesschk64 -ucqv <ServiceName>`.  
  *Look for*: Unquoted service paths (with spaces), weak SERVICE_CHANGE_CONFIG, or writable binary.  
  *Verdict*: Service exploitation leads to SYSTEM.

- [ ] 🟡 **3.3 – Examine named pipes & COM objects**  
  *Tools*: `pipelist.exe`, `accesschk64 \\.\pipe\<name>`.  
  *Look for*: Pipes with Everyone:Full control. Test if you can connect and impersonate a client or send malicious data.  
  *For COM*: Check registry under `HKCR\CLSID` for out-of-process servers with weak launch permissions.  
  *Verdict*: IPC hijacking can lead to privilege escalation or information leak.

- [ ] 🟢 **3.4 – Check for local database files**  
  *Search*: `dir /s /b *.db *.sqlite *.sqlite3 *.mdf` in install and AppData.  
  *Open with DB Browser*: Look for user tables, tokens, passwords.  
  *Verdict*: Plaintext credentials/keys stored locally.

- [ ] 🟢 **3.5 – Investigate registry for sensitive data or misconfigurations**  
  *In ProcMon, filter RegSetValue* → see what’s stored. Check `HKCU\Software\<App>`.  
  *Look for*: Debug flags, hardcoded proxy, plaintext passwords.  
  *Verdict*: Sensitive registry keys → info disclosure, possibly bypass restrictions.

---

### 🔬 PHASE 4: Deep Reverse Engineering & Memory Manipulation

**Goal**: Uncover custom crypto, bypass client-side checks, extract runtime secrets.

- [ ] 🔴 **4.1 – Bypass client-side logic (license, role, auth)**  
  *For .NET*: Debug with dnSpy, set breakpoint, change variables (`isAdmin = true`), or patch the method to always return true.  
  *For Java*: Use Frida or Recaf to modify the bytecode.  
  *For C++*: Use x64dbg to NOP the check or change a jump.  
  *Verdict*: Proves client-side enforcement only.

- [ ] 🟡 **4.2 – Hook crypto functions to capture plaintext and keys**  
  *For .NET*: Frida hook `System.Security.Cryptography.AesManaged` .CreateEncryptor or .Decrypt.  
  *For Java*: Frida hook `javax.crypto.Cipher.doFinal`.  
  *For C++*: Frida hook `CryptDecrypt` or `BCryptDecrypt` (and earlier key import functions).  
  *Output*: Extract encryption keys, decrypt traffic/config files.  
  *Verdict*: Weak crypto (static keys, wrong mode) → data exposure.

- [ ] 🟢 **4.3 – Reverse engineer custom network protocol**  
  *With Ghidra/IDA*: Analyze the functions that call `send`/`recv`. Understand packet structure.  
  *Write a Python client* that mimics the app, then fuzz the server for crashes or injection points.  
  *Verdict*: Custom protocol vulnerabilities (buffer overflow, injection, logic flaws).

- [ ] 🟢 **4.4 – Test for deserialization vulnerabilities**  
  *Look in decompiled code* for `BinaryFormatter.Deserialize`, `ObjectInputStream.readObject`, `JavaScriptSerializer.Deserialize` with type info, etc.  
  *Craft payload* with `ysoserial.net` or `ysoserial`.  
  *Verify* by sending payload and observing callback or execution.  
  *Verdict*: Remote code execution on server.

---

### 🌍 PHASE 5: Server-Side & API Attacks (Your Web Testing Playground)

**Goal**: Exploit the backend APIs just like a web application.

- [ ] 🔴 **5.1 – Test all endpoints for IDOR, privilege escalation**  
  *In Burp Repeater*: Change user IDs, order IDs, access admin endpoints without proper role.  
  *Verdict*: Unauthorized data access.

- [ ] 🔴 **5.2 – Test for classic injection flaws**  
  SQL injection, command injection (in filenames, parameters), XXE (if XML), path traversal in file download/upload.  
  *Verdict*: Server compromise/data breach.

- [ ] 🟡 **5.3 – Test JWT or token handling**  
  Check if tokens are signed weakly (none algorithm), expired tokens accepted, or tokens leaked in logs/URLs.  
  *Verdict*: Account takeover.

- [ ] 🟢 **5.4 – Check for missing rate limiting / brute-force**  
  Login endpoints, password reset, 2FA.  
  *Verdict*: Credential stuffing.

- [ ] 🟢 **5.5 – Assess business logic flaws**  
  Negative quantities, race conditions, bypassing payment flow.  
  *Verdict*: Financial/operational impact.

---


That’s it. In 30 minutes you’ve likely found hardcoded credentials, missing DLLs for hijacking, and understood the network architecture. From there, go deeper with the full checklist above.

---

