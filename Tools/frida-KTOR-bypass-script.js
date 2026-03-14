/*
 * ============================================================
 *  iRA (Tata Motors) — WORKING Merged Frida Script
 *  Frida : 16.7.19 (client + server must match!)
 *  Target: com.tatamotors.oneapp
 *
 *  Covers:
 *   1. SQLCipher key capture  (f1b, kta, SQLiteDatabase)
 *   2. SSL Pinning bypass     (TrustManager, OkHttp, Ktor, WebView)
 *   3. Proxy forcing          (System props, OkHttp, ProxySelector)
 *   4. Root detection bypass  (RootBeer, JailMonkey, IRoot, etc.)
 *   5. ADB/Debug bypass       (Settings.Global, Settings.Secure)
 *   6. pvcx API request hooks (all 4 envs: qa/uat/dev/prod)
 *   7. Remote command logger  (tatamotors remote-command endpoints)
 *   8. Flutter SSL bypass     (libflutter.so native memory scan)
 *
 *  Usage:
 *    frida -U -f com.tatamotors.oneapp --no-pause -l ira_working.js
 * ============================================================
 */

/* ====================== SCRIPT 1: SQLCipher Key Capture ====================== */
(function () {

    function out(msg) {
        console.log(msg);
        try { send(msg); } catch (e) { }
    }

    function bytesToHex(bytes) {
        if (!bytes) return "";
        var parts = [];
        for (var i = 0; i < bytes.length; i++) {
            var v = bytes[i];
            if (v < 0) v += 256;
            parts.push(("0" + v.toString(16)).slice(-2));
        }
        return parts.join("");
    }

    function bytesToPrintable(bytes) {
        if (!bytes) return "";
        var s = "";
        for (var i = 0; i < bytes.length; i++) {
            var v = bytes[i];
            if (v < 0) v += 256;
            s += (v >= 32 && v <= 126) ? String.fromCharCode(v) : ".";
        }
        return s;
    }

    function charsToString(chars) {
        if (!chars) return "";
        var s = "";
        for (var i = 0; i < chars.length; i++) {
            s += String.fromCharCode(chars[i]);
        }
        return s;
    }

    var installed = { f1b: false, kta: false, sqlcipher: false, classLoaderMonitor: false };

    function installF1bHookViaFactory(cf, sourceTag) {
        if (installed.f1b) return;
        try {
            var f1b = cf.use("com.tatamotors.oneapp.f1b");
            out("[SQLKEY] f1b overloads found via " + sourceTag + ": " + f1b.a.overloads.length);
            var f1bA = f1b.a.overload("android.content.Context");
            f1bA.implementation = function (ctx) {
                var ret = f1bA.call(this, ctx);
                try {
                    var pass = charsToString(ret);
                    out("[SQLKEY] f1b password: " + pass);
                } catch (e1) {
                    out("[SQLKEY] f1b conversion error: " + e1);
                }
                return ret;
            };
            installed.f1b = true;
            out("[SQLKEY] Hooked f1b.a(Context) via " + sourceTag);
        } catch (e) {
            out("[SQLKEY] f1b hook failed via " + sourceTag + ": " + e);
        }
    }

    function withClassInAnyLoader(className, onFound) {
        var hit = false;
        Java.enumerateClassLoaders({
            onMatch: function (loader) {
                if (hit) return;
                try {
                    loader.findClass(className);
                    hit = true;
                    var cf = Java.ClassFactory.get(loader);
                    onFound(cf);
                } catch (e) { }
            },
            onComplete: function () { }
        });
        return hit;
    }

    function ensureClassLoaderMonitor() {
        if (installed.classLoaderMonitor) return;
        try {
            var ClassLoader = Java.use("java.lang.ClassLoader");
            var loadClass = ClassLoader.loadClass.overload("java.lang.String");
            loadClass.implementation = function (name) {
                var res = loadClass.call(this, name);
                if (!installed.f1b && name === "com.tatamotors.oneapp.f1b") {
                    out("[SQLKEY] ClassLoader saw: " + name);
                    try {
                        var cf = Java.ClassFactory.get(this);
                        installF1bHookViaFactory(cf, "ClassLoader.loadClass");
                    } catch (e) { out("[SQLKEY] ClassLoader factory error: " + e); }
                }
                return res;
            };
            installed.classLoaderMonitor = true;
            out("[SQLKEY] ClassLoader monitor hooked");
        } catch (e) { out("[SQLKEY] ClassLoader monitor failed: " + e); }
    }

    function tryInstallHooks() {
        Java.perform(function () {
            if (!installed.f1b) {
                try { installF1bHookViaFactory(Java, "default-loader"); } catch (e) { }
                if (!installed.f1b) {
                    withClassInAnyLoader("com.tatamotors.oneapp.f1b", function (cf) {
                        installF1bHookViaFactory(cf, "enumerateClassLoaders");
                    });
                }
                if (!installed.f1b) { ensureClassLoaderMonitor(); }
            }

            if (!installed.kta) {
                try {
                    var kta = Java.use("com.tatamotors.oneapp.kta");
                    var ktaA = kta.a.overload("android.content.Context", "[B");
                    ktaA.implementation = function (ctx, key) {
                        out("[SQLKEY] kta key hex: " + bytesToHex(key));
                        out("[SQLKEY] kta key txt: " + bytesToPrintable(key));
                        return ktaA.call(this, ctx, key);
                    };
                    installed.kta = true;
                    out("[SQLKEY] Hooked kta.a(Context,[B)");
                } catch (e) { }
            }

            if (!installed.sqlcipher) {
                try {
                    var SDB = Java.use("net.zetetic.database.sqlcipher.SQLiteDatabase");
                    var openDb = SDB.openDatabase.overload(
                        "java.lang.String", "[B",
                        "net.zetetic.database.sqlcipher.SQLiteDatabase$CursorFactory",
                        "int",
                        "net.zetetic.database.DatabaseErrorHandler",
                        "net.zetetic.database.sqlcipher.SQLiteDatabaseHook"
                    );
                    openDb.implementation = function (path, key, factory, flags, err, hook) {
                        out("[SQLKEY] SQLCipher openDatabase path=" + path);
                        out("[SQLKEY] SQLCipher key hex: " + bytesToHex(key));
                        out("[SQLKEY] SQLCipher key txt: " + bytesToPrintable(key));
                        return openDb.call(this, path, key, factory, flags, err, hook);
                    };
                    installed.sqlcipher = true;
                    out("[SQLKEY] Hooked SQLCipher.openDatabase");
                } catch (e) { }
            }
        });
    }

    if (!Java.available) {
        console.log("[SQLKEY] Java not available");
    } else {
        out("[SQLKEY] Starting SQLCipher key capture...");
        var attempts = 0;
        var timer = setInterval(function () {
            attempts++;
            tryInstallHooks();
            if ((installed.f1b && installed.kta && installed.sqlcipher) || attempts >= 30) {
                clearInterval(timer);
                out("[SQLKEY] Status: f1b=" + installed.f1b + " kta=" + installed.kta + " sqlcipher=" + installed.sqlcipher);
            }
        }, 500);
    }

})();


