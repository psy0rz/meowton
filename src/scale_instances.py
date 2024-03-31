from scale import Scale
from scale_sensor_calibration import ScaleSensorCalibration

calibration_cat=ScaleSensorCalibration()
scale_cat=Scale(calibration_cat,'cat')

calibration_food=ScaleSensorCalibration()
scale_food=Scale(calibration_food, 'food')
