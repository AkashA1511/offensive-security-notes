
# 1) API-01 : Broken Object Level Authoriztion 
	
- BOLA happens when an API checks who you are but forgets to check what are you allowed to access.
like it do Authentication 

- “If I can access someone else’s data just by changing an ID, it’s BOLA.”

```
Imagine a bank locker room.
You have a bank entry card → authentication
Each locker has a number → object ID
You should access only your locker
Now imagine this:
Guard checks: “Is this person a valid customer?” 
Guard does NOT check: “Is this locker theirs?” 

So you just walk to locker #102 instead of #101
 BOOM — BOLA

```

-------------------------------------------------------

# 2) API-02: Broken Authentication 
- Broken Authenticatin happens when the api fails to correctly verify who you are and allowing attakers to improsonate users. 
  
 
```
The API fails at managing identity, such as:
Tokens
Sessions
Login logic
Password handling
OTP / reset flows
The attacker becomes you.
```

