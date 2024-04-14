import peewee

import settings
from scale_settings import save_scale_settings, load_scale_settings
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

    def save(self):
        save_scale_settings('cat', self.cat_reader.sensor_filter, self.cat_reader.scale.calibration,
                            self.cat_reader.scale)
        save_scale_settings('food', self.food_reader.sensor_filter, self.food_reader.scale.calibration,
                            self.food_reader.scale)

    def load(self):
        load_scale_settings('cat', self.cat_reader.sensor_filter, self.cat_reader.scale.calibration,
                            self.cat_reader.scale)
        load_scale_settings('food', self.food_reader.sensor_filter, self.food_reader.scale.calibration,
                            self.food_reader.scale)


meowton = Meowton(settings.dev_mode)
