import time

import scale_instances
import scale_reader
import settings


def startup():
    scale_reader.start(scale_instances.scale_cat, scale_instances.scale_food, scale_instances.sensor_filter_cat,
                       scale_instances.sensor_filter_food)

def shutdown():
    scale_reader.stop()

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
