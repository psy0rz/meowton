import asyncio
from datetime import datetime

from peewee import Model, ForeignKeyField, DateTimeField, IntegerField, FloatField, TimestampField

from cat_detector import CatDetector
from db_cat import DbCat
from db import db
from food_counter import FoodCounter


class DbCatSession(Model):
    """one cat feeding-session. stores how long and how much a cat has eaten while on the scale."""

    # fields definition
    cat = ForeignKeyField(DbCat, backref='cat_session')
    start_time = TimestampField(default=datetime.now)
    length = IntegerField(default=0)
    amount = FloatField(default=0) # food aten
    weight = FloatField(default=0)

    class Meta:
        database = db

    @staticmethod
    async def task(food_counter:FoodCounter, cat_detector: CatDetector):


        session=None

        while await asyncio.wait([food_counter.event_ate.wait(), cat_detector.event_changed.wait()], return_when=asyncio.FIRST_COMPLETED):

            #cat changed?
            pass







db.create_tables([DbCatSession])
