# bare minimum to initalize webrepl and start meowton


### network stuff
import config
import network
from network import WLAN
wlan = WLAN(network.STA_IF) # get current object, without changing the mode
wlan.active(True)
# wlan.ifconfig(config.network)
wlan.connect(config.wifi_essid, config.wifi_password)

import webrepl
webrepl.start()


from meowton import *
