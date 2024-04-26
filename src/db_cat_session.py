import time

from peewee import Model, ForeignKeyField, IntegerField, FloatField, TimestampField

from db import db
from db_cat import DbCat


class DbCatSession(Model):
    """one cat feeding-session. stores how long and how much a cat has eaten while on the scale."""

    # fields definition
    cat = ForeignKeyField(DbCat, backref='cat_session')
    start_time = TimestampField(default=time.time)
    length = IntegerField(default=0)
    amount = FloatField(default=0)  # food aten
    ate = FloatField(default=0)

    class Meta:
        database = db

    def end_session(self):
        self.length = int(time.time() - self.start_time)
        self.save()


db.create_tables([DbCatSession])
