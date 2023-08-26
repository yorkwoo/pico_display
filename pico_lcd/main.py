# RPi Pico Microshare LCD 1.14" application
# 多功能程式應用
# 平時：溫度顯示
# 功能鈕: 數位決策產生器，大樂透，威力彩
from machine import ADC,Pin,RTC,Timer,I2C
import utime
import random
import tft_config
import vga1_8x16 as font
import vga2_16x32 as fontbig
from usbserio import *
from uarttextio import *
from lcd7789 import *
import bignum as BigNum
import games
import commands as cmdParser
import ds3231_port
import valarray as vArr
import onewire, ds18x20

led = Pin(25, Pin.OUT)  # 這個使用標準 pico 所以可以閃光
DS18B20_PIN = 18
ds18b20 = None
ds18id = None
devTemp = "RP2"

# using DS18B20
def tempInit():
    global ds18b20
    global ds18id
    global DS18B20_PIN
    global devTemp
    
    pin = machine.Pin(DS18B20_PIN)
    ds18b20 = ds18x20.DS18X20(onewire.OneWire(pin))
    ds_roms = ds18b20.scan()
    if len(ds_roms) >= 1:
        ds18id = ds_roms[0]
        devTemp = "DS18"

def nowTemp():
    global ds18id
    global ds18b20
    if ds18id:
        ds18b20.convert_temp()
        utime.sleep_ms(750)
        return ds18b20.read_temp(ds18id)
    else:
        rp2_temp = ADC(4)
        cf = 3.3 / (65536)
        reading = rp2_temp.read_u16() * cf
        temp = 27 - (reading - 0.706)/0.001721
        return temp

now_temp = 0

# 先前功能完成以後，防止按鈕立刻生效的處理
nokey_count = 0
# Is there input recently? so reduce sleep
recent_in = 0
# in submenu
submenu = False
BACKLIGHT_PIN = 13

logfile = 'templog.csv'

# color code
WHITE = 0xFFFF
BLACK = 0x0000
bklit = 200
input_key = 0
bgColor = BLACK
reverseFlag = False
dimSeconds = 0

# 輸入按鈕
key0 = Pin(15,Pin.IN)
key1 = Pin(17,Pin.IN)
key2 = Pin(2 ,Pin.IN)
key3 = Pin(3 ,Pin.IN)

def read_jumper():
    sw1 = Pin(14 ,Pin.IN, Pin.PULL_UP)
    sw2 = Pin(16 ,Pin.IN, Pin.PULL_UP)
    s1 = sw1.value()
    s2 = sw2.value()
    return s1*2+s2

def lumin():
    # using A0
    luminPin = ADC(Pin(26, Pin.IN, None))
    luminv = luminPin.read_u16()
    return luminv;

#print("Init...")
utime.sleep(0.1)

# 檢查 RTC 初始是不是有正確值
rtc = RTC()
rtc_isInit = False
rt = rtc.datetime()
print("RTC:"+str(rt))
if rt[0] == 2021 and rt[1] == 1 and rt[2] == 1:
    rtc_isInit = False
else:
    rtc_isInit = True
    
# 綜合按鍵中斷處理
def button_handler(pin):
    global input_key
    global reverseFlag
    if pin == key0:
        input_key = 1
    elif pin == key1:
        input_key = 2
    elif pin == key2:
        input_key = 3
    elif pin == key3:
        input_key = 4
    if reverseFlag:
        if input_key > 0:
            input_key = 5 - input_key

key0.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)
key1.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)
key2.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)
key3.irq(trigger=machine.Pin.IRQ_RISING, handler=button_handler)

exitProg = False

mode = read_jumper()
if mode == 3:
    cmdio = UsbSerialIo()
    serialDev = "USB"
elif mode == 2:
    cmdio = UartTextIo(0, 115200, Pin(1), Pin(0))
    serialDev = "Uart0"
else:
    cmdio = UartTextIo(1, 115200, Pin(5), Pin(4))
    serialDev = "Uart1"

tempInit()

painter = LCD_st7789(BACKLIGHT_PIN)
cmdParser.Init(ioDev=cmdio, drawDev=painter)
lcd = painter.lcd
_RED = painter.colorValue(255,0,0)
_BLUE = painter.colorValue(0,0,255)
_YELLOW = painter.colorValue(255,255,0)
_GREEN = painter.colorValue(0,255,0)
_GRAY = painter.colorValue(128, 128, 128)

def lcdPrintCenter(y, strn, c=WHITE, bigfnt=False):
    yy = int(y)
    if bigfnt:
        x = int((lcd.width() - fontbig.WIDTH * len(strn))/2)
        lcd.text(fontbig,strn,x,yy,c)
    else:
        x = int((lcd.width() - font.WIDTH * len(strn))/2)
        lcd.text(font,strn,x,yy,c)

