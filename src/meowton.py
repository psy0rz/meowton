from sensor_reader import SensorReader


class Meowton:
    def __init__(self, sim: bool):
        self.food_reader = SensorReader('cat', 23, 24, sim)

        self.cat_reader = SensorReader('food', 27, 17, sim)
        # settings.load_scale_settings('cat', sensor_filter_cat, calibration_cat, scale_cat)

    def start(self):
        self.food_reader.start()
        self.cat_reader.start()

    def stop(self):
        self.food_reader.stop()
        self.cat_reader.stop()
