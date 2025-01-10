import time

class PeakDetect:
    def __init__(self) -> None:
        self.history = []

        self.direction = -1
        self.oldDirection = 1

        self.sampleCount = 5
        self.recentMax = -10000
        self.recentMin = 100000

    def addValue(self, ts, temp):
        value = {'ts': int(ts), 'temp': temp}
        if len(self.history) < self.sampleCount:
            self.history.append(value)
            values = self.getValues()
            self.recentMin = max(values)
            self.recentMax = min(values)
        else:
            self.history = self.history[1:] + [value]

    ## returns -1 if peak detected (and falling),
    # returns 1 if trough detected (and rising)
    # else returns 0 
    def detect(self):
        if len(self.history) < self.sampleCount:
            return False
        
        self.oldDirection = self.direction

        values = self.getValues()

        #print()
        #print('new', new)

        self.recentMax = max(self.recentMax, min(values))
        self.recentMin = min(self.recentMin, max(values))

        #print('max: ', self.recentMax, '    min: ', self.recentMin)

        if max(values) < self.recentMax and self.direction != -1:
            #falling
            self.recentMin = max(values)
            self.direction = -1
            
        
        if min(values) > self.recentMin and self.direction != 1:
            #rising
            self.recentMax = min(values)
            self.direction = 1

        return int((self.direction - self.oldDirection) * 0.5)

    def getValues(self):
        values = []

        for value in self.history:
            values.append(value['temp'])
        return values

    def getValue(self):
        val = input('give me a value: ')

        try:
            self.addValue(time.time(), float(val))
        except:
            self.getValue()

        self.detect()
        self.getValue()
