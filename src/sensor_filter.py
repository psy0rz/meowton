from peewee import Model, CharField, FloatField, IntegerField
from db import db


class SensorFilter(Model):
    """filter sudden spikes due to measurement errors"""
    name = CharField(primary_key=True)
    filter_diff = IntegerField(default=1000)

    class Meta:
        database = db

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__last_value = 0
        self.__prev_value = 0
        self.last_difference = 0

    def valid(self, value:int):
        ok = False
        diff = abs(value - self.__last_value)
        self.last_difference = diff
        if diff <= self.filter_diff:
            ok = True
        else:
            diff = abs(value - self.__prev_value)
            if diff <= self.filter_diff:
                ok = True

        self.__prev_value = self.__last_value
        self.__last_value = value

        return ok


db.create_tables([SensorFilter])
