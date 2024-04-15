# 3.3v  x   x   5v
# SDA   x   x   5v
# SLC   x   x   GND
# 1W    4   14  
# GND   x   15
# HEAT  17  18
#240 2  27  x
# fan   22  23
#      3.3  24
# led   10  G


import Control

control = Control.Control();

control.read()
#control.action()
#control.output()

control.run()

control.allOff()