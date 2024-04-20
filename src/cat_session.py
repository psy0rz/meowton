from datetime import datetime

from peewee import Model, ForeignKeyField, DateTimeField, IntegerField, FloatField, TimestampField

from cat import Cat
from db import db


class CatSession(Model):
    """one cat feeding-session. stores how long and how much a cat has eaten while on the scale."""

    # fields definition
    cat = ForeignKeyField(Cat, backref='cat_session')
    start_time = TimestampField(default=datetime.now)
    length = IntegerField(default=0)
    amount = FloatField(default=0)
    weight = FloatField(default=0)

    class Meta:
        database = db


db.create_tables([CatSession])
