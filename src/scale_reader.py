# read loadcells and send to Scale().measurement
import random
import sys
import threading
import time

import settings
from scale import Scale
from sensor_filter import SensorFilter

stop_event = threading.Event()

sim_food_value=198000
sim_food_min=188000
sim_food_max=300000

sim_cat_value=-40000
sim_cat_min=-50000
sim_cat_max=14000


def simulator_thread(scale_cat: Scale, scale_food: Scale, sensor_filter_cat: SensorFilter,
                     sensor_filter_food: SensorFilter):
    def send(raw_cat_value, raw_food_value):
        if raw_cat_value is not False and sensor_filter_cat.valid(raw_cat_value):
            scale_cat.measurement(raw_cat_value)
        if raw_food_value is not False and sensor_filter_food.valid(raw_food_value):
            scale_food.measurement(raw_food_value)

    while not stop_event.is_set():

        send(sim_cat_value + int(random.normalvariate(0, 20)),
             sim_food_value + int(random.normalvariate(0, 20)))

        time.sleep(0.1)


def reader_thread(scale_cat: Scale, scale_food: Scale, sensor_filter_cat: SensorFilter,
                  sensor_filter_food: SensorFilter):
    from RPi import GPIO
    from hx711 import HX711

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

    while not stop_event.is_set():
        raw_cat_value = hx711_cat._read()
        if raw_cat_value is not False and sensor_filter_cat.valid(raw_cat_value):
            scale_cat.measurement(raw_cat_value)

        raw_food_value = hx711_food._read()
        if raw_food_value is not False and sensor_filter_food.valid(raw_food_value):
            scale_food.measurement(raw_food_value)


def start(scale_cat: Scale, scale_food: Scale, sensor_filter_cat: SensorFilter, sensor_filter_food: SensorFilter):
    global thread
    if not settings.dev_mode:
        thread = threading.Thread(target=reader_thread,
                                  args=[scale_cat, scale_food, sensor_filter_cat, sensor_filter_food])
    else:
        thread = threading.Thread(target=simulator_thread,
                                  args=[scale_cat, scale_food, sensor_filter_cat, sensor_filter_food])

    thread.start()


def stop():
    stop_event.set()
    thread.join()

