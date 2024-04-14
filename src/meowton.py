
import settings
from scale import Scale
from sensor_filter import SensorFilter
# from scale_settings import save_scale_settings, load_scale_settings
from sensor_reader import SensorReader


class Meowton:

    food_reader: SensorReader
    cat_reader: SensorReader

    def __init__(self, sim: bool):

        self.init_food(sim)
        self.init_cat(sim)
        # settings.load_scale_settings('cat', sensor_filter_cat, calibration_cat, scale_cat)

    # food scale stuff and default settings
    def init_food(self, sim):
        name='food'

        scale=Scale.get_or_none(name=name)
        if scale is None:
            scale=Scale.create(name=name, stable_range=50, stable_measurements=25)

        sensor_filter=SensorFilter.get_or_none(name=name)
        if sensor_filter is None:
            sensor_filter=SensorFilter.create(name='food', filter_diff=1000)

        self.food_reader = SensorReader('cat', 23, 24, sim, sensor_filter, scale)

    # cat scale stuff and default settings
    def init_cat(self, sim):
        name = 'cat'

        scale = Scale.get_or_none(name=name)
        if scale is None:
            scale = Scale.create(name=name, stable_range=0.1, stable_measurements=2)

        sensor_filter = SensorFilter.get_or_none(name=name)
        if sensor_filter is None:
            sensor_filter = SensorFilter.create(name='food', filter_diff=1000)

        self.cat_reader = SensorReader('food', 27, 17, sim, sensor_filter, scale)


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
