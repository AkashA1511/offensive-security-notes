# DLL Hijacking

## DLL Hijacking – Thick Client Pentest Notes

### 1. Objective

Identify insecure DLL loading behavior in a thick client application and achieve code execution via DLL hijacking.

---

### 2. Key Concepts

- **DLL Hijacking**:  
    Occurs when an application loads a DLL without specifying a full path, allowing attackers to place a malicious DLL in a location that gets loaded first.
- **Search Order Abuse**:  
    Windows follows a specific DLL search order. If a DLL is missing, it looks in:
    1. Application directory
    2. System directories
    3. Current working directory
    4. PATH directories
- **Attack Goal**:  
    Place a malicious DLL in a higher-priority location to get executed.

---

### 3. Tools Used

- **Process Monitor (ProcMon)**  
    To monitor file system activity and identify missing DLLs
- **dnSpy**  
    For analyzing .NET binaries and understanding application behavior
- **GCC / MinGW**  
    To compile the malicious DLL

---

### 4. Reconnaissance

- Monitored application execution using ProcMon
- Applied filters:
    - Process Name = target application
    - Operation = `CreateFile`
    - Result = `NAME NOT FOUND`
- Identified missing DLL:
    
    profapi.dll
    

---

### 5. Vulnerability Identified

- Application attempted to load `profapi.dll` without specifying an absolute path
- DLL was not present in expected location
- This created an opportunity for DLL hijacking

---

### 6. Exploitation Steps

#### Step 1: Create Malicious DLL

Created a file:

profapi.c

Basic payload:

#include <windows.h>  
  
BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved) {  
    switch(fdwReason) {  
        case DLL_PROCESS_ATTACH:  
            MessageBox(NULL, "HIJACKED", "DLL Injection", MB_OK);  
            break;  
    }  
    return TRUE;  
}

---

#### Step 2: Compile DLL

Compiled using:

gcc -shared -o profapi.dll profapi.c -m32

- Ensured architecture matches target (32-bit)

---

#### Step 3: Place Malicious DLL

- Placed `profapi.dll` in application directory
- Required **administrative privileges** for placement

---

#### Step 4: Execution

- Launched the application
- Observed popup:
    
    HIJACKED
    
- Confirms successful DLL hijacking and code execution

---

### 7. Impact

- Arbitrary code execution
- Privilege escalation (if app runs with higher privileges)
- Persistence mechanism (if DLL remains in path)
- Potential for full system compromise

---

### 8. Root Cause

- Insecure DLL loading
- Missing DLL dependency
- No use of absolute paths
- No integrity verification of loaded libraries

---

### 9. Mitigation

- Use **absolute paths** when loading DLLs
- Implement **code signing validation**
- Use **SafeDllSearchMode**
- Avoid loading DLLs from writable directories
- Monitor unexpected DLL loads

---

### 10. Key Learning

- ProcMon is extremely powerful for identifying missing dependencies
- Matching architecture (x86/x64) is critical
- Even a simple MessageBox payload proves full execution capability
- DLL hijacking is low effort but high impact in real-world apps

--- 

### 1) DLL Hijacking (DLL file not found)

Report Soon...

### 2) DLL Hijacking (DLL File replace with importing functions )

Report Soon...

### 3) Privileged Escalation 

Report Soon....

### 4) Password Finding 

Password changed Forcefully from changing things at code