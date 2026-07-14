# do this things asap
# Phase 0: Core setup

Before deep learning, set up your system.

## Tools you should have

### Notes

- Obsidian
    
- GitHub private repo for notes/tools
    
- One folder for labs
    
- One folder for scripts
    
- One folder for case studies
    

### Web testing

- Burp Suite
    
- Caido optional
    
- Postman / Insomnia
    
- ffuf
    
- httpx
    
- nuclei
    
- jq
    
- curl
    
- Python requests
    
- browser devtools
    

### Reverse/thick client

- Procmon
    
- Process Explorer
    
- Autoruns
    
- Wireshark
    
- Fiddler / Burp
    
- dnSpyEx / ILSpy
    
- Ghidra
    
- x64dbg
    
- PEStudio
    
- Detect It Easy
    
- Sysinternals Suite
    

### Programming

- Python
    
- JavaScript
    
- C basics
    
- C# basics
    
- SQL
    
- Bash
    
- PowerShell
    

---

# Phase 1: Web fundamentals

You should be very strong here. Not “I know HTTP,” but **I can reason through any request flow**.

## Checklist

### HTTP

You should understand:

- methods: GET, POST, PUT, PATCH, DELETE
    
- headers
    
- cookies
    
- status codes
    
- redirects
    
- caching
    
- content types
    
- multipart requests
    
- JSON APIs
    
- WebSockets basics
    

### Browser behavior

Learn:

- Same-Origin Policy
    
- CORS
    
- cookies: `HttpOnly`, `Secure`, `SameSite`
    
- localStorage vs sessionStorage
    
- DOM behavior
    
- CSP basics
    
- frontend routing
    
- browser devtools
    

### Authentication

Learn deeply:

- login flow
    
- session-based auth
    
- JWT auth
    
- refresh tokens
    
- password reset
    
- email verification
    
- OTP logic
    
- MFA bypass
    
- account recovery
    
- OAuth/OIDC
    

### Authorization

This is your money area.

Learn:

- vertical privilege escalation
    
- horizontal privilege escalation
    
- IDOR/BOLA
    
- tenant isolation
    
- organization/workspace access
    
- role-based access control
    
- object-level permission checks
    
- function-level permission checks
    
- admin/user boundary
    
- API authorization mistakes
    

### Data layer

Learn:

- SQL basics
    
- joins
    
- transactions
    
- isolation levels basics
    
- NoSQL basics
    
- ORM behavior
    
- mass assignment
    
- hidden fields
    
- object mapping
    

---

# Phase 2: Web vulnerability checklist

This is your main PortSwigger/bounty checklist.

## 1. Access control

You should master:

- IDOR
    
- BOLA
    
- BFLA
    
- forced browsing
    
- missing server-side checks
    
- role tampering
    
- org ID / tenant ID bypass
    
- object ownership bypass
    
- admin API exposure
    
- user-to-user data access
    
- invitation/member role bugs
    

### Build lab

Create app with:

```text
/users/{id}
/api/invoices/{id}
/api/org/{org_id}/members
/admin/users
```

Intentionally forget ownership checks.

Then attack it with two users.

---

## 2. Authentication bugs

Master:

- username enumeration
    
- brute-force protection bypass
    
- rate-limit bypass
    
- weak password reset
    
- token reuse
    
- missing token invalidation
    
- MFA bypass
    
- remember-me cookie flaws
    
- session fixation
    
- password change without old password
    
- email change takeover
    

### Build lab

Create:

```text
/login
/forgot-password
/reset-password
/mfa
/change-email
/change-password
```

Break each flow manually.

---

## 3. Business logic

Master:

- price manipulation
    
- coupon abuse
    
- negative quantity
    
- workflow skipping
    
- replaying old steps
    
- state confusion
    
- referral abuse
    
- subscription downgrade/upgrade abuse
    
- cart/checkout mismatch
    
- refund abuse
    

### Build lab

Create a small shop:

```text
cart
coupon
checkout
wallet balance
refund
gift card
```

Then try to make money appear.

---

## 4. Race conditions

This is advanced and high value.

Master:

- check-then-act bugs
    
- double spending
    
- coupon double use
    
- wallet race
    
- invite race
    
- password reset race
    
- email verification race
    
- multi-endpoint race
    
- last-byte sync concept
    
- database locking basics
    

### Build lab

Bad flow:

```text
check balance
create order
deduct balance
```

Then send parallel requests.