def centerLcdGame(y, st, c=WHITE):
    if c == None:
        lcdPrintCenter(y, st)
    else:
        lcdPrintCenter(y, st, c)
        
def clearScreen():
    setBackColor(BLACK)
    
def makeRGB(r,g,b):
    return painter.colorValue(r, g, b)

def test_lcd():
    global lcd
    global _RED
    global _BLUE
    global _GREEN
    _WHITE = painter.colorValue(255,255,255)
    
    test_str1 = "Hello Pico!"
    test_str2 = "[;',./{}+]1234567890!@#$%^&*()"
    xx = int((lcd.width() - 8*len(test_str1))/2)
    xx2 = int((lcd.width() - 8*len(test_str2))/2)
    #lcd.backlight(1000)
    lcd.fill(_RED)
    lcdPrintCenter(10, test_str1)
    lcdPrintCenter(109, test_str2)
    utime.sleep(0.4)
    
    lcd.fill(_GREEN)
    lcdPrintCenter(20, test_str1, _GREEN)
    lcdPrintCenter(99, test_str2, _GREEN)
    utime.sleep(0.4)
    
    lcd.fill(_BLUE)
    lcdPrintCenter(30, test_str1)
    lcdPrintCenter(89, test_str2)
    utime.sleep(0.4)  

test_lcd()
    
def setBackColor(c):
    global bgColor
    lcd.fill(c)
    bgColor = c
    
def writeText(str, x, y, c=BLACK):
    global bgColor
    lcd.text(font, str ,x, y, c, bgColor)
    
# 僅在最底部顯示訊息
def bottomMsg(str, c):
    global bgColor
    yy = lcd.height()-font.HEIGHT
    lcd.block(0, yy, font.WIDTH, font.HEIGHT, bgColor)
    lcd.text(font, str, 0, yy, c, bgColor)

rtcDs3231 = False
def caliTime_Rtc():
    global rtc_isInit
    global rtcDs3231
    i2c = I2C(1, sda=Pin(6, pull=Pin.PULL_UP), scl=Pin(7, pull=Pin.PULL_UP), freq=400000)
    if(ds3231_port.DetectDs3231(i2c)):
        if not rtcDs3231:
            rtcDs3231 = ds3231_port.DS3231(i2c)
        if not rtc_isInit:
            dsT = rtcDs3231.get_time()
            print("Read time from RTC:"+str(dsT))
            rtcDs3231.get_time(True)
            rtc_isInit = True
        else:
            print("Set RTC time")
            rtcDs3231.save_time()
    else:
        #print("DS3231 not exist!")
        pass
        
def save_rtc():
    global rtcDs3231
    if rtcDs3231:
        #print("Set RTC time")
        rtcDs3231.save_time()
        return True
    else:
        #print("no RTC")
        return False
    
# 主機端給定時間
def setTime(timeStr):
    # timeStr 規格； YYYYMMDDhhmmss, 是 UTC
    global rtc_isInit
    global isDs3231
    if len(timeStr) == 14:
        try:
            yrs = int(timeStr[0:4])
            mnt = int(timeStr[4:6])
            dat = int(timeStr[6:8])
            hr = int(timeStr[8:10])
            mn = int(timeStr[10:12])
            ss = int(timeStr[12:14])
            if yrs >= 2020 and mnt > 0 and mnt <= 12:
                if dat > 0 and dat <= 31 and hr < 60:
                    if mn < 60 and ss < 60:
                        timetup = (yrs, mnt, dat, 0, hr, mn, ss, 0)
                        rtc.datetime(timetup)
                        rtc_isInit = True
                        if save_rtc():
                            return "OK"
                        else:
                            bottomMsg("RTC set error")
                            utime.sleep(3)
                            
        except ValueError:
            pass
    return "ERR"

caliTime_Rtc()

# 正常模式下進入點，會看是否有 helo 進來，沒來就沒事，來了就進入等待命令狀態
# 並停止正常系統運作
def read_server(inp):
    global exitProg
    #if len(inp) > 0:
        #print("rcvd: "+inp)
    # 這邊要用空格間隔喔!
    words = inp.split()
    if len(words) > 0:
        if words[0] == "helo":
            #print("enter controlled mode")
            cmdio.PutLine("OK")
            cmdParser.isEnd = False
            while not cmdParser.isEnd:
                buffLine = cmdio.GetLine()      # get a line if it is available?
                if len(buffLine)>0:             # if there is...
                    #print("rcvd: "+buffLine)
                    #debugfile.println("rcvd: "+buffLine)
                    cmdParser.parse_string(buffLine)
                else:
                    utime.sleep(0.01)
            drawMainMenu(True)
        elif words[0] == "settime":
            rtn = setTime(words[1])
            cmdio.PutLine(rtn)
        elif words[0] == "stop":
            exitProg = True
    
