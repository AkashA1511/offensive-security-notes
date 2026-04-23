#  1.Shodan ASN

Find Ips   
ASN = Autonomous System Number.  
  
Target.com might live on AS16509 (Amazon AWS).  
  
But TargetCorp.com (internal corp site) might live on AS12345 (Legacy On-Prem Data Center).  
  
# Shodan   
You have a list of IPs from subfinder or amass intel. You dumped them into Shodan CLI.  
  
Shodan Command to Rule Them All:  
  
bash  
shodan download target_ips.json.gz net:123.123.123.0/24  
shodan parse --fields ip_str,port,org,hostnames,domains,http.title,http.server,ssl.cert.issuer.CN,http.component_list target_ips.json.gz  
What are you looking for? (The "Oh Shit" List)  
  
http.title: "Index of /" -> Directory listing (CWE-548).  
  
http.server: "Microsoft-IIS/6.0" -> Legacy system. Do not scan aggressively. Do manual inspection for WebDAV or .asp source disclosure.  
  
port: 27017 (MongoDB) -> Check for NoSQL injection later, or just check if auth is disabled. Shodan filter: product:"MongoDB" port:27017 -authentication.  
  
ssl.cert.issuer.CN: "*.dev.target.com" -> Wildcard cert for dev environment. This IP is GOLD.  
  
http.favicon.hash mismatch. If the favicon belongs to a Cisco Router or Apache Tomcat, but the domain is api.target.com, you just found a misconfigured proxy.  

1. **### Step 1: Visual Sorting with** **`   ### aquatone   `** **###  or** **`   ### gowitness   `**

cat alive_200.txt | aquatone -out ./screenshots  
# OR (faster)  
gowitness file -f alive_200.txt --chrome-window-x 1920 --chrome-window-y 1080  

### **What to look for in the screenshot gallery:**

- **Login Panels with "Forgot Password?"** -> This is where **CWE-200** lives (Username Enumeration).

- **Blank White Pages with JSON errors.** -> API misconfigs.

- **"Welcome to JBoss"** or **"Apache Tomcat"** default pages. -> Default creds or `/manager/html` exposed.

- **"Swagger UI"** page title. -> **Immediate P1 potential.** Check `/swagger-ui.html`, `/api-docs`, `/v2/api-docs`, `/v3/api-docs`

1. Fuzz for backup and configs

2. Waybackurls, gau, gauplus, uro

# Fetch every URL ever seen for *.target.com  
echo "target.com" | gauplus --subs --providers wayback,commoncrawl,otx,urlscan | uro | grep -E "\.json|\.yaml|\.xml|\.js|\.php|\.aspx|\.do|\.action|api|v1|v2|v3|graphql|internal|admin|backup|swagger" | anew historical_urls.txt

1. The attack surface reduction
    1. Filter 403 status code and try to bypass it

I hear you. You've done the gathering—now you're staring at a pile of subdomains and URLs wondering *what actually matters*. You want the bridge between "I have a list of 200 OKs" and "I found a valid P1."  
  
Let's strip away IDOR and Auth. Let's talk pure **Reconnaissance Exploitation** and **CWE-200 (Information Disclosure)**.  
  
### Part 1: What is ASN and Why Should You Care?  
  
**ASN** = **Autonomous System Number**.  
Think of an ASN as the **Postal Code for a Company's entire network infrastructure**.  
  
- **Target.com** might live on `AS16509` (Amazon AWS).  
- But **TargetCorp.com** (internal corp site) might live on `AS12345` (Legacy On-Prem Data Center).  
  
**The 0.1% Hunter Mindset:** You find the *parent company's* ASN. You scan that ASN for *any* IP with port 443 open. You find `vpn.targetinternal.net` or `jenkins-build.target.com`. **This is how you find the assets NOT in scope but connected to the internet with default creds.**  
  
**How to Find ASN:**  
```bash  
# Use BGP.HE.NET (Web UI) or CLI tools  
whois -h whois.cymru.com " -v $(dig +short target.com A)"  
# Output: AS16509 AMAZON-02, US  
```  
  
### Part 2: I Found IPs on Shodan. Now What?  
  
