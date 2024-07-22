import time
from datetime import datetime
from gpiozero import LED
import subprocess
import traceback

heater = LED(17)
dcPow = LED(27)
fan = LED(22)
light = LED(10)
maxDelay = 0
doOutputting = True

def readWriteTs(attempts = 5):
        nowTs = int(time.time())

        watchdog = open('/home/adam/python/watchdog.ts', 'w')
        watchdog.write(str(nowTs))
        watchdog.close()

        incubate = open('/home/adam/python/incubate.ts', 'r')
        incubateTs = int(incubate.read())
        incubate.close()
        
        incubateDt = datetime.fromtimestamp(incubateTs).strftime('%H:%M:%S')
        nowDt = datetime.fromtimestamp(nowTs).strftime('Y/%m/%d %H:%M:%S')
        
        delay = incubateTs - nowTs
        global maxDelay
        maxDelay = min(delay, maxDelay)

        global doOutputting

        f = '-'
        h = '-'
        l = '-'
        d= '-'
        if fan.is_lit:
            f = 'f'
        if heater.is_lit:
            h = 'h'
        if light.is_lit:
            l = 'l'
        if dcPow.is_lit:
            d = 'd'

        onns = h + f + l + d

        if delay < -21: # how many seconds is allowed?
            if (attempts >= 5):
                 output(incubateDt, onns, nowDt, delay, maxDelay, attempts)
                 killAll()
                 doOutputting = False
            else:
                output(incubateDt, onns, nowDt, delay, maxDelay, attempts)
                time.sleep(5)
                readWriteTs(attempts + 1)
        else:
            attempts = 0
            doOutputting = True
            #output(incubateDt, onns, nowDt, delay, maxDelay)

def killAll():
    heater.off()
    dcPow.off()
    fan.off()
    light.off()
    
    output(subprocess.run(["pkill", "-f", "incubate.py"]), datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

def output(*args, end = '\n'):
    global doOutputting
    if doOutputting:
        print(*args, end = end);

def run():
     attempts = 0
     while True:
        time.sleep(10)

        try:
            readWriteTs(0)
            attempts = 0
        except Exception as e:
            print(Exception, attempts, datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
            print(e)
            traceback.print_exc()
            time.sleep(5)
            if attempts >= 6:
                killAll()

            attempts = attempts + 1
     

run()