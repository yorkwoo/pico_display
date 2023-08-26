import utime
import random

# 函式變數: 外部呼叫者必須先提供這些函式實體
# 傳回 key 是否按下
# 輸入: key 1-4 輸出 True,False
IsKeyDownF = None
# 在畫面某高度印出置中字串
# 參數 y, string, color
CenterStringF = None
# 等待任何按鍵按下
WaitAnyKeyF = None
# 設定隨機數種子
SetRandomSeedF = None
# 清空畫面
ClearScreenF = None
# 取得顏色數值
MakeRGBF = None
# 切換 LED 並等 0.1 秒
ToggleLEDF = None

# 從 min 到 max 中選擇不重複整數 items 個
def selectList(min, max, items):
    arr = list()
    outlst = list()
    n = min
    while n <= max:
        arr.append(False)
        n = n + 1
    x = 0
    #random.seed(getRndSeed())
    while x < items:
        while(True):
            n = random.randint(min, max)
            idx = n - min
            if not arr[idx]:
                arr[idx] = True
                outlst.append(n)
                break
        x = x + 1
    return outlst

def list2Str(lst):
    rstr = ""
    n = 0
    while n < len(lst):
        if n >= 1:
            rstr = rstr + ","
        rstr = rstr + str(lst[n])
        n = n + 1
    return rstr

# 大樂透
def RunDaLeTou():
    red = MakeRGBF(255, 0, 0)
    blue = MakeRGBF(0, 0, 255)
    yellow = MakeRGBF(255, 255, 0)
    SetRandomSeedF()
    ClearScreenF()
    CenterStringF(63, "Wait Calc...")
    result = selectList(1, 49, 6)
    # 製造計算效果
    n = 1
    while(n <= 6):
        ToggleLEDF()
        ToggleLEDF()
        n = n + 1
    # 顯示結果
    ClearScreenF()
    CenterStringF(36, "Results Are", blue)
    rstr = list2Str(result)
    CenterStringF(54, rstr)
    srst = sorted(result)
    rstr = list2Str(srst)
    CenterStringF(72, rstr, yellow)
    CenterStringF(90, "Press Any Key", red)
    WaitAnyKeyF()
    
# 威力彩
def RunWeLiChai():
    red = MakeRGBF(255, 0, 0)
    blue = MakeRGBF(0, 0, 255)
    yellow = MakeRGBF(255, 255, 0)
    ClearScreenF()
    SetRandomSeedF()
    CenterStringF(63, "Wait Calc...")
    rst1 = selectList(1, 38, 6)
    rst2 = selectList(1, 8, 1)
    # 製造計算效果
    n = 1
    while(n <= 7):
        ToggleLEDF()
        ToggleLEDF()
        n = n + 1
    # 顯示結果
    ClearScreenF()
    CenterStringF(36, "Results Are", blue)
    rstr2 = "("+str(rst2[0])+")"
    rstr = list2Str(rst1) + rstr2
    CenterStringF(54, rstr)
    srst = sorted(rst1)
    rstr = list2Str(srst) + rstr2
    CenterStringF(72, rstr, yellow)
    CenterStringF(90, "Press Any Key", red)
    WaitAnyKeyF()

# 畫出數位決策產生器畫面(參數 bool)
def drawBDG(dec, fin=False):
    white = MakeRGBF(255, 255, 255)
    red = MakeRGBF(255, 0, 0)
    ClearScreenF()
    gray = MakeRGBF(127, 127, 127)
    color = gray
    if not dec:
        color = white
    CenterStringF(54, "Decision 1", color)
    color = gray
    if dec:
        color = white
    CenterStringF(72, "Decision 2", color)
    if fin:
        CenterStringF(90, "Press Any Key", red)
    
# 數位決策產生器
def BinaryDecision():
    iters = 32
    SetRandomSeedF()
    val = random.getrandbits(iters)
    n = iters - 1
    turn = 0
    while n > 0:
        bit = val & 1
        val = val >> 1
        n = n - 1
        if bit > 0:
            turn = not turn
            drawBDG(turn)
            ToggleLEDF()
    drawBDG(turn, True)
    WaitAnyKeyF()

if __name__=='__main__':
    def keyDnF(n):
        return True

    def printCent(y, st, c=0):
        print("printCent("+st+")")
        
    def waitAnyK():
        print("waitAnyK()")
        
    def setRand():
        print("setRand()")
        
    def clrScreen():
        print("clrScreen()")
        
    def getRgb(r,g,b):
        v = r *65536 + g * 255 + b
        print("getRgb() ==> "+str(v))

    def toggleLed():
        utime.sleep(0.1)

    IsKeyDownF = keyDnF
    CenterStringF = printCent
    WaitAnyKeyF = waitAnyK
    SetRandomSeedF = setRand
    ClearScreenF = clrScreen
    MakeRGBF = getRgb
    ToggleLEDF = toggleLed

    print("----- DaLeTo ------")
    RunDaLeTou()
    print("----- WeLiChai ------")
    RunWeLiChai()
    print("----- BDM ------")
    BinaryDecision()
