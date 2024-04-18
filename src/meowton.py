import asyncio

import settings
from cat_detector import CatDetector
from scale import Scale
from sensor_filter import SensorFilter
# from scale_settings import save_scale_settings, load_scale_settings
from sensor_reader import SensorReader


class Meowton:
    food_reader: SensorReader
    food_scale:Scale

    cat_reader: SensorReader
    cat_scale:Scale
    cat_detector: CatDetector

    def __init__(self, sim: bool):

        self.init_food(sim)
        self.init_cat(sim)
        # settings.load_scale_settings('cat', sensor_filter_cat, calibration_cat, scale_cat)

    # food scale stuff and default settings
    def init_food(self, sim):
        name = 'food'

        self.food_scale = Scale.get_or_none(name=name)
        if self.food_scale is None:
            self.food_scale = Scale.create(name=name, stable_range=0.1, stable_measurements=2)

        self.food_reader = SensorReader(name, 23, 24, sim, self.food_scale.measurement)

    # cat scale stuff and default settings
    def init_cat(self, sim):
        name = 'cat'

        self.cat_scale = Scale.get_or_none(name=name)
        if self.cat_scale is None:
            self.cat_scale= Scale.create(name=name, stable_range=50, stable_measurements=25)

        self.cat_reader = SensorReader(name, 27, 17, sim, self.cat_scale.measurement)
        self.cat_detector = CatDetector(self.cat_scale)

    def start(self):
        self.food_reader.start()
        self.cat_reader.start()

    def stop(self):
        self.food_reader.stop()
        self.cat_reader.stop()

    # def save(self):
    #     save_scale_settings('cat', self.cat_reader.sensor_filter, self.cat_reader.scale.calibration,
    #                         self.cat_reader.scale)
    #     save_scale_settings('food', self.food_reader.sensor_filter, self.food_reader.scale.calibration,
    #                         self.food_reader.scale)
    #
    # def load(self):
    #     load_scale_settings('cat', self.cat_reader.sensor_filter, self.cat_reader.scale.calibration,
    #                         self.cat_reader.scale)
    #     load_scale_settings('food', self.food_reader.sensor_filter, self.food_reader.scale.calibration,
    #                         self.food_reader.scale)


meowton = Meowton(settings.dev_mode)