Fix with:

- transactions
    
- row lock
    
- atomic update
    
- idempotency key
    

---

## 5. SQL injection

You already did some labs, but learn professionally.

Master:

- error-based SQLi
    
- union SQLi
    
- blind boolean SQLi
    
- time-based SQLi
    
- second-order SQLi
    
- login bypass
    
- ORDER BY injection
    
- JSON SQLi
    
- ORM injection
    
- SQLi impact proof
    

### Build lab

Create vulnerable endpoints:

```text
/search?q=
/login
/sort?order=
/user?id=
```

Then fix using prepared statements.

---

## 6. XSS

You didn’t mention XSS much, so add it.

Master:

- reflected XSS
    
- stored XSS
    
- DOM XSS
    
- context-based payloading
    
- HTML context
    
- attribute context
    
- JavaScript string context
    
- URL context
    
- CSP bypass basics
    
- account takeover through XSS
    
- token/session impact limitations
    

### Build lab

Create:

```text
/comments
/profile?name=
/search?q=
```

Render user input in different contexts.

---

## 7. SSRF

Master:

- basic SSRF
    
- blind SSRF
    
- cloud metadata
    
- localhost targeting
    
- internal port probing
    
- DNS rebinding concept
    
- URL parser bypass
    
- allowlist bypass
    
- SSRF through PDF/image/webhook/import features
    

For real bounty, keep testing safe and within scope.

### Build lab

Create:

```text
/fetch?url=
/webhook-test
/import-image?url=
```

Then restrict allowlist badly and bypass it.

---

## 8. File upload

Master:

- extension bypass
    
- MIME bypass
    
- magic bytes
    
- path traversal in filename
    
- overwrite attacks
    
- stored XSS via SVG/HTML
    
- polyglot files
    
- image processing bugs conceptually
    
- public bucket exposure
    
- malware upload impact limits
    

### Build lab

Create upload feature with:

```text
avatar upload
document upload
image resize
download by filename
```

Break it.

---

## 9. Path traversal / file read

Master:

- `../`
    
- encoded traversal
    
- absolute path bypass
    
- Windows path tricks
    
- null byte concept
    
- file download bugs
    
- ZIP slip
    
- archive extraction bugs
    

### Build lab

Create:

```text
/download?file=
/view-template?name=
/extract-zip
```

---

## 10. Deserialization

Master basics:

- what serialization is
    
- insecure object deserialization
    
- PHP serialize
    
- Java deserialization concept
    
- Python pickle
    
- .NET deserialization concept
    
- signed vs unsigned serialized data
    

You don’t need to become Java deserialization monster immediately, but understand the idea.

---

## 11. SSTI

Master:

- template engines
    
- expression execution
    
- context detection
    
- Jinja2 basics
    
- Twig basics
    
- Handlebars basics
    
- sandbox concept
    
- file read/RCE chain in labs
    

### Build lab

Flask app with unsafe template rendering.

---

## 12. XXE

Master:

- XML entities
    
- external entity
    
- file read
    
- SSRF via XXE
    
- blind XXE
    
- SOAP/XML APIs
    

This still appears in enterprise apps.

---

## 13. Request smuggling

This is advanced. Don’t start here, but learn basics.

Master:

- `Content-Length`
    
- `Transfer-Encoding`
    
- front-end/back-end desync
    
- CL.TE
    
- TE.CL
    
- impact: auth bypass, cache poisoning, request hijacking
    

Do PortSwigger labs later.

---

## 14. OAuth/OIDC

Very important for modern apps.

Master:

- authorization code flow
    
- redirect URI validation
    
- state parameter
    
- nonce
    
- token substitution
    
- account linking bugs
    
- email trust issues
    
- open redirect chaining
    
- misconfigured clients
    

### Build lab

Use a small OAuth demo app or read flows deeply.

---

## 15. GraphQL

Master:

- introspection
    
- broken authorization
    
- batching abuse
    
- depth abuse
    
- IDOR through object IDs
    
- hidden mutations
    
- mass assignment
    

---

# Phase 3: API security roadmap

Since modern bug bounty is mostly API, get strong here.

## Checklist

You should test:

```text
GET /api/user/123
POST /api/user/update
PUT /api/user/123
DELETE /api/user/123
POST /api/org/1/invite
POST /api/admin/users
```

For every endpoint ask:

