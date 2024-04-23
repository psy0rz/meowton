import asyncio

from peewee import Model, CharField, BooleanField
import re

from db import db
from feeder import Feeder
from scale import Scale


def hours_to_list(hours):
    list_hours = re.split(r'[\s,;]+', hours)
    return [int(hour) for hour in list_hours if hour.isdigit()]


class FoodScheduler(Model):
    # always ensure full bowl regardless of schedule or quotas
    feed_unlimited = BooleanField(default=True)

    # dispense food at scheduled times, regardless of quota
    feed_on_schedule = BooleanField(default=False)

    # displense food as soon as all cats have quota
    feed_when_quota = BooleanField(default=False)

    # times when to add to quota
    hours = CharField(default="9, 13, 17, 21, 1")

    class Meta:
        database = db

    async def task(self, feeder: Feeder, food_scale: Scale):
        while True:

            if self.feed_unlimited:
                print("FoodScheduler: Unlimited, waiting for foodscale change..")
                await food_scale.event_stable.wait()
                print("FoodScheduler: req")
                feeder.request()
                continue

            await asyncio.sleep(1)

        pass


db.create_tables([FoodScheduler])
