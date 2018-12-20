import machine
import time
import utime
import scalecat
import scalefood
import scaleio
import displayio
import timer
from cats import Cats

### init
display=displayio.DisplayIO()
cats=Cats(display)
scale_cat=scalecat.ScaleCat(display, cats)
scale_food=scalefood.ScaleFood(display, cats)
scale_io=scaleio.ScaleIO()



import micropython

### this is the "userinterface" for now. replace with buttons or something ;)

def clear():
     import os
     os.remove("scale_food.state")
     os.remove("scale_cat.state")

def s():
    """save"""
    print("saving stuff")
    scale_cat.save()
    scale_food.save()

def t():
    print("tarring")
    scale_cat.tarre()
    scale_food.tarre()


def q(name, quota):
    '''set daily quota'''
    cats.by_name(name).state.feed_quota_max=quota
    cats.by_name(name).state.feed_quota_min=-quota
    cats.by_name(name).state.feed_daily=quota
    cats.by_name(name).save()
    print("set daily quota of cat")


def n(name):
    '''new cat or reset weight'''
    cats.new(name)


# prev=0


# led=machine.Pin(5,machine.Pin.OUT)
# oldvalue=True

slow_check_timestamp=timer.timestamp

def loop(sched=None):
    global slow_check_timestamp

    timer.update()

    ### read and update scales
    if scale_io.scales_ready():

        # read, without irqs
        c=scale_io.read_cat()
        f=scale_io.read_food()

        scale_cat.measurement(c)
        scale_food.measurement(f)


        # if not wlan.isconnected():
        #     global oldvalue
        #     led.value(oldvalue)
        #     oldvalue=not oldvalue
        # else:
        #     led.value(0)


    #stuff that doesnt have to be done every loop
    if timer.timestamp-slow_check_timestamp>1000:

        ### auto feed?
        if scale_food.should_feed():
            scale_io.feed()


        ### save settings
        if scale_cat.should_save and scale_cat.stable and abs(scale_cat.last_stable_weight)<5:
            scale_cat.save()
            scale_food.save()
            cats.save()
            scale_cat.should_save=False
            print("Saved")

        ### display realtime quota/cat food_weight
        display.refresh()
        slow_check_timestamp=timer.timestamp

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
import config
#
#



### network stuff
if hasattr(config, 'network'):
    import network
    from network import WLAN
    wlan = WLAN(network.STA_IF) # get current object, without changing the mode
    wlan.active(True)
    wlan.ifconfig(config.network)
    wlan.connect(config.wifi_essid, config.wifi_password)



#network.telnet.start()
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






loop()
