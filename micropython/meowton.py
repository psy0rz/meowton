try:
    import config
except:
    print("#### MEOWTON: config.py is missing, cant boot!")
    import sys
    sys.exit(1)

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

import gc
import uasyncio
import sys

### init

# Init display
try:
    print("Init display...")
    display=config.display_class()
except Exception as e:
    print("DISPLAY ERROR: "+str(e))
    print("Falling back to serial display.")
    import display
    display=display.Display()


# Init classes
cats=Cats(display)
db=db.Db(display)
scale_cat=scalecat.ScaleCat(display, cats, db)
scale_food=scalefood.ScaleFood(display, cats, scale_cat)
scale_io=scaleio.ScaleIO()

try:
    scale_io.start()
except Exception as e:
    # scale_io=None
    display.msg("Scale IO error: "+str(e))


# webserver?
if config.run_webserver:
    from webserver import Webserver
    webserver=Webserver(display)


# wifi setup
if sys.platform=='esp32':
    import network
    if config.wifi_essid:
        print("Configuring wifi {}".format(config.wifi_essid))
        wlan = network.WLAN(network.STA_IF) #station mode
        
        wlan.active(True)
        wlan.connect(config.wifi_essid, config.wifi_password)
    else:
        print("Running as wifi Access Point")
        print("NOTE: You cant use the webinterface in this mode.")
        wlan = network.WLAN(network.AP_IF) #AP mode
        wlan.config(essid='meowton')
        wlan.active(True)

last_ip=""



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
    '''new cat'''
    cats.new(name)

def r(amount=0):
    '''reset food quotas to 0'''
    print("resetting all quotas to {}".format(amount))
    cats.reset_all(amount)

def cal():
    scale_cat.recalibrate()
    scale_food.recalibrate()


def feed():
    scale_io.feed()
    scale_food.fed()

#pause
def p():
    Timer(-1).deinit()

# prev=0




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


################ read sensors, fast stuff
cam_detect_count=0
def read_sensor_loop():

    while True:
        timer.update()

        ### read and update scales

        #read all sensors and restart hx711 measurements (those take time, so restart them all at once)
        c=scale_io.read_cat()
        f=scale_io.read_food()

        if c:
            scale_cat.measurement(c)

        if f:
            scale_food.measurement(f)

        #realtime test output
        if config.print_weights and  c and f:
            weights=scale_cat.calibrated_weights(scale_cat.offset(c))
            print(" cat0 = {:4.0f}   cat1 = {:4.0f}   cat2 = {:4.0f}   cat3 = {:4.0f}   food = {:3.2f}".format(weights[0], weights[1], weights[2], weights[3], scale_food.last_realtime_weight))

        await uasyncio.sleep_ms(100)


################# loop that checks slow stuff every second or so
def check_loop():
    if sys.platform=='esp32':
        led=machine.Pin(5,machine.Pin.OUT)
        oldvalue=True

    while True:
        if sys.platform=='esp32':
            if not wlan.isconnected():
                led.value(oldvalue)
                oldvalue=not oldvalue
            else:
                ip=wlan.ifconfig()[0]
                global last_ip
                if last_ip!=ip:
                    print("MEOWTON: Interface at http://"+ip)
                    display.msg(ip)
                    last_ip=ip

            #heartbeat
            led.value(oldvalue)
            oldvalue=not oldvalue

        gc.collect()


        ###  feed?
        if scale_food.should_feed():
            feed()

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


        await uasyncio.sleep(1)


################################ INIT


# from machine import Timer
def start():

    event_loop=uasyncio.get_event_loop()
    event_loop.create_task(read_sensor_loop())
    event_loop.create_task(check_loop())

    print("MEOWTON: Boot complete.")
    # start webinterface?
    if config.run_webserver:
        webserver.run()
    else:
        event_loop.run_forever()

