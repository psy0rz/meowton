import time

from peewee import Model, CharField, IntegerField, FloatField

import settings
from db import db

MOVING_AVG_FACTOR=0.01

class Cat(Model):
    name = CharField(unique=True)
    weight = FloatField()

    feed_daily = IntegerField()
    feed_quota = IntegerField()
    feed_quota_last_hour = IntegerField()
    feed_quota_max = IntegerField()
    feed_quota_min = IntegerField()

    class Meta:
        database = db

    def __init__(self):
        super().__init__()

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

                if self.feed_quota > self.feed_quota_max:
                    self.feed_quota = self.feed_quota_max

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
        if self.feed_quota < self.feed_quota_min:
            self.feed_quota = self.feed_quota_min

    def update_weight(self, weight):
        """
        Update the weight value with moving average factor.

        Parameters:
        weight (float): The new weight value to be updated.

        Returns:
        None

        """
        self.weight = self.weight * (1-MOVING_AVG_FACTOR) + weight * (MOVING_AVG_FACTOR)


db.create_tables([Cat])