/* ====================== SCRIPT 2: SSL + Proxy + Root Bypass ====================== */
(function () {

    // --- CONFIGURATION ---
    const PROXY_HOST = "192.168.1.44";   // <-- Change to YOUR machine IP
    const PROXY_PORT = 8082;
    const DEBUG_LOGS = true;
    const API_DOMAINS = ["tatamotors", "pvcx.api.tatamotors", "adobedc.net", "juspay.in"];

    Java.perform(function () {
        console.log("\n[*] SSL + Proxy + Root bypass loading...");

        var System = Java.use("java.lang.System");
        var Proxy = Java.use("java.net.Proxy");
        var InetSock = Java.use("java.net.InetSocketAddress");
        var ProxyType = Java.use("java.net.Proxy$Type");

        // ── 1. System-level proxy ────────────────────────────────
        System.setProperty("http.proxyHost", PROXY_HOST);
        System.setProperty("http.proxyPort", PROXY_PORT.toString());
        System.setProperty("https.proxyHost", PROXY_HOST);
        System.setProperty("https.proxyPort", PROXY_PORT.toString());
        console.log("[+] System proxy → " + PROXY_HOST + ":" + PROXY_PORT);

        // ── 2. OkHttp3 proxy injection ───────────────────────────
        try {
            var OkBuilder = Java.use("okhttp3.OkHttpClient$Builder");
            OkBuilder.build.implementation = function () {
                try {
                    var addr = InetSock.$new(PROXY_HOST, PROXY_PORT);
                    var types = ProxyType.values();
                    var proxy = Proxy.$new(types[1], addr); // HTTP = index 1
                    this.proxy(proxy);
                    console.log("[+] OkHttp3 proxy injected");
                } catch (e) { console.log("[-] OkHttp3 proxy inner: " + e); }
                return this.build.call(this);
            };
        } catch (e) { console.log("[-] OkHttp3 Builder: " + e); }

        // ── 3. Ktor HttpClientEngineConfig proxy ─────────────────
        try {
            var KtorConfig = Java.use("io.ktor.client.engine.HttpClientEngineConfig");
            KtorConfig.$init.implementation = function () {
                KtorConfig.$init.call(this);
                try {
                    var addr = InetSock.$new(PROXY_HOST, PROXY_PORT);
                    var types = ProxyType.values();
                    var proxy = Proxy.$new(types[1], addr);
                    this.proxy.value = proxy;
                    console.log("[+] Ktor proxy injected");
                } catch (e) { console.log("[*] Ktor proxy.value: " + e); }
            };
        } catch (e) { console.log("[-] Ktor config: " + e); }

        // ── 4. SSL: TrustManager (trust all) ────────────────────
        try {
            var X509TrustManager = Java.use("javax.net.ssl.X509TrustManager");
            var TrustAll = Java.registerClass({
                name: "com.ira.bypass.TrustAll",
                implements: [X509TrustManager],
                methods: {
                    checkClientTrusted: function (chain, auth) { },
                    checkServerTrusted: function (chain, auth) { },
                    getAcceptedIssuers: function () { return []; }
                }
            });
            var SSLCtx = Java.use("javax.net.ssl.SSLContext");
            SSLCtx.init.implementation = function (km, tm, sr) {
                this.init.call(this, km, [TrustAll.$new()], sr);
                console.log("[+] SSLContext.init → trust-all");
            };
        } catch (e) { console.log("[-] TrustManager: " + e); }

        // ── 5. SSL: TrustManagerImpl (Conscrypt) ─────────────────
        try {
            var TMImpl = Java.use("com.android.org.conscrypt.TrustManagerImpl");
            TMImpl.verifyChain.implementation = function (untrusted, anchors, host, clientAuth, ocsp, sct) {
                console.log("[+] TrustManagerImpl bypassed → " + host);
                return untrusted;
            };
        } catch (e) { console.log("[-] TrustManagerImpl: " + e); }

        // ── 6. SSL: NetworkSecurityConfig pins ───────────────────
        try {
            Java.use("android.security.net.config.NetworkSecurityTrustManager")
                .checkPins.implementation = function (chain) {
                    console.log("[+] NSC pin bypassed");
                };
        } catch (e) { }
        try {
            Java.use("android.security.net.config.RootTrustManager")
                .checkServerTrusted.overloads.forEach(function (o) {
                    o.implementation = function () { console.log("[+] RootTrustManager bypassed"); };
                });
        } catch (e) { }

        // ── 7. SSL: OkHttp3 CertificatePinner ───────────────────
        try {
            var CertPin = Java.use("okhttp3.CertificatePinner");
            CertPin.check.overloads.forEach(function (o) {
                o.implementation = function (host) {
                    console.log("[+] OkHttp3 CertPin bypassed → " + host);
                };
            });
        } catch (e) { console.log("[-] CertificatePinner: " + e); }

        // ── 8. SSL: Ktor custom TrustManager (kf0) ───────────────
        try {
            Java.use("com.tatamotors.oneapp.kf0")
                .checkServerTrusted.implementation = function (c, a) {
                    console.log("[+] Ktor kf0.checkServerTrusted bypassed");
                };
        } catch (e) { console.log("[-] kf0: " + e); }

        // ── 9. SSL: Conscrypt sockets ────────────────────────────
        ["com.android.org.conscrypt.ConscryptFileDescriptorSocket",
            "com.android.org.conscrypt.OpenSSLSocketImpl"].forEach(function (cls) {
                try {
                    Java.use(cls).verifyCertificateChain.implementation = function () {
                        console.log("[+] " + cls.split(".").pop() + " bypassed");
                    };
                } catch (e) { }
            });

        // ── 10. SSL: WebView ─────────────────────────────────────
        try {
            Java.use("android.webkit.WebViewClient").onReceivedSslError.implementation =
                function (wv, handler, err) {
                    console.log("[+] WebView SSL → proceed()");
                    handler.proceed();
                };
        } catch (e) { }

        // ── 11. SSL: HostnameVerifier ────────────────────────────
        try {
            var HostnameVerifier = Java.use("javax.net.ssl.HostnameVerifier");
            var AllowAll = Java.registerClass({
                name: "com.ira.bypass.AllowAllHV",
                implements: [HostnameVerifier],
                methods: { verify: function (hostname, session) { return true; } }
            });
            Java.use("javax.net.ssl.HttpsURLConnection")
                .setDefaultHostnameVerifier(AllowAll.$new());
            console.log("[+] HostnameVerifier → allow-all");
        } catch (e) { console.log("[-] HostnameVerifier: " + e); }

        // ── 12. Request Logger ───────────────────────────────────
        try {
            var RealCall = Java.use("okhttp3.internal.connection.RealCall");
            RealCall.execute.implementation = function () {
                var req = this.request.call(this);
                var url = req.url().toString();
                var shouldLog = API_DOMAINS.some(function (d) { return url.indexOf(d) !== -1; });
                if (shouldLog) {
                    console.log("\n[📤] " + req.method() + " " + url);
                    console.log("[HDR] " + req.headers().toString().trim().replace(/\n/g, " | "));
                }
                var resp = this.execute.call(this);
                if (shouldLog) console.log("[📥] " + resp.code() + " " + resp.message());
                return resp;
            };
            console.log("[+] OkHttp3 request logger active");
        } catch (e) { console.log("[-] RealCall logger: " + e); }

        console.log("[+] SSL + Proxy hooks done\n");
    });


    // ── Root Detection Bypass ────────────────────────────────────
    setTimeout(function () {
        Java.perform(function () {
            // ADB detection
            var sdkVer = Java.use("android.os.Build$VERSION").SDK_INT.value;
            var settingClass = sdkVer <= 16
                ? "android.provider.Settings$Secure"
                : "android.provider.Settings$Global";
            try {
                var Settings = Java.use(settingClass);
                Settings.getInt.overloads.forEach(function (o) {
                    o.implementation = function (cr, name) {
                        if (name === "adb_enabled") { console.log("[+] ADB bypass"); return 0; }
                        return o.call(this, cr, name);
                    };
                });
            } catch (e) { }

            // Debug detection
            try {
                Java.use("android.os.Debug").isDebuggerConnected.implementation = function () { return false; };
            } catch (e) { }

            // RootBeer
            try {
                var RB = Java.use("com.scottyab.rootbeer.RootBeer");
                ["isRooted", "isRootedWithoutBusyBoxCheck", "detectRootManagementApps",
                    "detectPotentiallyDangerousApps", "detectTestKeys", "checkForBusyBoxBinary",
                    "checkForSuBinary", "checkSuExists", "checkForRWPaths", "checkForDangerousProps",
                    "checkForRootNative", "detectRootCloakingApps", "checkForMagiskBinary"].forEach(function (m) {
                        try { RB[m].overloads.forEach(function (o) { o.implementation = function () { return false; }; }); } catch (e) { }
                    });
                console.log("[+] RootBeer bypassed");
            } catch (e) { }

            // JailMonkey
            try {
                var JM = Java.use("com.gantix.JailMonkey.JailMonkeyModule");
                var HashMap = Java.use("java.util.HashMap");
                var FALSE = Java.use("java.lang.Boolean").FALSE.value;
                JM.getConstants.implementation = function () {
                    var h = HashMap.$new();
                    ["isJailBroken", "hookDetected", "canMockLocation", "isOnExternalStorage", "AdbEnabled"]
                        .forEach(function (k) { h.put(k, FALSE); });
                    return h;
                };
                console.log("[+] JailMonkey bypassed");
            } catch (e) { }

            // IRoot (CyberKatze)
            try {
                Java.use("de.cyberkatze.iroot.IRoot").isDeviceRooted.overload().implementation = function () { return false; };
                console.log("[+] IRoot bypassed");
            } catch (e) { }

            console.log("[+] Root detection bypass done");
        });
    }, 0);

})();


