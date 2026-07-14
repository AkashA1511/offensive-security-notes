# The Elite Bug Hunter's Complete Playbook

---

## My Mindset Before Anything Else

Most hunters fail before they open a browser. They fail in how they think.

The average hunter opens a target, runs some tools, looks for easy XSS, finds nothing, switches programs. This is why most people make nothing on bug bounty.

The elite mindset is different:

**I am not looking for bugs. I am understanding a system deeply enough that bugs reveal themselves.**

Every target is an application built by humans, under deadline pressure, with assumptions that are sometimes wrong. My job is to find where the assumptions broke. That requires understanding, not scanning.

---

## Part 1 — Vulnerability Classes to Master

Do not try to find every type of bug. Master specific classes deeply. Here's exactly which ones and why.

### Tier 1 — Master These First (Highest ROI)

**IDOR (Insecure Direct Object Reference)**

This is the highest volume high/critical bug on most programs. Every application that has users, objects, and permissions has potential IDOR surface.

What to master:

- Horizontal IDOR (access another user's data at same privilege)
- Vertical IDOR (access higher privilege data)
- IDOR through indirect references (hashed IDs, GUIDs — don't assume non-sequential = safe)
- IDOR in API endpoints that the frontend doesn't show you
- Chained IDOR — read + write + delete combined for critical impact

Where to find it: Anywhere the application references an object that belongs to a user. Order IDs, invoice IDs, user profile IDs, document IDs, message IDs.

**SSRF (Server Side Request Forgery)**

Consistently one of the highest paying bugs. In cloud environments it leads directly to metadata credential theft which is critical.

What to master:

- Basic SSRF to internal services
- Blind SSRF (no response, but you can detect via DNS or timing)
- SSRF to cloud metadata endpoints (169.254.169.254 for AWS, metadata.google.internal for GCP)
- SSRF filter bypasses — IP encoding, IPv6, DNS rebinding, redirect chains
- SSRF through PDF generators, image processors, webhooks, URL previews

Where to find it: Any feature that fetches a URL you provide. Webhooks, import from URL, link preview, PDF generation, image upload from URL, integrations.

**Authentication and Authorization Flaws**

Not just "login page testing." Deep auth logic.

What to master:

- JWT attacks — alg:none, weak secrets, kid injection, header injection
- OAuth flaws — state parameter missing, redirect_uri bypass, token leakage in referrer
- Password reset flaws — token predictability, token reuse, host header injection
- Session management — fixation, insufficient invalidation on logout
- 2FA bypasses — response manipulation, code reuse, backup code abuse
- Account takeover chains — combining small flaws for full ATO

**Business Logic Vulnerabilities**

These are the hardest to find and the hardest to automate. AI cannot find these. This is where elite hunters live.

What to master:

- Price manipulation (negative quantities, currency confusion, discount stacking)
- Workflow bypass (skip step 2 of a 3-step process, does it still work?)
- Race conditions (two requests simultaneously — can I buy something twice with one payment?)
- Privilege assumption flaws (developer assumed user X can never reach endpoint Y — what if they do?)
- State confusion (what happens if I do things out of order?)

**Mass Assignment**

Underrated and consistently found in modern APIs.

What to master:

- Sending extra parameters in JSON that the server shouldn't accept but does
- Role escalation through mass assignment (adding "role":"admin" to a profile update)
- Finding hidden fields by reading JavaScript source, old API versions, mobile apps

### Tier 2 — Add These After Tier 1

- **XXE** — anywhere XML is processed, file uploads that parse XML
- **SSTI (Server Side Template Injection)** — any feature that reflects input in a template context
- **SQLi** — less common now but still exists, especially in older apps and less-tested endpoints
- **Open Redirect** — low severity alone but powerful when chained with OAuth or SSRF
- **CORS Misconfiguration** — when combined with authenticated endpoints, becomes high severity
- **HTTP Request Smuggling** — complex but extremely high paying when found

### Tier 3 — Specialist Territory (Later)

- RCE through deserialization
- XXE to RCE chains
- OAuth full account takeover chains
- Cache poisoning
- HTTP/2 specific attacks

---

## Part 2 — Target Selection

This is where most hunters waste the most time. Here's exactly how I choose.

### Rule 1 — Never Hunt Overcrowded Programs

If a program has been running for 5 years and has 50,000 submissions, the obvious attack surface is exhausted. Hunting there means competing with thousands of people for scraps.

**What I look for instead:**

- Programs that launched in the last 3-6 months
- Programs that just expanded their scope
- Companies that recently acquired another company (the acquired company's assets are often less tested)
- VDP (Vulnerability Disclosure Programs) converting to paid programs
- Private programs — get invited by building reputation on public ones first

### Rule 2 — Scope Size vs Competition Ratio

I want **large scope + low competition**. Not just large scope.

Large scope programs with small bounties attract fewer hunters. A program paying $500 max but with 50 web apps in scope is often more profitable than a program paying $10,000 max with 1 app that 10,000 people have already hammered.

### Rule 3 — Look for Complexity

Simple brochure websites have nothing. I look for applications with:

- User accounts and roles (IDOR surface)
- File upload features (XXE, stored XSS, SSRF surface)
- Payment flows (logic bugs, race conditions)
- API integrations with third parties (OAuth flaws, SSRF via webhooks)
- Import/export features (XXE, SSRF, injection)
- Admin panels even if out of scope (they reveal how the app thinks)
- Mobile app + web app (mobile often has less-tested endpoints)

### Rule 4 — Read the Program Page Like a Document

Most hunters skim the scope and start hacking. I read everything:

- Every excluded vulnerability — tells me what they've already fixed (and what class of bugs they have history with)
- Every safe harbor statement
- What they say is high/critical — tells me what they value
- Previous hall of fame — tells me what bugs have been found (so I look for variants, not the same bug)

---

## Part 3 — Reconnaissance — The Full Process

Recon is not running tools and collecting output. Recon is building a mental map of the target.

### Phase 1 — Passive Recon (Before Touching the Target)

**Understand the company first:**

- What does this company actually do? What's their core business?
- Where does money flow in their application?
- Who are their customers? (B2B vs B2C changes the attack surface completely)
- What tech stack are they likely using? (Check job postings — "We're hiring Django engineers" tells you the stack)

**Enumerate the asset landscape:**

- Subdomain enumeration: amass, subfinder, assetfinder, crt.sh, dnsx
- Don't just collect — understand what each subdomain is for
- Check Wayback Machine (web.archive.org) for old endpoints, old parameters, old JS files
- Google dorks: site:target.com filetype:pdf, site:target.com inurl:api, site:target.com "internal"
- GitHub dorking: search for the company name, find leaked keys, internal endpoints, hardcoded credentials
- Shodan/Censys for exposed infrastructure

**JavaScript file analysis — this is underused and high value:**

- Download every JS file from the target
- Search for: API endpoints, internal URLs, access tokens, S3 bucket names, GraphQL schemas
- Tool: LinkFinder, JSParser, or manual grepping

**API discovery:**

- Check if they have a public API documentation (Swagger, Postman collections)
- Look for /api/v1, /api/v2 — often v1 is less tested
- Check mobile app traffic (more on this below)

### Phase 2 — Active Recon (Now You Touch the Target)

**HTTP probing:**

- httpx on all discovered subdomains — what's actually live and returning what status codes
- Screenshot all live hosts — eyewitness or gowitness
- Look for outliers — login pages on unusual subdomains, admin panels, staging environments

**Technology fingerprinting:**

- Wappalyzer tells you frameworks, CMS, CDN
- Response headers reveal server tech, framework versions
- Error messages (force errors intentionally) reveal stack traces

**Content discovery:**

- Directory brute forcing with ffuf using a good wordlist (SecLists is your bible)
- Parameter discovery — arjun for finding hidden parameters
- Check robots.txt and sitemap.xml — developers hide things there they shouldn't

**Intercept everything with Burp:**

- Set Burp as proxy, browse the entire application as a normal user first
- Click every button, fill every form, use every feature
- Map the application before you attack it
- The Burp sitemap after this is your attack surface map

---

## Part 4 — The Hunting Process — How I Actually Find Bugs

### The Mental Model I Use

Every feature in an application answers one question: **"What assumption did the developer make here, and is that assumption enforced?"**

Developer assumption: "Only the owner of this order can view it" → Test: can I view another user's order? Developer assumption: "This URL fetches external content" → Test: can I make it fetch internal content? Developer assumption: "This price comes from the frontend" → Test: can I send a different price from the backend?

### My Daily Hunting Flow

**Step 1 — Feature mapping (30 minutes)**

I list every feature in the application. Every single one. Not attack surface — features.

- User registration and login
- Profile management
- Password reset
- File upload
- Messaging between users
- Payment flow
- Admin actions
- Export data
- Import data
- API integrations
- Notification settings
- Account deletion

Each feature is a potential bug location.

**Step 2 — Prioritize by impact**

I rank features by potential impact if broken:

- Payment flow broken = critical
- Account takeover possible = critical
- Another user's private data accessible = high
- Admin actions available to regular users = critical

I start with highest potential impact features.

**Step 3 — Test one feature completely before moving**

This is the discipline that separates good hunters from scattered ones.

I pick one feature. I test it completely — every parameter, every state, every role. Then I move to the next.

I do not jump around.

**Step 4 — The actual testing approach per feature**

For every feature I ask these questions:

_Authorization questions:_

- What happens if I do this as a logged-out user?
- What happens if I do this as a different user?
- What happens if I do this as a lower-privileged user?
- What object IDs are referenced? Can I change them?

_Input questions:_

- Where does user input go? What does the server do with it?
- Is input reflected anywhere? (XSS surface)
- Is input used in a query? (SQLi, NoSQLi surface)
- Is input used in a file path? (path traversal)
- Is input used to fetch a URL? (SSRF surface)

_State questions:_

- What is the expected sequence of operations?
- What happens if I skip a step?
- What happens if I repeat a step?
- What happens if I do two things simultaneously? (race conditions)

_Business logic questions:_

- What is the business rule here?
- What assumption is the code making?
- What happens if that assumption is violated?

---

## Part 5 — Intercepting and Analyzing Traffic

This is where Burp Suite is your main tool. Here's how I use it at depth.

**Burp setup I always have:**

- Scope locked to target — no noise
- Logger++ extension for filtering and searching through all requests
- Autorize extension — this is critical for IDOR testing (more below)
- Param Miner extension — finds hidden parameters automatically
- JS Miner — extracts endpoints from JS files automatically

**The Autorize workflow for IDOR testing:**

This is the fastest way to find IDOR at scale:

1. Log in as User A, put User A's session cookie in Autorize
2. Log in as User B in the browser
3. Browse the entire application as User B
4. Autorize automatically replays every request with User A's cookie
5. Flags any request where User A's cookie gets the same response as User B's cookie
6. Every flag is a potential IDOR

This is systematic. You will find things manual testing misses.

**The Repeater workflow:**

Every interesting request goes to Repeater immediately. Then I:

- Change every parameter value one at a time
- Try negative numbers, zero, very large numbers
- Try another user's ID
- Try removing parameters entirely
- Try adding parameters that shouldn't be there (mass assignment)
- Try changing the HTTP method (GET → POST → PUT → DELETE)

**The Intruder workflow:**

For fuzzing parameters at scale — finding hidden endpoints, testing for injection points, brute forcing where rate limiting isn't enforced.

---

## Part 6 — Mobile App Testing (Underused Goldmine)

Most hunters ignore mobile apps. This means less competition for the same backend.

**My mobile testing setup:**

- Android emulator (Genymotion or Android Studio AVD)
- Burp certificate installed in the emulator
- Frida for SSL pinning bypass when needed
- MobSF for static analysis

**What I look for specifically:**

- API endpoints that only the mobile app calls — these are often less tested
- Hardcoded API keys or tokens in the APK (use jadx to decompile, grep for "key", "token", "secret")
- Different API versions (mobile app might hit v1 while web hits v3 — v1 may have unfixed bugs)
- Features in the API that the mobile UI doesn't expose but the endpoint still accepts

**The decompile process:**

- Pull the APK: adb pull or from APKPure for testing
- Decompile with jadx-gui
- Search source for: api.target.com, /api/, Bearer, Authorization, secret, key, password
- Every endpoint you find that isn't in the web app is new attack surface

---

## Part 7 — Chaining Bugs for Critical Impact

This is where elite hunters separate themselves. Single bugs are often medium severity. Chained bugs become critical.

**Classic chains I look for:**

**Chain 1 — Open Redirect → OAuth Token Theft** Open redirect on target.com/redirect?url= OAuth flow uses redirect_uri=target.com/redirect Attacker steals OAuth token via redirect → Account takeover Severity: Critical

**Chain 2 — SSRF → Cloud Metadata → Credential Theft** SSRF to 169.254.169.254/latest/meta-data/iam/security-credentials/ Returns temporary AWS credentials Attacker can access S3 buckets, internal services Severity: Critical

**Chain 3 — IDOR → PII Exposure → Account Takeover** IDOR exposes other user's email + phone Password reset uses phone number Combine: take over any account Severity: Critical

**Chain 4 — Mass Assignment → Privilege Escalation** Profile update endpoint accepts extra fields Add "role":"admin" or "is_admin":true Access admin functionality Severity: Critical

**The chaining mindset:** When I find a low/medium bug, I immediately ask: "What can I do _with_ this?" A bug is not the end. It is a starting point.

---

## Part 8 — Writing the Report

A bad report on a critical bug gets triaged slowly, sometimes incorrectly, and occasionally rejected. A good report gets paid fast.

**My report structure every time:**

**Title:** One line, clearly states the vulnerability type and impact Bad: "IDOR vulnerability found" Good: "IDOR in /api/v2/invoices/{id} allows any authenticated user to read, modify, and delete invoices belonging to other accounts"

**Severity:** State it and justify it with CVSS or impact reasoning

**Summary:** 3-5 sentences. What is the vulnerability, where is it, what can an attacker do with it.

**Impact:** Write this from a business perspective. Not "attacker can read user data" — "attacker can access the financial records, personal information, and private documents of every customer on the platform, enabling fraud, identity theft, and regulatory violations."

**Steps to Reproduce:** Numbered. Every step. Assume the reader has never used the application.

1. Log in as User A (attacker) — credentials provided
2. Navigate to [URL]
3. Intercept the request with Burp Suite
4. Change parameter X from [value] to [value]
5. Observe response contains User B's data

**Proof of Concept:** Screenshots and/or video of every step. Burp request and response in full. Never make the triager work to reproduce it.

**Remediation:** Suggest a fix. Shows you understand the vulnerability, not just the exploit.

**Test Accounts:** Always create dedicated test accounts. Never use real user data in reports.

---

## Part 9 — The Habits That Actually Make Money

**Hunt in sessions, not randomly:** 3-hour focused blocks. Phone away. One target, one feature area, full attention. Random 20-minute sessions produce nothing.

**Document everything even if it seems useless:** That parameter that behaved strangely but didn't lead anywhere — note it. Three months later you find a related bug and that note completes the chain.

**Retest old bugs in new versions:** Companies patch bugs and then reintroduce them 6 months later in a different form. If you found an IDOR before, check if the pattern exists in newly added features.

**Read every disclosed report on your target:** Before hunting a new program, read every disclosed report on HackerOne or Bugcrowd for that company. Understand what's been found. Then look for the same vulnerability class in untested features.

**Time targets strategically:** Hunt new features immediately after releases. When a company ships a new feature, it hasn't been tested by anyone yet. Follow company blogs, Twitter, changelogs.

**Track your own patterns:** What bug type do you find most often? What features do you look at that others miss? Double down on your own strengths.

---

## The One Page Summary of My Entire Process

```
1. Choose target — new program, large scope, complex app
2. Read program page completely
3. Understand the business — what does this company do?
4. Passive recon — subdomains, JS files, GitHub, Wayback
5. Active recon — live hosts, tech fingerprinting, content discovery
6. Map all features — list every single one
7. Prioritize by potential impact
8. Test one feature completely — all authorization, input, state, logic questions
9. Intercept with Burp — Autorize running the whole time
10. Find a bug → ask "what can I chain this with?"
11. Write a clear, complete report with full reproduction steps
12. Move to next feature
```

The hunters making $200k+ per year on bug bounty are not smarter. They are more systematic, more patient, and they go deeper on fewer targets rather than shallow on many.

That's the entire game.