You have a list of IPs from `subfinder` or `amass intel`. You dumped them into Shodan CLI.  
  
**Shodan Command to Rule Them All:**  
```bash  
shodan download target_ips.json.gz net:123.123.123.0/24  
shodan parse --fields ip_str,port,org,hostnames,domains,http.title,http.server,ssl.cert.issuer.CN,http.component_list target_ips.json.gz  
```  
  
**What are you looking for? (The "Oh Shit" List)**  
1.  **`http.title: "Index of /"`** -> Directory listing (CWE-548).  
2.  **`http.server: "Microsoft-IIS/6.0"`** -> Legacy system. *Do not scan aggressively. Do manual inspection for WebDAV or .asp source disclosure.*  
3.  **`port: 27017` (MongoDB)** -> Check for NoSQL injection later, or just check if auth is disabled. **Shodan filter:** `product:"MongoDB" port:27017 -authentication`.  
4.  **`ssl.cert.issuer.CN: "*.dev.target.com"`** -> Wildcard cert for dev environment. This IP is GOLD.  
5.  **`http.favicon.hash` mismatch**. If the favicon belongs to a **Cisco Router** or **Apache Tomcat**, but the domain is `api.target.com`, you just found a misconfigured proxy.  
  
---  
  
### Part 3: The Subdomain Triage (The "What Now?" Phase)  
  
You have `alive_200.txt` with 2,000 subdomains. You cannot open them all. You need to **cluster and gut-check**.  
  
**Step 1: Visual Sorting with `aquatone` or `gowitness`**  
This saves 3 hours of clicking.  
```bash  
cat alive_200.txt | aquatone -out ./screenshots  
# OR (faster)  
gowitness file -f alive_200.txt --chrome-window-x 1920 --chrome-window-y 1080  
```  
**What to look for in the screenshot gallery:**  
- **Login Panels with "Forgot Password?"** -> This is where **CWE-200** lives (Username Enumeration).  
- **Blank White Pages with JSON errors.** -> API misconfigs.  
- **"Welcome to JBoss"** or **"Apache Tomcat"** default pages. -> Default creds or `/manager/html` exposed.  
- **"Swagger UI"** page title. -> **Immediate P1 potential.** Check `/swagger-ui.html`, `/api-docs`, `/v2/api-docs`, `/v3/api-docs`.  
  
**Step 2: Content Discovery for Hidden Gems (CWE-200 Focus)**  
You want files developers forgot. This is not fuzzing for `/admin/login`. This is fuzzing for **BACKUPS** and **CONFIGS**.  
  
**Targeted Wordlist (Use `feroxbuster` with these specific extensions):**  
```bash  
feroxbuster -u https://subdomain.target.com -w /path/to/raft-small-words.txt -x php,asp,aspx,bak,backup,zip,tar.gz,old,sql,env,log,yml,yaml,json,conf,config --filter-status 403,404 --rate-limit 5  
```  
**Key Things to Catch in Output (200 OKs):**  
- `.env` -> Database credentials, API keys, APP_KEY.  
- `.git/config` -> Internal repo URL.  
- `wp-config.php.bak` -> MySQL root password in plaintext.  
- `sitemap.xml.gz` -> Hidden admin URLs.  
- `composer.json` / `package.json` -> Internal package registry URLs, exact version numbers (vulnerable versions).  
  
### Part 4: JavaScript Analysis (The Manual Goldmine)  
  
You asked *specifically* how to find JS files and scrape them. Here is the exact, no-bullshit manual method used when automation fails.  
  
**Step 1: Extracting JS URLs from the Homepage Manually**  
Do not rely on `waybackurls` for current JS. It gives you old, deleted code. You want **today's** secrets.  
1.  Open Browser DevTools (`F12`).  
2.  Go to **Sources** Tab.  
3.  **Ctrl+O** (Open File). Type `.js`.  
4.  You see all loaded scripts. Right-click the **Top Level Folder** (e.g., `target.com`) -> **Save all as HAR with content**.  
  
**Step 2: The Regex Scan (Do this in your Terminal)**  
Save that HAR file, convert to text, or just use the CLI tool `mantra` / `unfurl`.  
  
