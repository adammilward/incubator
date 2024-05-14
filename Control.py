
import time
import SensorRead
import UserIO
from gpiozero import LED
from datetime import datetime
import math

class Control:
    def __init__(self):
        self.heater = LED(17)
        self.dcPow = LED(27)
        self.fan = LED(22)
        self.light = LED(10)
        self.heater.off()
        self.dcPow.off()
        self.fan.off()
        self.light.off()

        self.heatingPeriodStartTs = 0
        self.heaterCycleCount = -1
        self.fanHysteresis = 0
        self.fanHysteresis = 0

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

        self.io = UserIO.UserIO(self.sensors)

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
            self.displayTemps('E')
            Exception('Heater should not be on max temp is' + str(self.sensors.maxTemp))


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

            if (self.heaterCycleCount >= 2 
                and self.sensors.spawnMedian < self.io.targetSpawnTemp - 0.1):
                self.io.heaterOnPercent += 0.5

            if heaterOnSeconds > 200:
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
        if (self.heaterCycleCount != -1):
            elapsedSeconds = int(time.time()) - self.heatingPeriodStartTs
            modifier = (elapsedSeconds) / self.io.heatingPeriod
            
            if(self.heaterCycleCount == 0):
                modifier = math.sqrt(modifier)
                modifier = modifier / 2 + 0.5
                self.io.heaterOnPercent = self.io.heaterOnPercent * modifier
            elif(self.heaterCycleCount == 1):
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
        if (self.sensors.maxTemp >= self.io.maxTemp):
            self.dontHeatReasons += ['sensors.maxTemp >= io.maxTemp ' + str(self.io.maxTemp)]
        if (self.sensors.spawnMedian >= self.io.targetSpawnTemp + hysteresis):
            self.dontHeatReasons += ['self.sensors.spawnMedian >= ' + str(self.io.targetSpawnTemp + hysteresis)]
        if (self.sensors.spawnMax >= self.io.targetSpawnTemp + self.io.spawnMaxOffset + hysteresis):
            self.dontHeatReasons += ['self.sensors.spawnMax >=' + str(self.io.targetSpawnTemp + self.io.spawnMaxOffset + hysteresis)]
        if (self.sensors.fruitMax >= self.io.targetFruitTemp + self.io.fruitMaxOffset + hysteresis):
            self.dontHeatReasons += ['self.sensors.fruitMax >= ' + str(self.io.targetFruitTemp + self.io.fruitMaxOffset + hysteresis)]
        if (self.sensors.fruitMax >= self.io.targetFruitTemp + 2):
            self.dontHeatReasons += ['self.sensors.fruitMax >= ' + str(self.io.targetFruitTemp + 2)]
        if (self.sensors.maxTemp >= self.io.targetSpawnTemp + 2):
            self.dontHeatReasons += ['self.sensors.maxTemp >= ' + str(self.io.targetSpawnTemp + 2)]

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
        if (hour >= 7 and hour < 19):
            self.lightOn()
        else:
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
            print('too hot!!! something has gone wrong')
            self.heaterOff()
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
        for i, temp in enumerate(self.sensors.detectors):
            detector = self.sensors.detectors[index]
            direction = detector.detect()

            if (direction != 0):
                elapsed = int(time.time()) - self.heatingPeriodStartTs
                if elapsed < self.io.heatingPeriod / 2:
                    elapsed += self.io.heatingPeriod
                    
                self.io.peakDetected(
                    direction,
                    index,
                    detector, 
                    elapsed
                )
            
            ++ index

    def run(self):
        try:
            self.read()
            self.displayTemps('^c')
            while True:
                if ((int(str(int(time.time()))[-1]) >= 5)):
                    self.read()
                    self.action()
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.allOff()
            self.lightOn()
            self.io.output('allOff, KeyboardInterrupt')
            self.io.userOptions()
        except Exception as e:
            self.allOff()
            self.io.output('allOff')
            self.io.output("FAILURE!")
            self.io.output(str(e))
            self.io.soundAllarm()
            self.sensors = SensorRead.SensorRead()

        self.run()
            