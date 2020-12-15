# Overview

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
