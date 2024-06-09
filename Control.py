
import time
import SensorRead
import UserIO
import traceback
from gpiozero import LED
from datetime import datetime
import math
import Camera

class Control:
    def __init__(self):
        self.writeIncubateTs(10)

        self.heater = LED(17)
        self.dcPow = LED(27)
        self.fan = LED(22)
        self.light = LED(10)
        self.heater.off()
        self.dcPow.off()
        self.fan.off()
        self.light.off()
        self.lightOn()

        self.heatingPeriodStartTs = 0
        self.heaterCycleCount = -1
        self.fanHysteresis = 0
        self.fanHysteresis = 0

        self.camera = Camera.Camera()
        self.lastCaptureHour = 99

        self.sunrise = 10
        self.sunset = 18

        self.sensors = SensorRead.SensorRead()
        self.lastMonitoredTemp = self.sensors.meanTemp
        self.rising = False
        self.wasRising = False

        self.heaterWasOn = False
        self.dcPowWasOn = False
        self.fanWasOn = False
        self.lightWasOn = False
        self.heatingWasRequired = False
        self.dontHeatReasons = []

        self.io = UserIO.UserIO(self.sensors, self.camera)

        self.lastDisplayTs = int(time.time()) - self.io.displayTempsTime

    def allOff(self):
        self.heater.off();
        self.dcPow.off()
        self.fan.off()
      
    def action(self):
        self.heatAction()
        self.fanAction()
        self.lightAction()
        self.displayAction('a')
        if (self.heater.is_lit 
            and self.sensors.maxTemp > self.io.targetSpawnTemp + self.io.spawnMaxOffset + 1):
            self.displayTemps('Err')
            raise Exception('Heater should not be on max temp is' + str(self.sensors.maxTemp))

    def heatAction(self):
        if self.isHeatingRequired():
            self.activateHeater()
        else:
            self.heaterInactive()

    def activateHeater(self):
        heaterOnSeconds = self.io.heaterOnPercent * self.io.heatingPeriod / 100
        now = int(time.time())

        if (now - self.heatingPeriodStartTs >= self.io.heatingPeriod):
            self.heaterCycleCount += 1
            self.heatingPeriodStartTs = int(time.time())

            if (self.heaterCycleCount >= 5
                and self.sensors.spawnMedian < self.io.targetSpawnTemp - 0.1):
                self.io.heaterOnPercent *= 1.1

            if heaterOnSeconds > 200 or self.io.heaterOnPercent > 100:
                raise Exception("heaterOnSeconds out of range: " + str(heaterOnSeconds))
 
        heatingTimeLeft = self.heatingPeriodStartTs + heaterOnSeconds - now

        if (heatingTimeLeft > 0 ):
            #print(heatingTimeLeft)
            self.heaterOn()
            if heatingTimeLeft < 15:
                #print('sleep', heatingTimeLeft)
                time.sleep(heatingTimeLeft)
                self.displayAction('c')
                self.heaterOff()
        else :
            self.heaterOff()

    def heaterInactive(self):
        self.heaterOff()

        if (self.heaterCycleCount != -1):
            elapsedSeconds = int(time.time()) - self.heatingPeriodStartTs
            modifier = (elapsedSeconds) / self.io.heatingPeriod
            
            if(self.heaterCycleCount <= 2):
                modifier = math.sqrt(modifier)
                modifier = modifier / 2 + 0.5
                self.io.heaterOnPercent = self.io.heaterOnPercent * modifier
            elif(self.heaterCycleCount <= 5):
                modifier = math.sqrt(math.sqrt(modifier))
                modifier = modifier / 2 + 0.5
                self.io.heaterOnPercent = self.io.heaterOnPercent * modifier
            else:
                modifier = math.sqrt(modifier)
                modifier = modifier / 2 + 0.5
                self.io.heaterOnPercent = self.io.heaterOnPercent * modifier

            self.heaterCycleCount = -1


    def isHeatingRequired(self):
        self.dontHeatReasons = []
        hysteresis = int(self.heatingWasRequired) * self.io.spawnHysteresis

        val = self.io.maxTemp + hysteresis
        if (self.sensors.maxTemp >= val):
            self.dontHeatReasons += ['sensors.maxTemp >= ' + str(val)]

        val = self.io.targetSpawnTemp + hysteresis
        if (self.sensors.spawnMedian >= val):
            self.dontHeatReasons += ['self.sensors.spawnMedian >= ' + str(val)]

        val = self.io.targetSpawnTemp + self.io.spawnMaxOffset + hysteresis
        if (self.sensors.spawnMax >= val):
            self.dontHeatReasons += ['self.sensors.spawnMax >=' + str(val)]

        val = self.io.targetFruitTemp + self.io.fruitMaxOffset + 0.3 + hysteresis
        if (self.sensors.fruitMax >= val):
            self.dontHeatReasons += ['self.sensors.fruitMax >= ' + str(val)]

        # idiot checks
        val = self.io.targetFruitTemp + 1 + hysteresis
        if (self.sensors.fruitMax >= val):
            self.dontHeatReasons += ['self.sensors.fruitMax >= ' + str(val)]

        val = self.io.idiotCheckTemp - 1
        if (self.sensors.medianTemp >= val):
            self.dontHeatReasons += ['self.sensors.medianTemp >= ' + str(val)]

        return len(self.dontHeatReasons) == 0

    def isFanRequired(self):
        hysteresis = int(self.fanWasOn) * self.io.fruitHysteresis
        return (self.sensors.fruitMedian < self.io.targetFruitTemp + hysteresis
                and self.sensors.fruitMax < self.io.targetFruitTemp + self.io.fruitMaxOffset + hysteresis)

    def fanAction(self):
        if self.isFanRequired():
            self.fanOn()
        else:
            self.fanOff()

    def lightAction(self):
        if (not self.io.lightsActive):
            self.lightOff()
            return
        
        hour = int(datetime.now().strftime("%H"))

    
        if (hour >= self.sunrise and hour < self.sunset):
            self.lightOn()
            lightsOn = True
        else:
            self.lightOff()
            lightsOn = False    

        if (hour != self.lastCaptureHour):
            self.capture(lightsOn)

    def capture(self, lightsOn = False):
        hour = int(datetime.now().strftime("%H"))
        self.lightOn()
        self.lastCaptureHour = hour
        self.camera.capture(str(hour))

        if (not lightsOn):
            self.lightOff()

    def displayAction(self, message = ''):
        if (
            self.heaterWasOn != self.heater.is_lit
            or self.fanWasOn != self.fan.is_lit
            or self.lightWasOn != self.light.is_lit
            or self.dcPowWasOn != self.dcPow.is_lit
            or self.heatingWasRequired != self.isHeatingRequired()
            ):
            self.displayTemps(message + '  ')
            #if (not self.isHeatingRequired()):
                # print(self.sensors.maxTemp, self.io.maxTemp + 0.1, self.sensors.maxTemp < self.io.maxTemp + 0.1, 
                # ' ... ', self.sensors.spawnMedian, self.io.targetSpawnTemp + 0.1, self.sensors.spawnMedian < self.io.targetSpawnTemp + 0.1,
                # ' ... ', self.sensors.spawnMax, self.io.targetSpawnTemp + 1.1, self.sensors.spawnMax < self.io.targetSpawnTemp + 1.1,
                # ' ... ', self.sensors.fruitMedian, self.io.targetFruitTemp + 1.1, self.sensors.fruitMedian < self.io.targetFruitTemp + 1.1)

        if (int(time.time()) - self.lastDisplayTs >= self.io.displayTempsTime):
            self.displayTemps(message + '..')

        self.heaterWasOn = self.heater.is_lit
        self.fanWasOn = self.fan.is_lit
        self.lightWasOn = self.light.is_lit
        self.dcPowWasOn = self.dcPow.is_lit
        self.heatingWasRequired = self.isHeatingRequired()     
        
    def heaterOff(self):
        self.heater.off()
    
    def heaterOn(self):
        if self.sensors.maxTemp >= self.io.targetSpawnTemp + self.io.spawnMaxOffset + 1:
            self.heaterOff()
            print('too hot!!! something has gone wrong max:', self.sensors.maxTemp)
            self.displayTemps('too hot')
        else:
            self.heater.on()

    def fanOff(self):
        self.fan.off()
        self.dcPowSupply()
        
    def fanOn(self):
        self.fan.on()
        self.dcPowSupply()

    def lightOff(self):
        self.light.off()
        self.dcPowSupply()
        
    def lightOn(self):
        self.light.on()
        self.dcPowSupply()

    def dcPowSupply(self):
        if (self.fan.is_lit or self.light.is_lit):
            self.dcPow.on()
        else:
            self.dcPow.off()

    def displayTemps(self, message = ''):
        self.io.displayTemps(
                self.dontHeatReasons,
                self.heater.is_lit,
                self.fan.is_lit,
                self.light.is_lit,
                self.dcPow.is_lit,
                str(int(time.time()) - self.lastDisplayTs),
                str(self.heaterCycleCount),
                message
            )
        self.lastDisplayTs = int(time.time())

    def read(self):
        self.sensors.readAll()
        self.detectPeaks()
    
    def detectPeaks(self):
        index = 3
        while index < len(self.sensors.detectors):
            detector = self.sensors.detectors[index]
            direction = detector.detect()

            if (direction < 0):
                elapsed = int(time.time()) - self.heatingPeriodStartTs
                if elapsed < self.io.heatingPeriod / 2:
                    elapsed += self.io.heatingPeriod

                self.io.peakDetected(
                    direction,
                    index,
                    detector, 
                    elapsed
                )
            
            index += 1

    def watchDog(self):
        nowTs = int(time.time())

        self.writeIncubateTs(0)
        
        watchdog = open('/home/adam/python/watchdog.ts', 'r')
        watchdogTs = int(watchdog.read())
        watchdog.close()

        if watchdogTs < nowTs - 20: # how many seconds is allowed?
            raise Exception('Watchdog timed out')
        
    def writeIncubateTs(self, delay = 0):
        incubate = open('/home/adam/python/incubate.ts', 'w')
        incubate.write(str(int(time.time()) + delay))
        incubate.close()


    def run(self):
        while True:
            try:
                self.watchDog()
                self.read()
                self.action()
                self.displayAction('start')
                while True:
                    if ((int(str(int(time.time()))[-1]) >= 5)):
                        self.watchDog()
                        self.read()
                        self.action()
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                self.allOff()
                self.writeIncubateTs(600)
                self.lightOn()
                self.io.output('allOff, KeyboardInterrupt')
                self.io.userOptions()
                self.lastCaptureHour = 100

            except Exception as e:
                self.allOff()
                self.writeIncubateTs(30)
                self.io.output('allOff')
                self.io.output("FAILURE!")
                self.io.output(str(e))
                traceback.print_exc()
                self.io.soundAllarm()
            