import asyncio


import settings
from cat_detector import CatDetector
from feeder import Feeder
from food_counter import FoodCounter
from scale import Scale
from sensor_reader import SensorReader

#NOTE: my catfood weigh aprox 0.33g per piece

class Meowton:
    food_reader: SensorReader
    food_scale: Scale
    food_counter: FoodCounter

    cat_reader: SensorReader
    cat_scale: Scale
    cat_detector: CatDetector

    def __init__(self, sim: bool):

        self.init_food(sim)
        self.init_cat(sim)

        self.feeder= Feeder.get_or_create(id=1)[0]

    # food scale stuff and default settings
    def init_food(self, sim):
        name = 'food'

        self.food_scale = Scale.get_or_none(name=name)
        if self.food_scale is None:
            self.food_scale = Scale.create(name=name, stable_range=0.1, stable_measurements=2)

        self.food_reader = SensorReader(name, 23, 24, sim, self.food_scale.measurement)
        self.food_counter = FoodCounter()

    # cat scale stuff and default settings
    def init_cat(self, sim):
        name = 'cat'

        self.cat_scale = Scale.get_or_none(name=name)
        if self.cat_scale is None:
            self.cat_scale = Scale.create(name=name, stable_range=50, stable_measurements=25)

        self.cat_reader = SensorReader(name, 27, 17, sim, self.cat_scale.measurement)
        self.cat_detector = CatDetector()

    def start(self):
        self.food_reader.start()
        self.cat_reader.start()

        asyncio.create_task(self.cat_detector.task(self.cat_scale))
        asyncio.create_task(self.food_counter.task(self.food_scale))

    def stop(self):
        self.food_reader.stop()
        self.cat_reader.stop()


meowton = Meowton(settings.dev_mode)
