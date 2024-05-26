import Camera
from gpiozero import LED

LED(10).on()
camera = Camera.Camera()



hour = '0'

print (bool(hour))

camera.capture()
# camera.capture('0')
# camera.capture('1')
# camera.capture('2')
# camera.capture('3')
# camera.capture('4')
# camera.capture('5')
# camera.capture('6')
# camera.capture('7')
# camera.capture('8')
# camera.capture('9')
# camera.capture('10')
# camera.capture('11')
# camera.capture('12')
# camera.capture('13')
# camera.capture('14')
# camera.capture('15')
# camera.capture('16')
# camera.capture('17')
# camera.capture('18')
# camera.capture('19')
# camera.capture('20')
# camera.capture('21')
# camera.capture('22')
# camera.capture('23')
LED(10).off()

camera.capture()
