# Authentication Bypass Vulnerabilities for Web Applications & APIs

---

## 1. Forced Browsing / Direct URL Access

**How it works:**  
Protected pages or endpoints are accessible without authentication by directly guessing URLs.

**Steps to Find**
1. Log in and capture protected URLs.
2. Log out.
3. Try accessing those URLs directly.
4. Test endpoints like `/admin`, `/dashboard`, `/api/user`.

**Impact**
- Unauthorized access to sensitive areas.

---

## 2. Workflow Step Bypass (Multi-Step Login Skip)

**How it works:**  
Login or authentication flows contain multiple steps that can be skipped by directly accessing the final endpoint.

**Steps to Find**
1. Complete login until the 2FA stage.
2. Note the post-2FA redirect URL.
3. Access the URL directly without completing 2FA.

**Impact**
- Complete authentication bypass.

---

## 3. Parameter Tampering (Role / Flag Injection)

**How it works:**  
Sensitive parameters like `role`, `isAdmin`, or privilege flags are trusted from the client side.

**Steps to Find**
1. Capture login or profile update requests.
2. Add or modify parameters such as `isAdmin=true` or `role=admin`.
3. Replay the request and check if access is elevated.

**Impact**
- Privilege escalation to admin-level access.

---

## 4. Session Fixation

**How it works:**  
Attacker forces a victim to log in using a session ID controlled by the attacker.

**Steps to Find**
1. Obtain an unauthenticated session ID.
2. Force the victim to authenticate using the same session.
3. Reuse the session after login.

**Impact**
- Account takeover.

---

## 5. Session Replay After Logout / Password Change

**How it works:**  
Old session tokens remain valid even after logout or password reset.

**Steps to Find**
1. Log in and capture session cookies or tokens.
2. Log out or change the password.
3. Replay the old token.

**Impact**
- Persistent unauthorized access.

---

## 6. Password Reset Token Reuse / Predictability

**How it works:**  
Password reset tokens are reusable, predictable, or not invalidated.

**Steps to Find**
1. Request password reset.
2. Use the token once.
3. Attempt to reuse the same token.
4. Try guessing tokens based on patterns.

**Impact**
- Repeated account takeover.

---

## 7. MFA / 2FA Bypass via Response Manipulation

**How it works:**  
Client trusts a manipulated response indicating successful authentication.

**Steps to Find**
1. Enter incorrect OTP.
2. Intercept the response.
3. Modify status or body (e.g., change `401` to `200`).
4. Forward the response.

**Impact**
- Client-side authentication bypass.

---

## 8. MFA Bypass via Rate Limit / Enumeration Abuse

**How it works:**  
OTP verification lacks proper rate limiting.

**Steps to Find**
1. Trigger OTP generation.
2. Send many OTP attempts rapidly.
3. Test empty or null OTP submissions.

**Impact**
- OTP brute force.

---

## 9. MFA Fatigue / Push Bombing Bypass

**How it works:**  
Attackers repeatedly trigger push authentication requests until the user accidentally approves one.

**Steps to Find**
1. Attempt repeated login requests.
2. Observe push notification behavior.
3. Check whether approval grants access.

**Impact**
- Social engineering–based MFA bypass.

---

## 10. SAML / SSO Parser Differential Bypass

**How it works:**  
Differences in XML or SAML parsing allow forged authentication responses.

**Steps to Find**
1. Intercept SAML responses.
2. Modify XML attributes.
3. Exploit parser inconsistencies.
4. Attempt forging admin assertions.

**Impact**
- Organization-wide account takeover.

---

## 11. OAuth / OpenID Connect Redirect or Code Misuse

**How it works:**  
Improper validation of redirect URIs or authorization codes.

**Steps to Find**
1. Intercept OAuth login flow.
2. Modify `redirect_uri`.
3. Replay or reuse authorization codes.

**Impact**
- OAuth authentication bypass.

---

## 12. JWT / Token Manipulation

**How it works:**  
JWT tokens are accepted without proper signature verification.

**Steps to Find**
1. Decode JWT token.
2. Modify payload.
3. Change algorithm to `none` or forge signature.
4. Replay modified token.

**Impact**
- Unauthorized access via forged tokens.

---

## 13. API Key / Token Exposure and Reuse

**How it works:**  
API keys exposed in code, logs, or URLs can be reused without restriction.

**Steps to Find**
1. Inspect client-side code.
2. Identify API keys or tokens.
3. Use them in unauthorized contexts.

