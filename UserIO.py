import time
from espeak import espeak
from datetime import datetime
import SensorRead

class UserIO:
    def __init__(self, sensors: SensorRead) -> None:
        self.sensors: SensorRead = sensors

        # 25/26 for spawn, 21 air temp for fruiting, 23 (max 24) for substrate

        self.targetFruitTemp = 22
        self.targetSpawnTemp = 25
        self.maxTemp = 29

        self.heaterOnTime = 60
        self.heaterCycleTime = 10 * 60

        self.displayTempsTime = 60

        self.RED = '\033[91m'
        self.GREEN = '\033[92m'
        self.DARKGREEN = '\033[32m'
        self.YELLOW = '\033[93m'
        self.BLUE = '\033[94m'
        self.PURPLE = '\033[95m'
        self.CYAN = '\033[96m'
        self.DARKCYAN = '\033[36m'

        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'
        self.END = '\033[0m'

    def status(self, appliance):
            if appliance:
                return "on"
            else:
                return "off"

    def displayTemps(
            self,
            heatingRequired,
            heaterIsOn,
            fanIsOn,
            lightIsOn,
            dcPowIsOn,
            message = ''
        ):

        print(self.tempsColour(heatingRequired, heaterIsOn, fanIsOn), end = '')
        print(
            message
                + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " "
                + str(self.tempStatus(heatingRequired, heaterIsOn, fanIsOn)) + " | "  
                + self.applianceStatus(heaterIsOn, fanIsOn, lightIsOn, dcPowIsOn) + " | "  
                + " l:" + '{:.1f}'.format(self.sensors.minTemp)
                + " med:" + '{:.1f}'.format(self.sensors.medianTemp)
                + " mean:" + '{:.2f}'.format(self.sensors.meanTemp)
                + " h:" + '{:.1f}'.format(self.sensors.maxTemp)
                + " | targets: "
                + '{:.1f}'.format(self.sensors.fruitMedian) + '(' + str(self.targetFruitTemp) + ') ' 
                + '{:.1f}'.format(self.sensors.spawnMedian) + '(' + str(self.targetSpawnTemp) + ') '
                + '{:.1f}'.format(self.sensors.maxTemp) + '(' + str(self.maxTemp) + ') '
                + "|| "
                , end = "\033[37m"
            )

        temps = [0 for i in range(len(self.sensors.temps))]
        for i, temp in enumerate(self.sensors.temps):
            temps[i] = '{:.1f}'.format(temp)
        print(temps, end = "")

        print(" || RH: " + '{:.1f}'.format(self.sensors.humidity))

    def tempStatus(self, heatingRequired, heaterIsOn, fanIsOn):
        temp = 'ok'
        if heatingRequired:
            temp = 'lo'

        return temp
    
    def applianceStatus(self, heaterIsOn, fanIsOn, lightIsOn, dcPowIsOn):
        fan = ' '
        heat = ' '
        light = ' '
        dcPow = ' '
        if fanIsOn:
            fan = 'f'
        if heaterIsOn:
            heat = 'h'
        if lightIsOn:
            light = 'l'
        if dcPowIsOn:
            dcPow = 'd'

        return heat + fan + light + dcPow

    def tempsColour(self, heatingRequired, heaterIsOn, fanIsOn):
        if fanIsOn and heaterIsOn:
            return self.PURPLE
        if fanIsOn:
            return self.YELLOW
        if heaterIsOn:
            return self.RED
        if heatingRequired:
            return self.CYAN
        return self.DARKGREEN


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
        targetFruitTemp = self.input("Enter max temperature. Default is " + str(self.targetFruitTemp) + ": ")
        if not targetFruitTemp: targetFruitTemp = self.targetFruitTemp

        targetSpawnTemp = self.input("Enter max temperature. Default is " + str(self.targetSpawnTemp) + ": ")
        if not targetSpawnTemp: targetSpawnTemp = self.targetSpawnTemp

        maxTemp = self.input("Enter max temperature. Default is " + str(self.maxTemp) + ": ")
        if not maxTemp: maxTemp = self.maxTemp

        heaterOnTime = self.input("Enter heater on time, default is " + str(self.heaterOnTime) + ": ")
        if not heaterOnTime: heaterOnTime = self.heaterOnTime

        heaterCycleTime = self.input("Heater cycle time, default is " + str(self.heaterCycleTime) + ": ")
        if not heaterCycleTime: heaterCycleTime = self.heaterCycleTime

        displayTempsTime = self.input("Heater cycle time, default is " + str(self.displayTempsTime) + ": ")
        if not displayTempsTime: displayTempsTime = self.displayTempsTime

        self.targetFruitTemp = float(targetFruitTemp)
        self.targetSpawnTemp = float(targetSpawnTemp)
        self.maxTemp = float(maxTemp)
        self.heaterOnTime = int(heaterOnTime)
        self.heaterCycleTime = int(heaterCycleTime)
        self.displayTempsTime = int(displayTempsTime)

        self.output(
            ''
                + " Fruit target temp is "
                + str(self.targetFruitTemp)
                + " Spawn target temp is "
                + str(self.targetSpawnTemp)
                + " Max temperature is "
                + str(self.maxTemp)
                + " Heater on for " + str(self.heaterOnTime)
                + " seconds in " + str(self.heaterCycleTime) + " seconds."
            )
    
    def input(self, string):
        #espeak.synth(string)
        return input(string)

    def output(self, string):
        #espeak.synth(string)
        print(string)

    def userOptions(self):
        self.output("What do you want?")
        request = self.input("T for temperatures, S for settings, C for calibrate").lower()
        return self.matchRequest(request)

    def matchRequest(self, request):
        if request == "t":
            self.displayTemps(self, False, False, False, False, 'user request')
            #self.speakTemps()
            return
        elif request == "s":
            return self.userInputs()
        elif request == "c":
            return self.calibrate()
        else:
            return self.output("Command not recognised")

    def calibrate(self):
            self.sensors.calibrate()

    