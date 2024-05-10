import time
from gpiozero import LED

def readWriteTs():
        nowTs = int(time.time())

        incubate = open('incubate.ts', 'r')
        incubateTs = int(incubate.read())

        if incubateTs < nowTs - 20: # how many seconds is allowed?
            killAll()

        watchdog = open('watchdog.ts', 'w')
        watchdog.write(int(time.time()))
        watchdog.close()

def killAll():
    heater = LED(17)
    dcPow = LED(27)
    fan = LED(22)
    light = LED(10)
    heater.off()
    dcPow.off()
    fan.off()
    light.off()

while True:
    try:
        readWriteTs()
    except Exception as e:
         killAll()
    time.sleep(10)