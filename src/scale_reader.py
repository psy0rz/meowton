# read loadcells and send to Scale().measurement

import threading
from RPi import GPIO
from hx711 import HX711

from scale import Scale



stop_event = threading.Event()

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

        #hx711 sometimes returns strange values, filter them
        MAX_CHANGE=10000

        last_cat =0
        last_food =0

        while not stop_event.is_set():
            raw_cat_value=hx711_cat._read()
            if raw_cat_value is not False:
                if abs(raw_cat_value-last_cat)<MAX_CHANGE:
                    scale_cat.measurement(raw_cat_value)
                last_cat = raw_cat_value

            raw_food_value=hx711_food._read()
            if raw_food_value is not False:
                if abs(raw_food_value-last_food)<MAX_CHANGE:
                    scale_food.measurement(raw_food_value)
                last_food=raw_food_value

    threading.Thread(target=reader).start()


def stop():
    stop_event.set()