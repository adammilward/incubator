
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
        self.heatingPeriod = 10 * 60
        self.heaterCycleCount = -1

        self.sensors = SensorRead.SensorRead()
        self.lastMonitoredTemp = self.sensors.meanTemp
        self.rising = False
        self.wasRising = False

        self.heaterWasOn = False
        self.dcPowWasOn = False
        self.fanWasOn = False
        self.lightWasOn = False
        self.heatingWasRequired = False

        self.io = UserIO.UserIO(self.sensors)

        self.lastDisplayTs = int(time.time()) - self.io.displayTempsTime

    def allOff(self):
        self.heater.off();
        self.dcPow.off()
        self.fan.off()
      
    def action(self):
        self.fanAction()
        self.lightAction()   
        self.displayAction()

    def heatAction(self):
        if self.isHeatingRequired():
            self.activateHeater()
        else:
            self.heaterInactive()

    def activateHeater(self):
        if (int(time.time()) - self.heatingPeriodStartTs >= self.heatingPeriod):
            self.heaterCycleCount += 1
            self.heatingPeriodStartTs = int(time.time())
            heaterOnSeconds = self.io.heaterOnPercent * self.heatingPeriod / 100

            if (self.heaterCycleCount >= 2 
                and self.sensors.spawnMedian < self.io.targetSpawnTemp - 0.1):
                self.io.heaterOnPercent += 0.5

            if heaterOnSeconds > 200:
                raise Exception("heaterOnSeconds out of range: " + str(heaterOnSeconds))
 
            self.heaterOn()
            self.displayAction()
            time.sleep(heaterOnSeconds)
            self.heaterOff()
            self.displayAction()

    def heaterInactive(self):
        if (self.heaterCycleCount != -1):
            elapsedSeconds = int(time.time()) - self.heatingPeriodStartTs
            modifier = (elapsedSeconds) / self.heatingPeriod
            
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
        hysteresis = int(self.heatingWasRequired) * 0
        error = 0.1
        return (self.sensors.maxTemp < self.io.maxTemp - error + hysteresis
                and self.sensors.spawnMedian < self.io.targetSpawnTemp - error + hysteresis
                and self.sensors.spawnMax < self.io.targetSpawnTemp + 1 - error + hysteresis
                # incase somehing went wrong and he fruit is geing too hot
                and self.sensors.fruitMax < self.io.targetFruitTemp + 0.8 - error + hysteresis
                #and self.sensors.fruitMedian < self.io.targetFruitTemp - error + hysteresis
                )

    def isFanRequired(self):
        hysteresis = int(self.fanWasOn) * 0.2
        error = 0
        return (self.sensors.fruitMedian < self.io.targetFruitTemp - error + hysteresis
                and self.sensors.fruitMax < self.io.targetFruitTemp + 0.3 - error + hysteresis)

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

    def displayAction(self):
        if (
            self.heaterWasOn != self.heater.is_lit
            or self.fanWasOn != self.fan.is_lit
            or self.lightWasOn != self.light.is_lit
            or self.dcPowWasOn != self.dcPow.is_lit
            or self.heatingWasRequired != self.isHeatingRequired()
            ):
            self.displayTemps('  ')
            #if (not self.isHeatingRequired()):
                # print(self.sensors.maxTemp, self.io.maxTemp + 0.1, self.sensors.maxTemp < self.io.maxTemp + 0.1, 
                # ' ... ', self.sensors.spawnMedian, self.io.targetSpawnTemp + 0.1, self.sensors.spawnMedian < self.io.targetSpawnTemp + 0.1,
                # ' ... ', self.sensors.spawnMax, self.io.targetSpawnTemp + 1.1, self.sensors.spawnMax < self.io.targetSpawnTemp + 1.1,
                # ' ... ', self.sensors.fruitMedian, self.io.targetFruitTemp + 1.1, self.sensors.fruitMedian < self.io.targetFruitTemp + 1.1)

        if (int(time.time()) - self.lastDisplayTs >= self.io.displayTempsTime):
            self.displayTemps('..')

        self.heaterWasOn = self.heater.is_lit
        self.fanWasOn = self.fan.is_lit
        self.lightWasOn = self.light.is_lit
        self.dcPowWasOn = self.dcPow.is_lit
        self.heatingWasRequired = self.isHeatingRequired()     
        
    def heaterOff(self):
        self.heater.off()
    
    def heaterOn(self):
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
                self.isHeatingRequired(),
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
        # self.displayDirectionChange()

    def displayDirectionChange(self):
        monitoredTemp = self.sensors.temps[-1]
        changed = monitoredTemp != self.lastMonitoredTemp
        rising = monitoredTemp > self.lastMonitoredTemp

        if (changed and self.wasRising != rising):
            if rising:
                message = '+ '
            else:
                message = '- '
            
            self.displayTemps(message + str(self.lastMonitoredTemp) + ' ' + str(monitoredTemp) + ' ')
            self.wasRising = rising
            
        self.lastMonitoredTemp = monitoredTemp

    def run(self):
        try:
            self.read()
            self.displayTemps('^c')
            while True:
                if ((int(str(int(time.time()))[-1]) >= 5)):
                    self.read()
                    self.action()
                self.heatAction()
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
            