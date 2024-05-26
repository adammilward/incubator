from picamera import PiCamera
from time import sleep
from datetime import datetime


class Camera:
    def __init__(self):
        self.camera = PiCamera()

    def capture(self, hour = ''):
        self.camera.annotate_text = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.camera.start_preview()
        sleep(5)
        fileName = '/home/adam/Desktop/fruit'
        self.camera.capture(fileName + '.jpg')
        
        if (hour):
            fileName += '-' + hour
            self.camera.capture(fileName + '.jpg')


        self.camera.stop_preview()