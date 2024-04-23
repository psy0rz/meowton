import asyncio
import enum
from datetime import datetime

from peewee import Model, CharField, BooleanField, IntegerField
import re

from db import db
from db_cat import DbCat
from feeder import Feeder
from scale import Scale


def hours_to_list(hours):
    list_hours = re.split(r'[\s,;]+', hours)
    return [int(hour) for hour in list_hours if hour.isdigit()]


class ScheduleMode(enum.Enum):
    UNLIMITED = 0
    SCHEDULED = 1
    ALL_QUOTA = 2  # all cats have quota
    CAT_QUOTA = 3  # cat on scale has quota
    DISABLED = 4  # never feed automaticly


class FoodScheduler(Model):

    mode = IntegerField(default=ScheduleMode.UNLIMITED.value)

    # times when to add to quota
    hours = CharField(default="9,13,17,21,1")

    class Meta:
        database = db

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.prev_hour = datetime.now().hour

    def update_quotas(self):
        """updates food quotas of all the cats"""

        for cat in DbCat.select():
            cat.update_quota()

    def check_schedule(self, feeder: Feeder):
        """check hourly schedule"""

        hour = datetime.now().hour
        if hour != self.prev_hour:
            self.prev_hour = hour
            if hour in hours_to_list(self.hours):
                print(f"FoodScheduler: Doing scheduled stuff of hour {hour}")
                if self.mode==ScheduleMode.SCHEDULED:
                    feeder.request()

    async def task(self, feeder: Feeder, food_scale: Scale):

        prev_hour = None

        while True:

            self.check_schedule(feeder)

            if self.mode==ScheduleMode.UNLIMITED:
                if food_scale.stable:
                    feeder.request()

                print("FoodScheduler: Unlimited, waiting for foodscale change..")
                await food_scale.event_stable.wait()
                continue

            # if self.feed_when_quota:

            await asyncio.sleep(1)

        pass


db.create_tables([FoodScheduler])
