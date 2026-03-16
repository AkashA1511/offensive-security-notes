## Password DOS
Passwords should accept limited number of characters, if the password is generating hash or something and we tried to  to add 500 char then it will leads to the DOS attack.
	- [  ] look for No password length Restriction POC 
-------------------------
## Buffer-Overflow 
A buffer overflow occurs when a program writes more data to a fixed-size memory buffer than it can hold, causing the excess data to overwrite adjacent memory location, This can lead to unpredictable behavior program crashes data corruption or allow attacker to add a malicious code, gain authorized access or take control of a system. 

##### Stack-Based Buffer Overflow 

```c
#include <stdio.h>
#include <string.h>

void vulnerable(char *input) {
    char buffer[64];
    strcpy(buffer, input);   //strcpt is not checking the size here and it also include variable input memory also
}

int main(int argc, char *argv[]) {
    vulnerable(argv[1]);
}
```

- If the attacker sends **more than 64 bytes**, memory beyond the buffer gets overwritten.

```
Before overflow

| buffer[64]        |
| saved EBP         |
| return address    | ---> normal execution


After overflow

| AAAAAAAAAAAAAAAA  |
| AAAAAAAAAAAAAAAA  |
| BBBBBBBB          |
| 0xdeadbeef        | ---> attacker control
```

```python

# Real Attack Flow Using fuzzing or manual testing.

python -c "print('A'*500)"

```

#####  Heap-Based Buffer Overflow 
Heap is used for **dynamic memory allocation**:
```
malloc()
calloc()
realloc()
free()


char *buf = malloc(64);

```

```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {

    char *buf1 = malloc(64);
    char *buf2 = malloc(64);

    gets(buf1);

    free(b
    return 0;
}
```

##### Integer Buffer Overflow  




```
#include <stdio.h>
#include <stdlib.h>

int main() {

    unsigned int size = 4000000000;
    unsigned int total = size + 100;

    char *buffer = malloc(total);

    return 0;
}
```

```
User Input
   ↓
Integer Calculation
   ↓
Overflow Occurs
   ↓
Wrong Buffer Size Allocated
   ↓
Large Copy Happens
   ↓
Memory Corruption

```

##### Format String buffer Overflow Vulnerabilities 

1)  How Format Functions Normally Work
```
printf()
fprintf()
sprintf()
snprintf()
syslog()

printf("Hello %s", name);

printf("Value: %d", 10);

```

```
#include <stdio.h>

int main() {

    char input[100];
    fgets(input, sizeof(input), stdin);

    printf(input);

    return 0;
}
```

-----------------------

[[Offensive_VC_Android]]
------------------------------------------------------------

## Subdomain Takeover 

#### 1. What is a Subdomain Takeover (Simple Explanation)

A **subdomain takeover happens when a subdomain points to a service that no longer exists, but the DNS record still exists.**

Example:

blog.example.com → cname → example.herokuapp.com

If the company **deleted the Heroku app** but **forgot to remove the DNS record**, you can:

1. Create a **Heroku app with that same name**
    
2. Attach the domain
    
3. Now **blog.example.com points to YOUR server**
    

You now control their subdomain.

This is a **subdomain takeover vulnerability**.

---

#### 2. Real Example DNS

Let's say you run:

dig blog.example.com

Output:

blog.example.com CNAME example.herokuapp.com

Now if you open the website you see:

No such app

This means the service is **unclaimed**.

If you claim it → **Takeover successful**.

---

#### 3. Why This Happens

Companies:

• Remove cloud service  
• Forget DNS record  
• Subdomain still points to dead service

Services commonly involved:

|Service|Message|
|---|---|
|AWS S3|NoSuchBucket|
|Heroku|No such app|
|GitHub Pages|There isn't a GitHub Pages site here|
|Shopify|Sorry this shop is currently unavailable|
|Fastly|Fastly error: unknown domain|
|Azure|404 Web Site not found|

These are **takeover fingerprints**.

---

#### 4. Step 1 — Find Subdomains

First collect subdomains.

Tools:

subfinder  
assetfinder  
amass  
crt.sh  
chaos

Example:

subfinder -d target.com -all -recursive > subs.txt

Then combine tools:

assetfinder --subs-only target.com >> subs.txt

Remove duplicates:

sort -u subs.txt -o subs.txt

---

#### 5. Step 2 — Find Alive Subdomains

Now check which ones respond.

Tool:

httpx

Example:

cat subs.txt | httpx -silent -status-code

But for takeover we also want **dead ones**.

So we keep both.

---

#### 6. Step 3 — Detect Possible Takeovers

Tool:

### Subjack

subjack -w subs.txt -t 100 -timeout 30 -ssl -v

or

### Nuclei

nuclei -l subs.txt -t takeovers/

or

### Subzy

subzy run --targets subs.txt

These tools detect **fingerprints**.

Example output:

vulnerable: blog.example.com (Heroku)

---

#### 7. Step 4 — Verify Manually (VERY IMPORTANT)

Tools give **false positives**.

You must verify.

Run:

dig subdomain.target.com

Check:

CNAME → service

Then open website.

If message says:

No such app

Then check if service **allows claiming**.

Example:

Go to Heroku → create app.

If it allows domain binding → vulnerability confirmed.

---

#### 8. Step 5 — Exploiting the Takeover

Example with **GitHub Pages**.

DNS:

blog.target.com CNAME username.github.io

But repo deleted.

You create:

username.github.io

Add:

blog.target.com

Now you control:

https://blog.target.com

Put a **PoC page**:

Subdomain takeover by Akash

---

#### 9. Advanced Hunting Method (Used by Pro Hunters)

Pro hunters don't rely only on tools.

They do **DNS analysis**.

Check for:

CNAME  
NS  
A records

Command:

dnsx -l subs.txt -resp

Look for:

CNAME → external service

Example:

dev.target.com → dev.herokuapp.com  
cdn.target.com → fastly.net  
assets.target.com → github.io

Then check if service is **unclaimed**.

---

#### 10. Cloud Services With Most Takeovers

Very important list:

AWS S3  
Heroku  
GitHub Pages  
Azure  
Shopify  
Fastly  
Cloudfront  
Bitbucket  
Ghost.io  
Pantheon  
Zendesk  
WordPress  
Tumblr

Bug hunters specifically hunt these.

---

#### 11. Advanced Automation Pipeline

Real hunters run pipelines like this:

subfinder -d target.com -all -recursive |  
httpx -silent |  
dnsx -cname |  
nuclei -t takeovers/

OR

amass enum -passive -d target.com |  
subjack -ssl -t 100

----
#### AWS s3 bucket takeover 

- you get error and 404 not found and or any error then you can takeover it and check with "can i take this subdomain"
-  create a S3 bucket first 
-  Upload  a file 
- create a static website hosting 
-  route 53 > DNS Management  > give domain name > custom name server 

#### Shopify takeover 

- Error : This shop is not currently available
- create  your store 
- add domain 

---
---

## IDOR 

You are already very good at IDOR you dont need any notes XD !!! 

Just changed ID's, Methods hit and trial and many more things that 

[[BugBounty/IDOR|IDOR]]

--- 


## Wordpress 
- wpscan 
	- enumerate all plugins 