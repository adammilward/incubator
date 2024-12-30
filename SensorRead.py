import glob
import os
import board
import adafruit_am2320
import statistics
import json
from pathlib import Path
import PeakDetect
import time
import traceback

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

class SensorRead:
    def __init__(self):
        self.OFFSETS_FILE = 'offsets.json'

        base_dir = '/sys/bus/w1/devices/'
        self.deviceFolders = glob.glob(base_dir + '28*')
        self.htSensor = adafruit_am2320.AM2320(board.I2C())

        tempsCount = len(self.deviceFolders) + 1 # w1 plus humidity sensors

        self.getOffsets()

        self.humidity = 0
        self.temps = [0.0 for i in range(tempsCount)]
        self.meanTemp = 0
        self.medianTemp = 0
        self.spawnMedian = 0
        self.fruitMedian = 0
        self.minTemp = 0
        self.maxTemp = 0
        self.detectors = [PeakDetect.PeakDetect() for i in range(tempsCount)]

        #print("Found folders: ")
        #print(self.deviceFolders)
        #self.readAll()
        #print(self.temps)

    def readAll(self):
        self.readHumidity()
        self.readTemps()
        self.detectPeaks()

    def detectPeaks(self):
        for i, temp in enumerate(self.temps):
            self.detectors[i].addValue(time.time(), self.temps[i])

    def readHumidity(self):
        try:
            self.humidity = self.htSensor.relative_humidity
        except Exception as e:
            print ("Exception caught reading htHumidity sensor caught (ignoing)")
            print(str(e))
            #traceback.print_exc()
            self.humidity = -1

    def readTemps(self):
        htTemps = []
        for i, folder in enumerate(self.deviceFolders):
            deviceFile = folder + '/w1_slave'
            self.temps[i] = round((self.read_temp(i) + self.offsets[i]), 1)
            if (i % 5 == 0):
                try:
                    htTemps.append(self.htSensor.temperature)
                except OSError as e:
                    print('OSError exception caught reading htTemps temperature. Rsisig SenorReadExcepon')
                    raise SensorReadException(str(e))

        lastSensorIndex = len(self.deviceFolders)
        self.temps[lastSensorIndex] = round((statistics.median(htTemps) + self.offsets[lastSensorIndex]), 1)

        self.meanTemp = round(statistics.median(self.temps), 2)

        self.heater = self.temps[0]
        self.medianTemp = statistics.median(self.temps)
        self.fruitMedian = statistics.median(self.temps[1:3])
        self.fruitMax = max(self.temps[1:3])
        self.spawnMedian = statistics.median(self.temps[3:6])
        self.spawnMax = max(self.temps[3:6])
        self.minTemp = min(self.temps) 
        self.maxTemp = max(self.temps)

    def read_temp_raw(self, deviceFile):
        f = open(deviceFile, 'r')
        lines = f.readlines()
        f.close()
        return lines
    
    def read_temp(self, i):
        lines = self.read_temp_raw(self.deviceFolders[i] + '/w1_slave')
        
        if not (1 < len(lines)):
            print(lines)
            raise SensorReadException("Could not read temp, insufficien lines")
        
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
        else:
            raise Exception("could not read temp")
        
    def calibrate(self):
        self.offsets = [0 for i in range(len(self.temps))]
        self.readTemps()
        for i, temp in enumerate(self.temps):
            self.offsets[i] = self.meanTemp - self.temps[i]
        self.recordOffsets()

        print('temps before offset')
        print(self.temps)
        print('offsets')
        print(self.offsets)
        self.readTemps()
        print('temps after offsets')
        print(self.temps)

    def recordOffsets(self):
        with open(self.OFFSETS_FILE, 'w') as offsetsFile:
            json.dump(self.offsets, offsetsFile)

    def getOffsets(self):
        if (Path(self.OFFSETS_FILE)).exists():
            offsetsFile = open(self.OFFSETS_FILE)
            self.offsets = json.load(offsetsFile)
        else:
            self.offsets = [0.0 for i in range(len(self.temps))]
        
        #print('getOffsets')
        #print(self.offsets)

class SensorReadException(Exception):
    pass
