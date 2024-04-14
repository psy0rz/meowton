import time

import scale_instances
import scale_reader
import settings
from scale import Scale
from scale_sensor_calibration import ScaleSensorCalibration
from sensor_filter import SensorFilter


def startup():
    scale_reader.start(scale_instances.scale_cat, scale_instances.scale_food, scale_instances.sensor_filter_cat,
                       scale_instances.sensor_filter_food)

def shutdown():
    scale_reader.stop()


def main():
    sensor_filter_cat = SensorFilter(1000)
    calibration_cat = ScaleSensorCalibration()
    scale_cat = Scale(calibration_cat, 'cat')
    settings.load_scale_settings('cat', sensor_filter_cat, calibration_cat, scale_cat)

    sensor_filter_food = SensorFilter(1000)
    calibration_food = ScaleSensorCalibration()
    scale_food = Scale(calibration_food, 'food', stable_range=0.1, stable_measurements=1)
    settings.load_scale_settings('food', sensor_filter_food, calibration_food, scale_food)

    #start
    if settings.headless:
        startup()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            # the program execution will continue here after Ctrl+C
            shutdown()
            pass
    else:
        import ui_main
        ui_main.run(startup, shutdown)


main()