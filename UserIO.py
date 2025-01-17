import time
from espeak import espeak
from datetime import datetime
import SensorRead
import Camera

class UserIO:
    def __init__(self, sensors: SensorRead, camera: Camera) -> None:
        self.sensors: SensorRead = sensors
        self.camera: Camera = camera

        # 25/26 for spawn, 21 air temp for fruiting, 23 (max 24) for substrate

        self.targetFruitTemp = 25 #21
        self.targetSpawnTemp = 25 #25
        self.maxTemp = 26 #26
        self.heaterTemp = 39 #39
        self.idiotCheckMedTemp = 26 #28

        self.heaterOnPercent = 4 #2
        self.displayTempsTime = 3600 #3600

        self.spawnHysteresis = 0
        self.spawnMaxOffset = 0.5
        self.fruitHysteresis = 0
        self.fruitMaxOffset = 0.5

        self.lightsActive = False
        self.isFruiting = True
        self.fanActive = False

        self.heatingPeriod = 10 #10 do not change

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
            dontHeatReasons,
            heaterIsOn,
            fanIsOn,
            lightIsOn,
            dcPowIsOn,
            elapsedSeconds: str,
            heaterCycleCount: str,
            message: str = ''
        ):
        isHeatingRequired = len(dontHeatReasons) == 0

        if (not isHeatingRequired) and heaterIsOn:
            print(dontHeatReasons, heaterIsOn, fanIsOn, lightIsOn, dcPowIsOn, elapsedSeconds, heaterCycleCount, message)
            raise Exception('Heater should not be on!!! 1')
        
        if self.sensors.medianTemp > self.idiotCheckMedTemp:
            print(dontHeatReasons, heaterIsOn, fanIsOn, lightIsOn, dcPowIsOn, elapsedSeconds, heaterCycleCount, message)
            raise Exception('Heat has exceeded ' + str(self.idiotCheckMedTemp) + 'C!!!')

        while len(message) < 4 :
            message = ' ' + message
        while len(elapsedSeconds) < 3 :
            elapsedSeconds = ' ' + elapsedSeconds 
        while len(heaterCycleCount) < 2 :
            heaterCycleCount = ' ' + heaterCycleCount 

        print(self.tempsColour(isHeatingRequired, heaterIsOn, fanIsOn), end = '')
        print(
                message 
                + elapsedSeconds + ' | '
                + heaterCycleCount + ' | '
                + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " "
                + str(self.tempStatus(isHeatingRequired, heaterIsOn, fanIsOn)) + " | "
                + '{:.2f}'.format(self.heaterOnPercent, 1) + '% ' 
                + '{:.2f}'.format(self.heaterOnPercent * self.heatingPeriod / 100) + 's |'
                + self.applianceStatus(heaterIsOn, fanIsOn, lightIsOn, dcPowIsOn)
                + self.targets()
                , end = ""
            )
    
        temps = ['' for i in range(len(self.sensors.temps))]
        print(self.colourTemp(self.sensors.temps[1], self.targetFruitTemp, self.fruitHysteresis, self.fruitMaxOffset), end = '')
        print(self.colourTemp(self.sensors.temps[2], self.targetSpawnTemp, self.spawnHysteresis, self.spawnMaxOffset), end = '')
        print(self.colourTemp(self.sensors.temps[3], self.targetSpawnTemp, self.spawnHysteresis, self.spawnMaxOffset), end = '')
        print(self.colourTemp(self.sensors.temps[4], self.targetSpawnTemp, self.spawnHysteresis, self.spawnMaxOffset), end = '')
        print(self.colourTemp(self.sensors.temps[5], self.targetSpawnTemp, self.spawnHysteresis, self.spawnMaxOffset), end = '')
        print(end = self.END)
        
        print(" || H:" + '{:.1f}'.format(self.sensors.temps[0]) +
              " T:" + '{:.1f}'.format(self.sensors.temps[6]) + 
              ' RH:' + '{:.0f}'.format(self.sensors.humidity), end = ' ')
        print(dontHeatReasons, end='')
        print(self.END)

    def targets(self,):
        a = self.colourTempTarget(self.sensors.fruitMedian, self.targetFruitTemp, self.fruitHysteresis, self.fruitMaxOffset)
        b = self.colourTempTarget(self.sensors.spawnMedian, self.targetSpawnTemp, self.spawnHysteresis, self.spawnMaxOffset)
        return f"| targets: {a} {b} | {self.END}"  

    def colourTemp(self, temp, target, hysteresis, maxOffset):
        return f"{self.targetColour(temp, target, hysteresis, maxOffset)}{temp:.1f} {self.END} "

    def colourTempTarget(self, temp, target, hysteresis, maxOffset):
        return f"{self.targetColour(temp, target, hysteresis, maxOffset)}{temp:.1f}({target}) {self.END}"

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

    def peakDetected(self, direction, i, detector, elapsed):

        temps = []
        j = i
        while j:
            j -= 1
            print('   ', end='')

        print ('                    ', end='')
        for record in detector.history:
            temps.append(record['temp'])
        if (direction < 0):
            print (self.RED2, i, datetime.now().strftime("| %H:%M:%S"), '| ', elapsed, '| falling, max was:', detector.recentMax, end=' ')
            print(temps, self.END)
        elif (direction > 0):
            print (self.BLUE2, i, datetime.now().strftime("| %H:%M:%S"), '| ', elapsed, '| rising, min was:', detector.recentMin, end='')
            print(temps, self.END)


    def speakTemps(self):
        espeak.synth("Current temps: max..")

        espeak.synth('{:.1f}'.format(self.sensors.maxTemp))
        espeak.synth("Current temps: mean. ")
        espeak.synth('{:.1f}'.format(self.sensors.medianTemp))
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
        i = 2
        while i:
            espeak.synth("Woooooop. Woooooop!")
            time.sleep(1)
            espeak.synth("Emergency")
            time.sleep(1)
            espeak.synth("Emergency!")
            time.sleep(3)
            i = i - 1

    def userInputs(self):
        if self.lightsActive:
            lightsDefault = 'yes'
        else:
            lightsDefault = 'no'

        if self.fanActive:
            fanDefault = 'yes'
        else:
            fanDefault = 'no'

        heaterOnPercent = self.input("Enter heater on percent, default is " + str(self.heaterOnPercent) + ": ")
        if not heaterOnPercent: heaterOnPercent = self.heaterOnPercent

        lightsActive = self.input("Activate Lighting. Default is " + lightsDefault + ": ")
        if not lightsActive: lightsActive = str(int(self.lightsActive))

        fanActive = self.input("Activate fan. Default is " + fanDefault + ": ")
        if not fanActive: fanActive = str(int(self.fanActive))

        targetFruitTemp = self.input("Enter fruit target temp. Default is " + str(self.targetFruitTemp) + ": ")
        if not targetFruitTemp: targetFruitTemp = self.targetFruitTemp

        targetSpawnTemp = self.input("Enter spawn target temp. Default is " + str(self.targetSpawnTemp) + ": ")
        if not targetSpawnTemp: targetSpawnTemp = self.targetSpawnTemp

        maxTemp = self.input("Enter max temp. Default is " + str(self.maxTemp) + ": ")
        if not maxTemp: maxTemp = self.maxTemp

        heaterTemp = self.input("Enter max heater temp. Default is " + str(self.heaterTemp) + ": ")
        if not heaterTemp: heaterTemp = self.heaterTemp

        displayTempsTime = self.input("Display temps time, default is " + str(self.displayTempsTime) + ": ")
        if not displayTempsTime: displayTempsTime = self.displayTempsTime

        self.targetFruitTemp = float(targetFruitTemp)
        self.targetSpawnTemp = float(targetSpawnTemp)
        self.maxTemp = float(maxTemp)
        self.heaterTemp = float(heaterTemp)
        self.heaterOnPercent = float(heaterOnPercent)
        self.displayTempsTime = int(displayTempsTime)

        self.lightsActive = (lightsActive == '1' or lightsActive[0].lower() == 'y')
        self.fanActive = (fanActive == '1' or fanActive[0].lower() == 'y')

        print(
            ''
                + "Lighting active is "
                + str(self.lightsActive)
                + "; Fan active is "
                + str(self.fanActive)
                + "; Fruit target temp is "
                + str(self.targetFruitTemp)
                + "; Spawn target temp is "
                + str(self.targetSpawnTemp)
                + "; Max temperature is "
                + str(self.maxTemp)
                + "; Heater on " + str(self.heaterOnPercent)
                + "%"
            )
    
    def input(self, string):
        print(string, end = '')
        #espeak.synth(string)
        return input()

    def output(self, string):
        print(string)
        espeak.synth(string)

    def userOptions(self):
        self.output("What do you want?")
        request = self.input("T for temperatures; S for settings; C for Capture; Ca for calibrate").lower()
        return self.matchRequest(request)
    
    def capture(self):
        self.camera.capture()

    def matchRequest(self, request):
        if request == "t":
            self.displayTemps(self, [], False, False, False, 'user request')
            #self.speakTemps()
            return
        elif request == "s":
            return self.userInputs()
        elif request == "c":
            return self.capture()
        elif request == "ca":
            return self.calibrate() #uncomment to calibrate
            return
        else:
            return self.output("Command not recognised")

    def calibrate(self):
            self.sensors.calibrate()

    
