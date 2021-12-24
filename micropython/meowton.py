VERSION='1.1'

try:
    import config
except:
    print("#### MEOWTON: config.py is missing, cant boot!")
    import sys
    sys.exit(1)

import machine
import time
import scalecat
import scalefood
import scaleio
import timer
import db
from cats import Cats

import gc
import uasyncio
import sys
import os

### init

# wifi setup
if sys.platform == 'esp32':
    import network

    try:
        if config.wifi_essid:
            print("Configuring wifi {}".format(config.wifi_essid))
            wlan = network.WLAN(network.STA_IF)  # station mode
            wlan.active(True)
            wlan.connect(config.wifi_essid, config.wifi_password)
        else:
            print("Running as wifi Access Point")
            print("NOTE: You cant use the webinterface in this mode.")
            wlan = network.WLAN(network.AP_IF)  # AP mode
            wlan.config(essid='meowton')
            wlan.active(True)
    except Exception as e:
        #make sure we continue without network if needed. (sometimes its broken after a few softreboots)
        print("NETWORK ERROR: "+str(e))

last_ip = ""

# Init display
try:
    print("Init display...")
    display=config.display_class()
except Exception as e:
    print("DISPLAY ERROR: "+str(e))
    print("Falling back to dummy display.")
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




import micropython


def sysinfo():
    return({
        'version': VERSION,
        'uptime' : time.time(),
        'mem'    : gc.mem_free(),
        'freq'   : machine.freq(),
        'os_version'     : os.uname().version,
        'os_machine'     : os.uname().machine,
    })




################ read sensors, fast stuff
# cam_detect_count=0
async def read_sensor_loop():

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
        if config.print_weights and c and f:
            weights=scale_cat.calibrated_weights(scale_cat.offset(c))
            print(" cat0 = {:4.0f}   cat1 = {:4.0f}   cat2 = {:4.0f}   cat3 = {:4.0f}   food = {:3.2f}".format(weights[0], weights[1], weights[2], weights[3], scale_food.last_realtime_weight))

        await uasyncio.sleep_ms(100)


################# loop that checks slow stuff every second or so
async def check_loop():
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
            scale_io.feed()
            scale_food.fed()

        ### save settings
        if scale_cat.should_save and scale_cat.stable and abs(scale_cat.last_stable_weight)<100:
            scale_cat.save()
            scale_food.save()
            cats.save()
            scale_cat.should_save=False
            print("Saved")

        ### display realtime quota/cat food_weight
        display.refresh()

        await uasyncio.sleep(1)


################################ INIT
def start():

    event_loop=uasyncio.get_event_loop()
    event_loop.create_task(read_sensor_loop())
    event_loop.create_task(check_loop())

    # webserver?
    if config.run_webserver:
        from webserver import Webserver
        webserver = Webserver(display)
        event_loop.create_task(webserver.server())

    print("MEOWTON: Boot complete.")
    # start webinterface?
    event_loop.run_forever()

