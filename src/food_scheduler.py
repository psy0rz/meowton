import asyncio
from datetime import datetime

from peewee import Model, CharField, BooleanField
import re

from db import db
from db_cat import DbCat
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

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.prev_hour=datetime.now().hour

    def update_quotas(self):
        """updates food quotas of all the cats"""

        for cat in DbCat.select():
            cat.update_quota()

    def check_schedule(self, feeder:Feeder):
        """check hourly schedule"""

        hour = datetime.now().hour
        if hour != self.prev_hour:
            self.prev_hour = hour
            if hour in hours_to_list(self.hours):
                print(f"FoodScheduler: Doing scheduled stuff of hour {hour}")
                if self.feed_on_schedule:
                    feeder.request()

    async def task(self, feeder: Feeder, food_scale: Scale):

        prev_hour=None

        while True:

            self.check_schedule(feeder)

            if self.feed_unlimited:
                if food_scale.stable:
                    feeder.request()

                print("FoodScheduler: Unlimited, waiting for foodscale change..")
                await food_scale.event_stable.wait()
                continue

            await asyncio.sleep(1)

        pass


db.create_tables([FoodScheduler])
