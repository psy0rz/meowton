import asyncio
import random
import threading
import time
from typing import TypeAlias, Callable

MeasurementCallback: TypeAlias = Callable[[int], None]


class SensorReader:
    """read data from hardware via a thread, filters it and calls measurement_callback. (in a threadsafe way)"""

    __loop: asyncio.AbstractEventLoop

    def __init__(self, name: str, data_pin: int, clk_pin: int, sim: bool,
                 measurement_callback: MeasurementCallback):

        self.sim_value = 0
        self.sim_noise = 20

        self.__data_pin = data_pin
        self.__clk_pin = clk_pin
        self.__sim = sim

        self.__thread: threading.Thread | None = None
        self.__stop_event = threading.Event()

        # self.__loop = asyncio.get_event_loop()
        self.__measurement_callback = measurement_callback

    def simulator_thread(self):

        while not self.__stop_event.is_set():
            raw_value = self.sim_value + int(random.normalvariate(0, self.sim_noise))
            # print(f"jan {raw_value}")
            self.__loop.call_soon_threadsafe(self.__measurement_callback, raw_value)

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
            if raw_value is not False:
                self.__loop.call_soon_threadsafe(self.__measurement_callback, raw_value)

    def start(self):
        """start reader thread, or simtrhead if data/clk are not specified"""

        if self.__thread is not None:
            raise Exception("Thread already started")

        self.__loop = asyncio.get_running_loop()

        self.__stop_event.clear()

        if self.__sim:
            self.__thread = threading.Thread(target=self.simulator_thread)
        else:
            self.__thread = threading.Thread(target=self.reader_thread)

        self.__thread.start()

    def stop(self):
        self.__stop_event.set()
        self.__thread.join()
        self.__thread = None
