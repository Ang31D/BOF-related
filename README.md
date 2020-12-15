# Overview
Related tools to help out with Buffer Overflow.

## fuzz.py
Find out how much buffer is required until we crash the application.


* Usage
```
usage: fuzz.py [-h] --target TARGET --port PORT [--timout TIMEOUT] [--start-at START_AT] [--increase-by INC_BY] [--halt-before HALT_BEFORE] [--stop-after STOP_AFTER] [--exit-oncrash] [--prefix PREFIX] [--byte-char BYTE_CHAR]
               [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --target TARGET, -t TARGET
                        target
  --port PORT, -p PORT  target port
  --timout TIMEOUT, -T TIMEOUT
                        adjust timeout (default: 5)
  --start-at START_AT, -b START_AT
                        initial size of buffer
  --increase-by INC_BY, -i INC_BY
                        increase buffer size by (default: 500)
  --halt-before HALT_BEFORE, -H HALT_BEFORE
                        halt before buffer size
  --stop-after STOP_AFTER, -S STOP_AFTER
                        stop after buffer size
  --exit-oncrash, -E    exit after crash
  --prefix PREFIX, -P PREFIX
                        prefix before buffer
  --byte-char BYTE_CHAR, -C BYTE_CHAR
                        Character in buffer to send (default: A)
  --verbose, -v
  ```
  ## Examples
  ### Crash the application
  ```
python3 ./fuzz.py -t $(cat target.ip) -p 1337 -P "OVERFLOW10 "
[*] Fuzzing - target: 10.10.251.195, port: 1337, timeout: 5s
[*] Config - prefix 'OVERFLOW10 ', start at: 0, increment by: 500, char: 'A'
[*] Debug - verbose: Off, halt at: 0, step on halt: On
[#] Phases: #1 crash, #2 pattern, #3 offset
[#] Phases: #4 stack offset & buffer size
[#] Actions: set inc(rement) <number>, set bytes <number>
[#] Actions: pattern <length>, offset <pattern>
[#] Actions: c(ontinue), r(erun), q(uit)
[*] Sending buffer of 10 bytes
[*] Sending buffer of 500 bytes
[*] Sending buffer of 1000 bytes
[+] Crash after sending '1000' bytes
Restart server and enter <action> (help):
  ```
* What internal commands can we do?
```
Restart server and enter <action> (help): help
[#] help, info, q(uit), c(ontinue)
[#] pattern <length>, offset <pattern>
[#] set <option> <value>
[#] * options
[#]   inc(rement) <number>, (b)ytes <number>
[#]   stack offset <size>, buffer size <size>
[#]   halt at <size>, step <on/off>
[#] * Phases: #1 crash, #2 pattern, #3 offset,
[#]           #4 stack offset & buffer size
Restart server and enter <action> (help): 
```
* Check current settings
```
Restart server and enter <action> (help): info
[*] target: 10.10.251.195, port: 1337, timeout: 5s
[*] prefix 'OVERFLOW10 ', bytes: 1000, increment: 500, char: 'A'
[*] stack offset: 0, buffer size: 0
[*] halt at buffer: 0 (bytes), step on halt: On
Restart server and enter <action> (help): 
```
* Rerun with increment of 100 bytes
```
Restart server and enter <action> (help): set b 0
[*] Set 'bytes' at 0
Restart server and enter <action> (help): set inc 100
[*] Set 'increment' by 100
Restart server and enter <action> (help): c
[*] Sending buffer of 100 bytes
[*] Sending buffer of 200 bytes
[*] Sending buffer of 300 bytes
[*] Sending buffer of 400 bytes
[*] Sending buffer of 500 bytes
[*] Sending buffer of 600 bytes
[+] Crash after sending '600' bytes
Restart server and enter <action> (help): 
```
