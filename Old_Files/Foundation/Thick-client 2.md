
---

## 1. Core Methodology – Unchanged
No matter if it's C++, Java, .NET, Electron, or Go:
1. **Recon** – Identify framework, network endpoints, dependencies.
2. **Static Analysis** – Extract strings, config files, decompile/disassemble, find hardcoded secrets, weak crypto.
3. **Dynamic Analysis** – Intercept traffic (HTTP, custom TCP), monitor file/reg/process activity (ProcMon), capture memory.
4. **Local Privilege Escalation & Client-Side Attacks** – DLL/.so hijacking, service misconfigs, file permission weaknesses, IPC abuses.
5. **Memory Analysis & Reverse Engineering** – Debug, hook, patch, extract keys.
6. **Server-Side Attacks** – Same as web testing: API flaws, injection, deserialization, business logic.

What changes is **how** you perform each step and **which tools** are effective.

---

## 2. C++ / Native (Win32) Thick Clients

Native applications (often compiled with MSVC, MinGW, or Delphi) are harder to decompile into readable source but expose many low-level avenues.

### Phase 0 – Recon
- Use **Detect It Easy** (DIE) or **CFF Explorer** to identify compiler, packer.
- Process Explorer shows `msvcrt.dll`, `kernel32.dll`, `user32.dll` — typical native. If it's packed (UPX, Themida), unpacking may be needed first.

### Phase 1 – Static Analysis (No Easy Decompile)
- **Strings** (`strings.exe -n 8 app.exe`) – still primary for secrets. Look for `password`, `AES`, `key`, URLs, SQL queries, and also **error strings** that reveal logic.
- **Disassembly** – Use **Ghidra** (free) or **IDA**. Even basic analysis reveals function calls like `CryptDecrypt`, `WinHttpConnect`, `RegOpenKeyEx`.
- **Config files** – Same as before (`.ini`, `.xml`, registry entries).
- **Import table analysis** – With `Dependencies` or `CFF Explorer`, see imported functions: if you see `CryptEncrypt`/`CryptDecrypt`, note possible custom crypto; `WinHttpGetProxyForUrl` might indicate proxy-aware networking.
- **Hardcoded keys/constants** – Often found as global byte arrays in data sections. Ghidra's search for specific byte patterns (like AES S-box) can locate crypto functions.

### Phase 2 – Dynamic Analysis
- **Intercepting HTTP/HTTPS** – Native apps often use WinHTTP/WinInet. Proxifier still works. For manual hooking, Frida can intercept `WinHttpOpenRequest` and `WinHttpSendRequest` to dump headers and modify body.
- **Wireshark** filters remain same.
- **ProcMon** – The most crucial tool. Same filters. Especially watch for missing DLLs and registry accesses.
- **Frida** – Extremely powerful for native. You can hook any exported function. Example: `Interceptor.attach(Module.findExportByName("kernel32.dll", "WriteFile"), { onEnter: function(args) { ... } });`

### Phase 3 – Local Privilege Escalation & Client-Side
- **DLL Hijacking** – Even more common in native apps because they rely heavily on DLLs and often have weak search order. Use ProcMon "NAME NOT FOUND" results. Classic technique: create a proxy DLL that exports the same functions and forward them using a `.def` file or forwarder exports. Tools: **AheadLib** or manual.
- **Unquoted service paths** – Same.
- **Memory corruption** – Not the focus of this guide, but buffer overflows in custom TCP parsing are a possibility if no memory protections. Fuzzing with custom Python clients can reveal crashes.
- **IPC** – Named pipes are common; test ACLs.

### Phase 4 – Memory & Reversing
- **Debugging** – **x64dbg/x32dbg** (user-friendly) or **WinDbg**. Set breakpoints on interesting Windows APIs (e.g., `CryptDecrypt`, `recv`).
- **Patching** – Use x64dbg to NOP out checks or change jumps. Save patched binary.
- **Frida hooking** – To bypass license checks, hook `GetProductInfo` or custom verification functions. To bypass SSL pinning, hook `SslSetCertificateValidationCallback` or similar.
- **Crypto extraction** – Hook crypto APIs directly: if it uses `CryptDecrypt`, hook it and dump plaintext/ciphertext and key handles. Then trace back to `CryptImportKey` to find the raw key bytes.

### Phase 5 – Server-Side
- Custom TCP protocols may require reverse engineering the binary format. Ghidra helps understand the `send`/`recv` structure. Then craft packets with Python.
- If the backend is a standard web service, no difference.

**Unique vulnerabilities in C++ apps:**
- Use of dangerous functions (`strcpy`, `sprintf`) leading to memory corruption (less common in modern apps but still exist).
- Static linking of vulnerable libraries (OpenSSL, zlib) that can't be patched easily.
- Easier to bypass client-side integrity checks via binary patching because no managed code verification.
- Harder to obfuscate than .NET? Not really, but often devs skip obfuscation, leaving clear string refs.

---

## 3. Java Thick Clients (Swing, JavaFX, or SWT)

Java brings its own ecosystem, but thankfully decompilation is as easy as .NET.

### Phase 0 – Recon
- **Identify Java** – Process Explorer shows `java.exe` or `javaw.exe`. JARs are in the application folder.
- **Check Java version** (`java -version`) and bundled JRE (often in app dir).

