#!/usr/bin/python3 -u
print("STARTING")
import threading
from time import sleep
from nicegui import ui

from RPi import GPIO
from hx711 import HX711

from scale import Scale

GPIO.setwarnings(False)

print("CREAT")
hx711 = HX711(
    dout_pin=23,
    pd_sck_pin=24,
    channel='A',
    gain=128
)

print("RESET")

hx711.reset()   # Before we start, reset the HX711 (not obligate)

scale=Scale(1, 'test.json')
if not scale.is_calibrated():
    scale.calibrate_weight=10
    scale.recalibrate()


label=ui.label("waardee")

def reader():
    previous=0
    while True:
        raw=hx711._read()
        if raw is not False:
            # print(raw)

            if abs(raw-previous)<10000:
                scale.measurement( [raw])
            else:
                print("IGNORED")
            previous=raw
        else:
            print("ERROR")
        sleep(0.1)
        label.set_text(f"{scale.last_realtime_weight:.2f}g")


threading.Thread(target=reader).start()
print("start ui")
ui.run(reload=False)