import statistics

class PeakDetect:
    def __init__(self) -> None:
        self.history = []

        self.up = 'up'
        self.down = 'down'
        self.direction = ''

    def addValue(self, value):
        if len(self.history) < 4:
            self.history.append(value)
        else:
            self.history = self.history[1:4] + [value]

    def detect(self):
        if len(self.history) < 4:
            print('short list')
            return False
        
        if statistics.median(self.history[0:3]) > statistics.median(self.history[1:3]):
            print ('dropping, ', statistics.median(self.history[0:3]), statistics.median(self.history[1:3]))
        
        print(self.history)

    def getValue(self):
        val = input('give me a value: ')

        self.addValue(float(val))
        self.detect()
        self.getValue()

detector = PeakDetect()

detector.getValue()