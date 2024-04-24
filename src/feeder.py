import asyncio
from asyncio import Event

from peewee import Model, IntegerField, FloatField

import settings
from db import db
from scale import Scale

SERVO_PIN = 18
PWM_FREQ = 50

SERVO_MAX = 8
SERVO_MIN = 5

ERROR_WEIGHT_BELOW = -1
ERROR_WEIGHT_ABOVE = 50

from enum import Enum


class Status(Enum):
    OK = 1
    BUSY = 2
    ERROR = 3


class Feeder(Model):
    """operate the feeder servo and monitor if the food correctly dropped on the food_scale """

    feed_duty = FloatField(default=8)
    feed_time = IntegerField(default=250)
    reverse_duty = FloatField(default=6)
    reverse_time = IntegerField(default=500)

    empty_weight = FloatField(default=1)
    retry_max = IntegerField(default=3)
    retry_timeout = IntegerField(default=1000)

    __food_scale: Scale

    class Meta:
        database = db

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.feeding = False
        self.__event_request = Event()

        self.status_msg = "Ready"
        self.status: Status = Status.OK

        if not settings.dev_mode:
            from RPi import GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(SERVO_PIN, GPIO.OUT)
            self.__pwm = GPIO.PWM(SERVO_PIN, PWM_FREQ)
            self.__pwm.start(0)

    def init(self, food_scale: Scale):
        self.__food_scale = food_scale

    async def run_motor(self, duty, time):
        if settings.dev_mode:
            # simulate
            await asyncio.sleep(time / 1000)
            return

        self.__pwm.ChangeDutyCycle(duty)
        await asyncio.sleep(time / 1000)
        self.__pwm.ChangeDutyCycle(0)

    async def __forward(self):
        await self.run_motor(self.feed_duty, self.feed_time)

    async def __reverse(self):
        await self.run_motor(self.reverse_duty, self.reverse_time)

    def __log(self, status: Status, msg: str, log: str):
        self.status = status
        self.status_msg = msg
        print(f"Feeder: {log}")

    def food_detected(self):
        return self.__food_scale.last_stable_weight > self.empty_weight

    async def task(self):
        """will wait for feed requests and monitor the foodscale to see if it succeeded.
        also handles retries and errorr"""

        async def food_landed():
            """scale should become unstable when the food lands"""
            if self.__food_scale.stable:
                self.__log(Status.BUSY, "Dropping", "Waiting for food to land.")
                try:
                    await asyncio.wait_for(self.__food_scale.event_unstable.wait(), timeout=self.retry_timeout / 1000)
                    return True
                except asyncio.TimeoutError:
                    self.__log(Status.BUSY, "Timeout", f"Timeout! (attempt {attempts})")
                    return False

        #program startup
        await self.__food_scale.event_stable.wait()

        # wait for feed request
        while await self.__event_request.wait():

            self.feeding = True

            # wait until scale is in valid range
            while self.__food_scale.last_stable_weight < ERROR_WEIGHT_BELOW or self.__food_scale.last_stable_weight > ERROR_WEIGHT_ABOVE:
                self.__log(Status.ERROR, "Out of range", "Error, scale out of range!")
                await self.__food_scale.event_stable.wait()

            # attempt a few times to get food in the scale
            attempts = 0
            while not self.food_detected() and attempts <= self.retry_max:

                if not self.__food_scale.stable:
                    self.__log(Status.BUSY, "Waiting", f"Waiting until scale is stable")
                    await self.__food_scale.event_stable.wait()

                self.__log(Status.BUSY, "Feeding", f"Feeding")
                await self.__forward()

                if await food_landed():
                    self.__log(Status.BUSY, "Weighing", f"Weighing food")
                    await self.__food_scale.event_stable.wait()

                attempts = attempts + 1

            self.feeding = False
            self.__event_request.clear()

            # succeeded or food silo empty?
            if self.food_detected():
                self.__log(Status.OK, "Ready", f"Ready: {self.__food_scale.last_stable_weight:0.2f}g")
            else:
                await self.__reverse()
                self.__log(Status.ERROR, "Refill!", f"PLEASE REFILL AND TOUCH SCALE")
                await self.__food_scale.event_stable.wait()
                self.__log(Status.OK, "Ready", f"Resuming operation")

    def request(self):
        """request a feed cycle, if its not already running and if foodscale is considered empty"""

        if self.food_detected():
            return

        self.__event_request.set()


db.create_tables([Feeder])
