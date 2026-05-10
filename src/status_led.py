import asyncio


import settings


from cat_detector import CatDetector
from feeder import Feeder
from util import Status
from RPi import GPIO

LED_PIN=4

class StatusLed():
    def __init__(self):

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN, GPIO.OUT)


    async def task(self, feeder:Feeder, cat_detector:CatDetector):
        if settings.dev_mode:
            return
        while True:
            if feeder.status==Status.OK and cat_detector.status==Status.OK:
                GPIO.output(LED_PIN, GPIO.HIGH)
                await asyncio.sleep(1)
                GPIO.output(LED_PIN, GPIO.LOW)
                await asyncio.sleep(0.1)
            else:
                GPIO.output(LED_PIN, GPIO.HIGH)
                await asyncio.sleep(0.1)
                GPIO.output(LED_PIN, GPIO.LOW)
                await asyncio.sleep(0.1)
