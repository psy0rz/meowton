#!/usr/bin/python3
from time import sleep

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
    scale.calibrate_weight=1534
    scale.recalibrate()


previous=0
while True:
    raw=hx711._read()
    if raw is not False:

        if abs(raw-previous)<1000:
            scale.measurement( [raw])
        previous=raw
    sleep(0.1)

