
import time
import SensorRead
import UserIO
from gpiozero import LED
import statistics

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
        
        self.heatingStartedTs = 0
        self.lastDisplayTs = 0
        self.readDelay = 10

        self.sensors = SensorRead.SensorRead()
        self.lastMonitoredTemp = self.sensors.meanTemp
        self.rising = False
        self.wasRising = False
        self.heatingWasActive = False

        self.io = UserIO.UserIO(self.sensors)
        #self.io.userInputs()

    def allOff(self):
        self.heater.off();
        self.dcPow.off()
        self.fan.off()
      
    def action(self):
        if self.isHeatingRequired():
            self.activateHeater()
        else:
            self.heaterOff()
            #if (self.heatingWasActive != self.isHeatingRequired()):
            #    self.displayTemps('a ')

        if self.isCirculationRequired():
            self.fanOn()
        else:
            self.fanOff()
            
        self.displayAction()    

        self.heatingWasActive = self.isHeatingRequired()

    def displayAction(self):
        if (int(time.time()) - self.lastDisplayTs >= self.io.displayTempsTime):
            self.lastDisplayTs = int(time.time())
            self.displayTemps('..')

    def isHeatingRequired(self):
        return (self.sensors.maxTemp < self.io.maxTemp
                and self.sensors.fruitMedian < self.io.targetFruitTemp
                and self.sensors.spawnMedian < self.io.targetSpawnTemp)

    def isCirculationRequired(self):
        return (self.sensors.fruitMedian < self.io.targetFruitTemp
                and self.sensors.fruitMax < self.io.targetFruitTemp + 1)

    def activateHeater(self):
        if (int(time.time()) - self.heatingStartedTs >= self.io.heaterCycleTime):
            self.heatingStartedTs = int(time.time())

        if (int(time.time()) - self.heatingStartedTs < self.io.heaterOnTime):
            self.heaterOn()
        else:
            self.heaterOff()
        
    def heaterOff(self):
        if (self.heater.is_lit):
            self.heater.off()
            self.dcPowSupply()
            self.displayTemps('b ')
    
    def heaterOn(self):
        if (not self.heater.is_lit):
            self.heater.on()
            self.dcPowSupply()
            self.displayTemps('c ')

    def fanOff(self):
        if(self.dcPow.is_lit):
            self.fan.off()
            self.dcPowSupply()
            self.displayTemps('d ')
        
    def fanOn(self):
        if(not self.dcPow.is_lit):
            self.fan.on()
            self.dcPowSupply()
            self.displayTemps('e ')

    def dcPowSupply(self):
        if (self.fan.is_lit or self.light.is_lit):
            self.dcPow.on()
        else:
            self.dcPow.off()


    def delayExceeded(self, lastReadTs):
            return 

    def displayTemps(self, message = ''):
        self.lastDisplayTs = int(time.time())
        self.io.displayTemps(
                self.isHeatingRequired(),
                self.heater.is_lit,
                self.fan.is_lit,
                self.light.is_lit,
                self.dcPow.is_lit,
                message
            )

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
            while True:
                self.delayTen()
                self.read()
                self.action()
                

        except KeyboardInterrupt:
            self.allOff()
            self.io.userOptions()
        except:
            self.allOff()
            self.io.output("FAILURE!")
            self.io.soundAllarm()
            self.sensors = SensorRead.SensorRead()

        self.displayTemps('^c')
        self.run()

    def delayTen(self):
        lastReadTs = int(time.time())
        while (int(time.time()) - lastReadTs < self.readDelay
                and int(time.time()) % 10 != 0):
            time.sleep(0.1)