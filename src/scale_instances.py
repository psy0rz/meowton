import settings
from scale import Scale
from scale_sensor_calibration import ScaleSensorCalibration
from sensor_filter import SensorFilter

sensor_filter_cat=SensorFilter(10000)
calibration_cat=ScaleSensorCalibration()
calibration_cat.factor=-0.5
scale_cat=Scale(calibration_cat,'cat')

sensor_filter_food=SensorFilter(100000)
calibration_food=ScaleSensorCalibration()
scale_food=Scale(calibration_food, 'food')

settings.load()
