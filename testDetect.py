import PeakDetect
import time

class Controll:
    def __init__(self) -> None:
        self.detector = PeakDetect.PeakDetect()

    def getValue(self):
        val = input('give me a value: ')

        try:
            self.detector.addValue(time.time(), float(val))
        except:
            self.getValue()

        direction = self.detector.detect()
        print(direction)

        if (direction < 0):
            print ('falling, max was: ', self.detector.recentMax)
            print(self.detector.history)
        elif (direction > 0):
            print ('rising, min was: ', self.detector.recentMin)
            print(self.detector.history)
        
        self.getValue()


control = Controll()
control.getValue()