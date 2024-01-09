from espeak import espeak
import time



espeak.synth("Current temps: max. " + str(1))
espeak.synth("mean" + str(1.1))
espeak.synth(" min" + str(1.11))
espeak.synth(" one. " + str(1.111))
espeak.synth("probe 2 ")
espeak.synth(str(2.22))
espeak.synth("probe three. ")
espeak.synth(str(3.33))
espeak.synth("probe four. " + str(4.44))
espeak.synth(" 5. " + str(1.1111111))

time.sleep(60)