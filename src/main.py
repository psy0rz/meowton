import time

import settings
from meowton import Meowton


meowton: None|Meowton

def main():
    #
    # sensor_filter_food = SensorFilter(1000)
    # calibration_food = ScaleSensorCalibration()
    # scale_food = Scale(calibration_food, 'food', stable_range=0.1, stable_measurements=1)
    # settings.load_scale_settings('food', sensor_filter_food, calibration_food, scale_food)

    # start
    global meowton
    meowton = Meowton(settings.dev_mode)
    meowton.start()
    if settings.headless:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            # the program execution will continue here after Ctrl+C
            meowton.stop()
            pass
    else:
        import ui_main
        ui_main.run(meowton.start, meowton.stop)


main()
