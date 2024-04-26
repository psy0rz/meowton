import time

from peewee import Model, CharField, IntegerField, FloatField, TimestampField

from db import db

MOVING_AVG_FACTOR = 0.1


class DbCat(Model):
    """a cat and its weight and food quota"""
    name = CharField()
    weight = FloatField(default=0)
    feed_daily = IntegerField(default=0)

    feed_quota = FloatField(default=0)
    feed_quota_last_update = IntegerField(default=time.time)

    # feed_quota_max = IntegerField(default=0)
    # feed_quota_min = IntegerField(default=0)

    cats: dict[int, 'DbCat'] = {}

    class Meta:
        database = db

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_quota(self):
        """update the quota according to daily quota and last update time"""

        diff = time.time() - self.feed_quota_last_update

        # update food quota
        quota_add = (self.feed_daily / (24 * 60 * 60)) * diff

        if (quota_add > 0):
            self.feed_quota = self.feed_quota + quota_add

            if self.feed_quota > self.feed_daily:
                self.feed_quota = self.feed_daily

        self.feed_quota_last_update = time.time()

        print(f"Cat [{self.name}]: added {quota_add:0.2f}g to quota. (total {self.feed_quota:0.2f}g)")
        self.save()

    def quota_time(self):
        return self.feed_quota / (self.feed_daily / (24 * 60))

    def ate(self, weight):

        print(f"Cat [{self.name}]: ate {weight:0.2f}g (quota {self.feed_quota:0.2f})g")
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

    @staticmethod
    def reload():

        # cache all cats since they will be referenced and updated from multiple locations
        DbCat.cats = {}

        for cat in DbCat.select():
            DbCat.cats[cat.id] = cat

    def delete_instance(self, **kwargs):
        super().delete_instance(**kwargs)
        if self.id in DbCat.cats:
            del (DbCat.cats[self.id])

    def save(self, **kwargs):
        super().save(**kwargs)
        if self.id not in DbCat.cats:
            DbCat.cats[self.id] = self


db.create_tables([DbCat])
DbCat.reload()
