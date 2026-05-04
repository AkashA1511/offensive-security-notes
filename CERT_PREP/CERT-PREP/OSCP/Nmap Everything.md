### Nmap Fundamentals 
- Host Discovery is it alive or not
- Port Scanning 
- Service and version information
- OS Detection 
- Script Scanning

### Port States 
|State|Meaning|Next Action in OSCP|
|---|---|---|
|**open**|Service is listening and accepting connections (TCP SYN/ACK, UDP response).|Banner grab, version scan, run relevant NSE scripts, manually probe. Prioritize.|
|**closed**|Port reached, but no service listening (RST for TCP, ICMP port unreachable for UDP).|Note it—host is alive, firewall likely not blocking these ports. Low priority, but keep in mind for firewall evasion later.|
|**filtered**|No response, or ICMP unreachable from firewall/router. Nmap can't determine if open/closed.|This is a flag: firewall in play. You might need to change scan type (SYN → ACK scan, or use source ports like 53, 80, 443). Try `-Pn` to skip host discovery if you haven't already.|
|**unfiltered**|Port accessible but Nmap can't figure out open/closed (rare, mostly in ACK scan).|Means firewall is stateless or the port is not filtered. Further scanning needed.|
|**open\|filtered**|No response (UDP common, or some TCP scans like NULL/FIN/Xmas).|Hit it again with `-sV` (version) or specific probe. For UDP, you might need to send a protocol-specific payload.|

**OSCP tip:** If you see lots of `filtered` ports, your first move is `-Pn` (skip ping) and then changing scan techniques (e.g., SYN -> `-sS`, then maybe `-sA` for firewall rules mapping).

### Scanning 

##### 1) My Default Scan 
```bash 

nmap -sS -p- -Pn <target>  # requires root 

```

##### 2) TCP Connect Scan (No raw sockets, works as normal user)
```bash 
nmap -sT -p- -Pn <target>  # - Completes three-way handshake. Noisier, needs no root. Use only if you can't run as root. Not preferred.
```

##### 3) UDP Scan 
```bash
nmap -sU -p- -Pn --min-rate 5000 <target>  # - UDP is slow. I always set a min rate (`--min-rate`) to speed up.
```