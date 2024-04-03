import sys

from peewee import Model, CharField, FloatField, IntegerField, DoesNotExist

from db import db
import scale_instances


dev_mode=sys.argv[1]=="dev"

class ScaleSettings(Model):
    name = CharField(primary_key=True)

    filter_diff = IntegerField()

    offset = IntegerField()
    factor = FloatField()

    stable_range = IntegerField()
    stable_measurements = IntegerField()
    stable_auto_tarre_count = IntegerField()
    stable_auto_tarre_max = IntegerField()

    class Meta:
        database = db


db.create_tables([ScaleSettings])


def save():
    ScaleSettings().replace(name='cat',
                            filter_diff=scale_instances.sensor_filter_cat.filter_diff,

                            offset=scale_instances.calibration_cat.offset,
                            factor=scale_instances.calibration_cat.factor,

                            stable_range=scale_instances.scale_cat.stable_range,
                            stable_measurements=scale_instances.scale_cat.stable_measurements,
                            stable_auto_tarre_count=scale_instances.scale_cat.stable_auto_tarre_count,
                            stable_auto_tarre_max=scale_instances.scale_cat.stable_auto_tarre_max,
                            ).execute()

    ScaleSettings().replace(name='food',
                            filter_diff=scale_instances.sensor_filter_food.filter_diff,

                            offset=scale_instances.calibration_food.offset,
                            factor=scale_instances.calibration_food.factor,

                            stable_range=scale_instances.scale_food.stable_range,
                            stable_measurements=scale_instances.scale_food.stable_measurements,
                            stable_auto_tarre_count=scale_instances.scale_food.stable_auto_tarre_count,
                            stable_auto_tarre_max=scale_instances.scale_food.stable_auto_tarre_max,
                            ).execute()


def load():
    try:
        food = ScaleSettings.get(name='food')

        scale_instances.sensor_filter_food.filter_diff = food.filter_diff

        scale_instances.calibration_food.offset = food.offset
        scale_instances.calibration_food.factor = food.factor

        scale_instances.calibration_food.stable_range = food.stable_range
        scale_instances.calibration_food.stable_measurements = food.stable_measurements
        scale_instances.calibration_food.stable_auto_tarre_count = food.stable_auto_tarre_count
        scale_instances.calibration_food.stable_auto_tarre_max = food.stable_auto_tarre_max

        cat = ScaleSettings.get(name='cat')

        scale_instances.sensor_filter_cat.filter_diff = cat.filter_diff

        scale_instances.calibration_cat.offset = cat.offset
        scale_instances.calibration_cat.factor = cat.factor

        scale_instances.calibration_cat.stable_range = cat.stable_range
        scale_instances.calibration_cat.stable_measurements = cat.stable_measurements
        scale_instances.calibration_cat.stable_auto_tarre_count = cat.stable_auto_tarre_count
        scale_instances.calibration_cat.stable_auto_tarre_max = cat.stable_auto_tarre_max




    except DoesNotExist:
        pass


load()
