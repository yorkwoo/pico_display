# 本模組定義繪圖函式界面
# 大體和 LCDProc Driver 有直接關係

# This to be a informal interface
class DrawInterface:
    # 清畫面
    def clear(self):
        print("clear")
    
    def info(self):
        sw = 0  #self.lcd.width()
        sh = 0  #self.lcd.height()
        fw = 0  #font.WIDTH
        fh = 0  #font.HEIGHT
        #self.cols = int((sw+fw-1) / fw)
        #self.rows = int((sh+fh-1) / fh)
        kv1 = "\"scrw\":"+str(sw)
        kv2 = "\"scrh\":"+str(sh)
        kv3 = "\"fntw\":"+str(fw)
        kv4 = "\"fnth\":"+str(fh)
        kv5 = "\"rows\":"+str(0)
        kv6 = "\"cols\":"+str(0)
        retstr = "{"+kv1+","+kv2+","+kv3+","+kv4+","+kv5+","+kv6+"}"
        return retstr
    
    # 強制輸出    
    def flush(self):
        print("flush")
        
    # 印字串
    def print(self, x, y, s):
        print("print("+str(x)+","+str(y)+": "+s)
        
    # 印字元
    def printc(self, x, y, c):
        print("printc("+str(x)+","+str(y)+": "+c)

    # 傳回按下按鈕代碼
    def button(self):
        ret = 0
        #print("button -->"+str(ret))
        return ret
        
    def hbar(self, x, y, spc, milli, options):
        print("hbar("+str(x)+","+str(y)+" l:"+str(spc)+" m:"+str(milli))

    def vbar(self, x, y, spc, milli, options):
        print("vbar("+str(x)+","+str(y)+" l:"+str(spc)+" m:"+str(milli))

    def heartbeat(self, mod):
        print("heartbeat("+str(mod)+")")
        
    def drawicon(self, x, y, iconname):
        print("drawicon("+str(x)+","+str(y)+": "+iconname)

    def drawcursor(self, x, y, t):
        print("drawcursor("+str(x)+","+str(y)+": "+t)

    def get_brightness(self, st):
        print("get_brightness("+str(st)+")")
        return 0
        
    def set_brightness(self, st, milli):
        print("set_brightness("+str(st)+","+milli+")")

    # return system color value from RGB
    def colorValue(self, r8 ,g8 ,b8):
        return 0xFFFF
    
    # draw empty rectangle
    def rect(self, px, py, pw, ph, c):
        pass

    # draw solid block
    def block(self, px, py, pw, ph, c):
        pass
