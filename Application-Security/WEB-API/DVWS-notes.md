


## Vulnerabilities Identified

### 1. User Enumeration
- User enumeration possible on the login endpoint.

---

### 2. NoSQL Injection
- Found in **Public Notes**.
- Payload used:
 
```
' || this.type == 'public' ||
```
---

### 3. IDOR (Insecure Direct Object Reference)

- Found in **Notes Area**.
    
- Affected operations:
    
    - Delete
        
    - Update
        
    - Create
        
- Full unauthorized access possible.
    

---

### 4. Missing Rate Limiting

- Rate limiting not implemented across multiple endpoints.
    

---

### 5. Cross-Site Scripting (XSS)

- Vulnerable endpoint:
    
    - `admin.html`

---

### 6. Hidden API Parameters Disclosure

- Swagger documentation exposed:
    
    - `/api-docs`
        

---

### 7. Command Injection

- Vulnerable endpoint:
    
    ```
    GET /api/v2/sysinfo/uname;ls
    ```
    

---

### 8. Information Disclosure

- User-related information exposed.
    

---

### 9. JSON Hijacking

- Vulnerable endpoint:
    
    - `/parsephrases/admin`
        
