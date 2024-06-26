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
doPrint = True

def readWriteTs(attempts = 5):
        nowTs = int(time.time())

        watchdog = open('/home/adam/python/watchdog.ts', 'w')
        watchdog.write(str(nowTs))
        watchdog.close()

        incubate = open('/home/adam/python/incubate.ts', 'r')
        incubateTs = int(incubate.read())
        incubate.close()
        
        incubateDt = datetime.fromtimestamp(incubateTs).strftime('%H:%M:%S')
        nowDt = datetime.fromtimestamp(nowTs).strftime('%H:%M:%S')
        
        delay = incubateTs - nowTs
        global maxDelay
        maxDelay = min(delay, maxDelay)

        global doPrint

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
            if (attempts >= 3):
                if doPrint: output(incubateDt, onns, nowDt, delay, maxDelay, attempts)
                killAll()
                doPrint = False
            else:
                if doPrint: output(incubateDt, onns, nowDt, delay, maxDelay, attempts)
                time.sleep(5)
                readWriteTs(attempts + 1)
        else:
            attempts = 0
            doPrint = True
            #output(incubateDt, onns, nowDt, delay, maxDelay)

def killAll():
    heater.off()
    dcPow.off()
    fan.off()
    light.off()
    global doPrint
    
    if doPrint:
        output(subprocess.run(["pkill", "-f", "incubate.py"]), datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    else:
        subprocess.run(["pkill", "-f", "incubate.py"]), datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        #output(subprocess.Popen(["python3", "/home/adam/python/incubate.py", '&']))

def output(*messages):
    output = '';
    for message in messages:
        output += str(message) + ' '
    print(output)
    sout = open('/home/adam/python/watchdogOut.txt', 'a')
    sout.write(output)
    sout.close()


def run():
     output(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "---- START --\n")
     while True:
        time.sleep(10)

        try:
            readWriteTs(0)
        except Exception as e:
            output(e)
            killAll()
            traceback.print_exc()
            run()
     

run()