**Manual Secret Extraction (Most Reliable):**  
```bash  
# Get all JS URLs from live subdomains  
cat alive_200.txt | waybackurls | grep "\.js$" | httpx -mc 200 -content-type | grep "application/javascript" | cut -d ' ' -f1 > js_urls_live.txt  
  
# Download them to a folder  
mkdir js_files && cd js_files  
cat ../js_urls_live.txt | while read url; do wget -q "$url"; done  
  
# Use `gf` (by tomnomnom) to find AWS keys, etc.  
gf aws-keys *.js  
gf base64 *.js  # Then decode the long strings  
gf ip *.js      # Internal IPs (10.x.x.x, 172.16.x.x)  
```  
  
**The "Sensitive Data" Manual Search (Use VSCode):**  
Open the folder in **VSCode**. Hit `Ctrl+Shift+F`.  
Search for **these exact strings** (This is how I find CWE-200 in 5 minutes):  
1.  **`v1/`** or **`/internal/`** -> This reveals API route structures hidden from UI.  
2.  **`authorization: `** -> Sometimes devs leave test Bearer tokens in comments.  
3.  **`debug: true`** -> Feature flags. Flip it to `false` in the console, refresh, see if you get admin tools.  
4.  **`s3.amazonaws.com`** -> Look for the bucket name. Check if it's **publicly listable**.  
    - **Test:** `aws s3 ls s3://bucket-name-found-in-js --no-sign-request`  
5.  **`GraphQL` endpoint strings** -> If you see `/graphql`, test for Introspection later.  
  
### Part 5: How to Find CWE-200 (Information Disclosure) Manually  
  
You don't need a scanner for this. You need to observe **Pattern Failures**.  
  
**Pattern 1: The `.git` Folder Exposure**  
- **Test:** Append `/.git/config` to any subdomain.  
- **Outcome:** If you see `[core] repositoryformatversion = 0`, you can use `git-dumper` to clone the entire source code of the application.  
- **Command:** `./git-dumper.sh https://target.com/.git/ ./output_folder`  
  
**Pattern 2: Verbose Stack Traces (Spring Boot / Django)**  
- **Test:** Go to `/api/user` and change the `Accept: application/json` header to **`Accept: application/x-www-form-urlencoded`** or **`Accept: text/html`**.  
- **Outcome:** The server crashes because it doesn't know how to serialize HTML. The error page reveals:  
    - Full file paths (`/var/www/html/vendor/laravel/...`)  
    - SQL Query structure (`SELECT * FROM users WHERE id = ?`)  
    - Framework version (Laravel 8.3.2)  
  
**Pattern 3: Unprotected API Endpoints That Leak All Users (Pre-IDOR)**  
- **Recon Step:** In JS files, look for `fetch("/api/users")`.  
- **Manual Test:** Visit `https://target.com/api/users?limit=100`.  
- **Scenario:** They thought hiding the "Admin Panel" button was security. They forgot to secure the API route. This is **Not IDOR** (you aren't changing IDs). This is **Direct Endpoint Exposure (CWE-200)** . This is a $3k bug at minimum.  
  
**Pattern 4: The "Server" Header Leak**  
- **Command:** `curl -I https://target.com | grep Server`  
- **Find:** `Server: nginx/1.14.0 (Ubuntu)`  
- **Next Step:** Search Google for `Nginx 1.14.0 Ubuntu exploit`. You find **CVE-2021-23017** (Request Smuggling). You now have a targeted attack path based purely on a header leak.  
  
### The Workflow Summary (What to do TOMORROW)  
  
1.  **Open `alive_200.txt`.**  
2.  Run **`gowitness`**. Look for Swagger UI in the thumbnails.  
3.  Pick the **ugliest** looking domain (the one that looks like it was built in 2004 with `.aspx`). This is your highest probability target for CWE-200.  
4.  Run **`feroxbuster`** with `-x bak,zip,old,env` on that single domain.  
5.  Open DevTools, pull the JS files, search for `pass` or `token` or `s3`.  
6.  If you find **nothing** in 30 mins, move to the next domain. **Speed is the 0.1% advantage.**