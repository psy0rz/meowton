import machine
import time
import utime
from hx711 import HX711

import scale

def measurement(timestamp, weight, changed):
    # print(weight, changed, s.offset(s.get_average()))
    lcd.move_to(0,0)
    lcd.putstr("%s   \n" % int(weight))
    if changed:
        lcd.putstr("*")
    else:
        lcd.putstr(" ")


def cal():
    s.calibrate_factors=s.offset(s.get_average())

#44000 lijkt goede default
s=scale.Scale(calibrate_weight=100, calibrate_factors=[47604], callback=measurement)
s.stable_auto_tarre_max=10
s.stable_wait=1
s.stable_skip_measurements=1
s.stable_range=5

#hx
hx=HX711(d_out=34, pd_sck=32)

#lcd
DEFAULT_I2C_ADDR = 0x27

from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd

i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

import micropython

prev=0
def jannify(timer):
    global prev
    timestamp=int(time.time()*1000)
    s.measurement(timestamp, [hx.read()])
    prev=timestamp

    micropython.schedule(jannify,None)

# from machine import Timer
# tim = Timer(1)
# tim.init(period=100, mode=Timer.PERIODIC, callback=jannify)
micropython.schedule(jannify,None)




# i = machine.I2C(0, sda=21, scl=22, freq=100000)
# while True:
#     print(i.scan())


# #hackety hack..will rewrite later
#
# print("Booting feeder")
# import machine
# import time
# import config
#
# led=machine.Pin(5,machine.Pin.OUT)
#
# ### network stuff
# import network
# from network import WLAN
# wlan = WLAN(network.STA_IF) # get current object, without changing the mode
# wlan.active(True)
# wlan.ifconfig(config.network)
# wlan.connect(config.wifi_essid, config.wifi_password)
#
# while not wlan.isconnected():
#     print("waiting for wifi..")
#     led.value(1)
#     time.sleep_ms(50)
#     led.value(0)
#     time.sleep_ms(50)
# print("BAM")
# network.telnet.start()
#
#
# ### servo stuff
# servo = machine.PWM(machine.Pin(17), freq=50)
#
# left_duty=8.5
# middle_duty=7.5
# right_duty=6
# servo.duty(0)
#
# def fade(pwm, start_duty, end_duty, fade_time):
#     '''pwm duty-cycle fader'''
#     start_time=time.time()
#     passed_time=0
#     while passed_time<fade_time:
#         value=start_duty + (end_duty-start_duty)*(passed_time/fade_time)
#         pwm.duty(value)
#         passed_time=time.time()-start_time;
#
#     pwm.duty(end_duty)
#
#
# def feed(amount):
#     #feed
#     fade(servo, middle_duty, right_duty, 0.2)
#     time.sleep(amount/1000)
#     fade(servo, right_duty, middle_duty, 0.2)
#
#
#     # ### retract
#     fade(servo, middle_duty, left_duty, 0.1)
#     fade(servo, left_duty, middle_duty, 0.1)
#
#     #disable
#     servo.duty(0)
#
#
#
# ### webserver
# from microWebSrv import MicroWebSrv
#
# @MicroWebSrv.route('/feed/<amount>')
# def handlerFeed(httpClient, httpResponse, routeArgs) :
#     try:
#         print("Handling feed request, amount=%s" % routeArgs['amount'])
#
#         feed(int(routeArgs['amount']))
#
#     except Exception as e:
#         print("FAILED: " + str(e))
#
#     servo.duty(0)
#
# # start webserver
# mws = MicroWebSrv() # TCP port 80 and files in /flash/www
# mws.Start()         # Starts server in a new thread
