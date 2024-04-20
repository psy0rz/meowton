from peewee import Model, IntegerField

from db import db
from RPi import GPIO

PWM_PIN = 18

class Feeder(Model):

    servo_middle=IntegerField()
    servo_speed=IntegerField()
    servo_time=IntegerField()

    class Meta:
        database=db


    def feed_cycle(self):

        # GPIO.


