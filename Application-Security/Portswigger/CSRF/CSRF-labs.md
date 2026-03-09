
# LAB : CSRF vulnerability with no defenses

Goal :  We have to craft some HTML use it in the exploit 

Approach : 

go the post request of email change > generate a CSRF POC > paste it in the Exploit 

--------------------------------

# LAB :  CSRF where token validation depends on request method

Goal : I have to use my exploit server to host an HTML page that uses CSRF attack to change viewer email address. 

Approach : 

Generate a CSRF_POC > paste it in the exploitation server and store and deliver to victim. 


----------------------------------------

# LAB : CSRF where token validation depends on token being present
- Remove the CSRF token from the generated poc and send it to victim
