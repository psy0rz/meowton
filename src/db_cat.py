import time

from peewee import Model, CharField, IntegerField, FloatField

import settings
from db import db

MOVING_AVG_FACTOR = 0.01


class DbCat(Model):
    name = CharField()
    weight = FloatField(default=0)
    feed_daily = IntegerField(default=0)

    feed_quota = IntegerField(default=0)
    feed_quota_last_hour = IntegerField(default=0)
    # feed_quota_max = IntegerField(default=0)
    # feed_quota_min = IntegerField(default=0)

    class Meta:
        database = db


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_quota(self):
        """
        Increments the food quota for the current hour based on the set feeding times and the daily quota.

        Parameters:
        None

        Returns:
        None

        Example Usage:
        add_quota()
        """

        (year, month, mday, hour, minute, second, weekday, yearday) = time.localtime()

        # hour changed?
        if self.feed_quota_last_hour.value != hour:

            self.feed_quota_last_hour.value = hour

            # feeding time?
            if hour in settings.feed_times:

                # update food quota
                quota_add = self.feed_daily / len(settings.feed_times)

                self.feed_quota.value = self.feed_quota.value + quota_add

                if self.feed_quota > self.feed_daily:
                    self.feed_quota = self.feed_daily

    def quota_time(self):
        """
        Calculates the time it takes to deplete the feed quota. (or to restore it, when its negative)

        Returns:
            float: The time in minutes it takes to deplete the feed quota.
        """
        return self.feed_quota / (self.feed_daily / (24 * 60))

    def ate(self, weight):
        """
        Decreases the feed_quota attribute by the given weight.

        Parameters:
            weight (float): The weight to be subtracted from the feed_quota.

        Returns:
            None

        """
        self.feed_quota = self.feed_quota - weight
        if self.feed_quota < -self.feed_daily:
            self.feed_quota = -self.feed_daily

    def update_weight(self, weight):
        """
        Update the weight value with moving average factor.

        Parameters:
        weight (float): The new weight value to be updated.

        Returns:
        None

        """
        self.weight = self.weight * (1 - MOVING_AVG_FACTOR) + weight * (MOVING_AVG_FACTOR)




db.create_tables([DbCat])
