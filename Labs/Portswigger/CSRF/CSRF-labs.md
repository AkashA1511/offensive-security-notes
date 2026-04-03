
# LAB : CSRF vulnerability with no defenses

Goal :  We have to craft some HTML use it in the exploit 

Approach : 

go the post request of email change > generate a CSRF POC > paste it in the Exploit 

--------------------------------

# LAB :  CSRF where token validation depends on request method

Goal : I have to use my exploit server to host an HTML page that uses CSRF attack to change viewer email address. 

Approach : 

change the csrf_token and send request we are gonna get the bad request, 
then just changed the method of the same wrong csrf token and send rqst and it gonna give us 302 OK so create a csrf poc of that and send it to the exploited server 


----------------------------------------

# LAB : CSRF where token validation depends on token being present
- Remove the CSRF token from the generated poc and send it to victim

---

# LAB : CSRF token is not tied to the user session

-  Attacker can login with his account --> get his own token -> use the same token for victim account 
-  Goal : use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address
- Approach : There are two user and  we have to check that can we use carlos CSRF token to wienr email changed !!  --> so for that we intercepted both the request and changed the CSRF to and take the CSRF POC and send it to victim. 
--- 

# LAB :  CSRF where token is tied to non-session cookie 
```
In a variation on the preceding vulnerability, some applications do tie the CSRF token to a cookie, but not to the same cookie that is used to track sessions. This can easily occur when an application employs two different frameworks, one for session handling and one for CSRF protection, which are not integrated together:

 POST /email/change HTTP/1.1
 Host: vulnerable-website.com 
 Content-Type: application/x-www-form-urlencoded 
 Content-Length: 68 
 Cookie: session=pSJYSScWKpmC60LpFOAHKixuFuM4uXWF; csrfKey=rZHCnSzEp8dbI6atzagGoSYyqJqTz5dv
 csrf=RhV7yQDO0xcq9gLEah2WVbmuFqyOq7tY&email=wiener@normal-user.com

This situation is harder to exploit but is still vulnerable. If the website contains any behavior that allows an attacker to set a cookie in a victim's browser, then an attack is possible. The attacker can log in to the application using their own account, obtain a valid token and associated cookie, leverage the cookie-setting behavior to place their cookie into the victim's browser, and feed their token to the victim in their CSRF attack.
```

- Goal : exploit server to html page host csrf attack 
  - here we have to use below code snippet and
```
`<form method="POST" action="https://YOUR-LAB-ID.web-security-academy.net/my-account/change-email"> <input type="hidden" name="email" value="anything%40web-security-academy.net"> </form> <script> document.forms[0].submit(); </script>`
```
- here CSRF token tied with the CSRF key and we have to add both we can add CSRF key in the response with Set-Cookie thing and here javascript wont work so remove that add in the html code inself. 
- here first view exploit then change email again and then deliver it to the victim. 
---

# LAB : CSRF where token is duplicated in cookie

- Goal : use your exploit server to host an HTML page that uses a CSRF attack to change the viewer's email address.
-  here we have to add fake crsf token in the both same code snippet and here also java script was not working but use that html one snippet. 
---

# LAB :  SameSite Lax bypass via method override

- Goal : changed the email but here in this lab they are using a Samesite LAX cookie so there is no CSRF token and with the same session we cannot changed the email. 
- Approach : 
   → just notice the POST request is not allowing a anything like without cookie or any other thing 
   → so we tried to changed that Method but changeing method is not allowed so 
   → so I use GET method but changed it to post method llike this : 
      ⇒ 
```
GET /my-account/change-email?email=foo%40web-security-academy.net&_method=POST HTTP/1.1
```

      ⇒ use this request in the script section in the HTML code snippet to changed the email. 
      ⇒ this is happend beacuse at login or a GET req cookie is diffrent and its behaviour to and at the time of changing its diffrent for the Methods so we did that. 

---

# Lab: CSRF where Referer validation depends on header being present

Goal : This lab's email change functionality is vulnerable to CSRF.  It attempts to block cross domain requests but has an insecure  fallback.
To solve the lab, use your exploit server to host an HTML  page that uses a CSRF attack to change the viewer's email address.         

Approch : 
	remove referrer completley 
	and add this in the HTML payload : “<meta name="referrer" content="no-referrer">” 
---


# Lab: CSRF with broken Referer validation
Goal : 
Approch : 
	history.pushState("", "", "/?YOUR-LAB-ID.web-security-academy.net")
	Referrer-Policy: unsafe-url 
	CSRF 
--- 


