# 🛡️ Advanced Recon & Vulnerability Mapping

## Phase 1: Infrastructure & Attack Surface
* **Passive Recon:** `subfinder -d target.com -all -o recon/subs.txt`
* **Alive Check:** `cat recon/subs.txt | httpx -sc -td -title -o recon/alive.txt`

---

## Phase 2: Content Discovery (Fuzzing)
> **Note:** Using your path `/usr/share/SecLists`

### 2.1 Directory Bruteforce
* **Command:** ```bash
    ffuf -u [https://target.com/FUZZ](https://target.com/FUZZ) \
    -w /usr/share/SecLists/Discovery/Web-Content/common.txt \
    -mc 200,301,302,403 -o recon/dirs.json
    ```

### 2.2 Sensitive File Discovery
* **Command:**
    ```bash
    ffuf -u [https://target.com/FUZZ](https://target.com/FUZZ) \
    -w /usr/share/SecLists/Discovery/Web-Content/raft-medium-files.txt \
    -e .php,.bak,.old,.env,.git,.json,.conf,.sql \
    -mc 200 -o recon/files.json
    ```

---

## Phase 3: Parameter Discovery (The "Entry Points")
* **Mining Parameters:** `waybackurls target.com | grep "=" | qsreplace -a | cut -d'=' -f1 | sort -u > recon/params.txt`
* **Backfilling with SecLists:**
    ```bash
    # Use this to find hidden parameters that aren't in history
    arjun -u [https://target.com/index.php](https://target.com/index.php) -w /usr/share/SecLists/Discovery/Web-Content/burp-parameter-names.txt
    ```

---

## Phase 4: Manual Analysis & Burp Suite Strategy
> Once you find an interesting endpoint (e.g., `/api/v1/user/settings`), move to Burp.

### 4.1 IDOR (Insecure Direct Object Reference)
* **The Test:** Capture a request that shows your profile.
* **The Move:** Change `id=123` to `id=122`. 
* **Advanced:** Try adding an ID to a request that doesn't have one (e.g., `GET /api/user` -> `GET /api/user?id=admin`).

### 4.2 Logic Flaws (The Money Makers)
* **Step Over:** If a process has Step 1, 2, and 3, try to skip Step 2 (the payment/verification step) and go straight to Step 3.
* **Quantity Manipulation:** In an e-cart, change the quantity from `1` to `0.01` or `-1`.

### 4.3 JWT Hacking
* **Check 1:** Change the `alg` to `None`.
* **Check 2:** Use your SecLists wordlist to crack the secret:
    ```bash
    hashcat -m 16500 jwt.txt /usr/share/SecLists/Passwords/Common-Credentials/10-million-password-list-top-10000.txt
    ```

---

## Phase 5: Reporting
* **Drafting:** Use your AI to summarize the impact. 
* **Example:** "Explain why an IDOR on the /settings page is a P2 (High) severity bug for a Bug Bounty program."