import time
from espeak import espeak
from datetime import datetime
import SensorRead

class UserIO:
    def __init__(self, sensors: SensorRead) -> None:
        self.sensors: SensorRead = sensors

        # 25/26 for spawn, 21 air temp for fruiting, 23 (max 24) for substrate

        self.targetFruitTemp = 21.5
        self.targetSpawnTemp = 25
        self.maxTemp = 27

        self.heaterOnPercent = 4
        self.displayTempsTime = 600
        self.heatingPeriod = 10 * 60

        self.spawnHysteresis = 0
        self.spawnMaxOffset = 0.8
        self.fruitHysteresis = 0.2
        self.fruitMaxOffset = 0.5

        self.lightsActive = False

        self.END      = '\33[0m'
        self.BOLD     = '\33[1m'
        self.ITALIC   = '\33[3m'
        self.URL      = '\33[4m'
        self.BLINK    = '\33[5m'
        self.BLINK2   = '\33[6m'
        self.SELECTED = '\33[7m'

        self.BLACK  = '\33[30m'
        self.RED    = '\33[31m'
        self.GREEN  = '\33[32m'
        self.YELLOW = '\33[33m'
        self.BLUE   = '\33[34m'
        self.VIOLET = '\33[35m'
        self.CYAN   = '\33[36m'
        self.WHITE  = '\33[37m'

        self.BLACKBG  = '\33[40m'
        self.REDBG    = '\33[41m'
        self.GREENBG  = '\33[42m'
        self.YELLOWBG = '\33[43m'
        self.BLUEBG   = '\33[44m'
        self.VIOLETBG = '\33[45m'
        self.BEIGEBG  = '\33[46m'
        self.WHITEBG  = '\33[47m'

        self.GREY    = '\33[90m'
        self.RED2    = '\33[91m'
        self.GREEN2  = '\33[92m'
        self.YELLOW2 = '\33[93m'
        self.BLUE2   = '\33[94m'
        self.VIOLET2 = '\33[95m'
        self.CYAN2   = '\33[96m'
        self.WHITE2  = '\33[97m'

        self.GREYBG    = '\33[100m'
        self.REDBG2    = '\33[101m'
        self.GREENBG2  = '\33[102m'
        self.YELLOWBG2 = '\33[103m'
        self.BLUEBG2   = '\33[104m'
        self.VIOLETBG2 = '\33[105m'
        self.BEIGEBG2  = '\33[106m'
        self.WHITEBG2  = '\33[107m'

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
            elapsedSeconds: str,
            heaterCycleCount: str,
            message: str = ''
        ):

        while len(message) < 4 :
            message = ' ' + message
        while len(elapsedSeconds) < 3 :
            elapsedSeconds = ' ' + elapsedSeconds 
        while len(heaterCycleCount) < 2 :
            heaterCycleCount = ' ' + heaterCycleCount 

        print(self.tempsColour(heatingRequired, heaterIsOn, fanIsOn), end = '')
        print(
                message 
                + elapsedSeconds + ' | '
                + heaterCycleCount + ' | '
                + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " "
                + str(self.tempStatus(heatingRequired, heaterIsOn, fanIsOn)) + " | "
                + str(round(self.heaterOnPercent, 1)) + '% ' 
                + str(self.heaterOnPercent * self.heatingPeriod / 100) + 's | '
                + self.applianceStatus(heaterIsOn, fanIsOn, lightIsOn, dcPowIsOn)
                + self.targets()
                , end = ""
            )
    
        temps = ['' for i in range(len(self.sensors.temps))]
        print(self.colourTemp(self.sensors.temps[0], self.targetFruitTemp, self.fruitHysteresis, self.fruitMaxOffset), end = '')
        print(self.colourTemp(self.sensors.temps[1], self.targetFruitTemp, self.fruitHysteresis, self.fruitMaxOffset), end = '')
        print(self.colourTemp(self.sensors.temps[2], self.targetFruitTemp, self.fruitHysteresis, self.fruitMaxOffset), end = '')
        print(self.colourTemp(self.sensors.temps[3], self.targetSpawnTemp, self.spawnHysteresis, self.spawnMaxOffset), end = '')
        print(self.colourTemp(self.sensors.temps[4], self.targetSpawnTemp, self.spawnHysteresis, self.spawnMaxOffset), end = '')
        print(self.colourTemp(self.sensors.temps[5], self.targetSpawnTemp, self.spawnHysteresis, self.spawnMaxOffset), end = '')
        print(end = self.END)
        
        print(" || T:", str(self.sensors.temps[6]) + ' RH: ' + '{:.1f}'.format(self.sensors.humidity), end = '')
        print(self.END)

    def targets(self,):
        a = self.colourTempTarget(self.sensors.fruitMedian, self.targetFruitTemp, self.fruitHysteresis, self.fruitMaxOffset)
        b = self.colourTempTarget(self.sensors.spawnMedian, self.targetSpawnTemp, self.spawnHysteresis, self.spawnMaxOffset)
        return f" | targets: {a} {b} | {self.END}"  

    def colourTemp(self, temp, target, hysteresis, maxOffset):
        return f"{self.targetColour(temp, target, hysteresis, maxOffset)} {temp} {self.END} "

    def colourTempTarget(self, temp, target, hysteresis, maxOffset):
        return f"{self.targetColour(temp, target, hysteresis, maxOffset)}{temp}({target}){self.END}"

    def targetColour(self, temp, target, hysteresis, maxOffset):
        if temp == target:
            return self.GREEN + self.ITALIC
        
        if temp <= target - maxOffset - 1 :
            return self.BLUEBG
        elif temp <= target - maxOffset:
            return self.BLUE2
        elif temp <= target:
            return self.CYAN2
        
        elif temp >= target + hysteresis + maxOffset + 1:
            return self.REDBG
        elif temp >= target + hysteresis+ maxOffset:
            return self.RED2
        elif temp >= target + hysteresis:
            return self.YELLOW2
        elif temp >= target:
            return self.GREEN
        
        else:
            return self.BLINK2

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
            return self.VIOLET2
        if fanIsOn:
            return self.YELLOW2
        if heaterIsOn:
            return self.RED2
        if heatingRequired:
            return self.CYAN2
        return self.GREEN

    def peakDetected(self, direction, i, detector):
        temps = []
        j = i
        while j:
            j -= 1
            print('   ', end='')

        for record in detector.history:
            temps.append(record['temp'])
        if (direction > 0):
            print (self.BLUE2 , '                    ', i, datetime.now().strftime("| %H:%M:%S"), '| falling, max was:', detector.recentMax, end=' ')
            print(temps, self.END)
        elif (direction < 0):
            print (self.RED2 ,  '                    ', i, datetime.now().strftime("| %H:%M:%S"), '| rising, min was:', detector.recentMin, end='')
            print(temps, self.END)


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
        if self.lightsActive:
            lightsDefault = 'yes'
        else:
            lightsDefault = 'no'

        lightsActive = self.input("Activate Lighting. Default is " + lightsDefault + ": ")
        if not lightsActive: lightsActive = str(int(self.lightsActive))

        targetFruitTemp = self.input("Enter fruit target temp. Default is " + str(self.targetFruitTemp) + ": ")
        if not targetFruitTemp: targetFruitTemp = self.targetFruitTemp

        targetSpawnTemp = self.input("Enter spawn target temp. Default is " + str(self.targetSpawnTemp) + ": ")
        if not targetSpawnTemp: targetSpawnTemp = self.targetSpawnTemp

        maxTemp = self.input("Enter overall max temp. Default is " + str(self.maxTemp) + ": ")
        if not maxTemp: maxTemp = self.maxTemp

        heaterOnPercent = self.input("Enter heater on percent, default is " + str(self.heaterOnPercent) + ": ")
        if not heaterOnPercent: heaterOnPercent = self.heaterOnPercent

        displayTempsTime = self.input("Display temps time, default is " + str(self.displayTempsTime) + ": ")
        if not displayTempsTime: displayTempsTime = self.displayTempsTime

        self.targetFruitTemp = float(targetFruitTemp)
        self.targetSpawnTemp = float(targetSpawnTemp)
        self.maxTemp = float(maxTemp)
        self.heaterOnPercent = float(heaterOnPercent)
        self.displayTempsTime = int(displayTempsTime)

        self.lightsActive = (lightsActive == '1' or lightsActive[0].lower() == 'y')

        self.output(
            ''
                + "Lighting active is "
                + str(self.lightsActive)
                + ", Fruit target temp is "
                + str(self.targetFruitTemp)
                + ", Spawn target temp is "
                + str(self.targetSpawnTemp)
                + ", Max temperature is "
                + str(self.maxTemp)
                + ", Heater on " + str(self.heaterOnPercent)
                + "%"
            )
    
    def input(self, string):
        print(string, end = '')
        espeak.synth(string)
        return input()

    def output(self, string):
        print(string)
        espeak.synth(string)

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

    