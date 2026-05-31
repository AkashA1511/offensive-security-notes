
# The core architecture topics you must master

## 1. HTTP and browser fundamentals

This is the base layer. Without this, everything else becomes magic.

Learn:

```text
HTTP methods
status codes
headers
cookies
redirects
CORS
caching
content types
same-origin policy
preflight requests
browser storage
CSRF model
CSP
iframes
postMessage
service workers
```

Why it matters for hunting:

```text
CORS bugs
cache poisoning
CSRF
session leaks
cookie issues
open redirect chains
DOM XSS
postMessage bugs
CSP bypass
OAuth redirect bugs
```

Read from:

- **MDN Web Docs** for browser behavior.
    
- **OWASP Web Security Testing Guide** for how to test web behavior. OWASP WSTG is a major testing resource for web app security and includes information gathering, authentication, authorization, session management, input validation, and client-side testing. ([OWASP](https://owasp.org/www-project-web-security-testing-guide/?utm_source=chatgpt.com "OWASP Web Security Testing Guide"))
    

For this topic, MDN is your “how browser works” book. OWASP WSTG is your “how hacker tests it” book.

---

## 2. Authentication architecture

Authentication means:

> **Who are you?**

Master:

```text
login flow
password reset
email verification
MFA
magic links
session creation
remember-me tokens
device trust
account recovery
rate limiting
credential stuffing protection
alternative login channels
```

Bug classes unlocked:

```text
account takeover
password reset bypass
MFA bypass
weak recovery flow
login CSRF
email change takeover
session fixation
rate-limit bypass
authentication bypass
```

Read from:

- **OWASP WSTG Authentication Testing** — it covers weak lockout, weak password reset, MFA testing, weak auth in alternative channels, and related flows. ([OWASP](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/04-Authentication_Testing/README?utm_source=chatgpt.com "WSTG - 04-Authentication Testing"))
    
- **OWASP Authentication Cheat Sheet**
    
- **PortSwigger Web Security Academy: Authentication**
    

Your pro question while reading:

```text
Where does the app prove identity?
Where can identity be changed?
Where can identity be recovered?
What token proves identity?
Can this token be reused, leaked, fixed, or confused?
```

---

## 3. Session management

Session management means:

> **After login, how does the server remember you?**

Master:

```text
session cookies
JWT sessions
server-side sessions
refresh tokens
access tokens
cookie flags
SameSite
HttpOnly
Secure
session timeout
logout behavior
concurrent sessions
session fixation
token rotation
device sessions
```

Bug classes unlocked:

```text
session hijacking
session fixation
logout bypass
JWT weakness
token leakage
refresh token reuse
weak cookie config
concurrent-session abuse
```

Read from:

- **OWASP WSTG Session Management Testing** — it includes cookie attributes, exposed session variables, CSRF, logout, timeout, session puzzling, JWT testing, and concurrent sessions. ([OWASP](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/README?utm_source=chatgpt.com "WSTG - 06-Session Management Testing"))
    
- **OWASP Session Management Cheat Sheet**
    
- **PortSwigger: JWT attacks**
    

Pro hacker mindset:

```text
What happens if password changes?
What happens if user logs out?
What happens if role changes?
What happens if user is removed from org?
Are old sessions killed?
Are refresh tokens rotated?
Can two devices behave differently?
```

This is where many real bugs hide.

---

## 4. Authorization and access control

Authorization means:

> **What are you allowed to do?**

This is probably your biggest money topic.

Master:

```text
RBAC
ABAC
object ownership
tenant isolation
workspace/org model
roles and permissions
admin/member/guest flows
resource-level checks
function-level checks
horizontal privilege escalation
vertical privilege escalation
```

Bug classes unlocked:

```text
IDOR
BOLA
BOPLA
privilege escalation
admin action bypass
tenant data leak
workspace takeover
cross-account access
```

Read from:

- **OWASP WSTG Authorization Testing** — includes bypassing authorization schema, privilege escalation, insecure direct object references, and OAuth weakness testing. ([OWASP](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/README?utm_source=chatgpt.com "WSTG - 06-Session Management Testing"))
    
- **OWASP API Security Top 10 2023**
    
- **PortSwigger: Access Control**
    

OWASP API Security says BOLA happens when attackers manipulate object IDs in requests, including path, query, headers, or body, and the API fails to enforce object-level authorization. ([OWASP](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/?utm_source=chatgpt.com "API1:2023 Broken Object Level Authorization"))

Pro questions:

```text
Who owns this object?
Who can read it?
Who can update it?
Who can delete it?
What happens across orgs?
What happens after role downgrade?
What happens after user removal?
Is authorization checked on every endpoint or only UI?
```

This is your main bounty weapon.

---

## 5. OAuth 2.0

OAuth means:

> **Delegated authorization.**  
> “Allow this app to access something on your behalf.”

Do not think OAuth is “login.” OAuth is mainly authorization. Login usually comes when OpenID Connect is added on top.

Master:

```text
authorization code flow
PKCE
redirect_uri
state
scope
client_id
client_secret
access token
refresh token
authorization server
resource server
public vs confidential clients
token exchange
token audience
token lifetime
```

Bug classes unlocked:

```text
account takeover
OAuth CSRF
redirect_uri bypass
code theft
token leakage
scope escalation
client confusion
open redirect chains
account linking bugs
missing PKCE
state bypass
```

Read from:

- **RFC 6749** — OAuth 2.0 core.
    
- **RFC 9700** — OAuth 2.0 Security Best Current Practice. It specifically covers security recommendations and weaknesses like insufficient redirect URI validation. ([IETF Datatracker](https://datatracker.ietf.org/doc/html/rfc9700?utm_source=chatgpt.com "RFC 9700 - Best Current Practice for OAuth 2.0 Security"))
    
- **PortSwigger OAuth labs**
    
- **OAuth.net resources**
    

Important modern note: RFC 9700 is the current security best-practice document for OAuth 2.0 and describes security requirements and recommendations for clients and servers. ([OAuth](https://oauth.net/2/oauth-best-practice/?utm_source=chatgpt.com "RFC 9700: OAuth 2.0 Security Best Current Practice"))

Pro hacker reading style:

```text
Read normal flow first.
Draw every redirect.
Mark where code/token appears.
Ask: who controls this parameter?
Ask: can attacker receive the code?
Ask: is state bound to session?
Ask: is redirect_uri exact match?
Ask: is token audience checked?
```

For OAuth, don’t just read. Draw this flow 20 times:

```text
User → Client App → Authorization Server → Login/Consent
Authorization Server → redirect_uri with code
Client App → exchanges code for token
Client App → uses token against Resource Server
```

Then hunt where this breaks.

---

## 6. OpenID Connect

OpenID Connect means:

> **Authentication layer on top of OAuth 2.0.**  
> It tells the app who the user is.

Master:

```text
id_token
userinfo endpoint
nonce
claims
issuer
audience
subject
JWKS
discovery document
hybrid flow
account linking
email_verified
```

Bug classes unlocked:

```text
login bypass
account takeover
wrong audience token acceptance
issuer confusion
email verification bypass
kid/JWKS confusion
account linking takeover
nonce bypass
```

Read from:

- **OpenID Connect Core 1.0** — it defines OIDC as an identity layer on top of OAuth 2.0 that lets clients verify the identity of the end user and obtain basic profile information. ([OpenID Foundation](https://openid.net/specs/openid-connect-core-1_0-final.html?utm_source=chatgpt.com "Final: OpenID Connect Core 1.0"))
    
- **OpenID Connect Discovery**
    
- **PortSwigger OAuth/OIDC labs**
    

Pro questions:

```text
Does the app trust email without email_verified?
Does it validate issuer?
Does it validate audience?
Does it validate nonce?
Can I link attacker IdP account to victim account?
Can I use token from another client?
```

OAuth bugs become serious when OIDC login is involved.

---

## 7. JWT and token architecture

JWT is just a format. Bugs come from bad validation and bad trust decisions.

Master:

```text
header.payload.signature
alg
kid
jku
jwks
iss
aud
sub
exp
nbf
iat
scope
roles
refresh tokens
access tokens
```

Bug classes unlocked:

```text
alg none
weak secret
kid injection
jku/JWKS confusion
audience confusion
issuer confusion
role tampering
expired token acceptance
token substitution
```

Read from:

- **RFC 7519** — JWT.
    
- **RFC 7515** — JWS.
    
- **PortSwigger JWT attacks**
    
- **OWASP JWT Cheat Sheet**
    

Pro mindset:

```text
Who issued this token?
Who is supposed to accept it?
What is the audience?
What is the issuer?
Where is the key coming from?
Can claims be trusted by frontend only?
Does backend check roles from token blindly?
```

JWT is not “decode and edit.” Real JWT hunting is **trust boundary hunting**.

---

## 8. API architecture

APIs are where bounty money lives.

Master:

```text
REST
GraphQL
gRPC basics
OpenAPI/Swagger
versioning
pagination
filtering
object IDs
mass assignment
rate limiting
webhooks
API keys
scopes
tenant isolation
mobile APIs
```

Bug classes unlocked:

```text
BOLA
BOPLA
mass assignment
broken authentication
excessive data exposure
rate-limit bypass
business logic abuse
GraphQL resolver auth bugs
API key scope bypass
```

Read from:

- **OWASP API Security Top 10 2023** — it lists BOLA, Broken Authentication, Broken Object Property Level Authorization, Unrestricted Resource Consumption, and more. ([OWASP](https://owasp.org/API-Security/editions/2023/en/0x11-t10/?utm_source=chatgpt.com "OWASP Top 10 API Security Risks – 2023"))
    
- **OWASP API1:2023 BOLA**
    
- **OWASP API2:2023 Broken Authentication** — includes examples like batching GraphQL requests to bypass rate limiting. ([OWASP](https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/?utm_source=chatgpt.com "API2:2023 Broken Authentication"))
    
- **PortSwigger API Testing**
    
- **GraphQL official docs**
    

Pro API questions:

```text
Can I change object ID?
Can I change org_id?
Can I send extra JSON fields?
Can I call admin endpoint directly?
Can I use mobile endpoint from web token?
Can old API version has weaker checks?
Can GraphQL query expose hidden fields?
```

This should become your daily practice.

---

## 9. Multi-tenant SaaS architecture

This is not one RFC, but it is pure bounty gold.

Master:

```text
organizations
workspaces
teams
roles
memberships
invites
billing admins
projects
resource ownership
tenant boundaries
audit logs
exports
data deletion
```

Bug classes unlocked:

```text
cross-tenant data leak
org takeover
role escalation
invite abuse
billing data leak
export IDOR
workspace deletion abuse
API key cross-tenant access
```

Read from:

- SaaS product docs.
    
- Auth0/Okta RBAC docs.
    
- OWASP Authorization Cheat Sheet.
    
- Real SaaS API docs like GitHub, Slack, Stripe, Notion, Linear, etc.
    

Pro exercise:

Build your own mini SaaS:

```text
User
Organization
Workspace
Project
Role
Invite
Invoice
API Key
Webhook
```

Then intentionally make bugs and fix them.

This one exercise will make you 10x better.

---

## 10. Payments, billing, and state machines

This is business logic territory.

Master:

```text
cart
checkout
payment intent
invoice
subscription
trial
coupon
refund
wallet
gift card
webhook confirmation
order state machine
idempotency
race conditions
```

Bug classes unlocked:

```text
free purchase
double refund
coupon stacking
trial reset
payment bypass
race condition
webhook spoofing
subscription upgrade abuse
```

Read from:

- **Stripe docs** — PaymentIntents, webhooks, idempotency, subscriptions.
    
- **Razorpay docs** if hunting Indian apps.
    
- **PortSwigger business logic and race condition labs.**
    

Pro questions:

```text
Who confirms payment: frontend or backend?
Can order become paid without payment success?
Can webhook be forged?
Can same coupon apply twice?
Can refund race?
Is idempotency used?
What are all valid and invalid states?
```

For payment bugs, think like a backend engineer.

---

## 11. Webhooks and integrations

Modern apps are full of integrations.

Master:

```text
webhook URL
signature
secret rotation
event replay
timestamp tolerance
integration tokens
OAuth scopes
third-party callbacks
SSRF through webhook
```

Bug classes unlocked:

```text
webhook SSRF
signature bypass
event replay
cross-tenant webhook trigger
secret disclosure
integration takeover
OAuth scope abuse
```

Read from:

- Stripe webhook security docs.
    
- GitHub webhook docs.
    
- Slack app docs.
    
- OWASP SSRF Prevention Cheat Sheet.
    

Pro questions:

```text
Can webhook URL point to internal IP?
Is signature verified?
Can old signatures replay?
Can lower role read webhook secret?
Can webhook of Org A be triggered by Org B?
```

---

## 12. File upload and storage architecture

File upload is not only extension bypass.

Master:

```text
multipart upload
content-type
magic bytes
image processing
PDF processing
AV scanning
S3/GCS storage
signed URLs
public/private ACLs
CDN caching
file conversion
metadata
path traversal
```

Bug classes unlocked:

```text
stored XSS
SSRF via parser
private file IDOR
malware upload impact
path traversal
RCE through parser
signed URL bypass
bucket exposure
```

Read from:

- OWASP File Upload Cheat Sheet.
    
- AWS S3 presigned URL docs.
    
- PortSwigger file upload labs.
    

Pro questions:

```text
Who can download the file?
Is access checked before signed URL generation?
Can signed URL be reused?
Can I overwrite another file?
Can metadata leak path/user info?
Does backend fetch remote URL for import?
```

---

## 13. Cloud basics

You do not need to become cloud guru first, but you need cloud fundamentals.

Master:

```text
AWS IAM
S3
CloudFront
Lambda
API Gateway
metadata service
temporary credentials
signed URLs
GCP buckets
Azure Blob
Kubernetes basics
secrets
environment variables
```

Bug classes unlocked:

```text
SSRF to metadata
public bucket exposure
over-permissive IAM
leaked cloud keys
signed URL weakness
serverless auth bypass
Kubernetes dashboard exposure
```

Read from:

- AWS IAM docs.
    
- AWS S3 security docs.
    
- AWS Well-Architected Security Pillar.
    
- OWASP Cloud-Native Application Security Top 10.
    

Pro question:

```text
If I get SSRF, what cloud am I in?
If I find a key, what permissions does it have?
If I find a bucket, is listing/read/write allowed?
```

Cloud turns medium bugs into high/critical bugs.

---

## 14. SSO/SAML enterprise auth

This is advanced but valuable.

Master:

```text
SAML Response
Assertion
ACS URL
Entity ID
IdP
SP
NameID
signature validation
attribute mapping
role mapping
tenant mapping
```

Bug classes unlocked:

```text
SAML signature bypass
wrong recipient/audience
account takeover
tenant confusion
role escalation
email attribute abuse
```

Read from:

- SAML technical overview.
    
- OWASP SAML Security Cheat Sheet.
    
- PortSwigger SSO/OAuth-related content.
    
- Okta/Auth0 SAML docs.
    

Pro questions:

```text
Is assertion signed?
Is response signed but assertion not?
Is audience checked?
Is recipient checked?
Can email attribute be attacker-controlled?
Can role attribute map to admin?
```

---

## 15. Race conditions and distributed systems

Race condition bugs come from architecture.

Master:

```text
TOCTOU
database transactions
locks
queues
eventual consistency
idempotency keys
async workers
message queues
caches
webhook delay
inventory counters
wallet balance
```

Bug classes unlocked:

```text
double spend
double refund
coupon reuse
limit bypass
race checkout
role-change race
invite reuse
multiple account actions
```

Read from:

- PortSwigger race condition labs.
    
- Database transaction docs.
    
- Stripe idempotency docs.
    
- General distributed systems basics.
    

Pro questions:

```text
Is check and update atomic?
Can I send two requests at same time?
Is state updated in DB or cache?
Is worker processing async?
Is there idempotency?
Can old state be reused?
```

This matches the lab you solved earlier.

---

# The “pro hacker reading stack”

Here is the exact order I would give you.

## Level 1: Web core

Read:

```text
MDN HTTP
MDN Cookies
MDN CORS
MDN Same-Origin Policy
OWASP WSTG Information Gathering
OWASP WSTG Authentication
OWASP WSTG Session Management
OWASP WSTG Authorization
PortSwigger Authentication
PortSwigger Access Control
PortSwigger Business Logic
```

Goal:

> Understand how web apps identify users, remember users, and enforce permissions.

## Level 2: API hunter

Read:

```text
OWASP API Security Top 10 2023
OWASP API1 BOLA
OWASP API2 Broken Authentication
REST API design basics
OpenAPI/Swagger docs
GraphQL docs
PortSwigger API Testing
```

Goal:

> Become dangerous with APIs, object IDs, tenant boundaries, and roles.

## Level 3: Identity pro

Read:

```text
RFC 6749 - OAuth 2.0
RFC 9700 - OAuth 2.0 Security Best Current Practice
OpenID Connect Core 1.0
RFC 7519 - JWT
OAuth.net guides
PortSwigger OAuth labs
```

Goal:

> Understand login, delegated access, tokens, scopes, redirects, and account linking.

## Level 4: Business-impact hunter

Read:

```text
Stripe PaymentIntents
Stripe Webhooks
Stripe Idempotency
SaaS RBAC docs
Auth0/Okta RBAC docs
OWASP Authorization Cheat Sheet
PortSwigger Race Conditions
PortSwigger Business Logic
```

Goal:

> Find bugs that affect money, roles, billing, teams, and customer data.

## Level 5: Scale and deep impact

Read:

```text
AWS IAM basics
AWS S3 security
Cloud metadata service docs
Kubernetes basics
OWASP SSRF Prevention
OWASP File Upload Cheat Sheet
Mobile Android basics with JADX
```

Goal:

> Chain web bugs into cloud, mobile API, or storage impact.

---

# How to read RFCs like a hacker

Do not read RFC like school textbook.

Use this method:

## Step 1: Draw the actors

For OAuth:

```text
Resource Owner = user
Client = app
Authorization Server = login/consent server
Resource Server = API
Attacker = controls browser/app/redirect maybe
```

## Step 2: Draw normal flow

For OAuth authorization code:

```text
1. Client redirects user to Authorization Server.
2. User logs in and consents.
3. Authorization Server redirects to client redirect_uri with code.
4. Client exchanges code for access token.
5. Client uses token to call Resource Server.
```

## Step 3: Mark trust boundaries

```text
Browser ↔ Client
Client ↔ Auth Server
Auth Server ↔ Resource Server
User-controlled parameters
Server-controlled parameters
Tokens
Redirects
```

## Step 4: Ask attacker questions

```text
Can attacker control redirect_uri?
Can attacker steal code?
Can attacker reuse code?
Can attacker remove state?
Can attacker use another client_id?
Can attacker swap token?
Can attacker confuse account linking?
```

## Step 5: Convert to checklist

For OAuth:

```text
state required?
PKCE used?
redirect_uri exact match?
code single-use?
token audience checked?
issuer checked?
scope enforced?
refresh token rotated?
open redirects chained?
```

That is pro reading.

---

# Your master checklist of topics

Save this.

```text
[ ] HTTP
[ ] Cookies
[ ] Same-Origin Policy
[ ] CORS
[ ] Browser storage
[ ] CSP
[ ] CSRF
[ ] Authentication
[ ] Password reset
[ ] MFA
[ ] Sessions
[ ] JWT
[ ] Authorization
[ ] RBAC/ABAC
[ ] IDOR/BOLA
[ ] Multi-tenant SaaS
[ ] REST APIs
[ ] GraphQL
[ ] OAuth 2.0
[ ] OpenID Connect
[ ] SAML/SSO
[ ] Webhooks
[ ] File upload
[ ] Object storage/S3
[ ] Payments/subscriptions
[ ] Race conditions
[ ] Caching/CDN
[ ] SSRF
[ ] Cloud basics
[ ] Mobile API reversing
[ ] Logging/audit systems
[ ] Queues/background jobs
```

This is the architecture map of a serious web/API hunter.

---

# What to build while reading

Do not only read. Build small systems.

Build these 5 apps:

## 1. Auth app

Features:

```text
signup
login
logout
password reset
email change
MFA mock
session timeout
```

Then break:

```text
reset token reuse
weak session invalidation
MFA bypass
email change takeover
```

## 2. SaaS workspace app

Features:

```text
org
workspace
owner/admin/member
invite
project
file
```

Then break:

```text
IDOR
role escalation
cross-tenant access
invite abuse
removed user still has access
```

## 3. OAuth demo app

Features:

```text
OAuth login
authorization code
state
PKCE
redirect_uri
id_token
```

Then break:

```text
missing state
redirect_uri bypass
account linking bug
wrong audience token
```

## 4. Payment demo app

Features:

```text
cart
coupon
checkout
webhook
subscription
refund
```

Then break:

```text
double coupon
fake webhook
race checkout
double refund
```

## 5. File upload app

Features:

```text
upload
private download
signed URL
image processing
metadata
```

Then break:

```text
private file IDOR
stored XSS
path traversal
signed URL reuse
```

This is how architecture becomes muscle memory.

---

# Best learning order for you personally

Because you already like web and race conditions, do this:

## Month 1

```text
HTTP
cookies
sessions
authentication
password reset
MFA
access control
```

## Month 2

```text
API security
BOLA
multi-tenant SaaS
JWT
GraphQL basics
```

## Month 3

```text
OAuth 2.0
OpenID Connect
SSO/account linking
OAuth labs
```

## Month 4

```text
payments
webhooks
race conditions
file upload
S3 basics
```

## Month 5

```text
cloud basics
SSRF
mobile API reversing
JS/source review
```

## Month 6

```text
real targets
deep app mapping
writeups
reports
portfolio
```

---

# The difference between beginner reading and pro reading

Beginner reads:

> “OAuth uses state parameter.”

Pro reads:

> “State binds the authorization response to the user’s browser session. If missing or not validated, I can cause login CSRF or account linking confusion.”

Beginner reads:

> “JWT has aud claim.”

Pro reads:

> “If API accepts token with wrong audience, I may use token meant for one client/API against another service.”

Beginner reads:

> “BOLA means IDOR.”

Pro reads:

> “Every endpoint that receives object ID must check ownership against authenticated principal and active tenant context.”

That is the shift.

# Your north star

Bro, become this guy:

> **I understand how modern apps are designed, how developers usually implement them, and where trust boundaries fail.**

That hunter earns.

Not because he remembers 500 payloads.

Because when he sees:

```http
POST /api/workspaces/ws_123/invites
```

His brain automatically asks:

```text
Who can invite?
Can role be changed?
Can org_id be swapped?
Can invite token be reused?
Can removed user accept?
Can pending invite access data?
Can API key create invite?
Can mobile endpoint skip check?
Can old v1 endpoint behave differently?
```

That is the architecture mindset.

Start with **Authentication → Session → Authorization → API → OAuth/OIDC → Business Logic/Race**.

That path will turn you from “lab solver” into a real hunter.