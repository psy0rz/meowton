import display_serial
import ntptime

VERSION='1.2'

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
import time
import db
from cats import Cats

import gc
import uasyncio
import os
from lib import multicall





class Meowton():

    def __init__(self):

        self.wlan=""
        self.last_ip=""

        self.event_loop = uasyncio.get_event_loop()

        displays = []

        # display LCD?
        if hasattr(config, 'lcd_pins'):
            try:
                import display_lcd20x4
                displays.append(display_lcd20x4.Display(config.lcd_pins[0], config.lcd_pins[1]))
            except Exception as e:
                print("LCD failed: {}".format(str(e)))

        # web server?
        if getattr(config, 'run_webserver', False):
            import display_web
            import webserver
            display_web = display_web.Display()
            displays.append(display_web)
            self.event_loop.create_task(webserver.Webserver(display_web, self).server())

        # display serial?
        if getattr(config, 'display_serial', False):
            import display_serial
            displays.append(display_serial.Display())

        # mqtt?
        if getattr(config, 'mqtt', False):
            try:
                import display_mqtt
                displays.append(display_mqtt.Display(settings=config.mqtt))
            except Exception as e:
                print("MQTT: Error: {}".format(str(e)))


        self.display = multicall.MultiCall(displays)

        self.setup_wifi()
        try:
            ntptime.settime()
            print("NTP time:")
            print (time.localtime())
        except Exception as e:
            print(e)
            # self.display.msg("Time error")


        # Init classes
        self.cats = Cats(self.display)
        db_instance = db.Db(self.display)
        self.scale_cat = scalecat.ScaleCat(self.display, self.cats, db_instance)
        self.scale_food = scalefood.ScaleFood(self.display, self.cats, self.scale_cat)
        self.scale_io = scaleio.ScaleIO()

    def sysinfo(self):

        gc.collect()
        return ({
            'version': VERSION,
            'uptime': time.time(),
            'mem': gc.mem_free(),
            'freq': machine.freq(),
            'os_version': os.uname().version,
            'os_machine': os.uname().machine,
        })

    def setup_wifi(self):
        # wifi setup
        import network

        try:
            if getattr(config, 'wifi_essid', False):
                print("Configuring wifi {}".format(config.wifi_essid))
                self.wlan = network.WLAN(network.STA_IF)  # station mode
                self.wlan.active(True)
                self.wlan.connect(config.wifi_essid, config.wifi_password)

                count=10
                while self.wlan.status()!=network.STAT_GOT_IP and count>0:
                    self.display.msg("Connect ({})".format(count))
                    time.sleep(1)
                    count=count-1

                if count==0:
                    self.display.msg("Cant connect")
                    


            else:
                print("Running as wifi Access Point")
                print("NOTE: You cant use the webinterface in this mode.")
                self.wlan = network.WLAN(network.AP_IF)  # AP mode
                self.wlan.config(essid='meowton')
                self.wlan.active(True)
        except Exception as e:
            # make sure we continue without network if needed. (sometimes its broken after a few softreboots)
            print("NETWORK ERROR: " + str(e))


    # read sensors and pass to approriate classes
    async def read_sensor_loop(self):

        while True:
            timer.update()

            ### read and update scales

            #read all sensors and restart hx711 measurements (those take time, so restart them all at once)
            c=self.scale_io.read_cat()
            f=self.scale_io.read_food()

            if c:
                self.scale_cat.measurement(c)

            if f:
                self.scale_food.measurement(f)

            #realtime test output
            if config.print_weights and c and f:
                weights=self.scale_cat.calibrated_weights(self.scale_cat.offset(c))
                print(" cat0 = {:4.0f}   cat1 = {:4.0f}   cat2 = {:4.0f}   cat3 = {:4.0f}   food = {:3.2f}".format(weights[0], weights[1], weights[2], weights[3], self.scale_food.last_realtime_weight))

            await uasyncio.sleep_ms(100)

    # slow stuff to check
    async def check_loop(self):

        led=machine.Pin(5,machine.Pin.OUT)
        oldvalue=True

        while True:
            if not self.wlan.isconnected():
                led.value(oldvalue)
                oldvalue=not oldvalue
            else:
                ip=self.wlan.ifconfig()[0]

                if self.last_ip!=ip:
                    print("MEOWTON: Interface at http://"+ip)
                    self.display.msg(ip)
                    self.last_ip=ip

                #heartbeat
                led.value(oldvalue)
                oldvalue=not oldvalue

            gc.collect()


            ###  feed?
            if self.scale_food.should_feed():
                self.scale_io.feed()
                self.scale_food.fed()

            ### save settings
            if self.scale_cat.should_save and self.scale_cat.stable and abs(self.scale_cat.last_stable_weight)<100:
                self.scale_cat.save()
                self.scale_food.save()
                self.cats.save()
                self.scale_cat.should_save=False
                print("Saved")

            ### display realtime quota/cat food_weight
            self.display.refresh()

            await uasyncio.sleep(1)

    def run(self):
        try:
            self.scale_io.start()
        except Exception as e:
            # scale_io=None
            self.display.msg("Scale IO error: " + str(e))

        self.event_loop.create_task(self.read_sensor_loop())
        self.event_loop.create_task(self.check_loop())

        print("MEOWTON: Starting event loop")
        self.event_loop.run_forever()




