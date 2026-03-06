# IDOR Vulnerabilities for Web Applications & APIs

##  1 Horizontal IDOR (Peer-to-Peer Access)

**How it works:**  
Authenticated user accesses another regular user's object by changing ID.

**Steps to Find**
1. Create 2+ low-priv accounts
2. Capture requests with your object ID
3. Swap with victim's ID in same session
4. Check for data leak (profile, orders, messages)

**Impact**
- Mass PII exposure
- Privacy breaches

---

## 2 Vertical IDOR (Privilege Escalation)

**How it works:**  
Low-priv user accesses admin/privileged objects.

**Steps to Find**
1. Identify admin resources (e.g., `/admin/settings/999`)
2. Swap your ID with guessed admin ID
3. Test elevation on sensitive endpoints

**Impact**
- Admin takeover
- Configuration changes
- Possible RCE chains

---

## 3 Blind / Inferential IDOR

**How it works:**  
No direct leak; infer via side-channels like timing, status codes, redirects, or response size differences.

**Steps to Find**
1. Send tampered requests
2. Compare `200` vs `403/404`
3. Observe timing differences or byte length
4. Use **Burp Intruder** for mass inference

**Impact**
- Stealthy enumeration
- Target preparation for ATO

---

## 4 File / Directory IDOR (Static Resource Access)

**How it works:**  
Direct links to files/uploads without ownership validation.

**Steps to Find**
1. Upload file → note ID/filename
2. Access `/files/victim-uuid.pdf` from another account
3. Test sequential filenames or weak hashing

**Impact**
- Arbitrary file disclosure
- Sensitive document leaks

---

## 5 API / REST IDOR

**How it works:**  
APIs expose IDs without object-level authorization.

**Steps to Find**
1. Map endpoints using **Swagger/Postman**
2. Tamper IDs in `GET/POST/PUT/DELETE`
3. Verify unauthorized read/write/delete

**Impact**
- Data theft at scale
- Unauthorized data modification

---

## 6 Predictable / Sequential ID Enumeration

**How it works:**  
Incremental IDs (1..n) allow easy guessing.

**Steps to Find**
1. Register multiple accounts
2. Observe ID growth
3. Increment/decrement IDs in requests
4. Automate enumeration

**Impact**
- Bulk data harvesting

---

## 7 UUID / Time-Based Predictability IDOR

**How it works:**  
UUIDv1 or patterned UUIDs leak creation order/time.

**Steps to Find**
1. Generate your own UUIDs
2. Extract patterns (timestamp bits)
3. Guess victim UUIDs

**Impact**
- Mass account enumeration

---

## 8 Second-Order / Stored IDOR

**How it works:**  
ID is stored and later processed without validation.

**Steps to Find**
1. Trigger action storing the ID
2. Tamper with stored reference
3. Observe delayed unauthorized effect

**Impact**
- Hard-to-detect persistent attack

---

## 9 Mass Assignment + IDOR

**How it works:**  
Undocumented parameters allow injecting foreign IDs.

**Steps to Find**
1. Capture update request
2. Add parameter like `user_id=victim`
3. Check if server accepts it

**Impact**
- Unauthorized account modifications

---

## 10 Password Reset / Token IDOR

**How it works:**  
Reset links/tokens embed manipulable user IDs.

**Steps to Find**
1. Request password reset
2. Intercept reset token/link
3. Modify embedded user ID
4. Attempt password reset

**Impact**
- Full Account Takeover (ATO)

---

## 11 Order / Invoice / Transaction IDOR

**How it works:**  
Access or modify orders by swapping `order_id`.

**Steps to Find**
1. Place multiple orders
2. Swap order IDs
3. Check PII or payment data exposure

**Impact**
- Financial fraud
- Privacy breaches

---

## 12 GraphQL IDOR

**How it works:**  
GraphQL queries fetch unauthorized objects via aliases or batching.

**Steps to Find**
1. Map schema using **InQL**
2. Query objects like `victim(id:"uuid")`
3. Check resolver authorization

**Impact**
- Large-scale data scraping

---

## 13 Multi-Tenant IDOR

**How it works:**  
Cross-tenant access via `org_id` or `tenant_id` manipulation.