```text
Can user A access user B?
Can normal user access admin function?
Can I change role?
Can I change price/status?
Can I add hidden fields?
Can I skip workflow?
Can I replay request?
Can I call old API version?
Can I change org_id/team_id/workspace_id?
```

## API-specific bugs

Learn:

- BOLA
    
- BFLA
    
- mass assignment
    
- excessive data exposure
    
- rate limit bypass
    
- object property tampering
    
- versioned API bugs
    
- mobile API hidden endpoints
    
- GraphQL authorization
    
- webhook signature bugs
    

---

# Phase 4: Thick client roadmap

This is where you can become rare.

## 1. Windows basics

Learn:

- users and groups
    
- UAC
    
- services
    
- scheduled tasks
    
- registry
    
- file permissions
    
- environment variables
    
- process privileges
    
- DLL search order
    
- named pipes
    
- local ports
    

---

## 2. Thick client testing checklist

For every app, check:

```text
Where is it installed?
Who can write to install folder?
Does it run as admin?
Does it install a service?
What DLLs does it load?
Any missing DLLs?
Any writable DLL path?
Does it store secrets locally?
Does it use DPAPI?
Does it use SQLite/config/XML/registry?
Does it validate TLS certificates?
Can traffic be intercepted?
Does client enforce authorization?
Can APIs be called directly?
Are updates signed?
Are logs leaking secrets?
```

---

## 3. DLL hijacking

Master:

- DLL search order
    
- missing DLL
    
- writable directories
    
- privileged process context
    
- service DLL hijacking
    
- PATH hijacking
    
- binary planting
    
- safe DLL loading mitigations
    

### Build lab

C/C# app:

```c
LoadLibrary("helper.dll")
```

Run with different permissions.

Use Procmon.

---

## 4. Insecure local storage

Master:

- config files
    
- SQLite DB
    
- registry storage
    
- logs
    
- temp files
    
- hardcoded secrets
    
- weak encryption
    
- DPAPI misuse
    
- machine-level vs user-level protection
    

---

## 5. Client-server trust bugs

Very important.

Learn:

- client-side role checks
    
- hidden admin buttons
    
- API direct calls
    
- hardcoded API keys
    
- offline license checks
    
- patching client-side validation
    
- replaying thick-client API requests
    

---

## 6. Update mechanism bugs

Learn:

- unsigned updates
    
- insecure update URL
    
- HTTP update download
    
- writable update folder
    
- DLL replacement
    
- executable replacement
    
- weak signature validation
    

---

# Phase 5: Reverse engineering roadmap

You don’t need to become malware expert first. Become good enough to understand applications.

## 1. Basic architecture

Learn:

- CPU registers
    
- stack
    
- heap
    
- function calls
    
- calling conventions basics
    
- strings
    
- branches
    
- loops
    
- memory addresses
    

---

## 2. File formats

Learn:

- PE files for Windows
    
- ELF basics for Linux
    
- sections
    
- imports
    
- exports
    
- entry point
    
- symbols
    
- strings
    

---

## 3. Static analysis

Tools:

- Ghidra
    
- IDA Free optional
    
- strings
    
- Detect It Easy
    
- PEStudio
    
- ILSpy/dnSpyEx for .NET
    

Skills:

```text
Find interesting strings
Find imported APIs
Trace function references
Find auth/license logic
Identify crypto usage
Identify file/registry/network operations
```

---

## 4. Dynamic analysis

Tools:

- x64dbg
    
- Procmon
    
- Process Monitor
    
- Process Explorer
    
- Wireshark
    
- Fiddler/Burp
    

Skills:

```text
Set breakpoint
Step into/over
Watch registers
Watch memory
Patch conditional jump
Trace API calls
Observe file/registry/network behavior
```

---

## 5. .NET reversing

This is very useful for thick clients.

Learn:

- decompile with dnSpyEx/ILSpy
    
- search strings
    
- inspect config
    
- inspect API endpoints
    
- find crypto keys
    
- find auth logic
    
- patch branch in lab
    
- understand obfuscation basics
    

---

## 6. Crackme path

Start with:

```text
simple password check
string comparison
encoded password
basic XOR
license key check
anti-debug check
packed binary basics
```

Do not jump to hard crackmes too early.

---

# Phase 6: Programming roadmap

You need programming not for job title, but for power.

## Python

You should be able to:

```text
send HTTP requests
maintain session
parse JSON
read/write files
regex basics
threading basics
async basics
write Burp-like PoC
build Flask vulnerable apps
parse scanner output
generate reports
```

