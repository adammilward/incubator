import time

class PeakDetect:
    def __init__(self) -> None:
        self.history = []

        self.direction = 0
        self.oldDirection = 0

        self.recentMax = -10000
        self.recentMin = 100000

    def addValue(self, ts, temp):
        value = {'ts': int(ts), 'temp': temp}
        if len(self.history) < 3:
            self.history.append(value)
        else:
            self.history = self.history[1:] + [value]

    def detect(self):
        if len(self.history) < 3:
            return False
        
        self.oldDirection = self.direction

        new = []

        for value in self.history:
            new.append(value['temp'])

        #print()
        #print('old', old)
        #print('new', new)

        self.recentMax = max(self.recentMax, min(new))
        self.recentMin = min(self.recentMin, max(new))

        #print('max: ', self.recentMax, '    min: ', self.recentMin)

        if max(new) < self.recentMax and self.direction > -1:
            self.recentMin = max(new)
            self.direction = -1
            
        
        if min(new) > self.recentMin and self.direction < 1:
            self.recentMax = min(new)
            self.direction = 1

        return self.oldDirection - self.direction

    def getValue(self):
        val = input('give me a value: ')

        try:
            self.addValue(time.time(), float(val))
        except:
            self.getValue()

        self.detect()
        self.getValue()