**Steps to Find**
1. Create accounts in different organizations
2. Tamper `org_id` in requests
3. Access resources across tenants

**Impact**
- SaaS data isolation breach

---

## 14 Cookie / Header-Based IDOR

**How it works:**  
IDs stored in cookies, headers, or JWT without validation.

**Steps to Find**
1. Modify values like `X-User-Id`
2. Replay requests

**Impact**
- Session-based privilege escalation

---

## 15 Method Switching IDOR

**How it works:**  
`GET` method protected but `PUT/POST/DELETE` lacks authorization.

**Steps to Find**
1. Test safe methods
2. Switch to mutating methods
3. Use foreign IDs

**Impact**
- Unauthorized changes or deletions

---

## 16 Path IDOR (Directory Traversal Hybrid)

**How it works:**  
File paths referenced without proper access checks.

**Steps to Find**
1. Tamper path segments
2. Use patterns like `../`
3. Attempt access to restricted files

**Impact**
- Configuration or server file leaks

---

## 17 WebSocket IDOR

**How it works:**  
WebSocket messages reference objects without proper validation.

**Steps to Find**
1. Intercept WebSocket traffic
2. Modify object IDs in messages
3. Observe unauthorized updates

**Impact**
- Real-time data manipulation

---

## 18 Timing / Side-Channel Enumeration IDOR

**How it works:**  
Response timing differences reveal valid IDs.

**Steps to Find**
1. Send requests with guessed IDs
2. Measure response time variations
3. Infer valid accounts

**Impact**
- User discovery and enumeration

---

## 19 Bulk Operation IDOR

**How it works:**  
Bulk APIs process foreign IDs without individual validation.

**Steps to Find**
1. Send bulk requests with victim IDs
2. Check if operations succeed

**Impact**
- Mass unauthorized actions

---

## 20 Feature Flag / Experiment IDOR

**How it works:**  
Manipulating experiment or feature flag IDs.

**Steps to Find**
1. Tamper flag IDs
2. Access premium/test features

**Impact**
- Unauthorized feature access

---

## 21 Notification / Audit Log IDOR

**How it works:**  
Viewing logs or notifications by swapping `user_id`.

**Steps to Find**
1. Trigger notifications
2. Swap user ID in log endpoint

**Impact**
- Sensitive activity disclosure

---

## 22 Referral / Invite Link IDOR

**How it works:**  
Invite links contain manipulable references.

**Steps to Find**
1. Generate invite link
2. Modify referral ID
3. Claim rewards

**Impact**
- Abuse of referral systems

---

## 23 Backup / Export IDOR

**How it works:**  
Export/download endpoints allow ID manipulation.

**Steps to Find**
1. Request export
2. Swap export ID
3. Download victim data

**Impact**
- Complete data exfiltration

---

## 24 Shared Resource IDOR (Comments / Attachments)

**How it works:**  
Attachments/comments tied to objects without ownership checks.

**Steps to Find**
1. View comments on your object
2. Swap `post_id` or object ID
3. Access private content

**Impact**
- Private conversation leakage

---

## 25 Hybrid / Chained IDOR

**How it works:**  
IDOR combined with other vulnerabilities.

**Examples**
- IDOR + Mass Assignment
- IDOR + Race Condition
- IDOR + Self-XSS

**Impact**
- Critical severity exploits (ATO / RCE)

---

# Testing Methodology

## Essential Tools

- **Burp Suite** (Intruder, Repeater, Autorize, Turbo Intruder)
- **OWASP ZAP**
- **Postman / Insomnia**
- **InQL / GraphQL Pathfinder**
- **Custom Python scripts**

---

## Best Practices

- Use multiple accounts (low privilege and admin)
- Test all HTTP methods
- Test APIs, GraphQL, and WebSockets
- Identify all ID usage in:
  - URL
  - Request body
  - Headers
  - Cookies
- Test blind IDOR using timing/status analysis
- Document PoC with two accounts

---

## Common Indicators

- Direct IDs in requests (`id`, `uuid`, `user_id`)
- `200 OK` response on foreign resources
- Missing ownership checks
- Sequential or predictable IDs