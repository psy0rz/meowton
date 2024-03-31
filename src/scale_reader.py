
# read loadcells and update scale() classes

import threading
from RPi import GPIO
from hx711 import HX711



def start(scale_cat:Scale, scale_food:Scale):
    GPIO.setwarnings(False)

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

    hx711_cat.reset()  # Before we start, reset the HX711 (not obligate)
    hx711_food.reset()

    def reader():

    raw_cat=hx711_cat._read()
    if raw_cat is not False:
        scale_cat.

            if abs(raw_cat-previous_cat)<10000:
                scale_cat.measurement( [raw_cat])
            previous_cat=raw_cat




threading.Thread(target=reader).start()
print("start ui")
# ui.run(reload=False)