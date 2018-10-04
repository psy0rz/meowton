import machine
import time
import utime
from hx711 import HX711
import linear_least_squares
import scale


class CatScale(scale.Scale):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def event_stable(self, timestamp, weight):
        """called once after scale has been stable according to specified stable_ parameters"""
        # print("Stable averaged weight: {}g".format(weight))

        # print(weight, changed, s.offset(s.get_average()))
        lcd.move_to(0,0)
        lcd.putstr("%sg   \n" % int(weight))
        # if changed:
        #     lcd.putstr("*")
        #     # print(weight)
        #
        #     # cals=8
        #     #calibration weight detected?
        #     if not s.state.no_tarre:
        #         for cal in cals:
        #             diff=abs(weight-cal)
        #             if diff< (cal*0.1):
        #                 print("Call diff {}g".format(diff))
        #                 s.add_calibration(cal)
        #
        # else:
        #     lcd.putstr(" ")


    def event_realtime(self, timestamp, weight):
        """called on every measurement with actual value (non averaged)"""
        # print("Weight: {}g".format(weight))
        lcd.move_to(0,1)
        lcd.putstr("(%sg)    \n" % int(weight))

    def event_unstable(self, timestamp):
        """called once when scale leaves stable measurement"""
        # print("Unstable")
        lcd.move_to(0,0)
        lcd.putstr("          \n")



cals=[100, 146, 288 ]





#44000 lijkt goede default
    # 4stuks
    # [0.0128931987830166, 0.000264813001603831, 0.00427765204759359, -0.001953125]
    # 5stuks 100g
    # [0.00214620581609728, 0.00208298308729234, 0.00208458315164178, 0.00207632560760407]
    #2988g
    # [0.00222479813131911, 0.00221998565648258, 0.00217477510101383, 0.00217539021034517]
    # [0.00220972717648679, 0.0022622285441247, 0.00215095809341364, 0.00217704175238537],
    # [0.00220906755943467, 0.00228430436231214, 0.002176687127307, 0.00217088009246745]
    # [0.00219813777170196, 0.00228887881929506, 0.00217398195523495, 0.00217199745507122]
c=[0.00221357925767506, 0.00220807260906328, 0.00217914086524251, 0.00217401971844616]
#per stuk met 288
c=[0.0021941514217544, 0.00218897609921167, 0.0021661151841795, 0.00216198636842856]

#light+heavy 8
c=[0.00221163928750856, 0.00220575015516021, 0.00217667088292277, 0.00217572827244]
# avg=0.002192447149507885
# c=[avg] * 4

s=CatScale(calibrate_factors=c )
s.state.load('s')

s.stable_auto_tarre_max=20
s.stable_wait=5
s.stable_skip_measurements=5
s.stable_range=10
s.stable_auto_tarre=10

#hx
cells=[
    HX711(d_out=34, pd_sck=32), #1
    HX711(d_out=25, pd_sck=33), #2
    HX711(d_out=27, pd_sck=26), #3
    HX711(d_out=17, pd_sck=5), #4
]


#lcd
DEFAULT_I2C_ADDR = 0x27

from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd

i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

import micropython

prev=0
def loop(timer):
    global prev
    timestamp=int(time.time()*1000)
    # s.measurement(timestamp, [hx.read()])
    prev=timestamp
    s.measurement(timestamp,
    [
        cells[0].read(),
        cells[1].read(),
        cells[2].read(),
        cells[3].read(),

    ])


    # print("{}\t{}\t{}\t{}".format(
    #     cells[0].read(),
    #     cells[1].read(),
    #     cells[2].read(),
    #     cells[3].read()
    # ))



    micropython.schedule(loop,None)

micropython.schedule(loop,None)

# while True:
#     loop(0)



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