/* ====================== SCRIPT 3: pvcx API Request Hooks ====================== */
(function () {
    if (Java.available) {
        Java.perform(function () {
            var targets = [
                "pvcxqa.api.tatamotors",
                "pvcxuat.api.tatamotors",
                "pvcxdev.api.tatamotors",
                "pvcx.api.tatamotors"
            ];

            function isTarget(s) {
                if (!s) return false;
                for (var i = 0; i < targets.length; i++) {
                    if (s.toString().indexOf(targets[i]) !== -1) return true;
                }
                return false;
            }

            // OkHttp3 newCall hook
            try {
                var OkHttpClient = Java.use("okhttp3.OkHttpClient");
                OkHttpClient.newCall.overload("okhttp3.Request").implementation = function (req) {
                    var url = req.url().toString();
                    if (isTarget(url)) {
                        console.log("[pvcx] OkHttp newCall → " + url);
                        send({ type: "okhttp", url: url });
                    }
                    return this.newCall.call(this, req);
                };
            } catch (e) { }

            // Remote command interceptor
            try {
                var RIC = Java.use("okhttp3.internal.http.RealInterceptorChain");
                RIC.proceed.overload("okhttp3.Request").implementation = function (req) {
                    var url = req.url().toString();
                    if (url.indexOf("tatamotors") !== -1 && url.indexOf("remote-command") !== -1) {
                        console.log("\n[!] REMOTE CMD: " + req.method() + " " + url);
                        try {
                            var b = req.body();
                            if (b) {
                                var buf = Java.use("okio.Buffer").$new();
                                b.writeTo(buf);
                                console.log("[!] BODY: " + buf.readUtf8());
                            }
                        } catch (e) { }
                    }
                    var resp = this.proceed.call(this, req);
                    if (url.indexOf("tatamotors") !== -1 && url.indexOf("remote-command") !== -1) {
                        console.log("[!] RESPONSE: " + resp.code());
                    }
                    return resp;
                };
            } catch (e) { console.log("[-] RIC hook: " + e); }

            console.log("[+] pvcx API hooks installed → " + targets.join(", "));
        });
    }
})();


/* ====================== SCRIPT 4: Flutter libflutter.so Native SSL Bypass ====================== */
setTimeout(function () {
    var patterns = [
        "ff 03 05 d1 fd 7b 0f a9 bc de 05 94 08 0a 80 52 48 00 00 39",
        "f1 4f 01 a9 f3 7b 02 a9 16 00 40 f9 08 0a 80 52 48 00 00 39",
        "ff 03 05 d1 fd 7b 01 a9 08 0a 80 52 48 00 00 39"
    ];
    try {
        var m = Process.findModuleByName("libflutter.so");
        if (!m) { console.log("[*] libflutter.so not found (Flutter may not be loaded yet)"); return; }
        console.log("[*] libflutter.so found @ " + m.base);
        patterns.forEach(function (p) {
            try {
                Memory.scan(m.base, m.size, p, {
                    onMatch: function (addr) {
                        try {
                            Interceptor.attach(addr, { onLeave: function (rv) { rv.replace(1); } });
                            console.log("[+] Flutter SSL hook @ " + addr);
                        } catch (e) { }
                    },
                    onComplete: function () { }
                });
            } catch (e) { }
        });
    } catch (e) { console.log("[-] Flutter scan: " + e); }
}, 5000);
