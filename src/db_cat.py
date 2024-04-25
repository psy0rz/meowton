import time

from peewee import Model, CharField, IntegerField, FloatField, TimestampField

import settings
from db import db

MOVING_AVG_FACTOR = 0.01


class DbCat(Model):
    """a cat and its weight and food quota"""
    name = CharField()
    weight = FloatField(default=0)
    feed_daily = IntegerField(default=0)

    feed_quota = FloatField(default=0)
    feed_quota_last_update = TimestampField(default=0)

    # feed_quota_max = IntegerField(default=0)
    # feed_quota_min = IntegerField(default=0)

    class Meta:
        database = db

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_quota(self):
        """update the quota according to daily quota and last update time"""

        diff = time.time() - self.feed_quota_last_update

        # update food quota
        quota_add = (self.feed_daily / 24 * 60 * 60) * diff

        if (quota_add > 0):
            self.feed_quota.value = self.feed_quota.value + quota_add

            if self.feed_quota > self.feed_daily:
                self.feed_quota = self.feed_daily

        self.feed_quota_last_update = time.time()
        self.save()

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

        if self.feed_quota > self.feed_daily:
            self.feed_quota = self.feed_daily

        self.save()

    def update_weight(self, weight):
        """
        Update the weight value with moving average factor.

        Parameters:
        weight (float): The new weight value to be updated.

        Returns:
        None

        """

        if self.weight == 0:
            self.weight = weight
        else:
            self.weight = self.weight * (1 - MOVING_AVG_FACTOR) + weight * (MOVING_AVG_FACTOR)
        self.save()


db.create_tables([DbCat])

cats: dict[int, DbCat]={}

def reload_cats(self):
    # cache all cats since they will be referenced and updated from multiple locations
    global cats
    cats = {}

    for cat in DbCat.select():
        self.cats[cat.id] = cat