def setRandomSeed():
    baseVal = sensor_temp.read_u16()
    remi = baseVal % 1000
    random.seed(int(remi))
    
def toggleLed():
    led.toggle()
    utime.sleep(0.1)
    
def anyKey():
    ret = False
    if key0.value() == 0:
        ret = True
    elif key1.value() == 0:
        ret = True
    elif key2.value() == 0:
        ret = True
    elif key3.value() == 0:
        ret = True
    return ret

# 等按下任何按鈕
def waitAnyKey():
    n = 0
    while(True):
        if(anyKey()):
            break
        n = n + 1
        if n >= 5:
            led.toggle()
            n = 0
        utime.sleep(0.1)

def init_games():
    games.CenterStringF = centerLcdGame
    games.WaitAnyKeyF = waitAnyKey
    games.SetRandomSeedF = setRandomSeed
    games.ClearScreenF = clearScreen
    games.MakeRGBF = makeRGB
    games.ToggleLEDF = toggleLed

# 畫面反轉    
def doReverse():
    global reverseFlag
    newRev = not reverseFlag
    if newRev:
        lcd.rotation(3)
    else:
        lcd.rotation(1)
    reverseFlag = newRev
    
# 計算分成 N 部份時，指定部份的 X 座標傳回 int
# columns: 分幾部份，ncol 為第幾部份(0開始), font為使用字型物件，pstr為欲印出字串
def calcTextX(columns, font, pstr, ncol=0):
    partw = lcd.width() / columns
    strw = font.WIDTH * len(pstr)
    ofst = partw * ncol
    posx = (partw - strw)/2
    return int(posx+ofst)

def showInfo():
    global serialDev
    global rtcDs3231
    clearScreen()
    devstr = "Dev: "+serialDev+" "+devTemp
    lcdPrintCenter(0, devstr, _GRAY, True)
    lcdPrintCenter(100, "Press a key", _GRAY, True)
    
    rtcstr = "Has"
    rtccolor = _GRAY
    if not rtcDs3231:
        rtcstr = "No"
        rtccolor = _RED
    rtcs = rtcstr+" DS3231"
    lcdPrintCenter(64, rtcs, rtccolor, True)
    isKey = False
    count = 0
    while not isKey:
        count = count + 1
        if count == 1 or count == 6:
            nowlum = lumin()
            luminf = 1 - (nowlum/65536)
            luminStr = "Lumin:"+str(nowlum)
            lumrgb = 64 + int(luminf*192)
            lumcolor = painter.colorValue(lumrgb, lumrgb, lumrgb)
            lcdPrintCenter(32, luminStr, lumcolor, True)
        elif count > 10:
            count = 0
        rem = count % 10
        if rem == 0:
            led.high()
        elif rem == 5:
            led.low()
        isKey = anyKey()
        utime.sleep(0.2)

# RTC time record
timeTuple = None

def drawBigTemp():
    showno = round(now_temp*10)/10
    fmtstr = "{cc:.1f}^C"
    tmpstr = fmtstr.format(cc=showno)
    color = painter.colorValue(0, 128, 0)
    if showno <= 15:
        color = painter.colorValue(0, 0, 192)
    elif showno >= 30:
        color = painter.colorValue(255, 96, 96)
    BigNum.BigNum_Temp(showno, color)    
    
def timeColor(hour):
    if hour < 5:
        return painter.colorValue(96,96,96)
    elif hour < 8:
        return painter.colorValue(224, 126, 52)
    elif hour < 17:
        return painter.colorValue(52, 221, 224)
    elif hour < 19:
        return painter.colorValue(224, 126, 52)
    elif hour < 23:
        return painter.colorValue(2, 209, 92)
    else:
        return painter.colorValue(96,96,96)

lastDayColor = BLACK    
def drawTime(setDate):
    global lastDayColor
    
    timet = rtc.datetime()
    # 依照幾點決定時鐘顏色
    txtcolor = timeColor(timet[4])
    if lastDayColor != txtcolor:
        lastDayColor = txtcolor
        setDate = True
    BigNum.BigNum_Time(timet[4], timet[5], timet[6], txtcolor)

# show temp
def measureTemp():
    global now_temp
    now_temp = nowTemp()
    setBackColor(BLACK)
    lcdPrintCenter(0, "Temperature", _GREEN)
    drawBigTemp()
    utime.sleep(5)

def measureLumin():
    # using A0
    luminPin = ADC(Pin(26))
    luminv = luminPin.read_u16()
    luminf = 1 - (luminv / 65536)
    setBackColor(BLACK)
    lcdPrintCenter(0, "Luminous", _GREEN)
    txtcolor = painter.colorValue(128, 128, 128)
    BigNum.BigNum_Percent(luminf, txtcolor)
    utime.sleep(5)