### Phase 1 – Static Analysis
- **Decompile** – Use **JADX-GUI** (my favourite, exports whole project), **JD-GUI**, or **CFR**. Drag the main JAR. You'll see fully readable Java code.
- **Search** for same keywords: `password`, `jdbc:`, `http://`, `AES`, `SecretKeySpec`.
- **Check `META-INF/MANIFEST.MF`** for main class, classpath, library versions.
- **Look at dependency JARs** for known vulnerabilities (e.g., Log4j, older Spring, older Apache Commons Collections).
- **Configuration files** – `application.properties`, `config.xml`, `*.prefs`.
- **Hardcoded passwords** in JDBC connection strings (`jdbc:mysql://...?user=root&password=...`) are very common.

### Phase 2 – Dynamic Analysis
- **Network traffic** – Java apps often respect system properties `-Dhttp.proxyHost` and `-Dhttps.proxyHost`. If the app is launched via a script, you can add these JVM args. If not, you can inject a Java agent or use Frida to set properties at runtime.
- **Better method**: Use **Proxifier** as before; it doesn't care about language.
- **Frida** with Java bridge: Frida can hook arbitrary Java methods using `Java.perform()`. Example: hook `javax.crypto.Cipher.doFinal()` to capture plaintext. Extremely powerful.
- **ProcMon** – still works to monitor file/reg activity (Java apps interact with filesystem just like any process).
- **Java-specific monitoring** – **VisualVM** or **JConsole** can attach to the JVM and show threads, memory, and even MBeans. If JMX is exposed without authentication, you can invoke methods remotely (huge finding).

### Phase 3 – Local Priv Esc & Client-Side
- **Java does not use traditional DLLs**, so DLL hijacking isn't applicable. However, Java loads native libraries via `System.loadLibrary()`. Check what `.dll` or `.so` files are loaded (ProcMon). If the library path is writable or can be influenced by `java.library.path`, you can inject a malicious native library (JNI hijack).
- **File permissions** – The JAR itself might be writable, allowing trojanization.
- **Java Web Start (JNLP)** – If the app uses Java Web Start, the JNLP file may be served over HTTP and unsigned, allowing remote code execution on startup (classic attack).
- **Deserialization** – Java deserialization is a massive attack vector. Look for `ObjectInputStream.readObject()` calls with untrusted data. Use **ysoserial** to generate payloads.
- **Local storage** – Java Preferences API stores data in XML files in user home. Check for secrets.

### Phase 4 – Memory & Reversing
- **Debugging** – You can debug Java apps with IDEs (IntelliJ community, Eclipse) if you have the source. Better: attach **JDB** or use **Frida**.
- **Patching** – Java bytecode can be edited with **Recaf** or **JByteMod**. Or simply recompile a modified class and replace it in the JAR (using `jar uf`).
- **Frida scripts** – Bypass license checks by hooking a specific method and changing return value.

### Phase 5 – Server-Side
- Same as before: REST, SOAP, RMI, JMX, JMS. Test API vulnerabilities.
- If the app uses RMI (Java RMI), check for RMI registry exposure and deserialization.

**Unique Java vulnerabilities:**
- RMI/JMX insecure deserialization.
- Misconfigured Java security policies (`.policy` files) granting `AllPermission`.
- Log4Shell if using vulnerable Log4j version.
- JNDI injection.
- Insecure Java Web Start.
- Weak keystore passwords (e.g., default `changeit` for truststore, or hardcoded private key passwords).

---

## 4. Summary Comparison Table

| Phase/Task               | .NET (C#/VB)             | C++ Native              | Java                     |
|--------------------------|--------------------------|-------------------------|--------------------------|
| Decompilation            | dnSpy (full source)      | Ghidra/IDA (assembly)  | JADX/JD-GUI (full source) |
| String extraction        | strings.exe, dnSpy       | strings.exe             | strings, JADX search     |
| Dynamic monitoring       | ProcMon, Proxifier       | ProcMon, Proxifier      | ProcMon, Proxifier       |
| HTTP interception        | Burp (via proxy or Proxifier) | same               | same, plus JVM args      |
| Custom protocol hooking  | Frida (CLR)              | Frida (native), x64dbg  | Frida (Java)             |
| DLL/Shared lib hijacking | DLL hijacking            | DLL hijacking (main!)   | JNI library hijacking    |
| Memory analysis          | dnSpy debug, Procdump    | x64dbg, WinDbg, Frida   | JDB, Frida, VisualVM     |
| Patching                 | dnSpy Edit Method        | x64dbg patch, hex edit  | Recaf, re-jar            |
| Deserialization attacks  | BinaryFormatter, JSON.NET| Rare (custom formats)   | ObjectInputStream (ysoserial) |
| Common secrets locations | .config, strings, code   | strings, registry       | .properties, code, JNDI  |
| Certificate pinning bypass | Frida (ServicePointManager) | Frida (SslSetCertificate...) | Frida (TrustManager) |

---

## 5. Your Action Plan for Multi-Language Targets

1. Start with **recon** to determine language.
2. If **.NET** → use the full guide I gave earlier.
3. If **C++** → Swap out dnSpy for Ghidra/x64dbg, but keep ProcMon, Wireshark, and Frida. Focus heavily on DLL hijacking and native API hooking.
4. If **Java** → Use JADX-GUI as your “dnSpy,” ProcMon, Frida with Java bridge. Be alert for deserialization and JMX.

The **phases and attack vectors are the same**, you just switch the decompiler and debugging tools. Your web testing brain still rules for API attacks. The methodology is robust—I've tested countless thick clients this way.

Now go break that VM app! And let me know what language it turned out to be.