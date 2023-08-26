# 本模組定義繪圖函式界面
# 大體和 LCDProc Driver 有直接關係
# drawfunc_7789 使用 st7789_mpy 當驅動
from machine import Pin, PWM
import st7789
import tft_config
import vga2_8x16 as font
import math
from baseDraw import *
from utime import sleep

class LCD_st7789(DrawInterface):
    def __init__(self, bklPin = -1):
        self.lcd = tft_config.config(0)
        self.lcd.init()
        self.lcd.rotation(3)
        self.bgcolor = st7789.BLACK
        self.fgcolor = st7789.WHITE
        self.info()
        # 初始亮度還是 Max 比較好，要測試...
        self.brightness = 1000
        self.pwm = None
        if bklPin > 0:
            self.pwm = PWM(Pin(bklPin))
            self.pwm.freq(4096)
            bval=int (self.brightness * 65536/1000)
            self.pwm.duty_u16(bval)
            
    def get_st7789():
        return self.lcd

    # 傳回JSON字串，內含系統資訊
    def info(self):
        sw = self.lcd.width()
        sh = self.lcd.height()
        fw = font.WIDTH
        fh = font.HEIGHT
        self.cols = int((sw+fw-1) / fw)
        self.rows = int((sh+fh-1) / fh)
        kv1 = "\"scrw\":"+str(sw)
        kv2 = "\"scrh\":"+str(sh)
        kv3 = "\"fntw\":"+str(fw)
        kv4 = "\"fnth\":"+str(fh)
        kv5 = "\"rows\":"+str(self.rows)
        kv6 = "\"cols\":"+str(self.cols)
        retstr = "{"+kv1+","+kv2+","+kv3+","+kv4+","+kv5+","+kv6+"}"
        return retstr

    # 清畫面
    def clear(self):
        #print("clear")
        self.lcd.fill(self.bgcolor)
    
    # 強制輸出    
    def flush(self):
        #print("flush")
        pass
    
    # 印字串 (x, y 假設是行列)
    def print(self, col, row, s):
        #print("print("+str(col)+","+str(row)+": "+s)
        x = font.WIDTH * col
        y = font.HEIGHT * row
        if y > self.lcd.height():
            return
        if x > self.lcd.width():
            return
        maxlen = self.cols - col
        #print("maxlen="+str(maxlen))
        if maxlen <= 0:
            return
        if maxlen < len(s):
            s = s[0:maxlen]
        self.lcd.text(font, s, x, y, self.fgcolor, self.bgcolor)
    
    # 印字元
    def printc(self, col, row, c):
        #print("printc("+str(col)+","+str(row)+": "+c)
        x = font.WIDTH * col
        y = font.HEIGHT * row
        if y > self.lcd.height():
            return
        if x > self.lcd.width():
            return
        self.lcd.text(font, str(c), x, y, self.fgcolor, self.bgcolor)

    # 傳回按下按鈕代碼
    def button(self):
        ret = 0
        #print("button -->"+str(ret))
        return ret
    
    # draw empty rectangle
    def rect(self, px, py, pw, ph, c):
        self.lcd.rect(px, py, pw, ph, c)

    # draw solid block
    def block(self, px, py, pw, ph, c):
        self.lcd.fill_rect(px, py, pw, ph, c)

        
    # 內部有處理寬高的 draw rect
    def __drawrect(self, x, y, w, h, fill):
        scrw = self.lcd.width()
        scrh = self.lcd.height()
        cc = self.fgcolor
        if x >= scrw:
            return
        if y >= scrh:
            return
        if x+w > scrw:
            w = scrw - x + 1
        if y+h > scrh:
            h = scrh - y + 1
        if fill:
            self.block(x, y, w, h, cc)
        else:
            self.rect(x, y, w, h, cc)
    
    def hbar(self, col, row, spc, milli, options):
        #print("hbar("+str(col)+","+str(row)+" l:"+str(spc)+" m:"+str(milli))
        x = font.WIDTH * col
        y = font.HEIGHT * row
        hh = font.HEIGHT
        ww = int(spc * font.WIDTH * milli / 1000)
        self.__drawrect(x, y, ww, hh, True)
        # 畫出空白部份
        remw = spc * font.WIDTH - ww
        self.__drawrect(x+ww-1, y, remw, hh, False)

    def vbar(self, col, row, spc, milli, options):
        #print("vbar("+str(col)+","+str(row)+" l:"+str(spc)+" m:"+str(milli))
        x = font.WIDTH * col
        y = font.HEIGHT * row
        ww = font.WIDTH
        hh = int(spc * font.HEIGHT * milli / 1000)
        self.__drawrect(x, y, ww, hh, True)
        # 畫出空白部份 注意 rect/fill_rect 似乎沒有自動縮減範圍
        remh = spc * font.HEIGHT - hh
        self.__drawrect(x, y+hh-1, ww, remh, False)

    def heartbeat(self, mod):
        #print("heartbeat("+str(mod)+")")
        if mod == 0:
            ch = chr(3)
        else:
            ch = chr(7)
        x = self.lcd.width() - font.WIDTH
        self.lcd.text(font, str(ch), x, 0, self.fgcolor, self.bgcolor)
    
    def drawicon(self, x, y, iconname):
        # icon name: refer to https://github.com/lcdproc/lcdproc/blob/master/server/widget.c
        #print("drawicon("+str(x)+","+str(y)+": "+iconname)
        pass

    def drawcursor(self, x, y, t):
        # on/off/under/block
        #print("drawcursor("+str(x)+","+str(y)+": "+t)
        pass

    def get_brightness(self, st):
        #print("get_brightness("+str(st)+")")
        if self.pwm:
            return self.brightness
        else:
            return 1000
    
    def set_brightness(self, st, milli):
        #print("set_brightness("+str(st)+","+milli+")")
        if self.pwm:
            if milli > 1000:
                milli = 1000
            self.brightness = milli
            data=int (milli*65536/1000)       
            self.pwm.duty_u16(data)
            
    # return system color value from RGB
    def colorValue(self, r8 ,g8 ,b8):
        return st7789.color565(r8,g8,b8)

    def set_bgcolor(self, r8, g8, b8):
        c = self.colorValue(r8,g8,b8)
        self.bgcolor = c
        
    def set_fgcolor(self, r8 ,g8 ,b8):
        c = self.colorValue(r8,g8,b8)
        self.fgcolor = c
        

# Unit Test                        
if __name__=='__main__':
    lcd = LCD_st7789()
    print(lcd.info())
    lcd.set_fgcolor(128, 255, 0)
    lcd.print(0,1,"Welcome to st7789 drawfunc library!")
    lcd.set_bgcolor(128, 128, 128)
    lcd.set_fgcolor(0,0,0)
    lcd.print(2,0,"Reversd text is also allowed!")
    lcd.set_fgcolor(128, 128, 128)
    lcd.set_brightness(0,1000)
    lcd.set_bgcolor(0,0,0)
    lcd.hbar(1,2,10, 125, 0)
    lcd.vbar(18,1,5, 768, 0)
    c = 1
    while c < 16:
        lcd.printc(c,3,chr(c))
        c = c+1
    while True:
        lcd.heartbeat(c)
        sleep(1)
        if c > 0:
            c = 0
        else:
            c = 1

        
