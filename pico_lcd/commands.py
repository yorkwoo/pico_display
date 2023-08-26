from baseTextIo import *
from baseDraw import *
#import debugfile

#baseTextIo
useIoDev = None
lcdDraw = None
# Provides outsides to check if exit
isEnd = False

def Init(ioDev, drawDev):
    global useIoDev
    global lcdDraw
    useIoDev = ioDev
    lcdDraw = drawDev

# 執行命令的函式，輸入引數都是 words[], 輸出則為 OK 或 ERR, 除了 info
def exec_clear(words):
    global lcdDraw
    lcdDraw.clear()
    return "OK"
    
def exec_info(words):
    global lcdDraw
    return lcdDraw.info()
    
def exec_text(words):
    global lcdDraw
    try:
        x = int(words[1])
        y = int(words[2])
        # 後面全部都是字串的部份，只是恰巧被切了
        msg = ""
        n = 3
        while n < len(words):
            msg = msg + words[n]
            n = n + 1
            if n < len(words):
                msg = msg + ","
        lcdDraw.print(x, y, msg)
        return "OK"
    except ValueError:
        return "ERR"
        
def exec_putc(words):
    global lcdDraw
    try:
        x = int(words[1])
        y = int(words[2])
        c = int(words[3])
        lcdDraw.printc(x, y, chr(c))
        return "OK"
    except ValueError:
        return "ERR"

# 顏色碼：RRGGBB 轉換為 LCD 色碼輸出
def parse_color(colorcode6):
    global lcdDraw
    try:
        if len(colorcode6) == 6:
            totval = int(colorcode6, 16)
            rr = colorcode6[0:2]
            #print(rr)
            gg = colorcode6[2:4]
            #print(gg)
            bb = colorcode6[4:6]
            #print(bb)
            ri = int(rr,16)
            gi = int(gg,16)
            bi = int(bb,16)
            return [ri, gi, bi]
        else:
            #print("len="+str(len(colorcode6)))
            return "ERR"
    except ValueError:
        #print("value error")
        return "ERR"
        
def exec_fgcolor(words):
    global lcdDraw
    col = parse_color(words[1])
    if type(col) is list:
        lcdDraw.set_fgcolor(col[0], col[1], col[2])
        return "OK"
    else:
        return "ERR"

def exec_bgcolor(words):
    global lcdDraw
    col = parse_color(words[1])
    if type(col) is list:
        lcdDraw.set_bgcolor(col[0], col[1], col[2])
        return "OK"
    else:
        return "ERR"
        
def exec_hbar(words):
    # hbar x y width millis options
    global lcdDraw
    try:
        x = int(words[1])
        y = int(words[2])
        w = int(words[3])
        m = int(words[4])
        o = int(words[5])
        lcdDraw.hbar(x, y, w, m, o)
        return "OK"
    except ValueError:
        return "ERR"

def exec_vbar(words):
    # vbar x y width millis options
    global lcdDraw
    try:
        x = int(words[1])
        y = int(words[2])
        w = int(words[3])
        m = int(words[4])
        o = int(words[5])
        lcdDraw.vbar(x, y, w, m, o)
        return "OK"
    except ValueError:
        return "ERR"
        
def exec_hb(words):
    global lcdDraw
    try:
        h = int(words[1])
        lcdDraw.heartbeat(h)
        return "OK"
    except ValueError:
        return "ERR"
        
def exec_exit(words):
    global lcdDraw
    global isEnd
    isEnd = True
    #init_bright(200)
    return "OK"
    
def exec_none(words):
    if words[0] == "OK":
        return None
    return None
    
# 命令碼和執行器        
cmd_table = {
    "OK": exec_none,
    "ERR": exec_none,
    "clear": exec_clear,
    "info": exec_info,
    "text": exec_text,
    "fgcolor": exec_fgcolor,
    "bgcolor": exec_bgcolor,
    "hbar": exec_hbar,
    "vbar": exec_vbar,
    "putc": exec_putc,
    "hb": exec_hb,
    "exit": exec_exit
    }

def dbgWrite(st):
    #debugfile.println(st)
    pass

def parse_string(inp):
    # Echo must be processed. They will be read.
    dbgWrite(">> "+inp+"("+str(len(inp))+")")
    words = inp.split(",")
    if len(inp) < 1:
        return
    firstch = inp[0]
    if firstch == '{':
        return
    if words[0] in cmd_table:
        dbgStr = "run cmd:'"+words[0]
        dbgWrite(dbgStr)
        outmsg = cmd_table[words[0]](words)
        if outmsg != None:
            dbgWrite("<< "+outmsg)
            useIoDev.PutLine(outmsg)
    else:
        errStr = "command not found: '"+words[0]+"'"
        dbgWrite(errStr)
        #print("command not found: '"+words[0]+"'")
        useIoDev.PutLine("ERR")

if __name__=='__main__':
    print("hello, world")
