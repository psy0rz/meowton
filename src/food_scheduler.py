import asyncio
import enum
import re
from datetime import datetime

from peewee import Model, CharField, IntegerField, TimestampField

from cat_detector import CatDetector
from db import db
from db_cat import DbCat
from feeder import Feeder


def hours_to_list(hours):
    list_hours = re.split(r'[\s,;]+', hours)
    return [int(hour) for hour in list_hours if hour.isdigit()]


class ScheduleMode(enum.Enum):
    UNLIMITED = 0  # nonstop feeding
    SCHEDULED = 1  # always feed at scheduled times
    ALL_QUOTA = 2  # feed at scheduled times, when all cats have quota
    CAT_QUOTA = 3  # only feed cat on scale that has quota
    DISABLED = 4  # never feed automaticly



class FoodScheduler(Model):
    """determines when to increase food quotas and when to dispense food."""
    mode = IntegerField(default=ScheduleMode.UNLIMITED.value)

    # times when to add to quota
    hours = CharField(default="9,13,17,21,1")

    prev_hour=TimestampField(default=0)

    class Meta:
        database = db

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)


    def update_quotas(self):
        """updates food quotas of all the cats"""

        for cat in DbCat.cats.values():
            cat.update_quota()

    def check_schedule(self):
        """check hourly schedule, return true if we should do our hourly things"""

        hour = datetime.now().hour
        if hour != self.prev_hour:
            self.prev_hour = hour
            self.save()
            if hour in hours_to_list(self.hours):
                return True

        return False

    async def task(self, feeder: Feeder, cat_detector: CatDetector):

        while True:


            if self.check_schedule():
                self.update_quotas()

                match self.mode:

                    case ScheduleMode.SCHEDULED.value:
                        print("FoodScheduler: Feeding at scheduled time")
                        feeder.request()


                    case ScheduleMode.ALL_QUOTA.value:
                        all_quota = False
                        for cat in DbCat.cats.values():
                            if cat.feed_quota <= 0:
                                all_quota = False

                        if all_quota:
                            print("FoodScheduler: All cats have quota, feeding.")
                            feeder.request()

                    case ScheduleMode.CAT_QUOTA.value:
                        #handled below
                        pass

            # unlimited feeding
            if self.mode == ScheduleMode.UNLIMITED.value:
                feeder.request()
            # always feed as long as detected cat has quota, unless we're disabled
            elif self.mode != ScheduleMode.DISABLED:
                if cat_detector.cat is not None and cat_detector.cat.feed_quota > 0:
                    feeder.request()

            await asyncio.sleep(1)

        pass


db.create_tables([FoodScheduler])
