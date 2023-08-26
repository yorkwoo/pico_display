#
# Input interface for USB serial
#
from sys import stdin
import select
import utime
import micropython
import sys
from baseTextIo import *

# Read/Write text data from USB serial
class UsbSerialIo(baseTextIo):
    # constructor
    def __init__(self):
        self.poller = select.poll()
        self.poller.register(stdin, select.POLLIN)

    # Get line from system
    def GetLine(self):
        events = self.poller.poll(10)
        okread = False
        st = ''
        for f in events:
            if f[0] == stdin:
                okread = True
                st = st + stdin.readline().rstrip('\n')
        return st
        
    def PutLine(self, line):
        newln = line + "\n"
        print(newln)
        
# Test code
if __name__=='__main__':
    print("Init...")
    usb = UsbSerialIo()
    #micropython.kbd_intr(-1)    # disable break
    try:
        print("Enter text plz:")
        while True:
            ss = usb.GetLine()
            if len(ss) < 1:
                print ("------")
                utime.sleep(0.2)
            else:
                print (ss+"("+str(len(ss))+")")
                
    except KeyboardInterrupt:
        print("Bye!")
        sys.exit()

