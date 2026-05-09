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

#  Flawed enforcement of business rules

Goal : Lightweight l33t leather jacket 

Approach :  so there are  one coupan which is visible so there is one newsletter we apply to that we get a new coupan and from those coupan use alternatively we get the jacker as a free. 

---

# Infinite money logic flow 

already found this type of bug in the CERT-IN Exam which was refund leads me to infinite money via rate limit 

Goal : This lab has a logic flaw in its purchasing workflow. To solve the lab, exploit this flaw to buy a "Lightweight l33t leather jacket".

Approach : 

Buy a gift card and use it . 

Open session handeling rules from the settings --> Add run a macro --> select macro --> add (choose 5 request) 
```
POST /cart 
POST /cart/coupan
POST /cart/checkout
GET /cart/order-confirmation?order-confirm=true
POST /giftcard
```

then choose order request and --> configure item --> add (parameter name = gift card ) --> select coupan code from then response 
then choose giftcard request --? configure item -->  parameter hadneling --> change `use present value` to `derive prior response`
test macro you will get a new coupan code 

then send GET /my- accout to intruder set null payload and send multiple  request and money is getting in to the account. 

--- 

