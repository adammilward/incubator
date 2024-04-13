
import time
import SensorRead
import UserIO
from gpiozero import LED
from datetime import datetime

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
        self.readDelay = 10

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
        self.heatAction()
        self.fanAction()
        self.lightAction()   
        self.displayAction()

        self.heaterWasOn = self.heater.is_lit
        self.fanWasOn = self.fan.is_lit
        self.lightWasOn = self.light.is_lit
        self.dcPowWasOn = self.dcPow.is_lit
        self.heatingWasRequired = self.isHeatingRequired() 

    def heatAction(self):
        if self.isHeatingRequired():
            self.activateHeater()
        else:
            self.heaterOff()

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
        elapsedSeconds = str(int(time.time()) - self.lastDisplayTs)
        if (
            self.heaterWasOn != self.heater.is_lit
            or self.fanWasOn != self.fan.is_lit
            or self.lightWasOn != self.light.is_lit
            or self.dcPowWasOn != self.dcPow.is_lit
            or self.heatingWasRequired != self.isHeatingRequired()
            ):
            self.displayTemps(elapsedSeconds)

        if (int(time.time()) - self.lastDisplayTs >= self.io.displayTempsTime):
            self.displayTemps('.' + elapsedSeconds)

    def isHeatingRequired(self):
        hysteresis = int(self.heatingWasRequired) * 0.1
        return (self.sensors.maxTemp < self.io.maxTemp + hysteresis
                #and self.sensors.fruitMedian < self.io.targetFruitTemp + histerisis
                and self.sensors.fruitMax < self.io.targetFruitTemp + 1 + hysteresis
                and self.sensors.spawnMedian < self.io.targetSpawnTemp + hysteresis
                and self.sensors.spawnMax < self.io.targetSpawnTemp + 2 + hysteresis)

    def isFanRequired(self):
        hysteresis = int(self.fanWasOn) * 0.1
        return (self.sensors.fruitMedian < self.io.targetFruitTemp + hysteresis
                and self.sensors.fruitMax < self.io.targetFruitTemp + 1 + hysteresis)

    def activateHeater(self):
        if (int(time.time()) - self.heatingStartedTs >= self.io.heaterCycleTime):
            self.heatingStartedTs = int(time.time())

        if (int(time.time()) - self.heatingStartedTs < self.io.heaterOnTime):
            self.heaterOn()
        else:
            self.heaterOff()
        
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
        self.lastDisplayTs = int(time.time())
        while len(message) < 4 :
            message = ' ' + message 
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
            self.lightOn()
            self.io.userOptions()
        except:
            self.allOff()
            self.io.output("FAILURE!")
            self.io.soundAllarm()
            self.sensors = SensorRead.SensorRead()

        self.displayTemps('^c')
        self.run()

    def delayTen(self):
        while (int(str(int(time.time()))[-1]) < 5):
            time.sleep(0.1)