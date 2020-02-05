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
import gc
import uasyncio


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
scale_io=scaleio.ScaleIO(display)


# webserver?
if config.run_webserver:
    from webserver import Webserver
    webserver=Webserver(display)


# wifi setup
if config.wifi_essid:
    print("Configuring wifi {}".format(config.wifi_essid))
    wlan = network.WLAN(network.STA_IF) # get current object, without changing the mode
    wlan.active(True)
    wlan.connect(config.wifi_essid, config.wifi_password)
else:
    print("Running as wifi Access Point")
    wlan = network.WLAN(network.AP_IF)
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
    scale_io.feed(config.servo_fade_time, config.servo_sustain_time, config.servo_retract_time)
    scale_food.fed()

#pause
def p():
    Timer(-1).deinit()

# prev=0


led=machine.Pin(5,machine.Pin.OUT)
oldvalue=True


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

        await uasyncio.sleep_ms(100)


################# loop that checks slow stuff every second or so
def check_loop():
    while True:
        if not wlan.isconnected():
            global oldvalue
            led.value(oldvalue)
            oldvalue=not oldvalue

        gc.collect()

        #heartbeat
        global oldvalue
        led.value(oldvalue)
        oldvalue=not oldvalue


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

        await uasyncio.sleep(1)


################################ INIT


from machine import Timer
def start():

    event_loop=uasyncio.get_event_loop()
    event_loop.create_task(read_sensor_loop())
    event_loop.create_task(check_loop())
   
    # start webinterface?
    if config.run_webserver:
        webserver.run()
    else:
        event_loop.run_forever()

