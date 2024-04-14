import sys

from peewee import DoesNotExist

from meowton import meowton
from scale import Scale
from scale_sensor_calibration import ScaleSensorCalibration
from scale_settings import ScaleSettings
from sensor_filter import SensorFilter

dev_mode = "dev" in sys.argv[1]
if dev_mode:
    print("Using dev mode")
headless = "headless" in sys.argv[1]
if headless:
    print("Running in headless mode")

feed_times = [9, 13, 17, 21, 1]



