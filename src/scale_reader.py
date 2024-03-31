# read loadcells and send to Scale().measurement

import threading
from RPi import GPIO
from hx711 import HX711

from scale import Scale
from sensor_filter import SensorFilter

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
        filter_cat=SensorFilter(10000)
        filter_food=SensorFilter(100000)

        while not stop_event.is_set():
            raw_cat_value=hx711_cat._read()
            if raw_cat_value is not False and filter_cat.valid(raw_cat_value):
                scale_cat.measurement(raw_cat_value)

            raw_food_value=hx711_food._read()
            if raw_food_value is not False and filter_food.valid(raw_food_value):
                scale_food.measurement(raw_food_value)

    threading.Thread(target=reader).start()


def stop():
    stop_event.set()