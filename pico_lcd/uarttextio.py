from baseTextIo import *
from machine import UART, Pin
import select
import utime

class UartTextIo(baseTextIo):
    # constructor
    # for uartNo=0, tx/rx can be 0/1,12/13,16/17
    # for uartNo=1, tx/rx can be 4/5, 8/9
    def __init__(self, uartNo, baud, rxPin, txPin):
        self.poller = select.poll()
        self.uart = UART(uartNo, baud, rx=rxPin, tx=txPin)
        self.poller.register(self.uart, select.POLLIN)
        self.bufferSize = 1024                 # size of circular buffer to allocate
        self.buffer = [' '] * self.bufferSize
        self.nextIn = 0
        self.nextOut = 0
        self.echo = False

    def __readUart(self):
        events = self.poller.poll(0)
        for f in events:
            if f[0] == self.uart:
                chrs = self.uart.any()
                cnt = 0
                pos = 0
                while cnt < chrs:
                    cnt += 1
                    pos += 1
                    chr = self.uart.read(1)
                    #print("["+str(cnt)+"]="+str(chr))
                    # backspace
                    if self.echo:
                        self.Echo(chr)
                    if chr == b'\x7f':
                        if pos > 0:
                            pos -= 1
                            self.nextIn -= 1
                        continue
                    # ignored chars
                    if chr == b'\xff':
                        continue
                    # control key on terminal, skip all
                    if chr == b'\x1b' and cnt == 1:
                        cnt = chrs
                        continue
                    self.buffer[self.nextIn] = chr
                    self.nextIn += 1
                    if self.nextIn >= self.bufferSize:
                        self.nextIn = 0
                #print(str(chrs)+" chrs, ptr="+str(self.nextIn))
                return chrs
        return 0

    # Get line from system
    def GetLine(self):
        nchr = self.__readUart()
        
        if self.nextOut == self.nextIn:
            return ''
        n = self.nextOut
        while n < self.nextIn:
            #print("scan "+str(self.buffer[n]))
            asc = self.buffer[n]
            if asc == b'\n' or asc == b'\r':
                break
            n += 1
            if n == self.bufferSize:
                n = 0
            # No LF found
            if n == self.nextIn:
                return ''
            
        #print("got n="+str(n))
        lin = ''
        n += 1
        if n == self.bufferSize:
            n = 0
        while self.nextOut != n:
            addch = True
            lup = True
            asc = self.buffer[self.nextOut]
            if asc == b'\r' or asc == b'\n':
                addch = False
                lup = False
            
            #print("chk ["+str(self.nextOut)+"]:"+str(self.buffer[self.nextOut]))
            if addch:
                lin = lin + self.buffer[self.nextOut].decode('UTF-8')
            self.nextOut += 1
            if self.nextOut == self.bufferSize:
                self.nextOut = 0
            if not lup:
                break
                
        return lin
    
    def Echo(self, ch):
        self.uart.write(ch)
        
    def PutLine(self, line):
        newln = line + "\n"
        self.uart.write(newln)
        #print("PutLine:"+newln)
        
# Test code
if __name__=='__main__':
    print("Init...")
    myuart = UartTextIo(0, 115200, Pin(1), Pin(0))
    myuart.PutLine("Hello, enter some text:\r\n")
    print("Receiving text from remote")
    cnt = 0
    while True:
        ss = myuart.GetLine()
        if len(ss) < 1:
            utime.sleep(0.1)
            cnt += 1
            if cnt >= 100:
                myuart.PutLine("Hello! Reply me:\n\r")
                cnt = 0
        else:
            writeS = ss+"("+str(len(ss))+")"
            myuart.PutLine(writeS)
            print(writeS)
