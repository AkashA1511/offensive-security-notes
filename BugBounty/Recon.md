
`If you scrap the JS files use the jsluice for scrapping the secreat credentials.


- Just dont use subfinder and sublister directly and also configure thier config.yaml files for better results 

- Use shuffledns [https://github.com/projectdiscovery/shuffledns]
  - Ticket Resolvers [https://github.com/trickest/resolvers]
  -  wordlist
     -  seclist
     -  assetwordlist 
  ``` bash 
    shuffledns -d <target.com> -w wordlist.txt -r resolver.txt 

    shuffledns -d <target.com> -w wordlist.txt -r resolver.txt -mode bruteforce
   ```

## Asset Discovery 
    with our existing domain keyword it will help us find combination with diffrent API, dev etc with ALTERX 

    ```
    cat domains.txt | alterx | dnsx 
    ``
    After that use dnsX for check whether those sites are up or not 

--------------------------------------------------------- 

## Naabu (for port scanning)

```
    cat domains.txt | alterx | dnsx | naabu -p -tp -ep 22 
```

same as nmap 

then do httpx 

-----------

katana for finding JS 

```
checkout chaos-client tool 
```

---------------
---------------

## Recon part I 
1. Find All Subdomains 
2. do [CRT.sh](http://CRT.sh) 
3. use censys for checking which technology target use 
4. Enumerate All  subdomains 
    
    ```bash
    sudo subfinder -d netflix.com -all > sundomain.txt
    ```
    
5. Also use Assetfinder 
    
    ```bash
    sudo assetfinder -subs-only netflix.com > subdomain1.txt
    ```
    
6. Combined both the list 
    
    ```bash
    sort -u subdomain.txt subdomain1.txt > miansundomain.txt
    ```
    
7. check HTTPX 
    
    ```bash
    	cat mainsubdomain.txt | sudo httpx > alive_subdoamin.txt
    	
    		cat alive_subdomains.txt | sudo httpx -sc > alive_domains_code.txt 
    ```
    
8. check subdomain takeover available or not  using subzy
    
    ```bash
    sudo subzy run --targets mainsubdomains.txt
    
    #Here check youtube about subdomain takeover
    ```
    
9. Check domains Katana katanan is crawler tool it scan all URLs
    
     
    
    ```bash
    sudo katana -u https://brand.netflix.com -jc -o allurls.txt
    
    #only javascript path find 
    
    sudo katana -u <alive subdmains.coo=m> 5 -ef woff, css, png, svg,jpg, woff2, jpeg,gif, svg -o allurls.txt
    
    #chck all subdomains who are alive 
    
    If we find any parameter in katana allurl like "=" then try XSS and sql injection 
    ```
----------------
----------------

## Recon Part II 
1. check technologies via  censys 
2. [crt.sh](http://crt.sh) for finding manual subdomain 
    1. copy all that subdomain 
3. Use Virustotal for gathering info
4. [chaos.projectdiscovery.io](http://chaos.projectdiscovery.io) for more subdomains 
    1. download subdomains file from there 
5. automatic subdomain
    
     
    
    ```bash
    sudo subfinder -d paydient.com-all > domain1.txt
    ```
    
6. Also try asset finder 
    
    ```bash
    sudo assetfinder -subs-only paydient.com > domain2.txt
    
    ```
    
7. try bruteforcing subdomains ffuf 
    
    ```bash
    ffuf -u https://FUZZ.paydient.com -W n0kovo_subdomanins/n0kovo_subdomains_medium.txt domain3.txt
    
    Fuzz is like a which loaction we like to bruteforce 
    ```
    
8. sort all text files together 
    
    ```bash
    sort -u domain1.txt domain2.txt > domain.txt
    ```
    
9. check for lives domains 
    
     
    
    ```bash
    cat domain.txt | sudo httpx > live_domains.txt 
    ```
    
10. check subzy for subdomain takeover 
    
    ```bash
    subzy run --targets domain.txt
    ```
    
11. try nuclei 
    
    ```bash
    # All subdomain list 
    nuclei -l domain.txt -t nuclei-templates/detect-all-takeovers.yaml  
    
    # Also check live subdomains 
    nuclei -l http://code.paydient.com -t nuclei-templates/detect-all-takeovers.yaml  
    ```
    
12. use katana and use alive domains from httpx
    
    ```bash
    katana -u http://code.paydient.com -o urls.txt 
    ```
    
    <aside>
    💡
    
    Use katana for every other live subdomain who gives you 200 status code 
    
    </aside>
    
13. Use ONEFORALL tool very powerful china tool 
    
    ```bash
    chmod +x oneforall.py
    
    python3 oneforall.py --targets ../live_sundomains.txt run 
    ```
    
14. and use wayback urls if katana not worked 
    
    ```bash
    echo "https://paydient.com" | waybackurls > urls.txt 
    ```
    
15. USE grep method to sort this urls 
    
    ```bash
    cat urls.txt | grep = 
    
    cat urls.txt | grep ?*
    
    cat urls.txt | grep search 
    
    cat urls.txt | grep ?*= 
    
    so here we have to check urls so we are gonna able to find xss and sqli injection 
    ```
    
16. so try  google doking to find login pages, reset passwords and all and those files are in telegram downlaod that 
17. later try github dorking 
    
    developers forgot some API keys and all in code so we have to find that 
    
18. use ARJUN , gowitness tools 
19. use socialhunter for social media links for broken link hijack