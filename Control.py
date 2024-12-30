
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

        self.periodStartTs = 0
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
        self.periodStartTs = 0
        self.periodElapsedSeconds = 0
        self.previousPeriodElapsedSeconds = 0
        self.heaterWasPropperActive = True

        self.io = UserIO.UserIO(self.sensors, self.camera)

        self.lastDisplayTs = int(time.time()) - self.io.displayTempsTime

    def __del__(self):
        print ("Control destroyed");
        #del(self.camera)

    def allOff(self):
        self.heater.off();
        self.dcPow.off()
        self.fan.off()
        print('allOff')
      
    def action(self):
        now = int(time.time())
        if (self.heatingWasRequired != self.isHeatingRequired()
            or self.periodStartTs == 0):
            self.periodStartTs = now
        self.periodElapsedSeconds = now - self.periodStartTs
        
        self.heatAction()
        self.fanAction()
        self.lightAction()
        self.displayAction('a')
        
        self.fanWasOn = self.fan.is_lit
        self.lightWasOn = self.light.is_lit
        self.dcPowWasOn = self.dcPow.is_lit
        self.heatingWasRequired = self.isHeatingRequired()
        self.heaterWasOn = self.heater.is_lit
        self.previousPeriodElapsedSeconds = self.periodElapsedSeconds
        
        if (self.heater.is_lit 
            and self.sensors.medianTemp > self.io.idiotCheckMedTemp):
            self.displayTemps('Err')
            raise Exception('Heater should not be on median temp is' + str(self.sensors.medianTemp))

    def heatAction(self):
        if self.isHeatingRequired():
            self.activateHeater()
        else:
            self.heaterInactive()

    def activateHeater(self):
        if (self.heatingWasRequired != self.isHeatingRequired()
            and self.heaterWasPropperActive):
            if (self.previousPeriodElapsedSeconds >= 2400):
                self.io.heaterOnPercent *= 0.5
            elif (self.previousPeriodElapsedSeconds >= 1200):
                self.io.heaterOnPercent *= 0.6
            elif (self.previousPeriodElapsedSeconds >= 600):
                self.io.heaterOnPercent *= 0.7
            elif (self.previousPeriodElapsedSeconds >= 300):
                self.io.heaterOnPercent *= 0.8
            elif (self.previousPeriodElapsedSeconds >= 120):
                self.io.heaterOnPercent *= 0.9
            else:
                self.io.heaterOnPercent *= 1
        
        heaterOnSeconds = self.io.heaterOnPercent * self.io.heatingPeriod / 100

        if (self.periodElapsedSeconds >= 600
            and self.sensors.spawnMedian < self.io.targetSpawnTemp - 0.3):
            self.io.heaterOnPercent *= 1 + (0.0003 * self.io.heatingPeriod)

        if heaterOnSeconds > 4 or self.io.heaterOnPercent > 20:
            self.io.heaterOnPercent = 20
            heaterOnSeconds = self.io.heaterOnPercent * self.io.heatingPeriod / 100
            self.io.output("heaterOnPercent exceeded 20%. Resetting to 20%")

        if (heaterOnSeconds > 4):
            raise Exception('heaterOSeconds isgreter than 4')
        
        self.heaterOn()
        time.sleep(heaterOnSeconds)
        self.heaterOff()
        
        self.heaterWasProppeActive = False

    def heaterInactive(self):
        if self.heatingWasRequired != self.isHeatingRequired():
            if (self.previousPeriodElapsedSeconds >= 60):
                self.heaterWasPropperActive = True
        self.heaterOff()


    def isHeatingRequired(self):
        self.dontHeatReasons = []
        hysteresis = int(self.heatingWasRequired) * self.io.spawnHysteresis

        val = self.io.maxTemp + hysteresis
        if (self.sensors.maxTemp >= val):
            self.dontHeatReasons += ['maxTemp >= ' + str(val)]

        val = self.io.targetSpawnTemp + hysteresis
        if (self.sensors.spawnMedian >= val):
            self.dontHeatReasons += ['spawnMedian >= ' + str(val)]

        val = self.io.targetSpawnTemp + self.io.spawnMaxOffset + hysteresis
        if (self.sensors.spawnMax >= val):
            self.dontHeatReasons += ['spawnMax >=' + str(val)]

        if self.io.isFruiting:
            val = self.io.targetFruitTemp + self.io.fruitMaxOffset + hysteresis
            if (self.sensors.fruitMax >= val):
                self.dontHeatReasons += ['fruitMax >= ' + str(val)]

        return len(self.dontHeatReasons) == 0

    def isFanRequired(self):
        hysteresis = int(self.fanWasOn) * self.io.fruitHysteresis
        return (self.sensors.fruitMedian < self.io.targetFruitTemp + hysteresis
                and self.sensors.fruitMax < self.io.targetFruitTemp + self.io.fruitMaxOffset + hysteresis
                and self.sensors.spawnMedian > self.io.targetFruitTemp + hysteresis * 2)

    def fanAction(self):
        if self.isFanRequired() and self.io.fanActive:
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

    def heaterOff(self):
        self.heater.off()
    
    def heaterOn(self):
        if self.sensors.medianTemp >= self.io.idiotCheckMedTemp:
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
                self.isHeatingRequired(),
                self.fan.is_lit,
                self.light.is_lit,
                self.dcPow.is_lit,
                str(int(time.time()) - self.lastDisplayTs),
                str(self.periodElapsedSeconds),
                message
            )
        self.lastDisplayTs = int(time.time())

    def read(self):
        try:
            self.sensors.readAll()
        except SensorRead.SensorReadException as e:
            raise e
        except Exception as e:
            self.io.output("Exception cought reading sensors. rasing SensorReadExceptioon")
            self.io.output(str(e))
            traceback.print_exc()
            raise SensorRead.SensorReadException('Caught exception reading sensors')
            
        self.detectPeaks()
    
    def detectPeaks(self):
        indexs = [0,3,4,5,6]
        for index in indexs:
            detector = self.sensors.detectors[index]
            direction = detector.detect()

            if (direction < 0):
                elapsed = self.periodElapsedSeconds
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
                while True:
                    if ((int(str(int(time.time()))[-1]) >= 5)):
                        self.watchDog()
                        self.read()
                        self.action()
                    time.sleep(0.1)

            except SensorRead.SensorReadException as e:
                self.allOff()
                self.io.output("Sensor Read Exception")
                self.io.output(str(e))
                #traceback.print_exc()

            except KeyboardInterrupt:
                self.allOff()
                self.writeIncubateTs(30)
                self.lightOn()
                self.io.output('KeyboardInterrupt')
                self.io.userOptions()
                self.lastCaptureHour = 100

            except Exception as e:
                self.allOff()
                self.writeIncubateTs(30)
                self.io.output("FAILURE! All things turned off.")
                self.io.output(str(e))
                traceback.print_exc()
                self.io.soundAllarm()
                time.sleep(20)
                raise e
            
            self.displayTemps('restart')
            