Projects:

- IDOR checker
    
- endpoint extractor
    
- JWT decoder/checker
    
- race condition request sender
    
- SCA report parser
    
- vulnerable Flask lab
    

---

## JavaScript

Learn:

```text
DOM
events
fetch
promises
async/await
Node.js
Express
prototype chain
JSON handling
frontend auth mistakes
```

Projects:

- vulnerable Express API
    
- DOM XSS lab
    
- JWT auth demo
    
- prototype pollution demo
    

---

## C

Learn:

```text
pointers
arrays
strings
structs
stack
heap basics
function calls
compilation
shared libraries/DLL basics
```

Projects:

- simple password checker
    
- vulnerable buffer program in lab
    
- DLL loading demo
    
- basic keygen crackme
    

---

## C#

Learn:

```text
.NET assemblies
Windows Forms basics
config files
DPAPI
SQLite
HTTP client
DLL references
services basics
```

Projects:

- thick client login app
    
- local encrypted credential store
    
- app that loads DLL
    
- app that calls API
    
- app with auto-update simulation
    

---

## SQL

Learn:

```text
select
insert
update
delete
joins
where
order by
transactions
locks
isolation basics
stored procedures basics
```

This helps SQLi and race condition understanding.

---

# Phase 7: Bug bounty roadmap

Don’t hunt randomly.

## First 30 days

Pick one program.

Do only:

```text
account creation
login
profile
organization/team
roles
invitations
billing
API endpoints
mobile/API traffic if available
```

Your focus:

```text
IDOR
role bypass
business logic
race
mass assignment
auth bugs
```

## Program mapping checklist

Create this note:

```markdown
# Program Name

## Users
- normal user
- admin
- org owner
- invited user

## Objects
- user_id
- org_id
- team_id
- invoice_id
- project_id
- file_id

## Auth flows
- login
- signup
- reset password
- invite
- email change
- MFA

## Sensitive endpoints
- billing
- members
- roles
- API keys
- exports
- integrations

## Possible attacks
- user A to user B
- member to admin
- org A to org B
- unpaid to paid
- old token reuse
```

## Your hunting style

For your current skill, hunt:

- access control
    
- API authorization
    
- business logic
    
- race
    
- auth flow bugs
    
- file upload bugs
    
- webhook issues
    

Avoid spending too much time initially on:

- reflected XSS on hardened apps
    
- subdomain takeover noise
    
- low-impact scanner findings
    
- random nuclei spam
    
- duplicate-prone endpoints
    

---

# Phase 8: CTF roadmap

CTF is training, not identity.

## Web CTF order

Do:

```text
HTTP basics
SQLi
Auth bypass
IDOR
SSTI
SSRF
File upload
Path traversal
Deserialization
Race
Request smuggling basics
Crypto basics
```

## Reverse CTF order

Do:

```text
strings
simple password checks
encoded strings
XOR
control flow
patching jumps
keygen
basic anti-debug
packed samples basics
```

## CTF solving template

Every challenge note:

```markdown
# Challenge Name

## Category
Web / Rev

## Goal
What do we need? Flag/admin/RCE/key?

## Inputs I control
...

## Outputs I observe
...

## Interesting behavior
...

## Failed attempts
...

## Root cause
...

## Final solution
...

## What I learned
...
```

---

# Your PortSwigger decision

You asked: should you do labs again?

My answer:

## Don’t redo everything.

Redo only important sections like this:

### Redo deeply

- Access control
    
- Authentication
    
- Business logic
    
- Race conditions
    
- OAuth
    
- SSRF
    
- File upload
    
- JWT
    
- API testing if available
    
- Request smuggling later
    

### Don’t waste time redoing easy labs

If you already understand basic SQLi, don’t redo every beginner SQLi lab. Instead do:

```text
1 easy lab to refresh
2 medium labs to sharpen
1 hard lab with notes
then build your own mini lab
```

The real rule:

> For every topic, solve labs + build one mini vulnerable version yourself.

That combination is unbeatable.

---

# Your 6-month roadmap

## Month 1: Web authorization mastery

Focus:

```text
Access control
IDOR/BOLA
Auth bugs
JWT
Session bugs
API authorization
```

Do:

- PortSwigger access control/auth labs
    
- Build Flask/Express access control lab
    
- Test one bounty program auth flows
    

Output:

