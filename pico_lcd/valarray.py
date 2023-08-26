import time

is_error_now = False
valArray = []
maxSize = 24

def AddValue(val):
    nowt = time.time()
    itm = (nowt, val)
    valArray.append(itm)
    if len(valArray) > maxSize:
        del(valArray[0])
        
def Length():
    return len(valArray)
    
def Get(idx):
    return valArray[idx]
    
def GetAll():
    return valArray
    
def GetArray():
    ret = []
    idx = 0
    while idx < len(valArray):
        ret.append(valArray[idx][1])
        idx += 1
    return ret
    
def GetTimes():
    ret = []
    idx = 0
    while idx < len(valArray):
        ret.append(valArray[idx][0])
        idx += 1
    return ret
    
def DumpValues():
    print(valArray)

def Save(filename):
    global valArray
    ret = True
    try:
        with open(filename, "w") as file:
            idx = 0
            while idx < len(valArray):
                vv = Get(idx)
                ln = str(vv[0])+','+str(vv[1])+'\n'
                file.write(ln)
                idx += 1
            file.close()
    except OSError as e:
        is_error_now = True
        print("Error save "+filename)
        ret = False
    return ret

def Load(filename):
    global valArray
    ret = True
    try:
        with open(filename, 'r') as file:
            valArray = []
            for ln in file.readlines():
                vals = ln.split(',')
                if len(vals) > 1:
                    tup = (int(vals[0]),float(vals[1]))
                    valArray.append(tup)
            file.close()
    except OSError as e:
        is_error_now = True
        print("Error load "+filename)
        ret = False
    return ret

# unit test
if __name__=='__main__':
    if Load('templog.csv'):
        rr = GetArray()
        print(rr)
    else:
        idx = 1
        while idx <= 10:
            n = idx * 111
            AddValue(n)
            idx += 1
        Save('templog.csv')
