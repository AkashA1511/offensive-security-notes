- Censys API key:
- - SecurityTrails API key:
- - VirusTotal API key: subfinder -d example.com --set-config VIRUSTOTAL_API_KEY=your_api_key


## Step 3: API Keys to Collect

Here's every provider subfinder supports, what it's for, and how to get the key:

|Provider|Free Tier|Get Key At|
|---|---|---|
|**Shodan**|Yes (limited)|shodan.io/account|
|**Censys**|Yes|censys.io/register|
|**VirusTotal**|Yes|virustotal.com/gui/my-apikey|
|**SecurityTrails**|Yes (50 req/mo)|securitytrails.com|
|**Chaos** (ProjectDiscovery)|Invite only|chaos.projectdiscovery.io|
|**FOFA**|Yes|fofa.info|
|**Hunter.io**|Yes|hunter.io/api-keys|
|**Passivetotal / RiskIQ**|Yes|community.riskiq.com|
|**Binaryedge**|Yes|binaryedge.io|
|**Fullhunt**|Yes|fullhunt.io|
|**Intelx**|Yes|intelx.io/account|
|**LeakIX**|Yes|leakix.net|
|**Netlas**|Yes|netlas.io|
|**Quake (360)**|Yes|quake.360.net|
|**ZoomEye**|Yes|zoomeye.org|
|**Whoisxmlapi**|Yes|whoisxmlapi.com|
|**Robtex**|Free, no key|—|
|**DNSrepo**|Free, no key|—|
|**Crtsh**|Free, no key|—|
|**Bufferover**|Free, no key|—|


hen check if the config was created:

bash

```bash
ls ~/.config/subfinder/
```

You should see `provider-config.yaml` there.

---

## Step 3: Edit the Config File

bash

```bash
nano ~/.config/subfinder/provider-config.yaml
```



Don't worry about limits at all — subfinder handles this gracefully. If a source runs out of quota or has no key, it simply skips that source rather than failing the whole scan. So your tool will always work, it'll just use whatever sources still have quota left.

Here's the full breakdown of everything worth adding:

---

## 🟢 Tier 1 — Add These First (Best Free Value)

|Provider|Free Limit|Get Key|
|---|---|---|
|**GitHub**|Unlimited (rotate multiple tokens)|github.com → Settings → Developer Settings → PAT|
|**VirusTotal**|500 req/day|virustotal.com/gui/my-apikey|
|**Shodan**|Limited free|account.shodan.io|
|**SecurityTrails**|2000 results/req (free)|securitytrails.com/app/account/credentials|
|**Censys**|250 req/month|search.censys.io/account/api|
|**AlienVault**|✅ No key needed|—|
|**HackerTarget**|✅ No key needed|—|
|**CertSpotter**|Free tier|sslmate.com/account/api_credentials|

> 💡 **GitHub tip** — create 3–4 GitHub accounts and add all their PAT tokens. Subfinder supports multiple tokens per source and rotates them automatically.

---

## 🟡 Tier 2 — Good Free Options

|Provider|Free Limit|Get Key|
|---|---|---|
|**Netlas**|50 req/day|netlas.io|
|**Fullhunt**|50 req/day|fullhunt.io|
|**BinaryEdge**|Trial available|app.binaryedge.io/account/api|
|**LeakIX**|Free tier|leakix.net|
|**Bevigil**|Limited free|bevigil.com|
|**Intelx**|Free tier|intelx.io/account → format: `host:api_key`|
|**PassiveTotal (RiskIQ)**|Free tier|community.riskiq.com/settings → format: `user:key`|
|**WhoisXMLAPI**|Free tier|whoisxmlapi.com|
|**Chaos**|Apply for access|chaos.projectdiscovery.io|

---

## 🔴 Chinese Platforms (Good Coverage, Free Signup)

|Provider|Notes|Get Key|
|---|---|---|
|**ZoomEye**|Great Chinese internet data, free tier|zoomeye.org/profile → format: `user:password`|
|**FOFA**|Massive scan database, free tier available|fofa.info → format: `email:api_key`|
|**Quake (360)**|Free tier, solid coverage|quake.360.net → format: `api_key`|
|**ThreatBook**|Free tier|threatbook.cn|
|**Chinaz**|Free, Chinese DNS data|chinaz.com|

> These platforms have great coverage especially for Chinese infrastructure companies in scope. Worth signing up!

---

## ✅ No Key Needed (Work Automatically)

These are already working in your config even with `[]`:

- `alienvault`, `hackertarget`, `robtex`, `dnsdumpster`, `crtsh`, `bufferover`, `certspotter` (without key), `dnsrepo`

---

## Your Final Config Should Look Like:

```yaml
github:
  - ghp_token1xxxxxxxxxxxx
  - ghp_token2xxxxxxxxxxxx
  - ghp_token3xxxxxxxxxxxx    # Add as many as you can!

virustotal:
  - your_vt_key

shodan:
  - your_shodan_key

securitytrails:
  - your_st_key

censys:
  - your_api_id:your_api_secret

netlas:
  - your_netlas_key

fullhunt:
  - your_fullhunt_key

leakix:
  - your_leakix_key

bevigil:
  - your_bevigil_key

intelx:
  - 2.intelx.io:your_api_key

passivetotal:
  - youremail@gmail.com:your_api_key

whoisxmlapi:
  - your_key

zoomeyeapi:
  - youremail:yourpassword

fofa:
  - youremail@gmail.com:your_api_key

quake:
  - your_quake_key

threatbook:
  - your_key

chinaz:
  - your_key
```

---

## Pro Tip — Run With All Sources:

```bash
subfinder -d target.com -all -v
```

The `-v` flag will show exactly which sources responded and which were skipped due to no key or exhausted quota. That way you always know what's working! 🎯