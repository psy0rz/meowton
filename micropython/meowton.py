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
import network
# import re
### init

# from display_web import DisplayWeb
# from webserver import Webserver

#todo: via config
# display_web=DisplayWeb()
# display=display_web
# webserver=Webserver(display_web)

try:
    print("Init display...")
    display=config.display_class()
except Exception as e:
    print("DISPLAY ERROR: "+str(e))
    print("Falling back to serial display.")
    import display
    display=display.Display()

cats=Cats(display)
db=db.Db(display)
scale_cat=scalecat.ScaleCat(display, cats, db)
scale_food=scalefood.ScaleFood(display, cats, scale_cat)
scale_io=scaleio.ScaleIO(display)

# wifi setup
wlan = network.WLAN(network.STA_IF) # get current object, without changing the mode
wlan.active(True)
wlan.connect(config.wifi_essid, config.wifi_password)
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
    scale_io.feed(config.servo_fade_time, config.servo_sustain_time, config.servo_retract_time)
    scale_food.fed()

#pause
def p():
    Timer(-1).deinit()

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


################ webinterface

# import picoweb
# webapp = picoweb.WebApp(__name__)
#
# @webapp.route("/")
# def handle_index(req, resp):
#     yield from picoweb.start_response(resp)
#     yield from resp.awrite("""
# <header><meta http-equiv="refresh" content="1"></header>
# <a href='feed'><button>Feed</button></a>
# <a href='feed'><button>Settings</button></a>
#     """)
#
#
# @webapp.route("/feed")
# def handle_feed(req, resp):
#     feed()
#     yield from picoweb.start_response(resp, status="302", headers='Location: /')






################ main loop
cam_detect_count=0
def loop(sched=None):
    global slow_check_timestamp

    timer.update()

    ### read and update scales
    if scale_io.scales_ready():

        #read all sensors and restart hx711 measurements (those take time, so restart them all at once)
        c=scale_io.read_cat()
        f=scale_io.read_food()

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



        ### display IP
        if wlan.isconnected():
            ip=wlan.ifconfig()[0]
            global last_ip
            if last_ip!=ip:
                print(ip)
                display.msg(ip)
                last_ip=ip


################################ INIT


from machine import Timer
def start():

    if not config.loop_async:
        while True:
            loop()
    else:
        tim = Timer(-1)
        tim.init(period=10, mode=Timer.PERIODIC, callback=loop)


    #start webinterface
    # try:
    #     webserver.run()


    # except KeyboardInterrupt:
    #     tim.deinit()
    #     raise
