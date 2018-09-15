#hackety hack..will rewrite later

print("Booting feeder")
import machine
import time
import config

import network
from network import WLAN
wlan = WLAN(network.STA_IF) # get current object, without changing the mode

# if machine.reset_cause() != machine.SOFT_RESET:
# wlan.init(WLAN.STA)
wlan.active(True)
# configuration below MUST match your home router settings!!
wlan.ifconfig(config.network)

# if not wlan.isconnected():
# change the line below to match your network ssid, security and password
wlan.connect(config.wifi_essid, config.wifi_password)



# if machine.reset_cause() != machine.SOFT_RESET:
# # if True:
#     print("Configuring network")
#     #connect wifi
#     import network
#     sta_if = network.WLAN(network.STA_IF)
#     sta_if.ifconfig(config.network)
#     sta_if.active(True)
#     sta_if.connect(config.wifi_essid, config.wifi_password)

#init servo
servo = machine.PWM(machine.Pin(5), freq=50)

left_duty=50
off_duty=77
right_duty=84
servo.duty(off_duty)


#configure webhandlers
from microWebSrv import MicroWebSrv

@MicroWebSrv.route('/feed/<amount>')
def handlerFeed(httpClient, httpResponse, routeArgs) :
    try:
        print("Handling feed request, amount=%s" % routeArgs['amount'])

        ### feed
        for duty in range(off_duty, left_duty,-1):
            servo.duty(duty)
            time.sleep_ms(20)

        time.sleep_ms(int(routeArgs['amount']))

        for duty in range(left_duty, off_duty,1):
            servo.duty(duty)
            time.sleep_ms(20)


        ### retract
        for duty in range(off_duty, right_duty,1):
            servo.duty(duty)
            time.sleep_ms(20)

        for duty in range(right_duty, off_duty,-1):
            servo.duty(duty)
            time.sleep_ms(20)


    except Exception as e:
        print("FAILED: " + str(e))

    servo.duty(off_duty)

# start webserver
mws = MicroWebSrv() # TCP port 80 and files in /flash/www
mws.Start()         # Starts server in a new thread