def drawMainMenu(whole):
    global now_temp
    global lcd
    
    if whole:
        setBackColor(BLACK)
        if submenu:
            writeText("<DaLeTo", 0, 0, _GREEN)
            writeText("BinDecide>", lcd.width() - font.WIDTH*10, 0, _YELLOW)
            writeText("<WeLiChai", 0, lcd.height()-font.HEIGHT, _BLUE)
            writeText("Back>", lcd.width() - font.WIDTH*5, lcd.height()-font.HEIGHT, _RED)
        else:
            writeText("<Function", 0, 0, _GREEN)
            writeText("Temp>", lcd.width() - font.WIDTH*10, 0, _YELLOW)
            writeText("<Info", 0, lcd.height()-font.HEIGHT, _BLUE)
            writeText("Reverse>", lcd.width() - font.WIDTH*8, lcd.height()-font.HEIGHT, _RED)
    
    #debug    
    #writeText(str(dimSeconds), 14*8, 0, _RED)
    if rtc_isInit:
        drawTime(False)
    else:
        drawBigTemp()

nowDimFlg = None
def setDim(isDim):
    global nowDimFlg
    if isDim != nowDimFlg:
        if isDim:
            painter.set_brightness(0,50)
        else:
            painter.set_brightness(0,200)
        nowDimFlg = isDim
    
def inputMain():
    global nokey_count
    global input_key
    global recent_in
    global dimSeconds
    global submenu
    
    if nokey_count > 0:
        input_key = 0
        return
        
    nowInput = input_key
    input_key = -1
    if nowInput > 0:
        #print("in key="+str(nowInput)+" submenu:"+str(submenu))
        if nowInput == 1:
            if submenu:
                games.RunDaLeTou()
            else:
                submenu = True
                
        elif nowInput == 2:
            if submenu:
                games.RunWeLiChai()
            else:
                showInfo()
                #measureLumin()
                
        elif nowInput == 3:
            if submenu:
                games.BinaryDecision()
            else:
                measureTemp()
                
        elif nowInput == 4:
            if submenu:
                submenu = False
            else:
                doReverse()
            
        if nowDimFlg:
            dimSeconds = 0
            setDim(False)
                
        recent_in = 30
        nokey_count = 2
        drawMainMenu(True)

oneSecFlag = False
def timerIntr(tmrId):
    global oneSecFlag
    global dimSeconds
    global nokey_count
    global recent_in
    
    oneSecFlag = True
    if dimSeconds < 30:
        dimSeconds += 1
    if nokey_count > 0:
        nokey_count -= 1
    if recent_in > 0:
        recent_in -= 1

init_games()
lcd.rotation(1)
BigNum.BigNum_SetLcd(painter)
tmr = Timer(-1)
tmr.init(period=1000, mode=Timer.PERIODIC, callback=timerIntr)

setDim(False)
count = 0
tempCnt = 0
#lastDate = -1
lastHour = -1
nowDimC = dimSeconds
now_temp = nowTemp()
drawMainMenu(True)
submode = submenu
vArr.Load(logfile)
while True:
    redraw = False
    recordTmp = False
    chkTemp = False
    if oneSecFlag:
        timeTuple = rtc.datetime()
        #upDay = timeTuple[2] != lastDate
        recordTmp = lastHour >= 0 and timeTuple[4] != lastHour
        # switch mode
        if not rtc_isInit:
            # 沒有時間可以顯示就顯示溫度
            if tempCnt == 0:
                chkTemp = True
            tempCnt += 1
            if tempCnt >= 10:
                tempCnt = 0
        else:
            redraw = True
                
        if chkTemp:
            now_temp = nowTemp()
            redraw = True
            
        led.toggle()
        oneSecFlag = False
        lastHour = timeTuple[4]

    if recordTmp:
        vArr.AddValue(nowTemp())
        vArr.Save(logfile)
        #vArr.DumpValues()
        
    if submenu != submode:
        redraw = True
        submode = submenu
        
    if redraw:
        drawMainMenu(False)
        
    if nowDimC != dimSeconds:
        if(dimSeconds == 30):
            setDim(True)
        nowDimC = dimSeconds

    inputMain()
    
    buffLine = cmdio.GetLine()      # get a line if it is available?
    if len(buffLine) > 0:                    # if there is...
        setDim(False)
        dimSeconds = 0
        read_server(buffLine)
        if exitProg:
            break
        recent_in = 0
    else:
        slpt = 0.5
        if recent_in > 0:
            slpt = 0.1
        utime.sleep(slpt)
