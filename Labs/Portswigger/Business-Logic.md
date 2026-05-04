# LAB : Insufficient workflow validation

Goal : We have to buy that jacket under $100 and cost of that jacket is $1337. 

Approach : so first purchased any smaller number item and view the requests so we saw that there is not specific  request that is taking with backend which has product details but there is confirmation request which is talking to backend. so we just add jacaket to cart and send that confirmation request to burp through repeter. 

---

# Authentication bypass via flawed state machine

Goal : Authentication Bypass to admin and delete carlos

Approach :  

so there are two request one login and after login there is a /role-selector
what i have done is, login though the wiener and drop the /role-selector request and i directly got the Admin panel access. 

There is another way like discover the content using engagement tools and do response manipulation and change the /role path to admin path. --> Try this method also (not able to discover that admin endpoint) -> watch solution. 

---
