# 3.3v  x   x   5v
# SDA   2   x   5v
# SLC   3   x   GND
# 1W    4   14  
# GND   x   15
# HEAT  17  18
#240 2  27  x
# fan   22  23
#      3.3  24
# led   10  G
#        9  25
#       11  8

import Control
import traceback

while True:
    control = False
    try:
        control = Control.Control()
        control.read()
        control.run()
        control.allOff()
    
    except Exception as e:
        control.allOff()
        del(control)
        print('inpcubate.py: Exception caught, control destoryed, restarting.')
        print(str(e))
        traceback.print_exc()