**Impact**
- API authentication bypass.

---

## 14. Alternate Path / Channel Bypass

**How it works:**  
Different application channels enforce authentication inconsistently.

**Steps to Find**
1. Test `/web/login`.
2. Test `/api/login`.
3. Compare authentication enforcement.

**Impact**
- Authentication bypass through alternate channels.

---

## 15. Broken Password Recovery Flow

**How it works:**  
Password recovery logic bypasses authentication checks.

**Steps to Find**
1. Trigger password recovery.
2. Modify user identifiers.
3. Attempt password reset without proper verification.

**Impact**
- Account takeover via recovery flow.

---

## 16. HTTP Method Switching Bypass

**How it works:**  
Authentication checks apply only to certain HTTP methods.

**Steps to Find**
1. Test endpoint with POST request.
2. Switch method to GET or PUT.
3. Check if authentication is bypassed.

**Impact**
- Unauthorized access via method switching.

---

## 17. Orphaned / Zombie Sessions

**How it works:**  
Sessions remain valid even after account deletion or role change.

**Steps to Find**
1. Log in and capture session token.
2. Delete account or change role.
3. Replay the old token.

**Impact**
- Access after account removal.

---

## 18. GraphQL / Batch Authentication Bypass

**How it works:**  
GraphQL batch queries execute unauthorized operations within a single request.

**Steps to Find**
1. Send batched GraphQL queries.
2. Mix authenticated and unauthenticated operations.
3. Observe if unauthorized queries execute.

**Impact**
- Partial authentication bypass.

---

## 19. CAS / SSO Ticket Replay

**How it works:**  
Authentication tickets reused across services.

**Steps to Find**
1. Capture CAS ticket.
2. Replay it across different services.

**Impact**
- Cross-service account takeover.

---

## 20. Cookie Attribute Misconfiguration

**How it works:**  
Missing security flags expose session cookies.

**Steps to Find**
1. Inspect cookie attributes.
2. Check for missing `Secure`, `HttpOnly`, or `SameSite`.
3. Attempt cookie theft through XSS or MITM.

**Impact**
- Session hijacking.

---

## 21. Null Byte / Canonicalization Bypass

**How it works:**  
Null bytes manipulate string processing during authentication checks.

**Steps to Find**
1. Attempt login with payloads like `user%00@evil.com`.
2. Observe parser behavior.

**Impact**
- Authentication logic confusion.

---

## 22. Race Condition in Login / Token Issuance

**How it works:**  
Simultaneous authentication requests bypass security checks.

**Steps to Find**
1. Send multiple login requests simultaneously.
2. Use tools like Turbo Intruder.

**Impact**
- Limit bypass and unauthorized access.

---

## 23. Backdoor / Debug Authentication Endpoints

**How it works:**  
Debug or test authentication endpoints remain accessible in production.

**Steps to Find**
1. Fuzz endpoints.
2. Look for `/test/login`, `/debug`, or parameters like `?bypass=1`.

**Impact**
- Direct developer backdoor access.

---

## 24. Multi-Tenant SSO Bypass

**How it works:**  
Tenant identifiers can be manipulated during authentication.

**Steps to Find**
1. Modify `tenant_id` in SAML or OAuth flows.
2. Attempt cross-tenant access.

**Impact**
- SaaS data isolation breach.

---

## 25. Chained Authentication Bypass

**How it works:**  
Authentication bypass combined with other vulnerabilities such as IDOR or mass assignment.

**Steps to Find**
1. Identify authentication weaknesses.
2. Combine with privilege escalation vulnerabilities.

**Impact**
- Critical account takeover or admin compromise.

---

# Testing Methodology

## Essential Tools

- Burp Suite (Proxy, Repeater, Intruder, Turbo Intruder)
- OWASP ZAP
- Postman or Insomnia
- jwt.io and jwt_tool
- SAML Raider
- Custom scripts (Python requests)

---

## Best Practices

- Use multiple accounts (victim and attacker).
- Test login, 2FA, OAuth, SSO, and API authentication flows.
- Intercept all requests including cookies, headers, and bodies.
- Test behavior after logout or password change.
- Check alternate application channels (web, mobile, API).
- Document proof of concept with before and after access.

---

## Common Indicators

- Access to `/dashboard` without login.
- Tokens remain valid after logout.
- Modified parameters grant unauthorized access.
- Inconsistent `401` and `403` responses.
- Missing rate limiting on OTP or password reset.