from datetime import datetime
import time
import SensorRead
from gpiozero import LED
from espeak import espeak



class Control:
    def __init__(self):
        self.min = 100
        self.max = 0
        self.targetTemp = 24
        self.delay = 10
        self.heater = LED(17)
        self.heater.off()
        self.userInputs()

        self.sensors = SensorRead.SensorRead();

    def allOff(self):
        self.heater.off();

    def read(self):
            self.sensors.readAll()
            self.min = min(self.sensors.min, self.min)
            self.max = max(self.sensors.max, self.max)
            
    def action(self):
        if self.sensors.max < self.targetTemp:
             self.heater.on()
        else: 
            self.heater.off()

    def status(self, appliance):
        if appliance.is_lit:
            return "on"
        else:
            return "off"

    def displayTemps(self):
        print(datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                + " || " + self.status(self.heater)
                + " | " + '{:.1f}'.format(self.sensors.min)
                + " | " + '{:.1f}'.format(self.sensors.mean)
                + " | " + '{:.1f}'.format(self.sensors.max)
                + " || min/max: " + '{:.1f}'.format(self.min)+ "/" + '{:.1f}'.format(self.max)
                + " || count: " + str(len(self.sensors.deviceFolders))
                + " || "
                , end = ""
            )
        
        temps = [0 for i in range(len(self.sensors.temps))]
        for i, temp in enumerate(self.sensors.temps):
            temps[i] = '{:.1f}'.format(temp)

        print(temps)

    def speakTemps(self):
        espeak.synth("Current temps: max..")
        espeak.synth('{:.1f}'.format(self.sensors.max))
        espeak.synth("Current temps: mean. ")
        espeak.synth('{:.1f}'.format(self.sensors.mean))
        espeak.synth("Current temps: min. ")
        espeak.synth('{:.1f}'.format(self.sensors.mean))
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
        
        delay = self.input("Enter delay, seconds. Default is " + str(self.delay) + ": ")
        if not delay: delay = self.delay

        self.targetTemp = int(targetTemp)
        self.delay = int(delay)

        self.output(
            "Target temperature is "
                + str(self.targetTemp)
                + " and delay is "
                + str(self.delay)
                + " seconds"
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

    def run(self):
        try:
            while True:
                self.lastReadTs = int(time.time())
                self.read()
                self.action()
                self.displayTemps()
                while(int(time.time()) - self.lastReadTs < self.delay):
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