import machine
import time
import utime
import scalecat
import scalefood
import scaleio
import timer
import db
from cats import Cats
import usocket
import config

### init
display=config.display_class()
cats=Cats(display)
db=db.Db(display)
scale_cat=scalecat.ScaleCat(display, cats, db)
scale_food=scalefood.ScaleFood(display, cats, scale_cat)
scale_io=scaleio.ScaleIO(display)

#doing my part :)
display.msg("Subscribe2Pewdiepie!")


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
    cats.save()

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


led=machine.Pin(5,machine.Pin.OUT)
oldvalue=True

slow_check_timestamp=timer.timestamp

global last_state
last_state="bla"
def cam_send(state):
    global last_state
    if state!=last_state:
        try:
            # print("Setting cam to "+state)
            s=usocket.socket()
            sockaddr = usocket.getaddrinfo('192.168.13.233', 1234)[0][-1]
            s.connect(sockaddr)
            s.send(state+"\n")
            s.close()
            # print("Cam send done")
        except Exception as e:
            # print("failed: "+str(e))
            pass
    last_state=state

cam_detect_count=0
def loop(sched=None):
    global slow_check_timestamp

    timer.update()

    ### read and update scales
    if scale_io.scales_ready():

        # read, without irqs
        c=scale_io.read_cat()
        f=scale_io.read_food()
        # print(f)

        if c:
            scale_cat.measurement(c)
        if f:
            scale_food.measurement(f)


        if not wlan.isconnected():
            global oldvalue
            led.value(oldvalue)
            oldvalue=not oldvalue
        else:
            led.value(0)


    #stuff that doesnt have  to be done every loop
    if timer.diff(timer.timestamp,slow_check_timestamp)>1000:

        ###  feed?
        if scale_food.should_feed():
            scale_io.feed(config.servo_length)
            scale_food.fed()


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



        global cam_detect_count
        ### cat cam hack
        if scale_cat.stable and scale_cat.last_stable_weight<100 and scale_cat.state.stable_count>300:
            cam_detect_count=0
            cam_send("false")
        else:
            if scale_cat.last_realtime_weight>100:
                cam_detect_count=cam_detect_count+1
                #sometimes there are bogus measurements, so make sure we have more than one
                if cam_detect_count==3:
                    cam_send("true")



    if config.loop_async:
        micropython.schedule(loop,None)


import config



### network stuff
import network
from network import WLAN
wlan = WLAN(network.STA_IF) # get current object, without changing the mode
wlan.active(True)
# wlan.ifconfig(config.network)
wlan.connect(config.wifi_essid, config.wifi_password)




import sys
def input_thread():
    while True:
        c=sys.stdin.read(1)
        print("JA"+c)




if not config.loop_async:
    while True:
        loop()
else:
    loop()
