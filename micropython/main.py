# bare minimum to initalize webrepl and start meowton

import machine
machine.freq(240000000) #only recently discovered it runs on 160Mhz by default.

# disable debug
# import esp
# esp.osdebug(None)

# import webrepl
# webrepl.start()

# print("Press CTRL-C to cancel boot...")
# import time
# time.sleep(0.25)
# print("Continuing boot.")
print("MEOWTON: Booting")

from meowton import Meowton
meowton_instance=Meowton()
meowton_instance.run()