```text
2 deep notes
1 mini lab
1 private case study
```

---

## Month 2: Business logic + race conditions

Focus:

```text
checkout flaws
coupon abuse
wallet bugs
race conditions
database transactions
idempotency
```

Do:

- PortSwigger business logic/race labs
    
- Build mini shop app
    
- Break and fix race bugs
    

Output:

```text
race condition note
business logic checklist
mini shop lab
```

---

## Month 3: Thick client foundation

Focus:

```text
Procmon
DLL hijacking
file permissions
registry
local storage
DPAPI
services
```

Do:

- Build C# thick client demo
    
- Practice Procmon daily
    
- Create DLL hijacking lab
    

Output:

```text
thick client testing checklist
DLL hijacking case study
DPAPI note
```

---

## Month 4: Reverse engineering foundation

Focus:

```text
Ghidra
x64dbg
dnSpyEx
assembly basics
crackmes
.NET reversing
```

Do:

- 10 beginner crackmes
    
- 5 .NET crackmes/apps
    
- Reverse your own C# lab
    

Output:

```text
reverse engineering notes
crackme writeups
tool workflow
```

---

## Month 5: Advanced web

Focus:

```text
SSRF
SSTI
XXE
deserialization
file upload
request smuggling basics
GraphQL
OAuth
```

Do:

- PortSwigger advanced topics
    
- Build SSRF/SSTI/file upload labs
    
- Hunt one real program
    

Output:

```text
advanced web checklist
3 vulnerable labs
1 bounty target map
```

---

## Month 6: Portfolio + job upgrade

Focus:

```text
resume
case studies
interview preparation
public notes
bug bounty consistency
```

Create:

```text
1 web authorization case study
1 race condition case study
1 DLL hijacking/privesc case study
1 thick client testing checklist
1 GitHub repo with safe labs/tools
```

Then start applying seriously.

---

# Your weekly checklist

Use this every week.

```markdown
# Weekly Offensive Security Checklist

## Web
[ ] Solved 3 PortSwigger/CTF labs
[ ] Tested one real app workflow
[ ] Wrote one vulnerability note

## Thick Client / Reverse
[ ] Practiced one tool: Procmon/Ghidra/x64dbg/dnSpy
[ ] Reversed one small app/crackme
[ ] Wrote one observation note

## Programming
[ ] Built or improved one small lab/tool
[ ] Read code for one vulnerable feature
[ ] Fixed one vulnerability in my lab

## Bug Bounty
[ ] Mapped one program feature
[ ] Tested auth/access control
[ ] Logged failed attempts

## Career
[ ] Added one case-study bullet
[ ] Improved resume/LinkedIn/GitHub
```

---

# Your master concept checklist

Keep this in Obsidian and tick slowly.

## Web/API

```text
[ ] HTTP request/response
[ ] Cookies and sessions
[ ] JWT
[ ] OAuth/OIDC
[ ] CORS
[ ] CSRF
[ ] SOP
[ ] Authentication
[ ] Authorization
[ ] IDOR/BOLA
[ ] BFLA
[ ] SQLi
[ ] XSS
[ ] SSRF
[ ] SSTI
[ ] XXE
[ ] File upload
[ ] Path traversal
[ ] Deserialization
[ ] Race conditions
[ ] Business logic
[ ] Request smuggling
[ ] Cache poisoning
[ ] WebSockets
[ ] GraphQL
[ ] Webhooks
[ ] API versioning
[ ] Rate limiting
[ ] Mass assignment
```

## Thick client / Windows

```text
[ ] Windows users/groups
[ ] UAC
[ ] Services
[ ] Scheduled tasks
[ ] Registry
[ ] File permissions
[ ] Process privileges
[ ] DLL search order
[ ] DLL hijacking
[ ] PATH hijacking
[ ] Binary planting
[ ] Named pipes
[ ] Local ports
[ ] DPAPI
[ ] Local storage
[ ] SQLite
[ ] Config files
[ ] Logs
[ ] Update mechanisms
[ ] TLS interception
[ ] Client-side trust
[ ] Hardcoded secrets
```

## Reverse engineering

```text
[ ] Registers
[ ] Stack
[ ] Heap basics
[ ] Assembly basics
[ ] Function calls
[ ] Strings
[ ] Control flow
[ ] PE format
[ ] ELF basics
[ ] Imports/exports
[ ] Static analysis
[ ] Dynamic analysis
[ ] Breakpoints
[ ] Patching jumps
[ ] .NET decompilation
[ ] Obfuscation basics
[ ] Anti-debug basics
```

