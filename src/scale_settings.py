# from peewee import Model, CharField, IntegerField, FloatField, DoesNotExist
#
# from scale import Scale
# from scale_sensor_calibration import ScaleSensorCalibration
# from sensor_filter import SensorFilter
# from db import db
#
# # NOTE: the reason we do it like, is so that Scale() and related classes stay reusable without depending on peewee or some other database.
#
# class ScaleSettings(Model):
#     name = CharField(primary_key=True)
#
#     filter_diff = IntegerField()
#
#     offset = IntegerField()
#     factor = FloatField()
#
#     stable_range = FloatField()
#     stable_measurements = IntegerField()
#     stable_auto_tarre_count = IntegerField()
#     stable_auto_tarre_max = IntegerField()
#
#     class Meta:
#         database = db
#
#
# db.create_tables([ScaleSettings])
#
#
# def load_scale_settings(name: str, sensor_filter: SensorFilter, calibration: ScaleSensorCalibration, scale: Scale):
#     try:
#         food = ScaleSettings.get(name=name)
#
#         sensor_filter.filter_diff = food.filter_diff
#
#         calibration.offset = food.offset
#         calibration.factor = food.factor
#
#         scale.stable_range = food.stable_range
#         scale.stable_measurements = food.stable_measurements
#         scale.stable_auto_tarre_count = food.stable_auto_tarre_count
#         scale.stable_auto_tarre_max = food.stable_auto_tarre_max
#     except DoesNotExist as e:
#         print(e)
#         pass
#
#
# def save_scale_settings(name: str, sensor_filter: SensorFilter, calibration: ScaleSensorCalibration, scale: Scale):
#     ScaleSettings().replace(name=name,
#                             filter_diff=sensor_filter.filter_diff,
#
#                             offset=calibration.offset,
#                             factor=calibration.factor,
#
#                             stable_range=scale.stable_range,
#                             stable_measurements=scale.stable_measurements,
#                             stable_auto_tarre_count=scale.stable_auto_tarre_count,
#                             stable_auto_tarre_max=scale.stable_auto_tarre_max,
#                             ).execute()
