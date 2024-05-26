import time
from gpiozero import LED
import subprocess

def readWriteTs(attempts = 5):
        nowTs = int(time.time())

        watchdog = open('/home/adam/python/watchdog.ts', 'w')
        watchdog.write(str(nowTs))
        watchdog.close()

        incubate = open('/home/adam/python/incubate.ts', 'r')
        incubateTs = int(incubate.read())
        print(incubateTs)

        if incubateTs < nowTs - 16: # how many seconds is allowed?
            if (attempts >= 2):
                 killAll()
            else:
                print('attempts = ', attempts)
                time.sleep(5)
                readWriteTs(2)

def killAll():
    heater = LED(17)
    dcPow = LED(27)
    fan = LED(22)
    light = LED(10)
    heater.off()
    dcPow.off()
    fan.off()
    light.off()

    print(subprocess.run(["pkill", "-f", "incubate.py"]))
    print('killed all')

def run():
     while True:
        time.sleep(10)

        try:
            readWriteTs(1)
        except Exception as e:
            print(e)
            killAll()
            run()
     

run()