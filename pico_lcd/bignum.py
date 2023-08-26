from machine import ADC
from lcd7789 import *
import random

arr_rows = 15
arr_cols = 30
bmparr = [[0 for i in range(arr_cols)] for j in range(arr_rows)]
# range of rows to draw
ShowRows = (3,12)

# type: DrawInterface
_painter = None

BLK_WIDTH=8
BLK_HEIGHT=9
FNT7X9=\
b'\x78\x84\x84\x84\x84\x84\x84\x84\x78'\
b'\x10\x30\x10\x10\x10\x10\x10\x10\x38'\
b'\x78\x84\x04\x04\x08\x10\x20\x40\xfc'\
b'\x78\x04\x04\x04\x38\x04\x04\x04\x78'\
b'\x08\x18\x28\x48\x88\xfc\x08\x08\x1c'\
b'\xfc\x80\x80\x80\x78\x04\x04\x84\x78'\
b'\x78\x84\x80\x80\xf8\x84\x84\x84\x78'\
b'\xfc\x84\x08\x08\x10\x10\x20\x20\x20'\
b'\x78\x84\x84\x84\x78\x84\x84\x84\x78'\
b'\x78\x84\x84\x84\x7c\x04\x04\x84\x78'\
b'\x40\xa0\x4c\x12\x20\x20\x20\x12\x0c'\
b'\x00\xe2\xa4\xe8\x10\x2e\x4a\x8e\x00'\

fntdata = memoryview(FNT7X9)

def BigNum_SetLcd(lcd):
    global _painter
    _painter = lcd

def __bnDrawPixel(val, x, y, c):
    global _painter
    px = x * BLK_WIDTH
    py = y * BLK_HEIGHT
    if val > 0:
        _painter.block(px, py, BLK_WIDTH, BLK_HEIGHT-1, c)
    else:
        _painter.block(px, py, BLK_WIDTH, BLK_HEIGHT-1, 0)
        
def __bnDrawDigit(x, y, dgt):
    begin = 9 * dgt
    byte = 0
    msktable = (0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02)
    while byte < 9:
        fb = fntdata[begin]
        begin += 1
        pxl = 0
        while pxl < 7:
            nn = fb & msktable[pxl]
            if nn > 0:
                bmparr[y+byte][x+pxl] = 1
            else:
                bmparr[y+byte][x+pxl] = 0
            pxl += 1
        byte += 1
        
def __bnDisplay(clr):
    for y in range(ShowRows[0], ShowRows[1]):
        for x in range(arr_cols):
            #print("x="+str(x)+" y="+str(y)+" :="+str(bmparr[y][x]))
            __bnDrawPixel(bmparr[y][x], x, y, clr)

def __clrMid():
    for i in range(arr_rows):
        bmparr[i][14] = 0

def fatTemp(tmp):
    tenth = int(tmp * 10)
    dgt100 = tenth // 100
    rem1 = tenth - 100 * dgt100
    dgt10 = rem1 // 10
    rem2 = rem1 - 10 * dgt10
    __clrMid()
    __bnDrawDigit(0, 3, dgt100)
    __bnDrawDigit(7, 3, dgt10)
    bmparr[11][14] = 1
    __bnDrawDigit(16, 3, rem2)
    __bnDrawDigit(23, 3, 10)

def fatTime(hour, mint, sec):
    hr0 = hour//10
    hr1 = hour - 10*hr0
    mn0 = mint//10
    mn1 = mint - 10*mn0
    __clrMid()
    __bnDrawDigit(0, 3, hr0)
    __bnDrawDigit(7, 3, hr1)
    if sec % 2 > 0:
        bmparr[5][14] = 1
        bmparr[9][14] = 1
    __bnDrawDigit(16, 3, mn0)
    __bnDrawDigit(23, 3, mn1)
    
def fatPercent(val01):
    # val01: 0~1
    time1k = int(val01 * 1000)
    v0 = time1k//100
    over = False
    if v0 >= 10:
        over = True
        v0 = 1
        v1 = 0
        v2 = 0
    else:
        time1k-=(100*v0)
        v1 = time1k//10
        v2 = time1k%10
    __clrMid()
    __bnDrawDigit(0, 3, v0)
    __bnDrawDigit(7, 3, v1)
    if not over:
        bmparr[11][14] = 1
    __bnDrawDigit(16, 3, v2)
    __bnDrawDigit(23, 3, 11)
    
def BigNum_Time(hour, minu, sec, color):
    fatTime(hour, minu, sec)
    __bnDisplay(color)

def BigNum_Temp(temp, color):
    fatTemp(temp)
    __bnDisplay(color)
    
def BigNum_Percent(val, color):
    fatPercent(val)
    __bnDisplay(color)

if __name__=='__main__':
    sensor_temp = ADC(4)
    conversion_factor = 3.3 / (65536)
    BigNum_SetLcd(LCD_st7789(13))
    
    def nowTemp():
        reading = sensor_temp.read_u16() * conversion_factor
        temp = 27 - (reading - 0.706)/0.001721
        return temp
        
    fatTime(12,34,51)
    _painter.clear()
    __bnDisplay(0xffff)
    sleep(3)

    while True:
        #t = nowTemp()
        #fatTemp(t)
        v = random.random()
        fatPercent(v)
        
        clr = _painter.colorValue(128, 0, 0)
        #if t < 15:
        #    clr = _painter.colorValue(32, 32, 64)
        #elif t < 28:
        clr = _painter.colorValue(0, 64, 0)
        _painter.clear()
        __bnDisplay(clr)
        sleep(10)


