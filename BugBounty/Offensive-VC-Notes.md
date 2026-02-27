## Password DOS
Passwords should accept limited number of characters, if the password is generating hash or something and we tried to  to add 500 char then it will leads to the DOS attack.
	- [  ] look for No password length Restriction POC 
-------------------------
## Buffer-Overflow 
A buffer overflow occurs when a program writes more data to a fixed-size memory buffer than it can hold, causing the excess data to overwrite adjacent memory location, This can lead to unpredictable behavior program crashes data corruption or allow attacker to add a malicious code, gain authorized access or take control of a system. 

##### Stack-Based Buffer Overflow 

```c
#include <stdio.h>
#include <string.h>

void vulnerable(char *input) {
    char buffer[64];
    strcpy(buffer, input);   //strcpt is not checking the size here and it also include variable input memory also
}

int main(int argc, char *argv[]) {
    vulnerable(argv[1]);
}
```

- If the attacker sends **more than 64 bytes**, memory beyond the buffer gets overwritten.

```
Before overflow

| buffer[64]        |
| saved EBP         |
| return address    | ---> normal execution


After overflow

| AAAAAAAAAAAAAAAA  |
| AAAAAAAAAAAAAAAA  |
| BBBBBBBB          |
| 0xdeadbeef        | ---> attacker control
```

```python

# Real Attack Flow Using fuzzing or manual testing.

python -c "print('A'*500)"

```

#####  Heap-Based Buffer Overflow 
Heap is used for **dynamic memory allocation**:
```
malloc()
calloc()
realloc()
free()


char *buf = malloc(64);

```

```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {

    char *buf1 = malloc(64);
    char *buf2 = malloc(64);

    gets(buf1);

    free(b
    return 0;
}
```

##### Integer Buffer Overflow  




```
#include <stdio.h>
#include <stdlib.h>

int main() {

    unsigned int size = 4000000000;
    unsigned int total = size + 100;

    char *buffer = malloc(total);

    return 0;
}
```

```
User Input
   ↓
Integer Calculation
   ↓
Overflow Occurs
   ↓
Wrong Buffer Size Allocated
   ↓
Large Copy Happens
   ↓
Memory Corruption

```

##### Format String buffer Overflow Vulnerabilities 

1)  How Format Functions Normally Work
```
printf()
fprintf()
sprintf()
snprintf()
syslog()

printf("Hello %s", name);

printf("Value: %d", 10);

```

```
#include <stdio.h>

int main() {

    char input[100];
    fgets(input, sizeof(input), stdin);

    printf(input);

    return 0;
}
```


