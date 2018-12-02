import machine
import time
import utime
import scalecat
import scalefood
import scaleio
import displayio

### init
scale_cat=scalecat.ScaleCat()
scale_food=scalefood.ScaleFood()
scale_io=scaleio.ScaleIO()
display=displayio.DisplayIO()




import micropython

def clear():
     os.remove("scale_food.state")
     os.remove("scale_cat.state")

def s():
    """save"""
    print("saving stuff")
    scale_cat.state.save()
    scale_food.state.save()

def food_cal():
    scale_food.state.calibrations=[]
    scale_food.add_calibration(10)
    print("Recalibrated food with 10g")
    s()

prev=0
def loop(timer):
    global prev
    timestamp=int(time.time()*1000)
    prev=timestamp

    scale_food.measurement(timestamp, scale_io.read_food())
    scale_cat.measurement(timestamp, scale_io.read_cat())

    display.cat_weight(scale_cat.state.last_stable_weight, scale_cat.state.stable)
    display.food_weight(scale_food.state.last_stable_weight, scale_food.state.stable)

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
