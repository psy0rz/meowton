import random
import threading
import time

from scale import Scale
from sensor_filter import SensorFilter


class SensorReader:
    """read data from hardware via a thread, filters it and sends it to a Scale() instance"""
    def __init__(self, name:str, data_pin:int, clk_pin:int, sim:bool):

        self.sensor_filter=SensorFilter(1000)
        self.scale = Scale( name)

        self.sim_value=0
        self.sim_noise=20

        self.__data_pin=data_pin
        self.__clk_pin=clk_pin
        self.__sim=sim

        self.__thread: threading.Thread|None = None
        self.__stop_event = threading.Event()

    def simulator_thread(self):

        while not self.__stop_event.is_set():
            raw_value=self.sim_value + int(random.normalvariate(0, self.sim_noise))
            if self.sensor_filter.valid(raw_value):
                self.scale.measurement(raw_value)

            time.sleep(0.1)

    def reader_thread(self):
        from RPi import GPIO
        from hx711 import HX711

        GPIO.setwarnings(False)

        hx711 = HX711(
            dout_pin=self.__data_pin,
            pd_sck_pin=self.__clk_pin,
            channel='A',
            gain=128
        )

        hx711.reset()  # Before we start, reset the HX711 (not obligate)

        while not self.__stop_event.is_set():
            raw_value = hx711._read()
            if raw_value is not False and self.sensor_filter.valid(raw_value):
                self.scale.measurement(raw_value)


    def start(self):
        """start reader thread, or simtrhead if data/clk are not specified"""

        if self.__sim:
            self.__thread = threading.Thread(target=self.simulator_thread)
        else:
            self.__thread = threading.Thread(target=self.reader_thread)

        self.__thread.start()

    def stop(self):
        self.__stop_event.set()
        self.__thread.join()

