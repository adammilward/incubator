
import glob
import os
import board
import adafruit_am2320

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

class SensorRead:
    def __init__(self):
        base_dir = '/sys/bus/w1/devices/'
        self.deviceFolders = glob.glob(base_dir + '28*')
        self.htSensor = adafruit_am2320.AM2320(board.I2C())

        tempsCount = len(self.deviceFolders) + 1 # w1 plus humidity sensors

        self.humidity = 0
        self.temps = [0 for i in range(tempsCount)]
        self.mean = 0
        self.min = 0
        self.max = 0
        
        print("Found folders: ")
        print(self.deviceFolders)

    def readAll(self):
        self.readHumidity()
        self.readTemps()

    def readHumidity(self):
        self.humidity = self.htSensor.relative_humidity

    def readTemps(self):
        for i, folder in enumerate(self.deviceFolders):
            deviceFile = folder + '/w1_slave'
            self.temps[i] = self.read_temp(i)
        
        self.temps[len(self.deviceFolders)] = self.htSensor.temperature
        
        self.mean = sum(self.temps) / len(self.temps)
        self.min = min(self.temps)
        self.max = max(self.temps)

    def read_temp_raw(self, deviceFile):
        f = open(deviceFile, 'r')
        lines = f.readlines()
        f.close()
        return lines
    
    def read_temp(self, i):
        lines = self.read_temp_raw(self.deviceFolders[i] + '/w1_slave')
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
        else:
            raise Exception("could not read temp")