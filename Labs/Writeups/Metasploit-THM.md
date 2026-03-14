# Metasploit: Introduction

`msfconsole`

###### Auxiliary 
	Scanners, crawlers and fuzzers can be found here
```
auxiliary
```

###### Encoders 
Encoders will allow you to encode the exploit and payload in the hope that a signature-based antivirus solution may miss them.
Signature-based antivirus and security solutions have a database of known threats. They detect threats by comparing suspicious files to this database and raise an alert if there is a match. Thus encoders can have a limited success rate as antivirus solutions can perform additional checks.

###### Evasion 
While encoders will encode the payload, they should not be considered a direct attempt to evade antivirus software. On the other hand, “evasion” modules will try that, with more or less success.

###### NOPs 

NOPs (No OPeration) do nothing, literally. They are represented in the Intel x86 CPU family with 0x90, following which the CPU will do nothing for one cycle. They are often used as a buffer to achieve consistent payload sizes.

-------------------------
###### Task 1 : Introduction to Metasploit

No Answer Needed

###### ===========================

###### Task 2 : Main Components of Metasploit

###### ===========================

[Question 1] : What is the name of the code taking advantage of a flaw on the target system?

[Answer] : Exploit

###### ===========================

[Question 2] : What is the name of the code that runs on the target system to achieve the attacker's goal?

[Answer] : payload

###### ===========================

[Question 3] : What are self-contained payloads called?

[Answer] : Singles

###### ===========================

[Question 4] : Is "windows/x64/pingback_reverse_tcp" among singles or staged payload?

[Answer] : Singles

###### ===========================

###### Task 3 : Msfconsole

[Question 2] : Who provided the auxiliary/scanner/ssh/ssh_login module?

[Answer] : todb

###### ===========================

###### Task 4 : Working with modules

###### ===========================

[Question 1] : How would you set the LPORT value to 6666?

[Answer] : set LPORT 6666

###### ===========================

[Question 2] : How would you set the global value for RHOSTS to 10.10.19.23 ?

[Answer] : setg RHOSTS 10.10.19.23

###### ===========================

[Question 3] : What command would you use to clear a set payload?

[Answer] : unset PAYLOAD

###### ===========================

[Question 4] : What command do you use to proceed with the exploitation phase?

[Answer] : exploit

###### ===========================

###### Task 5 : Summary

No Answer Needed