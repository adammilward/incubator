from datetime import datetime
import time
import SensorRead
from gpiozero import LED
from espeak import espeak



class Control:
    def __init__(self):
        self.min = 100
        self.max = 0
        self.heater = LED(17)
        self.fan1 = LED(27)
        self.fan2 = LED(22)
        self.heater.off()
        self.fan1.off()
        self.fan2.off()

        self.targetTemp = 25
        self.maxTargetTemp = 26
        self.delay = 300
        self.heaterCycleCount = 0
        self.heaterOnCycles = 10 # denominator for heater on fraction
        self.heaterDelay = 30 # denominator for heater on fraction
        self.userInputs()


        self.sensors = SensorRead.SensorRead();

    def allOff(self):
        self.heater.off();
        self.fan1.off()
        self.fan2.off()

    def read(self):
            self.sensors.readAll()
            self.min = min(self.sensors.medianTemp, self.min)
            self.max = max(self.sensors.medianTemp, self.max)
      
    def action(self):
        if self.heatingRequired():
            self.fanOff()
            self.heaterOn()
        else: 
            self.heaterOff()
            if self.coolingRequired():
                self.fanOn()
            else: 
                self.fanOff()
                
    def heaterOn(self):
        if self.heaterCycleCount % self.heaterOnCycles == 0:
            self.heater.on()
        else:
            self.heater.off()
        self.heaterCycleCount += 1
    
    def heaterOff(self):
        self.heater.off()
        self.heaterCycleCount = 0
    
    def fanOff(self):
        self.fan1.off()
        self.fan2.off()
        
    def fanOn(self):
        self.fan1.on()
        self.fan2.on()    

    def heatingRequired(self) :
        l = len(self.sensors.sortedTemps)
        return (self.sensors.sortedTemps[l -1] < self.targetTemp + 13 
                and self.sensors.sortedTemps[l -2] < self.targetTemp + 3
                and self.sensors.medianTemp < self.targetTemp)
    
    def coolingRequired(self) :
        return self.sensors.medianTemp > self.maxTargetTemp

    def status(self, appliance):
        if appliance.is_lit:
            return "on"
        else:
            return "off"

    def displayTemps(self):
        if (self.heatingRequired()):
            tempStatus = "low"
        elif (self.coolingRequired()):
            tempStatus = "high"
        else:
            tempStatus = "ok"

        print(self.tempsColour(), end = '')
        print(
            datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " "
                + str(tempStatus) + " ||"  
                + " " + self.status(self.heater)
                + " " + self.status(self.fan1)
                + " " + self.status(self.fan2)
                + " l:" + '{:.1f}'.format(self.sensors.minTemp)
                + " med:" + '{:.1f}'.format(self.sensors.medianTemp)
                + " h:" + '{:.1f}'.format(self.sensors.maxTemp)
                + " || min/max: " + '{:.1f}'.format(self.min)+ "/" + '{:.1f}'.format(self.max)
                + " || count: " + str(len(self.sensors.deviceFolders))
                + " || "
                , end = "\033[37m"
            )

        temps = [0 for i in range(len(self.sensors.temps))]
        for i, temp in enumerate(self.sensors.temps):
            temps[i] = '{:.1f}'.format(temp)
        print(temps, end = "")

        print(" || RH: " + '{:.1f}'.format(self.sensors.humidity))

    def tempsColour(self):
        if self.coolingRequired():
            return '\033[93m'
        if self.heater.is_lit:
            return '\033[96m'
        if self.heatingRequired():
            return '\033[94m'
        return '\033[32m'


    def speakTemps(self):
        espeak.synth("Current temps: max..")
        espeak.synth('{:.1f}'.format(self.sensors.maxTemp))
        espeak.synth("Current temps: mean. ")
        espeak.synth('{:.1f}'.format(self.sensors.meanTemp))
        espeak.synth("Current temps: min. ")
        espeak.synth('{:.1f}'.format(self.sensors.meanTemp))
        self.speakProbes()
        espeak.synth("Overall max.")
        espeak.synth('{:.1f}'.format(self.max))
        espeak.synth("Overall min.")
        espeak.synth('{:.1f}'.format(self.min))
        time.sleep(1)
        espeak.synth('Relative humidity ' + str(self.sensors.humidity) + ' %')

    def speakProbes(self):
        espeak.synth("Individual probes")
        for i, temp in enumerate(self.sensors.temps):
            espeak.synth("probe " + str(i))
            espeak.synth('{:.1f}'.format(temp))

    def soundAllarm(self):
        i = 5
        while i:
            espeak.synth("Woooooop. Woooooop!")
            time.sleep(1)
            espeak.synth("Emergency")
            time.sleep(1)
            espeak.synth("Emergency!")
            time.sleep(3)
            i -= 1

    def userInputs(self):
        targetTemp = self.input("Enter target temperature. Default is " + str(self.targetTemp) + ": ")
        if not targetTemp: targetTemp = self.targetTemp
        
        maxTargetTemp = self.input("Enter max target temperature. Default is " + str(self.maxTargetTemp) + ": ")
        if not maxTargetTemp: maxTargetTemp = self.maxTargetTemp
        
        delay = self.input("Enter delay, seconds. Default is " + str(self.delay) + ": ")
        if not delay: delay = self.delay

        heaterDelay = self.input("Enter heater on time, default is " + str(self.heaterDelay) + ": ")
        if not heaterDelay: heaterDelay = self.heaterDelay

        heaterOnModulus = self.input("Heater on cycles, default is " + str(self.heaterOnCycles) + ": ")
        if not heaterOnModulus: heaterOnModulus = self.heaterOnCycles

        self.targetTemp = float(targetTemp)
        self.delay = int(delay)
        self.heaterDelay = int(heaterDelay)
        self.heaterOnCycles = int(heaterOnModulus)
        self.maxTargetTemp = max(self.targetTemp + 0.5, int(maxTargetTemp))

        self.output(
            "Target temperature is "
                + str(self.targetTemp)
                + " Max target temp is "
                + str(self.maxTargetTemp)
                + " and delay is "
                + str(self.delay)
                + " seconds. "
                + " Heater on for " + str(self.heaterDelay)
                + " seconds in " + str(self.heaterOnCycles) + " cycles."
            )
    
    def input(self, string):
        espeak.synth(string)
        return input(string)

    def output(self, string):
        espeak.synth(string)
        print(string)

    def userOptions(self):
        self.output("What do you want?")
        request = self.input("T for temperatures, S for settings").lower()
        self.matchRequest(request)

    def matchRequest(self, request):
        if request == "t":
            self.displayTemps()
            return self.speakTemps()
        elif request == "s":
            return self.userInputs()
        else:
            return self.output("Command not recognised")

    def delayExceeded(self):
        if self.heatingRequired():
            return int(time.time()) - self.lastReadTs >= self.heaterDelay
        else:    
            return int(time.time()) - self.lastReadTs >= self.delay

    def run(self):
        try:
            while True:
                self.lastReadTs = int(time.time())
                self.read()
                self.action()
                self.displayTemps()
                while(not self.delayExceeded()):
                    time.sleep(0.1)
        except KeyboardInterrupt:
            self.allOff()
            self.userOptions()
        except:
            self.allOff()
            self.output("FAILURE!")
            self.soundAllarm()
            self.sensors = SensorRead.SensorRead()

        self.run()