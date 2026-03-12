
I need  4 pillers for me : 

## Network : I am Weak here (Soon gonna be be beast here)
	**Why:** Everything in Red Team runs over a network. AD attacks, C2 traffic, lateral movement — all of it requires you to understand what's happening at the packet level.
	
	**What exactly to learn:**
	
	- TCP/IP model — how packets actually travel
	- DNS, HTTP, SMB, LDAP, Kerberos protocols (these 5 are essential for AD attacks)
	- Subnetting and routing basics
	- How firewalls and proxies work at a traffic level
	- Wireshark — reading and analyzing packet captures
	
	**Free Resources:**
	
	- Professor Messer Network+ (YouTube, completely free) — watch at 1.5x speed
	- TryHackMe "Pre-Security" path — free, hands-on, covers networking properly
	- Wireshark official sample captures — practice reading real traffic
	- TCPDump man page + practice in any Linux VM
## Active Directory (Heart of red teaming) 
	**Why:** 90% of real enterprise environments run Windows AD. If you don't know AD deeply, you are not a Red Teamer — you're a web tester. This is non-negotiable.
	
	**What exactly to learn:**
	
	- What AD is — domains, forests, trusts, OUs
	- Authentication protocols — NTLM and Kerberos in depth
	- Core AD attacks:
	    - AS-REP Roasting
	    - Kerberoasting
	    - Pass-the-Hash
	    - Pass-the-Ticket
	    - DCSync
	    - BloodHound enumeration
	    - GPO abuse
	- Basic AD enumeration with PowerView, SharpHound, BloodHound
	
	**Free Resources:**
	
	- TryHackMe "Active Directory Basics" room — free
	- TCM Security "Practical Ethical Hacking" (paid but ~$30, worth every rupee) — has full AD section
	- HTB Starting Point machines — free tier, several AD focused
	- PayloadsAllTheThings GitHub — AD attack cheatsheet, reference it constantly
	- BloodHound official documentation — read the whole thing
	**Goal by end:** You can take a foothold in an AD environment and enumerate paths to Domain Admin using BloodHound. 
## Linux and Windows Internals Basics 
	**Why:** You need to understand what you're operating inside — how processes work, how privileges are structured, how shells behave.

	**What exactly to learn:**
	
	**Linux:**
	
	- File permissions, SUID/SGID bits
	- Process management, /proc filesystem
	- Privilege escalation vectors — sudo misconfigs, cron jobs, weak file permissions, capabilities
	- Bash scripting for automation
	
	**Windows:**
	
	- Registry structure
	- Windows token model and privileges
	- UAC and how to bypass it
	- Windows services and scheduled tasks as attack vectors
	- PowerShell for offensive use
	
	**Free Resources:**
	
	- GTFOBins — Linux privesc reference (bookmark this now)
	- LOLBAS — Windows living-off-the-land binaries reference (bookmark this too)
	- TryHackMe "Linux PrivEsc" and "Windows PrivEsc" rooms — both free
	- HackTricks GitBook — free, covers everything, use as reference constantly
## WEB/API 
	- Business logic vulnerabilities
	- Access control
	- OAuth and SSO attacks
	- HTTP request smuggling
	- GraphQL attacks