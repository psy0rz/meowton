#!/usr/bin/python3 -u
print("STARTING")
import threading
from time import sleep
# from nicegui import ui

from RPi import GPIO
from hx711 import HX711

from scale import Scale

GPIO.setwarnings(False)

print("CREAT")
hx711_food = HX711(
    dout_pin=23,
    pd_sck_pin=24,
    channel='A',
    gain=128
)
hx711_cat = HX711(
    dout_pin=27,
    pd_sck_pin=17,
    channel='A',
    gain=128
)

print("RESET")

hx711_cat.reset()   # Before we start, reset the HX711 (not obligate)
hx711_food.reset()

scale_cat=Scale(1, 'cat.json')
if not scale_cat.is_calibrated():
    scale_cat.calibrate_weight=200
    scale_cat.recalibrate()

scale_food=Scale(1, 'food.json')
if not scale_food.is_calibrated():
    scale_food.calibrate_weight=10
    scale_food.recalibrate()


def reader():
    previous_food=0
    previous_cat=0
    while True:
        raw_food=hx711_food._read()
        if raw_food is not False:

            if abs(raw_food-previous_food)<10000:
                scale_food.measurement( [raw_food])
            previous_food=raw_food

        raw_cat=hx711_cat._read()
        if raw_cat is not False:

            if abs(raw_cat-previous_cat)<10000:
                scale_cat.measurement( [raw_cat])
            previous_cat=raw_cat


threading.Thread(target=reader).start()
print("start ui")
# ui.run(reload=False)