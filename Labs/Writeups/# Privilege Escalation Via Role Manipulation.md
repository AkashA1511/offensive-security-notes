
# Privilege Escalation via Role Manipulation in a Healthcare Reporting Platform

Last month I discovered a vulnerability in a **private healthcare program** that rewarded me _**_$ through their bug bounty program.

After waiting for the responsible disclosure period (30+ days), I’m sharing a **redacted version** of the finding for educational purposes.

Due to program policy, I cannot disclose:

- The company name
- The domain or endpoints
- Screenshots of the system
- Sensitive request data

However, the vulnerability and methodology are reproduced in a safe and educational way.

---

# Target Overview

The affected asset was a **subdomain responsible for managing diagnostic machine reports** used in the healthcare industry.

The platform handled reports generated from machines such as:

- X-Ray systems
- MRI scanners
- CT scanners etc

Because of this functionality, the application processed **large amounts of sensitive patient-related data**, making proper access control extremely critical.

---

# Initial Access

I had access to the platform with a role I will refer to as:

**Standard Manager Role**

This role allowed several management actions such as:

- Creating users
- Assigning basic roles
- Managing certain user settings

However, one restriction existed.

Users with this role **should not be able to create or assign a higher privileged role**, which I will refer to as:

**System-Level Role**

---

# Observing the Restriction

When attempting to create a user with the **System-Level Role** directly through the interface, the application blocked the action.

The system returned an error similar to:

```
Only administrators can create or modify users with this role.
```

At first glance, it appeared that proper authorization checks were implemented.

But security testing always requires verifying what happens **behind the interface**.

---

# Testing an Alternate Flow

Instead of assigning the restricted role immediately, I tried a different approach.

Step 1: Create a user with a normal role.

Example:

```
basic_user_role
```

This worked successfully and the user was created.

---

# Intercepting the Edit Request

Next, I edited that newly created user while intercepting the traffic through a proxy.

The request looked similar to this:

```
POST /api/v1/users/update HTTP/1.1
Host: redacted-domain.com
Content-Type: application/json
Authorization: Bearer REDACTED

{
  "user_id": "84291",
  "role": "basic_user_role"
}
```

The UI still prevented selecting the restricted role.

But the request itself could still be modified before reaching the server.

---

# Manipulating the Request

Before forwarding the request, I modified the role value.

```
POST /api/v1/users/update HTTP/1.1

{
  "user_id": "84291",
  "role": "system_level_role"
}
```

Then I forwarded the request to the backend.

---

# Result

Despite the interface restriction, the backend **accepted the modified request**.

Example response:

```
HTTP/1.1 200 OK

{
  "status": "updated",
  "role": "system_level_role"
}
```

The user account now possessed the **restricted System-Level Role**.

---

# Root Cause

The vulnerability occurred because authorization was enforced only on the **client side**.

The backend failed to properly validate whether the current user had permission to assign that role.

This allowed a malicious user to intercept and modify requests to bypass the restriction.

---

# Security Impact

If exploited in the real world, this issue could potentially lead to:

- Privilege escalation
- Unauthorized administrative capabilities
- Access to sensitive healthcare-related systems
- Potential exposure or manipulation of patient-associated records

In environments that handle diagnostic data, the risk is especially significant.

---

# Responsible Disclosure

I responsibly reported this issue through the private bug bounty program.

The security team acknowledged the report and fixed the vulnerability.

After the **30-day responsible disclosure period**, I am sharing this redacted explanation so other security researchers and developers can learn from it.

---

# Key Lesson

Never rely solely on **client-side validation** for enforcing permissions.

All access control checks must be implemented and validated on the **server side**.

If the server trusts the client, attackers can simply change the request.

---

# Final Thoughts

Privilege escalation bugs often appear in places developers assume are safe.

Whenever testing applications, always try:

- Intercepting role changes
- Modifying hidden parameters
- Replaying requests with altered values
- Exploring alternate workflows

Sometimes the interface says **“not allowed”**, but the backend silently disagrees.