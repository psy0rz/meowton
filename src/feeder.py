import asyncio

from peewee import Model, IntegerField, FloatField

import settings
from db import db

SERVO_PIN = 18
PWM_FREQ = 50


class Feeder(Model):
    feed_duty = FloatField(default=8)
    feed_time = IntegerField(default=250)
    reverse_duty = FloatField(default=6)
    reverse_time = IntegerField(default=500)

    class Meta:
        database = db

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.dev_mode:
            from RPi import GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(SERVO_PIN, GPIO.OUT)
            self.__pwm = GPIO.PWM(SERVO_PIN, PWM_FREQ)
            self.__pwm.start(0)

    async def feed_cycle(self):
        if settings.dev_mode:
            return

        self.__pwm.ChangeDutyCycle(self.feed_duty)
        await asyncio.sleep(self.feed_time / 1000)
        self.__pwm.ChangeDutyCycle(0)


db.create_tables([Feeder])
