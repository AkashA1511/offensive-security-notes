
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