## Programming

```text
[ ] Python requests
[ ] Python Flask
[ ] Python threading
[ ] Python file parsing
[ ] JavaScript DOM
[ ] JavaScript fetch
[ ] Node.js Express
[ ] SQL queries
[ ] SQL transactions
[ ] C pointers
[ ] C memory basics
[ ] C DLL/shared library
[ ] C# .NET basics
[ ] C# DPAPI
[ ] PowerShell basics
[ ] Bash basics
```

---

# What to build first

Start with these 8 projects.

## 1. Access control lab

Users, roles, orgs, invoices.

Vulnerabilities:

```text
IDOR
role bypass
org bypass
admin API access
mass assignment
```

## 2. Auth lab

Login, reset password, MFA.

Vulnerabilities:

```text
weak reset token
OTP bypass
no rate limit
session not invalidated
email change takeover
```

## 3. Mini shop lab

Cart, coupon, wallet.

Vulnerabilities:

```text
price tampering
coupon reuse
race condition
negative quantity
refund abuse
```

## 4. File upload lab

Avatar/document upload.

Vulnerabilities:

```text
extension bypass
stored XSS via SVG
path traversal filename
public file exposure
```

## 5. SSRF lab

URL fetcher.

Vulnerabilities:

```text
localhost access
allowlist bypass
blind callback
URL parser confusion
```

## 6. SSTI lab

Template preview.

Vulnerabilities:

```text
unsafe template rendering
expression execution
file read in lab
```

## 7. DLL hijacking lab

C/C# app loading DLL.

Vulnerabilities:

```text
relative DLL loading
writable folder
privileged context simulation
```

## 8. C# thick client lab

Login app with local storage and API.

Vulnerabilities:

```text
hardcoded API key
local SQLite secrets
weak encryption
client-side role check
DPAPI usage/misuse
```

---

# Priority order for you

Because you already know some web and are currently getting thick client work, your order should be:

```text
1. Access control/API authorization
2. Authentication deep flows
3. Business logic
4. Race conditions
5. Thick client Windows fundamentals
6. DLL hijacking/privesc
7. .NET reversing
8. SSRF/SSTI/file upload/deserialization
9. Request smuggling/OAuth/GraphQL
10. Advanced reversing
```

Do not jump to advanced reversing before you master app logic and Windows basics.

---

# The simple rule

For every topic:

```text
Read 20%
Solve labs 30%
Build vulnerable app 30%
Write notes 20%
```

That is your learning formula.

Most people do:

```text
Read 80%
Try payload 20%
```

That is why they stay average.

---

# Your next 7 days

Do this exactly.

## Day 1

Create Obsidian vault and folders.

Make note:

```text
IDOR/BOLA - Deep Note
```

## Day 2

Redo 3 PortSwigger access control labs.

Not for solution. Write root cause.

## Day 3

Build small Flask/Express app:

```text
/users/1
/users/2
/invoices/1
/org/1/members
```

Add broken authorization.

## Day 4

Attack your own app with two users.

Write failed attempts and detection checklist.

## Day 5

Fix authorization properly.

Add server-side ownership checks.

## Day 6

Test one real bug bounty/private lab app for object ID issues.

Only map. Don’t rush report.

## Day 7

Write one mini case study:

```text
How IDOR happens architecturally
How to detect it
How to fix it
```

---
1. **Morning Lockdown (60 min no-screen, movement, WHY reading).** This is the queen habit that makes all others possible.

2. **Daily Lab (1 PortSwigger, before office).** Non-negotiable sharpening of the sword.

3. **Daily Hunt (30 min active probing, not passive recon).** Output-focused: 3 endpoints tested, notes taken.

4. **Daily Code/ Tooling (30 min).** Even if it's just refactoring or adding one function.

5. **Weekly Bug Submission (minimum 1 per week).** The act of shipping a report builds the "earner" mindset.

6. **Weekly Job Application (2 applications, personalized).** Track them.

7. **Physical Prime (20 min walk/exercise).** Health is the foundation.

8. **Dopamine Control (no phone in bedroom, no reels, no porn/masturbation, WhatsApp only 2x/day).** This will feel like withdrawal for 2 weeks. Push through.

9. **Nightly Review (score, plan tomorrow, read WHY aloud).** Closes the loop.
   
   d
